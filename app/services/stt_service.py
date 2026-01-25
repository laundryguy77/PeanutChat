"""STT service using Whisper for speech-to-text transcription."""
import logging
import asyncio
import tempfile
import os
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from app import config

logger = logging.getLogger(__name__)

# Thread pool for running STT in background
_stt_executor: Optional[ThreadPoolExecutor] = None


def _get_stt_executor() -> ThreadPoolExecutor:
    """Get or create the STT thread pool executor."""
    global _stt_executor
    if _stt_executor is None:
        _stt_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="stt")
    return _stt_executor


class WhisperSTTService:
    """STT service using OpenAI Whisper model."""

    def __init__(self):
        self._model = None
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Lazy initialization of Whisper model."""
        if self._initialized:
            return True

        async with self._init_lock:
            if self._initialized:
                return True

            if not config.VOICE_ENABLED:
                logger.warning("Voice features are disabled. Set VOICE_ENABLED=true to enable.")
                return False

            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(_get_stt_executor(), self._load_model)
                self._initialized = True
                logger.info(f"STT model loaded: whisper-{config.STT_MODEL} on {config.STT_DEVICE}")
                return True
            except Exception as e:
                logger.error(f"Failed to load STT model: {e}")
                return False

    def _load_model(self):
        """Load the Whisper model (runs in thread pool)."""
        import whisper

        logger.info(f"Loading Whisper model {config.STT_MODEL}...")

        # Determine device
        device = config.STT_DEVICE
        if device.startswith("cuda"):
            import torch
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU for STT")
                device = "cpu"

        self._model = whisper.load_model(
            config.STT_MODEL,
            device=device
        )

    def _transcribe_sync(
        self,
        audio_path: str,
        language: str = "en"
    ) -> dict:
        """Transcribe audio file (sync, runs in thread pool)."""
        if not self._model:
            raise RuntimeError("STT model not loaded")

        result = self._model.transcribe(
            audio_path,
            language=language if language != "auto" else None,
            task="transcribe"
        )

        return {
            "text": result["text"].strip(),
            "language": result.get("language", language),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip()
                }
                for seg in result.get("segments", [])
            ]
        }

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        format: str = "wav"
    ) -> Optional[dict]:
        """Transcribe audio data asynchronously.

        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., "en", "es", "auto")
            format: Audio format ("wav", "mp3", "webm", etc.)

        Returns:
            Dict with 'text', 'language', and 'segments' or None on error
        """
        if not await self._ensure_initialized():
            return None

        # Check audio length (approximate based on file size)
        # Rough estimate: 1 second of 16kHz 16-bit mono audio = ~32KB
        max_bytes = config.VOICE_MAX_AUDIO_LENGTH * 32000
        if len(audio_data) > max_bytes:
            logger.warning(f"Audio too long, truncating to {config.VOICE_MAX_AUDIO_LENGTH}s")
            audio_data = audio_data[:max_bytes]

        # Write to temp file (Whisper requires file path)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=f".{format}",
                delete=False
            ) as f:
                f.write(audio_data)
                temp_path = f.name

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                _get_stt_executor(),
                self._transcribe_sync,
                temp_path,
                language
            )
            return result

        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return None

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

    async def transcribe_file(
        self,
        file_path: str,
        language: str = "en"
    ) -> Optional[dict]:
        """Transcribe an audio file.

        Args:
            file_path: Path to audio file
            language: Language code

        Returns:
            Dict with 'text', 'language', and 'segments' or None on error
        """
        if not await self._ensure_initialized():
            return None

        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                _get_stt_executor(),
                self._transcribe_sync,
                file_path,
                language
            )
            return result

        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return None

    async def cleanup(self):
        """Clean up STT resources."""
        if self._model is not None:
            import torch
            del self._model
            self._model = None
            torch.cuda.empty_cache()
            logger.info("STT model unloaded")

        self._initialized = False


# Singleton instance
_stt_service: Optional[WhisperSTTService] = None


def get_stt_service() -> WhisperSTTService:
    """Get the global STT service instance."""
    global _stt_service
    if _stt_service is None:
        _stt_service = WhisperSTTService()
    return _stt_service


async def cleanup_stt_service():
    """Clean up the STT service on shutdown."""
    global _stt_service, _stt_executor
    if _stt_service is not None:
        await _stt_service.cleanup()
        _stt_service = None
    if _stt_executor is not None:
        _stt_executor.shutdown(wait=False)
        _stt_executor = None
