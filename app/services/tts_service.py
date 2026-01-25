"""TTS service using Qwen3-TTS for text-to-speech streaming."""
import logging
import asyncio
import io
from typing import Optional, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

from app import config

logger = logging.getLogger(__name__)

# Thread pool for running TTS in background
_tts_executor: Optional[ThreadPoolExecutor] = None


def _get_tts_executor() -> ThreadPoolExecutor:
    """Get or create the TTS thread pool executor."""
    global _tts_executor
    if _tts_executor is None:
        _tts_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tts")
    return _tts_executor


class QwenTTSService:
    """TTS service using Qwen3-TTS model."""

    def __init__(self):
        self._model = None
        self._processor = None
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Lazy initialization of TTS model."""
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
                await loop.run_in_executor(_get_tts_executor(), self._load_model)
                self._initialized = True
                logger.info(f"TTS model loaded: {config.TTS_MODEL} on {config.TTS_DEVICE}")
                return True
            except Exception as e:
                logger.error(f"Failed to load TTS model: {e}")
                return False

    def _load_model(self):
        """Load the TTS model (runs in thread pool)."""
        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor

        logger.info(f"Loading TTS model {config.TTS_MODEL}...")

        self._processor = AutoProcessor.from_pretrained(
            config.TTS_MODEL,
            trust_remote_code=True
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            config.TTS_MODEL,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            device_map=config.TTS_DEVICE
        )

    def _generate_audio_sync(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> bytes:
        """Generate audio from text (sync, runs in thread pool)."""
        import torch
        import numpy as np

        if not self._model or not self._processor:
            raise RuntimeError("TTS model not loaded")

        # Truncate text to max length
        if len(text) > config.VOICE_MAX_TTS_LENGTH:
            text = text[:config.VOICE_MAX_TTS_LENGTH]
            logger.warning(f"TTS text truncated to {config.VOICE_MAX_TTS_LENGTH} chars")

        # Prepare input
        inputs = self._processor(
            text=text,
            return_tensors="pt"
        ).to(self._model.device)

        # Generate audio tokens
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=4096,
                do_sample=True,
                temperature=0.7
            )

        # Decode audio
        audio = self._processor.decode(
            outputs[0],
            skip_special_tokens=True
        )

        # Convert to WAV bytes
        sample_rate = 24000  # Qwen3-TTS default sample rate

        # Apply speed adjustment
        if speed != 1.0 and 0.5 <= speed <= 2.0:
            # Resample for speed change
            from scipy import signal
            new_length = int(len(audio) / speed)
            audio = signal.resample(audio, new_length)

        # Convert to int16 WAV
        audio_int16 = (audio * 32767).astype(np.int16)

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        import wave
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(int(sample_rate * speed))
            wav_file.writeframes(audio_int16.tobytes())

        return wav_buffer.getvalue()

    async def generate_audio(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> Optional[bytes]:
        """Generate audio from text asynchronously."""
        if not await self._ensure_initialized():
            return None

        try:
            loop = asyncio.get_event_loop()
            audio_bytes = await loop.run_in_executor(
                _get_tts_executor(),
                self._generate_audio_sync,
                text,
                voice,
                speed
            )
            return audio_bytes
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    async def generate_stream(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        chunk_size: int = 4096
    ) -> AsyncGenerator[bytes, None]:
        """Generate audio as a stream of chunks."""
        audio_bytes = await self.generate_audio(text, voice, speed)
        if audio_bytes:
            # Yield in chunks for streaming
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i + chunk_size]

    async def cleanup(self):
        """Clean up TTS resources."""
        if self._model is not None:
            import torch
            del self._model
            self._model = None
            torch.cuda.empty_cache()
            logger.info("TTS model unloaded")

        if self._processor is not None:
            del self._processor
            self._processor = None

        self._initialized = False


# Singleton instance
_tts_service: Optional[QwenTTSService] = None


def get_tts_service() -> QwenTTSService:
    """Get the global TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = QwenTTSService()
    return _tts_service


async def cleanup_tts_service():
    """Clean up the TTS service on shutdown."""
    global _tts_service, _tts_executor
    if _tts_service is not None:
        await _tts_service.cleanup()
        _tts_service = None
    if _tts_executor is not None:
        _tts_executor.shutdown(wait=False)
        _tts_executor = None
