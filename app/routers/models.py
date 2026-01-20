from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import subprocess
import logging
from app.services.ollama import ollama_service
from app.config import get_settings, update_settings
from app.models.schemas import ModelSelectRequest
from app.middleware.auth import require_auth, optional_auth
from app.models.auth_schemas import UserResponse
from app.services.user_profile_service import get_user_profile_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["models"])

# Keywords indicating uncensored/adult models
ADULT_MODEL_KEYWORDS = ["uncensored", "abliterated", "nsfw", "adult", "xxx"]


async def get_vram_usage() -> dict:
    """Get GPU VRAM usage via nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            total_used = 0
            total_mem = 0
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2:
                    total_used += int(parts[0].strip())
                    total_mem += int(parts[1].strip())

            if total_mem > 0:
                return {
                    "used_mb": total_used,
                    "total_mb": total_mem,
                    "percent": round((total_used / total_mem) * 100, 1),
                    "available": True
                }
    except FileNotFoundError:
        logger.debug("nvidia-smi not found - no NVIDIA GPU")
    except subprocess.TimeoutExpired:
        logger.warning("nvidia-smi timed out")
    except Exception as e:
        logger.warning(f"VRAM query failed: {e}")

    return {"used_mb": 0, "total_mb": 0, "percent": 0, "available": False}

@router.get("")
async def list_models(user: Optional[UserResponse] = Depends(optional_auth)) -> Dict[str, Any]:
    """List chat-capable models with their capabilities.

    Returns filtered list excluding embedding models, with capability flags.
    Filters uncensored models when adult mode is disabled.
    """
    try:
        models = await ollama_service.get_chat_models_with_capabilities()
        current = get_settings().model

        # Check adult mode status if user is authenticated
        # Both Tier 1 (adult_mode_enabled) AND Tier 2 (full_unlock) required for uncensored models
        adult_mode = False
        if user:
            try:
                profile_service = get_user_profile_service()
                adult_status = await profile_service.get_adult_mode_status(user.id)
                full_unlock_status = await profile_service.get_full_unlock_status(user.id)
                # Both tiers required for uncensored models
                adult_mode = (
                    adult_status.get("enabled", False) and
                    full_unlock_status.get("enabled", False)
                )
            except Exception as e:
                logger.debug(f"Could not get adult mode status: {e}")

        # Filter out uncensored models if adult mode is disabled
        if not adult_mode:
            filtered_models = []
            for model in models:
                model_name_lower = model.get("name", "").lower()
                is_adult_model = any(keyword in model_name_lower for keyword in ADULT_MODEL_KEYWORDS)
                if not is_adult_model:
                    filtered_models.append(model)
            models = filtered_models

        return {
            "models": models,
            "current": current,
            "adult_mode": adult_mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@router.post("/select")
async def select_model(request: ModelSelectRequest) -> Dict[str, str]:
    """Set the current model"""
    settings = get_settings()
    settings.model = request.model
    update_settings(settings)
    return {"model": request.model, "status": "selected"}

@router.get("/current")
async def get_current_model() -> Dict[str, str]:
    """Get currently selected model"""
    return {"model": get_settings().model}


@router.get("/capabilities")
async def get_model_capabilities() -> Dict[str, Any]:
    """Get capabilities of the current model"""
    settings = get_settings()
    model = settings.model

    # Get full capability info
    info = await ollama_service.get_model_capabilities(model)
    capabilities = info.get("capabilities", [])

    is_vision = "vision" in capabilities or await ollama_service.is_vision_model(model)
    supports_tools = "tools" in capabilities or await ollama_service.supports_tools(model)
    supports_thinking = "thinking" in capabilities

    # Define available tools based on capabilities
    tools = []
    if supports_tools:
        tools.append({
            "id": "web_search",
            "name": "Web Search",
            "description": "Search the web for information",
            "icon": "search"
        })
        tools.append({
            "id": "browse_website",
            "name": "Browse Website",
            "description": "Visit and read a specific URL",
            "icon": "language"
        })
        tools.append({
            "id": "search_conversations",
            "name": "Search Conversations",
            "description": "Search past conversations",
            "icon": "history"
        })
        tools.append({
            "id": "search_knowledge_base",
            "name": "Knowledge Base",
            "description": "Search your uploaded documents",
            "icon": "folder_open"
        })

    return {
        "model": model,
        "capabilities": capabilities,
        "is_vision": is_vision,
        "supports_tools": supports_tools,
        "supports_thinking": supports_thinking,
        "tools": tools
    }


@router.get("/usage")
async def get_usage_stats():
    """Get current VRAM usage statistics."""
    vram_info = await get_vram_usage()
    return {"vram": vram_info}


@router.get("/capabilities/{model_name}")
async def get_model_capabilities_endpoint(model_name: str):
    """Get comprehensive capabilities for a specific model."""
    return await ollama_service.get_comprehensive_capabilities(model_name)
