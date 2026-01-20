import logging
from fastapi import APIRouter, HTTPException, status, Response, Depends, Request

from app import config
from app.models.auth_schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserSettings, PasswordChange
)
from app.services.auth_service import get_auth_service
from app.services.rate_limiter import get_login_limiter
from app.middleware.auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, response: Response):
    """Register a new user"""
    auth_service = get_auth_service()

    user = auth_service.create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # Create access token
    access_token = auth_service.create_access_token(user.id, user.username)

    # Set token in cookie for browser sessions
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24  # 24 hours
    )

    return TokenResponse(
        access_token=access_token,
        user=user
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, request: Request, response: Response):
    """Login with username and password"""
    # Rate limiting: use IP + username as key
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{credentials.username}"

    limiter = get_login_limiter()
    allowed, retry_after = limiter.is_allowed(rate_key)

    if not allowed:
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {retry_after} seconds."
        )

    auth_service = get_auth_service()
    user = auth_service.authenticate_user(credentials.username, credentials.password)

    if not user:
        # Record failed attempt
        limiter.record_attempt(rate_key, success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Record successful attempt (clears rate limit tracking)
    limiter.record_attempt(rate_key, success=True)

    # Create access token
    access_token = auth_service.create_access_token(user.id, user.username)

    # Set token in cookie for browser sessions
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24  # 24 hours
    )

    logger.info(f"User logged in: {user.username}")

    return TokenResponse(
        access_token=access_token,
        user=user
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout and clear session"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """Refresh the access token using existing valid token"""
    from jose import jwt, ExpiredSignatureError, JWTError

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    auth_service = get_auth_service()

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        user_id = int(sub)
        username = payload.get("username")

        # Issue new token with fresh expiration
        new_token = auth_service.create_access_token(user_id, username)

        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=config.COOKIE_SECURE,
            samesite="lax",
            path="/",
            max_age=60 * 60 * 24  # 24 hours
        )
        return {"message": "Token refreshed"}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired - please login again")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: UserResponse = Depends(require_auth)):
    """Get current authenticated user info"""
    return user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    user: UserResponse = Depends(require_auth)
):
    """Change user's password"""
    auth_service = get_auth_service()

    success = auth_service.change_password(
        user.id,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return {"message": "Password changed successfully"}


@router.get("/settings", response_model=UserSettings)
async def get_settings(user: UserResponse = Depends(require_auth)):
    """Get user-specific settings"""
    auth_service = get_auth_service()
    settings = auth_service.get_user_settings(user.id)

    if not settings:
        return UserSettings()

    return settings


@router.put("/settings")
async def update_settings(
    settings: UserSettings,
    user: UserResponse = Depends(require_auth)
):
    """Update user-specific settings"""
    auth_service = get_auth_service()
    auth_service.update_user_settings(user.id, settings)
    return {"message": "Settings updated successfully"}


@router.delete("/account")
async def delete_account(
    response: Response,
    user: UserResponse = Depends(require_auth)
):
    """Delete user account and all associated data"""
    auth_service = get_auth_service()
    await auth_service.delete_user(user.id)
    response.delete_cookie(key="access_token")
    return {"message": "Account deleted successfully"}
