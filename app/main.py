from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.routers import chat, models, settings

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Ensure generated directories exist
(PROJECT_ROOT / "generated_images").mkdir(exist_ok=True)

app = FastAPI(
    title="AI Assistant",
    description="Chat with an LLM that can search the web and generate images",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")
app.mount("/generated_images", StaticFiles(directory=PROJECT_ROOT / "generated_images"), name="images")

# Include routers
app.include_router(chat.router)
app.include_router(models.router)
app.include_router(settings.router)

@app.get("/")
async def index():
    """Serve the main HTML page"""
    return FileResponse(PROJECT_ROOT / "static" / "index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
