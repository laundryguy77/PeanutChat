import base64
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_APP_NAME,
    OPENROUTER_APP_URL,
    OPENROUTER_BASE_URL,
)

logger = logging.getLogger(__name__)


class OpenRouterService:
    """OpenRouter chat client (OpenAI-compatible).

    Notes:
    - Streaming responses are SSE. We normalize events to match the OllamaService stream
      shape used by `app/routers/chat.py`:
        {"message": {"content": "..."}} / {"message": {"thinking": "..."}} / {"message": {"tool_calls": [...]}}
        plus a terminal {"done": True} marker.
    - Tool call deltas are accumulated during streaming and emitted once at the end.
    """

    def __init__(self):
        self.base_url = OPENROUTER_BASE_URL.rstrip("/")
        self.api_key = OPENROUTER_API_KEY
        self.client = httpx.AsyncClient(timeout=300.0)

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Optional attribution headers (recommended by OpenRouter)
        if OPENROUTER_APP_URL:
            headers["HTTP-Referer"] = OPENROUTER_APP_URL
        if OPENROUTER_APP_NAME:
            headers["X-Title"] = OPENROUTER_APP_NAME
        return headers

    @staticmethod
    def _guess_image_mime(image_b64: str) -> str:
        # Best-effort sniff based on magic bytes.
        try:
            head = image_b64[:96]
            pad = "=" * (-len(head) % 4)
            raw = base64.b64decode(head + pad)
        except Exception:
            return "image/png"

        if raw.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if raw.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if raw.startswith(b"GIF87a") or raw.startswith(b"GIF89a"):
            return "image/gif"
        if raw.startswith(b"RIFF") and len(raw) >= 12 and raw[8:12] == b"WEBP":
            return "image/webp"
        return "image/png"

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Ollama-style image payloads to OpenAI-style multipart content.

        - Ollama: {"role":"user","content":"...","images":["<b64>", ...]}
        - OpenAI: {"role":"user","content":[{"type":"text","text":"..."},{"type":"image_url","image_url":{"url":"data:...;base64,<b64>"}}]}
        """
        normalized: List[Dict[str, Any]] = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue

            # Copy to avoid mutating caller
            m = dict(msg)

            # Normalize tool_calls arguments for OpenAI compatibility
            tool_calls = m.get("tool_calls")
            if isinstance(tool_calls, list):
                fixed = []
                for tc in tool_calls:
                    if not isinstance(tc, dict):
                        continue
                    tc2 = dict(tc)
                    fn = tc2.get("function")
                    if isinstance(fn, dict):
                        fn2 = dict(fn)
                        args = fn2.get("arguments")
                        if isinstance(args, dict):
                            fn2["arguments"] = json.dumps(args)
                        tc2["function"] = fn2
                    fixed.append(tc2)
                m["tool_calls"] = fixed

            # Convert images -> multipart content
            images = m.pop("images", None)
            if isinstance(images, list) and images:
                parts: List[Dict[str, Any]] = []
                text = m.get("content")
                if isinstance(text, str) and text:
                    parts.append({"type": "text", "text": text})
                for img_b64 in images:
                    if not isinstance(img_b64, str) or not img_b64:
                        continue
                    mime = self._guess_image_mime(img_b64)
                    parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{img_b64}"},
                    })
                m["content"] = parts

            # Tool result messages should not include Ollama-only keys
            if m.get("role") == "tool":
                m.pop("tool_name", None)

            normalized.append(m)
        return normalized

    def _map_options(self, options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Map app settings/ollama-style options to OpenAI/OpenRouter params."""
        if not options:
            return {}
        out: Dict[str, Any] = {}
        if "temperature" in options and options["temperature"] is not None:
            out["temperature"] = options["temperature"]
        if "top_p" in options and options["top_p"] is not None:
            out["top_p"] = options["top_p"]
        # Intentionally ignore Ollama-specific keys like num_ctx, repeat_penalty, top_k.
        return out

    def _map_thinking(self, think: Optional[bool]) -> Dict[str, Any]:
        """Best-effort mapping for 'thinking' toggle.

        OpenRouter supports passing provider-specific parameters through the OpenAI schema.
        We send a generic reasoning hint that is safe for most OpenAI-compatible stacks.
        """
        if not think:
            return {}
        return {
            "reasoning": {"effort": "high"},
            "include_reasoning": True,
        }

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
        think: Optional[bool] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "stream": True,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        payload.update(self._map_options(options))
        payload.update(self._map_thinking(think))

        # Accumulate tool call deltas (OpenAI streaming sends partial args)
        tool_calls_accum: Dict[int, Dict[str, Any]] = {}

        url = f"{self.base_url}/chat/completions"
        headers = self._headers()

        async with self.client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                # OpenAI-style SSE lines look like: "data: {...}"
                if not line.startswith("data:"):
                    continue

                data_str = line[len("data:"):].strip()
                if not data_str:
                    continue
                if data_str == "[DONE]":
                    break

                try:
                    evt = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choices = evt.get("choices") or []
                for choice in choices:
                    delta = (choice or {}).get("delta") or {}

                    # Reasoning/thinking tokens (provider-specific keys vary)
                    thinking = None
                    if isinstance(delta.get("reasoning"), str):
                        thinking = delta.get("reasoning")
                    elif isinstance(delta.get("reasoning_content"), str):
                        thinking = delta.get("reasoning_content")
                    elif isinstance(delta.get("thinking"), str):
                        thinking = delta.get("thinking")

                    if thinking:
                        yield {"message": {"thinking": thinking}}

                    content = delta.get("content")
                    if isinstance(content, str) and content:
                        yield {"message": {"content": content}}

                    tool_calls = delta.get("tool_calls")
                    if isinstance(tool_calls, list) and tool_calls:
                        for tc in tool_calls:
                            if not isinstance(tc, dict):
                                continue
                            idx = tc.get("index", 0)
                            try:
                                idx_int = int(idx)
                            except Exception:
                                idx_int = 0

                            existing = tool_calls_accum.get(idx_int)
                            if not existing:
                                existing = {
                                    "id": tc.get("id"),
                                    "type": tc.get("type", "function"),
                                    "function": {"name": None, "arguments": ""},
                                }
                                tool_calls_accum[idx_int] = existing

                            if tc.get("id"):
                                existing["id"] = tc.get("id")

                            fn = tc.get("function") or {}
                            if isinstance(fn, dict):
                                if fn.get("name"):
                                    existing["function"]["name"] = fn.get("name")
                                args_piece = fn.get("arguments")
                                if isinstance(args_piece, str) and args_piece:
                                    existing["function"]["arguments"] += args_piece

        # Emit accumulated tool calls (if any) once at end
        if tool_calls_accum:
            ordered = [tool_calls_accum[i] for i in sorted(tool_calls_accum.keys())]
            yield {"message": {"tool_calls": ordered}, "done": True}
            return

        yield {"done": True}

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
        think: Optional[bool] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        payload.update(self._map_options(options))
        payload.update(self._map_thinking(think))

        url = f"{self.base_url}/chat/completions"
        headers = self._headers()
        resp = await self.client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self.client.aclose()


openrouter_service = OpenRouterService()
