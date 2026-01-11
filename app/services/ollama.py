import httpx
import json
from typing import AsyncGenerator, List, Optional, Dict, Any
from app.config import OLLAMA_BASE_URL, get_settings


class OllamaService:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.client = httpx.AsyncClient(timeout=300.0)
        self._vision_models_cache = None

    async def list_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from Ollama"""
        response = await self.client.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])

    async def get_model_capabilities(self, model_name: str) -> dict:
        """Get model capabilities from Ollama API"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "capabilities": data.get("capabilities", []),
                    "details": data.get("details", {}),
                    "template": data.get("template", "")
                }
        except Exception as e:
            print(f"Failed to get model capabilities: {e}")
        return {"capabilities": [], "details": {}, "template": ""}

    async def is_vision_model(self, model_name: str) -> bool:
        """Check if a model supports vision/images"""
        info = await self.get_model_capabilities(model_name)
        print(f"[OLLAMA] Checking vision for {model_name}, capabilities: {info['capabilities']}")

        # Check capabilities array from Ollama API
        if "vision" in info["capabilities"]:
            print(f"[OLLAMA] {model_name} has vision capability from API")
            return True

        # Fallback: check model name for vision keywords
        vision_keywords = ['vision', 'vl', 'llava', 'bakllava', 'moondream', 'cogvlm', 'yi-vl', 'minicpm-v']
        model_lower = model_name.lower()
        for keyword in vision_keywords:
            if keyword in model_lower:
                print(f"[OLLAMA] {model_name} matched vision keyword: {keyword}")
                return True

        print(f"[OLLAMA] {model_name} is NOT a vision model")
        return False

    async def supports_tools(self, model_name: str) -> bool:
        """Check if a model supports function/tool calling"""
        info = await self.get_model_capabilities(model_name)

        # Check capabilities array from Ollama API
        if "tools" in info["capabilities"]:
            return True

        # Fallback: check template for tool-related syntax
        template = info["template"].lower()
        if any(kw in template for kw in ['tool', 'function', '<tools>', '<<tool']):
            return True

        return False

    def build_system_prompt(self, persona: Optional[str] = None, has_vision: bool = True, has_tools: bool = True) -> str:
        """Build system prompt with optional persona"""
        if has_tools:
            base_prompt = """You are a helpful AI assistant with the ability to search the web, search conversation history, and generate images.

Available tools:
- web_search: Use this when asked about current events, news, or information you need to look up online.
- search_conversations: Use this when the user references something from a previous conversation, asks "remember when we discussed...", or when you need context from past chats.
- generate_image: Use this when a user wants to create/generate an image from a description.

When the user refers to past discussions or asks about something you talked about before, use the search_conversations tool to find relevant context."""
        else:
            base_prompt = """You are a helpful AI assistant. You provide accurate, helpful, and thoughtful responses to user questions."""

        if persona:
            persona_intro = f"""You are embodying the following persona. Stay in character at all times and never break character, even if asked directly about being an AI or your true nature.

PERSONA:
{persona}

---

"""
            if has_tools:
                return persona_intro + """Additionally, you can generate images from descriptions using the generate_image tool and search the web using the web_search tool when needed."""
            else:
                return persona_intro.rstrip()

        return base_prompt

    def build_messages(
        self,
        user_message: str,
        history: List[Dict[str, Any]],
        persona: Optional[str] = None,
        images: Optional[List[str]] = None,
        is_vision_model: bool = True,
        has_tools: bool = True
    ) -> List[Dict[str, Any]]:
        """Build messages array for Ollama API"""
        messages = []

        # System prompt with persona
        messages.append({
            "role": "system",
            "content": self.build_system_prompt(persona, has_vision=is_vision_model, has_tools=has_tools)
        })

        # Add conversation history (strip images if not vision model)
        for msg in history:
            if is_vision_model:
                messages.append(msg)
            else:
                # Remove images from non-vision model messages
                clean_msg = {k: v for k, v in msg.items() if k != "images"}
                messages.append(clean_msg)

        # Add current user message
        user_msg = {"role": "user", "content": user_message}
        if images and is_vision_model:
            user_msg["images"] = images
            print(f"[OLLAMA] Adding {len(images)} images to user message")
        messages.append(user_msg)

        print(f"[OLLAMA] Built {len(messages)} messages, user_msg has images: {'images' in user_msg}")
        return messages

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict]] = None,
        options: Optional[Dict] = None,
        think: Optional[bool] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat response from Ollama"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }

        if tools:
            payload["tools"] = tools

        if options:
            payload["options"] = options

        if think is not None:
            # Some models (gpt-oss) need string values: "low", "medium", "high"
            # Others (qwq, deepseek-r1) need boolean
            model_lower = model.lower()
            if 'gpt-oss' in model_lower:
                # gpt-oss uses string reasoning effort levels
                payload["think"] = "high" if think else "low"
                print(f"[OLLAMA] gpt-oss model: setting think='{'high' if think else 'low'}'")
            else:
                payload["think"] = think
                print(f"[OLLAMA] Sending request with think={think}")

        print(f"[OLLAMA] Payload keys: {list(payload.keys())}")

        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict]] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        if tools:
            payload["tools"] = tools

        if options:
            payload["options"] = options

        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()


# Global service instance
ollama_service = OllamaService()
