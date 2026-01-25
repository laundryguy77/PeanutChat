"""
TTS Service - Orchestrates TTS backend based on configuration.

Handles backend selection, initialization, and request routing.

Usage:
    service = get_tts_service()
    audio = await service.generate("Hello world")

    # Streaming
    async for event in service.generate_stream("Hello world"):
        # Handle SSE events
        pass
"""

import base64
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List

from app.services.tts_backends import (
    TTSBackend, TTSConfig, TTSVoice,
    get_tts_backend_class
)

logger = logging.getLogger(__name__)


class TTSService:
    """
    TTS orchestration service.

    Loads the configured backend and routes requests to it.
    Supports lazy loading and backend swapping.
    """

    def __init__(self):
        self._backend: Optional[TTSBackend] = None
        self._backend_name: Optional[str] = None
        self._model_name: Optional[str] = None

    def _get_config(self) -> tuple:
        """Get TTS configuration from app config."""
        from app import config
        return (
            getattr(config, 'TTS_BACKEND', 'edge'),
            getattr(config, 'TTS_MODEL', 'default'),
            getattr(config, 'TTS_DEVICE', 'cpu')
        )

    def _get_backend(self) -> TTSBackend:
        """Get or create the configured backend."""
        backend_name, model_name, device = self._get_config()

        # Reinitialize if backend or model changed
        if (self._backend_name != backend_name or
            self._model_name != model_name):

            if self._backend:
                # Cleanup old backend asynchronously
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self._backend.cleanup())
                    else:
                        loop.run_until_complete(self._backend.cleanup())
                except Exception as e:
                    logger.warning(f"Failed to cleanup old backend: {e}")

            backend_class = get_tts_backend_class(backend_name)
            self._backend = backend_class(
                model_name=model_name,
                device=device
            )
            self._backend_name = backend_name
            self._model_name = model_name

        return self._backend

    async def generate(
        self,
        text: str,
        config: Optional[TTSConfig] = None
    ) -> bytes:
        """Generate complete audio for text."""
        backend = self._get_backend()
        cfg = config or TTSConfig()
        return await backend.generate(text, cfg)

    async def generate_stream(
        self,
        text: str,
        config: Optional[TTSConfig] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream audio generation as SSE events.

        Yields dicts with:
            {"event": "metadata", "data": {...}}
            {"event": "audio", "data": {"chunk": base64, "index": int}}
            {"event": "done", "data": {"total_chunks": int}}
            {"event": "error", "data": {"code": str, "message": str}}
        """
        backend = self._get_backend()
        cfg = config or TTSConfig()

        try:
            # Ensure backend is initialized
            await backend.ensure_initialized()

            # Yield metadata
            yield {
                "event": "metadata",
                "data": {
                    "sample_rate": cfg.sample_rate,
                    "format": cfg.format,
                    "voice": cfg.voice,
                    "backend": backend.name,
                    "supports_streaming": backend.supports_streaming
                }
            }

            # Stream audio chunks
            chunk_index = 0
            async for audio_chunk in backend.generate_stream(text, cfg):
                yield {
                    "event": "audio",
                    "data": {
                        "chunk": base64.b64encode(audio_chunk).decode('utf-8'),
                        "index": chunk_index
                    }
                }
                chunk_index += 1

            yield {
                "event": "done",
                "data": {"total_chunks": chunk_index}
            }

        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            yield {
                "event": "error",
                "data": {"code": "generation_failed", "message": str(e)}
            }

    async def get_voices(self) -> List[TTSVoice]:
        """Get available voices from the current backend."""
        backend = self._get_backend()
        await backend.ensure_initialized()
        return await backend.get_voices()

    async def get_backend_info(self) -> Dict[str, Any]:
        """Get info about the current backend."""
        backend = self._get_backend()
        return {
            "name": backend.name,
            "model": backend.model_name,
            "device": backend.device,
            "supports_streaming": backend.supports_streaming,
            "supports_voices": backend.supports_voices,
            "supported_formats": backend.supported_formats,
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
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """Get TTS service singleton."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
