import json
import os
import logging
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def setup_logging():
    """Configure application logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger

# Initialize logging
logger = setup_logging()

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

# Server settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

# Ollama API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Brave Search API
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "peanutchat.db")

# JWT Authentication settings
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production-use-a-long-random-string")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours default

# Knowledge Base settings
KB_EMBEDDING_MODEL = os.getenv("KB_EMBEDDING_MODEL", "nomic-embed-text")
KB_CHUNK_SIZE = int(os.getenv("KB_CHUNK_SIZE", "512"))
KB_CHUNK_OVERLAP = int(os.getenv("KB_CHUNK_OVERLAP", "50"))

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")

# Cookie security (set to true in production with HTTPS)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# Trusted proxy configuration for correct client IP detection
# Set to comma-separated list of trusted proxy IPs (e.g., "127.0.0.1,10.0.0.1")
# When set, X-Forwarded-For header from these proxies will be trusted
TRUSTED_PROXIES = [p.strip() for p in os.getenv("TRUSTED_PROXIES", "").split(",") if p.strip()]

# Hugging Face settings (for video generation)
HF_TOKEN = os.getenv("HF_TOKEN", "")
VIDEO_GENERATION_SPACE = os.getenv("VIDEO_GENERATION_SPACE", "Heartsync/NSFW-Uncensored-video")

class AppSettings(BaseModel):
    persona: Optional[str] = None
    model: str = "huihui_ai/qwen3-vl-abliterated:8b"
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_ctx: int = 4096
    repeat_penalty: float = 1.1
    # Context compaction settings
    compaction_enabled: bool = True
    compaction_buffer_percent: int = 15  # % of context reserved for summaries (5-30)
    compaction_threshold_percent: int = 70  # Trigger compaction at this % of active window (50-90)
    compaction_protected_messages: int = 6  # Recent messages never compacted (4-12)

def load_settings() -> AppSettings:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            return AppSettings(**json.load(f))
    return AppSettings()

def save_settings(settings: AppSettings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=2)

# Global settings instance
_settings: Optional[AppSettings] = None

def get_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings

def update_settings(new_settings: AppSettings):
    global _settings
    _settings = new_settings
    save_settings(new_settings)
