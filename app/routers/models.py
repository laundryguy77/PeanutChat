from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.ollama import ollama_service
from app.config import get_settings, update_settings
from app.models.schemas import ModelSelectRequest

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("")
async def list_models() -> Dict[str, Any]:
    """List all available Ollama models"""
    try:
        models = await ollama_service.list_models()
        current = get_settings().model
        return {
            "models": models,
            "current": current
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

    is_vision = await ollama_service.is_vision_model(model)
    supports_tools = await ollama_service.supports_tools(model)

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
            "id": "generate_image",
            "name": "Generate Image",
            "description": "Create images from text",
            "icon": "image"
        })

    return {
        "model": model,
        "is_vision": is_vision,
        "supports_tools": supports_tools,
        "tools": tools
    }
