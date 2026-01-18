from fastapi import APIRouter
from typing import Dict, Any
from app.config import get_settings, update_settings, AppSettings
from app.models.schemas import SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("")
async def get_all_settings() -> Dict[str, Any]:
    """Get all current settings"""
    settings = get_settings()
    return settings.model_dump()

@router.put("")
async def update_all_settings(updates: SettingsUpdate) -> Dict[str, Any]:
    """Update settings"""
    current = get_settings()

    # Update only provided fields
    update_dict = updates.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(current, key, value)

    update_settings(current)

    return current.model_dump()

@router.get("/persona")
async def get_persona() -> Dict[str, Any]:
    """Get current persona"""
    return {"persona": get_settings().persona}

@router.put("/persona")
async def update_persona(data: Dict[str, Any]) -> Dict[str, Any]:
    """Update persona"""
    settings = get_settings()
    settings.persona = data.get("persona")
    update_settings(settings)
    return {"persona": settings.persona, "status": "updated"}
