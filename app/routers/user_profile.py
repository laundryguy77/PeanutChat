"""User profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
import logging

from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse
from app.services.user_profile_service import get_user_profile_service
from app.models.profile_schemas import (
    ProfileUpdateRequest,
    ProfileReadRequest,
    LogEventRequest,
    AddNestedRequest,
    ProfileQueryRequest,
    ProfileExportRequest,
    ProfileResetRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("")
async def get_profile(user: UserResponse = Depends(require_auth)) -> Dict[str, Any]:
    """Get the full user profile."""
    service = get_user_profile_service()
    return await service.get_profile(user.id)


@router.put("")
async def update_profile(
    request: ProfileUpdateRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Update profile fields."""
    service = get_user_profile_service()
    updates = [u.model_dump() for u in request.updates]
    return await service.update_profile(user.id, updates, request.reason)


@router.post("/sections/read")
async def read_sections(
    request: ProfileReadRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Read specific profile sections."""
    service = get_user_profile_service()
    result = await service.read_sections(
        user.id,
        request.sections,
        request.include_disabled
    )
    return {"success": True, "sections": result}


@router.post("/log-event")
async def log_event(
    request: LogEventRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Log an interaction event."""
    service = get_user_profile_service()
    return await service.log_event(
        user.id,
        request.event_type.value,
        request.context,
        request.severity.value
    )


@router.post("/add-nested")
async def add_nested(
    request: AddNestedRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Add to a nested section."""
    service = get_user_profile_service()
    return await service.add_nested(
        user.id,
        request.section,
        request.domain,
        request.key,
        request.value
    )


@router.post("/query")
async def query_profile(
    request: ProfileQueryRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Query profile with natural language."""
    service = get_user_profile_service()
    return await service.query_profile(user.id, request.query)


@router.get("/export")
async def export_profile(
    format: str = "json",
    tier: str = "exportable",
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Export profile data."""
    service = get_user_profile_service()
    result = await service.export_profile(
        user.id,
        format=format,
        tier=tier,
        user_confirmed=(tier != "full")  # Full tier needs explicit confirmation via POST
    )
    return {"success": True, "format": format, "tier": tier, "data": result}


@router.post("/export")
async def export_profile_full(
    request: ProfileExportRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Export profile with full tier (requires confirmation)."""
    service = get_user_profile_service()
    result = await service.export_profile(
        user.id,
        format=request.format.value,
        tier=request.tier.value,
        user_confirmed=request.user_confirmed or False
    )
    return {"success": True, "format": request.format.value, "tier": request.tier.value, "data": result}


@router.delete("")
async def reset_profile(
    request: ProfileResetRequest,
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Reset profile sections to defaults."""
    if not request.user_confirmed:
        raise HTTPException(status_code=400, detail="User confirmation required")

    service = get_user_profile_service()
    logger.info(f"Profile reset for user {user.id}: {request.confirmation_phrase}")
    return await service.reset_profile(
        user.id,
        request.sections,
        request.preserve_identity
    )


@router.post("/evaluate")
async def trigger_evaluation(
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Manually trigger profile evaluation."""
    # Import here to avoid circular dependency
    from app.services.evaluator_service import get_evaluator_service
    evaluator = get_evaluator_service()
    result = await evaluator.evaluate(user.id)
    return result


@router.get("/system-prompt")
async def get_system_prompt(
    user: UserResponse = Depends(require_auth)
) -> Dict[str, Any]:
    """Get generated system prompt for debugging/inspection."""
    profile_service = get_user_profile_service()
    profile = await profile_service.read_sections(user.id, ["all"], include_disabled=False)

    from app.services.system_prompt_builder import get_prompt_builder
    builder = get_prompt_builder()

    prompt = builder.build_prompt(
        profile_context=profile,
        has_tools=True
    )

    return {
        "success": True,
        "system_prompt": prompt
    }
