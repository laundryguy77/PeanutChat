"""
Admin Router - Administrative API endpoints.

All endpoints require admin authentication.

Provides:
- User management (CRUD, password reset, activate/deactivate)
- Feature flag management (global defaults, per-user overrides)
- Audit log viewing
- Dashboard statistics
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse
from app.services.admin_service import get_admin_service
from app.services.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


# =============================================================================
# Request/Response Models
# =============================================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    is_admin: bool = False


class UserUpdate(BaseModel):
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    mode_restriction: Optional[str] = Field(
        default=None,
        description="null, 'normal_only', or 'no_full_unlock'"
    )
    voice_enabled: Optional[bool] = None


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=8)


class FeatureFlagUpdate(BaseModel):
    default_enabled: bool


class UserFeatureOverride(BaseModel):
    enabled: Optional[bool] = Field(
        default=None,
        description="True/False to override, null to use global default"
    )


# =============================================================================
# Dependencies
# =============================================================================

async def require_admin(user: UserResponse = Depends(require_auth)) -> UserResponse:
    """Dependency that requires admin status."""
    db = get_database()

    row = db.fetchone(
        "SELECT is_admin, is_active FROM users WHERE id = ?",
        (user.id,)
    )

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    is_admin = bool(row[0]) if row[0] is not None else False
    is_active = bool(row[1]) if row[1] is not None else True

    if not is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    return user


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# User Management Endpoints
# =============================================================================

@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    include_inactive: bool = False,
    admin: UserResponse = Depends(require_admin)
):
    """List all users with pagination."""
    service = get_admin_service()
    return await service.list_users(
        page=page,
        page_size=page_size,
        search=search,
        include_inactive=include_inactive
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin: UserResponse = Depends(require_admin)
):
    """Get detailed user information."""
    service = get_admin_service()
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Create a new user."""
    service = get_admin_service()
    result = await service.create_user(
        admin_id=admin.id,
        username=user_data.username,
        password=user_data.password,
        is_admin=user_data.is_admin,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdate,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Update user attributes."""
    # Validate mode_restriction
    if updates.mode_restriction is not None:
        valid_restrictions = {None, "normal_only", "no_full_unlock"}
        if updates.mode_restriction not in valid_restrictions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode_restriction. Must be one of: {valid_restrictions}"
            )

    service = get_admin_service()
    result = await service.update_user(
        user_id=user_id,
        admin_id=admin.id,
        updates=updates.model_dump(exclude_none=True),
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Delete a user and all their data."""
    service = get_admin_service()
    result = await service.delete_user(
        user_id=user_id,
        admin_id=admin.id,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    password_data: PasswordReset,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Reset a user's password."""
    service = get_admin_service()
    result = await service.reset_password(
        user_id=user_id,
        admin_id=admin.id,
        new_password=password_data.new_password,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# =============================================================================
# Feature Flag Endpoints
# =============================================================================

@router.get("/features")
async def list_features(admin: UserResponse = Depends(require_admin)):
    """Get all feature flags with their defaults."""
    service = get_admin_service()
    return await service.list_feature_flags()


@router.patch("/features/{feature_key}")
async def update_feature(
    feature_key: str,
    update: FeatureFlagUpdate,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Update a global feature flag default."""
    service = get_admin_service()
    result = await service.update_feature_flag(
        admin_id=admin.id,
        feature_key=feature_key,
        default_enabled=update.default_enabled,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/users/{user_id}/features")
async def get_user_features(
    user_id: int,
    admin: UserResponse = Depends(require_admin)
):
    """Get effective feature flags for a user."""
    service = get_admin_service()
    return await service.get_user_features(user_id)


@router.put("/users/{user_id}/features/{feature_key}")
async def set_user_feature(
    user_id: int,
    feature_key: str,
    override: UserFeatureOverride,
    request: Request,
    admin: UserResponse = Depends(require_admin)
):
    """Set a per-user feature override."""
    service = get_admin_service()
    result = await service.set_user_feature_override(
        admin_id=admin.id,
        user_id=user_id,
        feature_key=feature_key,
        enabled=override.enabled,
        ip_address=get_client_ip(request)
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# =============================================================================
# Dashboard & Audit Log Endpoints
# =============================================================================

@router.get("/dashboard")
async def get_dashboard(admin: UserResponse = Depends(require_admin)):
    """Get system statistics for dashboard."""
    service = get_admin_service()
    return await service.get_dashboard_stats()


@router.get("/audit-log")
async def get_audit_log(
    page: int = 1,
    page_size: int = 50,
    admin_filter: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: UserResponse = Depends(require_admin)
):
    """Get admin audit log."""
    service = get_admin_service()
    return await service.get_audit_log(
        page=page,
        page_size=page_size,
        admin_id=admin_filter,
        action=action,
        start_date=start_date,
        end_date=end_date
    )


# =============================================================================
# Public User Endpoints (for regular users to check their own features)
# =============================================================================

@router.get("/my-features")
async def get_my_features(user: UserResponse = Depends(require_auth)):
    """Get current user's effective feature flags (non-admin)."""
    service = get_admin_service()
    return await service.get_user_features(user.id)
