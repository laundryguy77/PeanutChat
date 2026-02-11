from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.ollama import ollama_service


PROVIDER_OLLAMA = "ollama"
PROVIDER_OPENROUTER = "openrouter"


# Curated OpenRouter models (from Not-A-Project/prompts/peanutchat_refactor.md)
# Keep these stable so the model selector stays predictable during refactor work.
_OPENROUTER_MODELS: List[Dict[str, Any]] = [
    {
        "name": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion"],
        "supports_tools": False,
        "supports_vision": False,
        "supports_thinking": False,
        "context_window": 32768,
        "parameter_size": "24B class",
    },
    {
        "name": "qwen/qwen3-next-80b-a3b-instruct:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools"],
        "supports_tools": True,
        "supports_vision": False,
        "supports_thinking": False,
        "context_window": 262144,
        "parameter_size": "80B/3B active (A3B)",
    },
    {
        "name": "qwen/qwen3-coder:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools"],
        "supports_tools": True,
        "supports_vision": False,
        "supports_thinking": False,
        "context_window": 262000,
        "parameter_size": "480B/35B active",
    },
    {
        "name": "openai/gpt-oss-120b:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools", "thinking"],
        "supports_tools": True,
        "supports_vision": False,
        "supports_thinking": True,
        "context_window": 131072,
        "parameter_size": "117B/5.1B active",
    },
    {
        "name": "nvidia/nemotron-3-nano-30b-a3b:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools", "thinking"],
        "supports_tools": True,
        "supports_vision": False,
        "supports_thinking": True,
        "context_window": 256000,
        "parameter_size": "30B/3B active (A3B)",
    },
    {
        "name": "tngtech/deepseek-r1t2-chimera:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "thinking"],
        "supports_tools": False,
        "supports_vision": False,
        "supports_thinking": True,
        "context_window": 163840,
        "parameter_size": "671B",
    },
    {
        "name": "arcee-ai/trinity-large-preview:free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools"],
        "supports_tools": True,
        "supports_vision": False,
        "supports_thinking": False,
        "context_window": 131000,
        "parameter_size": "400B/13B active",
    },
    {
        "name": "openrouter/free",
        "provider": PROVIDER_OPENROUTER,
        "capabilities": ["completion", "tools", "vision", "thinking"],
        "supports_tools": True,
        "supports_vision": True,
        "supports_thinking": True,
        "context_window": 200000,
        "parameter_size": None,
    },
]

_OPENROUTER_MODEL_IDS = {m["name"] for m in _OPENROUTER_MODELS}


def is_openrouter_model(model_id: str) -> bool:
    return model_id in _OPENROUTER_MODEL_IDS


def get_openrouter_models() -> List[Dict[str, Any]]:
    # Shallow copy is fine; values are primitives.
    return [dict(m) for m in _OPENROUTER_MODELS]


def get_openrouter_model_info(model_id: str) -> Optional[Dict[str, Any]]:
    for m in _OPENROUTER_MODELS:
        if m["name"] == model_id:
            return dict(m)
    return None


def get_model_provider(model_id: str) -> str:
    return PROVIDER_OPENROUTER if is_openrouter_model(model_id) else PROVIDER_OLLAMA


async def get_model_capabilities(model_id: str) -> Dict[str, Any]:
    """Return a unified capability payload for both providers."""
    if is_openrouter_model(model_id):
        info = get_openrouter_model_info(model_id) or {}
        return {
            "supports_vision": bool(info.get("supports_vision")),
            "supports_tools": bool(info.get("supports_tools")),
            "supports_thinking": bool(info.get("supports_thinking")),
            "context_window": int(info.get("context_window") or 4096),
            "capabilities": info.get("capabilities", []),
            "provider": PROVIDER_OPENROUTER,
        }

    caps = await ollama_service.get_comprehensive_capabilities(model_id)
    caps["provider"] = PROVIDER_OLLAMA
    return caps

