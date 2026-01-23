import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from app import config


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filter in browsers that support it
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Prevent caching of sensitive responses (for API endpoints)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response
from app.routers import auth, chat, commands, knowledge, mcp, memory, models, settings, user_profile
from app.services.ollama import ollama_service

logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(
    title="PeanutChat",
    description="Chat with an LLM that can search the web",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")

# Mount avatars directory for serving generated avatar images
import os
avatars_dir = PROJECT_ROOT / "avatars"
os.makedirs(avatars_dir, exist_ok=True)
app.mount("/avatars", StaticFiles(directory=avatars_dir), name="avatars")

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(commands.router)
app.include_router(knowledge.router)
app.include_router(mcp.router)
app.include_router(memory.router)
app.include_router(models.router)
app.include_router(settings.router)
app.include_router(user_profile.router)

@app.get("/")
async def index():
    """Serve the main HTML page"""
    return FileResponse(PROJECT_ROOT / "static" / "index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_security_check():
    """Verify security configuration on startup."""
    if config.JWT_SECRET == "change-this-in-production-use-a-long-random-string":
        logger.critical("SECURITY ERROR: Default JWT_SECRET detected! Set JWT_SECRET in .env to a secure random value (32+ characters).")
        raise RuntimeError("Application cannot start with default JWT_SECRET. Set JWT_SECRET environment variable.")

    if len(config.JWT_SECRET) < 32:
        logger.warning("SECURITY WARNING: JWT_SECRET is shorter than 32 characters. Consider using a longer secret.")

    if not config.ADULT_PASSCODE:
        logger.critical("SECURITY ERROR: ADULT_PASSCODE environment variable must be set.")
        raise RuntimeError("Application cannot start without ADULT_PASSCODE. Set ADULT_PASSCODE environment variable.")

    if len(config.ADULT_PASSCODE) < 4:
        logger.warning("SECURITY WARNING: ADULT_PASSCODE is shorter than 4 characters. Consider using a longer passcode.")

    # Feature availability warnings
    if not config.WEB_SEARCH_AVAILABLE:
        logger.warning("BRAVE_SEARCH_API_KEY not set - web search feature disabled")
    if not config.VIDEO_GENERATION_AVAILABLE:
        logger.warning("HF_TOKEN not set - video generation feature disabled")


@app.on_event("shutdown")
async def shutdown_cleanup():
    """Clean up resources on shutdown"""
    await ollama_service.close()
