import json
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

# Server settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

# Ollama API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Brave Search API
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")

class AppSettings(BaseModel):
    persona: Optional[str] = None
    model: str = "huihui_ai/qwen3-vl-abliterated:8b"
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_ctx: int = 4096
    repeat_penalty: float = 1.1
    tts_enabled: bool = False
    # TTS voice settings
    tts_speaker: int = 0
    tts_temperature: float = 0.9
    tts_topk: int = 50

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
