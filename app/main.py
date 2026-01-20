import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app import config
from app.routers import auth, chat, commands, knowledge, mcp, memory, models, settings, user_profile

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
    if config.JWT_SECRET == "change-this-in-production-use-a-long-random-string":
        logger.warning("SECURITY WARNING: Using default JWT_SECRET! Set JWT_SECRET environment variable for production.")
