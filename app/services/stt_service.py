"""
STT Service - Orchestrates STT backend based on configuration.

Handles backend selection, initialization, and request routing.

Usage:
    service = get_stt_service()
    result = await service.transcribe(audio_data)
"""

import logging
from typing import Dict, Any, Optional

from app.services.stt_backends import (
    STTBackend, STTConfig, TranscriptionResult,
    get_stt_backend_class
)

logger = logging.getLogger(__name__)


class STTService:
    """
    STT orchestration service.

    Loads the configured backend and routes requests to it.
    Supports lazy loading and backend swapping.
    """

    def __init__(self):
        self._backend: Optional[STTBackend] = None
        self._backend_name: Optional[str] = None
        self._model_name: Optional[str] = None

    def _get_config(self) -> tuple:
        """Get STT configuration from app config."""
        from app import config
        return (
            getattr(config, 'STT_BACKEND', 'faster_whisper'),
            getattr(config, 'STT_MODEL', 'small'),
            getattr(config, 'STT_DEVICE', 'cpu')
        )

    def _get_backend(self) -> STTBackend:
        """Get or create the configured backend."""
        backend_name, model_name, device = self._get_config()

        # Reinitialize if backend or model changed
        if (self._backend_name != backend_name or
            self._model_name != model_name):

            if self._backend:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self._backend.cleanup())
                    else:
                        loop.run_until_complete(self._backend.cleanup())
                except Exception as e:
                    logger.warning(f"Failed to cleanup old backend: {e}")

            backend_class = get_stt_backend_class(backend_name)
            self._backend = backend_class(
                model_name=model_name,
                device=device
            )
            self._backend_name = backend_name
            self._model_name = model_name

        return self._backend

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        word_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes (wav, mp3, webm, etc.)
            language: Language code or None for auto-detect
            word_timestamps: Include word-level timing

        Returns:
            Dict with:
                text: Transcribed text
                language: Detected language
                confidence: Confidence score (0-1)
                duration: Audio duration in seconds
                segments: Word timestamps (if requested)
        """
        backend = self._get_backend()

        stt_config = STTConfig(
            language=language,
            word_timestamps=word_timestamps
        )

        result = await backend.transcribe(audio_data, stt_config)

        return {
            "text": result.text,
            "language": result.language,
            "confidence": result.confidence,
            "duration": result.duration,
            "segments": result.segments
        }

    async def get_backend_info(self) -> Dict[str, Any]:
        """Get info about the current backend."""
        backend = self._get_backend()
        return {
            "name": backend.name,
            "model": backend.model_name,
            "device": backend.device,
            "supports_streaming": backend.supports_streaming,
            "supports_word_timestamps": backend.supports_word_timestamps,
            "supported_languages": backend.supported_languages,
            "initialized": backend._initialized
        }

    async def cleanup(self) -> None:
        """Release backend resources."""
        if self._backend:
            await self._backend.cleanup()
            self._backend = None
            self._backend_name = None
            self._model_name = None


# Singleton instance
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    """Get STT service singleton."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
