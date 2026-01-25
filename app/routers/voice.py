"""
Voice Router - TTS and STT API endpoints.

Provides:
- POST /api/voice/tts/stream - Stream TTS audio
- GET /api/voice/tts/voices - List available voices
- POST /api/voice/transcribe - Transcribe audio to text
- GET /api/voice/settings - Get user voice settings
- PUT /api/voice/settings - Update user voice settings
- GET /api/voice/capabilities - Get backend capabilities
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse
from app.services.tts_service import get_tts_service
from app.services.tts_backends import TTSConfig
from app.services.stt_service import get_stt_service
from app.services.voice_settings_service import get_voice_settings_service
from app import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])


# =============================================================================
# Request/Response Models
# =============================================================================

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Text to synthesize")
    voice: Optional[str] = Field(default=None, description="Voice ID to use")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    format: Optional[str] = Field(default="mp3", description="Audio format")


class TranscriptionResponse(BaseModel):
    text: str
    language: str
    confidence: float
    duration: float


class VoiceSettings(BaseModel):
    voice_mode: str = Field(default="disabled", description="disabled, transcribe_only, tts_only, conversation")
    tts_voice: str = "default"
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    tts_format: str = "mp3"
    auto_play: bool = True
    stt_language: str = "auto"


class VoiceCapabilities(BaseModel):
    """Backend capabilities response."""
    tts_enabled: bool
    stt_enabled: bool
    tts_backend: Optional[str] = None
    stt_backend: Optional[str] = None
    tts_voices: list = []
    stt_languages: list = []


# =============================================================================
# Dependencies
# =============================================================================

async def require_voice_enabled(user: UserResponse = Depends(require_auth)):
    """Check if voice features are enabled globally and for user."""
    if not getattr(config, 'VOICE_ENABLED', False):
        raise HTTPException(status_code=503, detail="Voice features are disabled")

    # Check user-specific setting
    settings_service = get_voice_settings_service()
    if not await settings_service.is_voice_enabled_for_user(user.id):
        raise HTTPException(status_code=403, detail="Voice features disabled for your account")

    return user


# =============================================================================
# TTS Endpoints
# =============================================================================

@router.post("/tts/stream")
async def tts_stream(
    request: TTSRequest,
    user: UserResponse = Depends(require_voice_enabled)
):
    """
    Stream TTS audio for given text.

    Returns Server-Sent Events with audio chunks:
    - event: metadata - Audio format info
    - event: audio - Base64 encoded audio chunk
    - event: done - Stream complete
    - event: error - Error occurred
    """
    tts_service = get_tts_service()
    settings_service = get_voice_settings_service()

    # Get user's voice settings
    user_settings = await settings_service.get_settings(user.id)

    # Build config
    tts_config = TTSConfig(
        voice=request.voice or user_settings.get("tts_voice", "default"),
        speed=request.speed or user_settings.get("tts_speed", 1.0),
        format=request.format or user_settings.get("tts_format", "mp3"),
        sample_rate=24000
    )

    async def event_generator():
        try:
            async for event in tts_service.generate_stream(request.text, tts_config):
                event_type = event["event"]
                event_data = json.dumps(event["data"])
                yield f"event: {event_type}\ndata: {event_data}\n\n"
        except Exception as e:
            logger.error(f"TTS stream error: {e}")
            error_data = json.dumps({"code": "stream_error", "message": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/tts/voices")
async def get_voices(user: UserResponse = Depends(require_voice_enabled)):
    """Get available TTS voices from current backend."""
    tts_service = get_tts_service()

    try:
        voices = await tts_service.get_voices()
        return [
            {
                "id": v.id,
                "name": v.name,
                "language": v.language,
                "gender": v.gender
            }
            for v in voices
        ]
    except Exception as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voices")


# =============================================================================
# STT Endpoints
# =============================================================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(default=None, description="Language code or 'auto'"),
    user: UserResponse = Depends(require_voice_enabled)
):
    """Transcribe audio file to text."""
    # Validate file type
    allowed_types = {
        "audio/webm", "audio/wav", "audio/wave", "audio/x-wav",
        "audio/mp3", "audio/mpeg", "audio/ogg", "audio/m4a",
        "audio/x-m4a", "audio/mp4", "audio/flac"
    }

    content_type = audio.content_type or ""
    if content_type not in allowed_types:
        # Also check file extension
        filename = audio.filename or ""
        valid_ext = filename.lower().endswith(('.wav', '.mp3', '.webm', '.ogg', '.m4a', '.flac'))
        if not valid_ext:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio format '{content_type}'. Allowed: wav, mp3, webm, ogg, m4a, flac"
            )

    # Read and validate size (10MB max)
    content = await audio.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file too large. Maximum size: 10MB"
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file"
        )

    stt_service = get_stt_service()

    # Get user's preferred language if not specified
    if not language or language == "auto":
        settings_service = get_voice_settings_service()
        user_settings = await settings_service.get_settings(user.id)
        lang = user_settings.get("stt_language")
        language = None if lang == "auto" else lang

    try:
        result = await stt_service.transcribe(
            audio_data=content,
            language=language
        )

        return TranscriptionResponse(
            text=result["text"],
            language=result["language"],
            confidence=result["confidence"],
            duration=result["duration"]
        )

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed")


# =============================================================================
# Settings Endpoints
# =============================================================================

@router.get("/settings", response_model=VoiceSettings)
async def get_voice_settings(user: UserResponse = Depends(require_auth)):
    """Get user's voice settings."""
    service = get_voice_settings_service()
    settings = await service.get_settings(user.id)
    return VoiceSettings(**settings)


@router.put("/settings", response_model=VoiceSettings)
async def update_voice_settings(
    settings: VoiceSettings,
    user: UserResponse = Depends(require_auth)
):
    """Update user's voice settings."""
    # Validate voice_mode
    valid_modes = {"disabled", "transcribe_only", "tts_only", "conversation"}
    if settings.voice_mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice_mode. Must be one of: {valid_modes}"
        )

    service = get_voice_settings_service()
    updated = await service.update_settings(user.id, settings.model_dump())
    return VoiceSettings(**updated)


# =============================================================================
# Info Endpoints
# =============================================================================

@router.get("/capabilities", response_model=VoiceCapabilities)
async def get_capabilities(user: UserResponse = Depends(require_auth)):
    """Get voice backend capabilities."""
    voice_enabled = getattr(config, 'VOICE_ENABLED', False)

    if not voice_enabled:
        return VoiceCapabilities(
            tts_enabled=False,
            stt_enabled=False
        )

    # Check user-specific setting
    settings_service = get_voice_settings_service()
    user_enabled = await settings_service.is_voice_enabled_for_user(user.id)

    if not user_enabled:
        return VoiceCapabilities(
            tts_enabled=False,
            stt_enabled=False
        )

    tts_info = None
    stt_info = None
    tts_voices = []
    stt_languages = []

    try:
        tts_service = get_tts_service()
        tts_info = await tts_service.get_backend_info()
        voices = await tts_service.get_voices()
        tts_voices = [{"id": v.id, "name": v.name} for v in voices]
    except Exception as e:
        logger.warning(f"Failed to get TTS info: {e}")

    try:
        stt_service = get_stt_service()
        stt_info = await stt_service.get_backend_info()
        stt_languages = stt_info.get("supported_languages", [])
    except Exception as e:
        logger.warning(f"Failed to get STT info: {e}")

    return VoiceCapabilities(
        tts_enabled=tts_info is not None,
        stt_enabled=stt_info is not None,
        tts_backend=tts_info["name"] if tts_info else None,
        stt_backend=stt_info["name"] if stt_info else None,
        tts_voices=tts_voices,
        stt_languages=stt_languages
    )
