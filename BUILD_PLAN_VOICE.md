# PeanutChat Voice Integration Build Plan

## Document Information
- **Feature:** Voice Integration (TTS + STT)
- **Version:** 2.0 (Model-Swappable Architecture)
- **Last Updated:** 2026-01-25
- **Status:** Ready for Implementation

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial draft |
| 1.1 | 2026-01-25 | Audit corrections applied |
| 2.0 | 2026-01-25 | Added backend abstraction for model swapping |

---

## Executive Summary

This document provides a complete implementation guide for adding voice capabilities to PeanutChat with **model-swappable architecture**:

- **TTS (Text-to-Speech):** Backend abstraction supporting multiple models (Qwen3-TTS, Coqui, Piper, etc.)
- **STT (Speech-to-Text):** Backend abstraction supporting multiple models (Whisper, faster-whisper, etc.)
- **Easy Model Swapping:** Change models via environment variables without code changes

### Voice Modes
| Mode | STT | TTS | Description |
|------|-----|-----|-------------|
| `disabled` | No | No | No voice features (default) |
| `transcribe_only` | Yes | No | Voice input, text responses |
| `tts_only` | No | Yes | Text input, voice responses |
| `conversation` | Yes | Yes | Full voice-to-voice chat |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase 1.1: TTS Backend Abstraction](#2-phase-11-tts-backend-abstraction)
3. [Phase 1.2: STT Backend Abstraction](#3-phase-12-stt-backend-abstraction)
4. [Phase 1.3: Voice Router](#4-phase-13-voice-router)
5. [Phase 1.4: Frontend Integration](#5-phase-14-frontend-integration)
6. [Database Schema](#6-database-schema)
7. [Configuration](#7-configuration)
8. [API Reference](#8-api-reference)
9. [Adding New Models](#9-adding-new-models)
10. [Testing Requirements](#10-testing-requirements)

---

## 1. Architecture Overview

### 1.1 Backend Pattern

Following the existing `image_backends.py` and `video_backends.py` pattern:

```
                          ┌─────────────────────┐
                          │   Voice Router      │
                          │  /api/voice/*       │
                          └──────────┬──────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │  TTS Service    │   │  STT Service    │   │ Voice Settings  │
    │  (orchestrator) │   │  (orchestrator) │   │    Service      │
    └────────┬────────┘   └────────┬────────┘   └─────────────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │  TTSBackend     │   │  STTBackend     │
    │  (abstract)     │   │  (abstract)     │
    └────────┬────────┘   └────────┬────────┘
             │                     │
    ┌────────┼────────┐   ┌────────┼────────┐
    │        │        │   │        │        │
    ▼        ▼        ▼   ▼        ▼        ▼
┌───────┐┌───────┐┌─────┐┌───────┐┌───────┐┌─────┐
│Qwen3  ││Coqui  ││Piper││Whisper││Faster ││etc. │
│TTS    ││TTS    ││TTS  ││       ││Whisper││     │
└───────┘└───────┘└─────┘└───────┘└───────┘└─────┘
```

### 1.2 Model Selection via Environment

```bash
# TTS Configuration
TTS_BACKEND=qwen3            # Options: qwen3, coqui, piper, kokoro
TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B
TTS_DEVICE=cuda:1

# STT Configuration
STT_BACKEND=whisper          # Options: whisper, faster_whisper
STT_MODEL=openai/whisper-small
STT_DEVICE=cuda:1
```

### 1.3 Hardware Requirements

| GPU | VRAM | Workload |
|-----|------|----------|
| V100 32GB | Primary | Chat model (7B-30B) |
| V100 16GB | Secondary | TTS (~1.2GB) + STT (~0.5GB) |

**Single GPU Fallback:** If `TTS_DEVICE` or `STT_DEVICE` not set, defaults to `cuda:0` with lazy loading to share with chat model.

---

## 2. Phase 1.1: TTS Backend Abstraction

### 2.1.1 TTS Backend Base Class

**New File:** `app/services/tts_backends.py`

```python
"""
TTS Backends - Model-swappable text-to-speech implementations.

Follows the same pattern as image_backends.py and video_backends.py.
Add new TTS models by subclassing TTSBackend.
"""

import asyncio
import base64
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator, Dict, Any, Optional, List

logger = logging.getLogger(__name__)


@dataclass
class TTSConfig:
    """Configuration for TTS generation."""
    voice: str = "default"
    speed: float = 1.0
    format: str = "opus"  # opus, mp3, wav, pcm
    sample_rate: int = 24000
    language: str = "en"


@dataclass
class TTSVoice:
    """Represents an available voice."""
    id: str
    name: str
    language: str
    gender: Optional[str] = None
    preview_url: Optional[str] = None


class TTSBackend(ABC):
    """
    Abstract base class for TTS backends.

    Subclass this to add support for new TTS models.
    """

    name: str = "base"
    supports_streaming: bool = False
    supports_voices: bool = False
    supported_formats: List[str] = field(default_factory=lambda: ["wav"])

    def __init__(self, model_name: str, device: str = "cuda:0"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._lock = asyncio.Lock()
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Load model onto device. Called lazily on first use."""
        pass

    @abstractmethod
    async def generate(
        self,
        text: str,
        config: TTSConfig
    ) -> bytes:
        """
        Generate complete audio for text.

        Args:
            text: Text to synthesize
            config: TTS configuration

        Returns:
            Audio bytes in requested format
        """
        pass

    async def generate_stream(
        self,
        text: str,
        config: TTSConfig
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks for text.

        Default implementation generates all at once then yields.
        Override for true streaming support.
        """
        audio = await self.generate(text, config)
        yield audio

    async def get_voices(self) -> List[TTSVoice]:
        """Get available voices. Override if backend supports multiple voices."""
        return [TTSVoice(id="default", name="Default", language="en")]

    async def cleanup(self) -> None:
        """Release resources. Override for GPU cleanup."""
        pass

    async def ensure_initialized(self) -> None:
        """Thread-safe initialization check."""
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self.initialize()
                    self._initialized = True


# =============================================================================
# Qwen3-TTS Backend
# =============================================================================

class Qwen3TTSBackend(TTSBackend):
    """
    Qwen3-TTS text-to-speech backend.

    Model: Qwen/Qwen3-TTS-12Hz-0.6B (or variants)
    VRAM: ~1.2GB
    """

    name = "qwen3"
    supports_streaming = True
    supports_voices = True
    supported_formats = ["wav", "opus", "mp3"]

    # Available voices (Qwen3-TTS speaker IDs)
    VOICES = {
        "default": TTSVoice("default", "Default (Female)", "en", "female"),
        "male_1": TTSVoice("male_1", "Male 1", "en", "male"),
        "female_1": TTSVoice("female_1", "Female 1", "en", "female"),
        "narrator": TTSVoice("narrator", "Narrator", "en", "neutral"),
    }

    async def initialize(self) -> None:
        """Load Qwen3-TTS model."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(f"Loading Qwen3-TTS model {self.model_name} on {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map=self.device
        )

        logger.info("Qwen3-TTS model loaded successfully")

    async def generate(self, text: str, config: TTSConfig) -> bytes:
        """Generate audio using Qwen3-TTS."""
        await self.ensure_initialized()

        import torch
        import io
        import soundfile as sf

        # Prepare input with voice/speed markers
        voice_id = config.voice if config.voice in self.VOICES else "default"
        input_text = f"[voice:{voice_id}][speed:{config.speed}]{text}"

        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            # Generate audio tokens
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=True,
                temperature=0.7
            )

            # Decode audio tokens to waveform
            # (Implementation depends on Qwen3-TTS specific API)
            audio_tokens = outputs[0][inputs.input_ids.shape[1]:]
            waveform = self._decode_audio_tokens(audio_tokens, config.sample_rate)

        # Convert to requested format
        buffer = io.BytesIO()
        sf.write(buffer, waveform, config.sample_rate, format=config.format.upper())
        buffer.seek(0)

        return buffer.read()

    async def generate_stream(
        self,
        text: str,
        config: TTSConfig
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio in chunks."""
        await self.ensure_initialized()

        import torch

        # Split text into sentences for streaming
        sentences = self._split_sentences(text)

        for sentence in sentences:
            if sentence.strip():
                audio_chunk = await self.generate(sentence, config)
                yield audio_chunk
                await asyncio.sleep(0)  # Allow other tasks

    async def get_voices(self) -> List[TTSVoice]:
        return list(self.VOICES.values())

    async def cleanup(self) -> None:
        """Release GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None

            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self._initialized = False
            logger.info("Qwen3-TTS model unloaded")

    def _decode_audio_tokens(self, tokens, sample_rate: int):
        """Decode model output to audio waveform."""
        # Placeholder - actual implementation depends on Qwen3-TTS API
        import numpy as np
        return np.zeros(sample_rate, dtype=np.float32)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences for streaming."""
        import re
        return re.split(r'(?<=[.!?])\s+', text)


# =============================================================================
# Coqui TTS Backend
# =============================================================================

class CoquiTTSBackend(TTSBackend):
    """
    Coqui TTS backend (XTTS, VITS, etc.)

    Model: tts_models/multilingual/multi-dataset/xtts_v2
    VRAM: ~1.5GB
    """

    name = "coqui"
    supports_streaming = True
    supports_voices = True
    supported_formats = ["wav", "mp3"]

    async def initialize(self) -> None:
        """Load Coqui TTS model."""
        from TTS.api import TTS

        logger.info(f"Loading Coqui TTS model {self.model_name} on {self.device}")

        # Map device string to Coqui format
        gpu = self.device != "cpu"

        self.tts = TTS(model_name=self.model_name, gpu=gpu)

        logger.info("Coqui TTS model loaded successfully")

    async def generate(self, text: str, config: TTSConfig) -> bytes:
        """Generate audio using Coqui TTS."""
        await self.ensure_initialized()

        import io
        import soundfile as sf
        import numpy as np

        # Generate audio
        wav = self.tts.tts(
            text=text,
            speaker=config.voice if config.voice != "default" else None,
            language=config.language,
            speed=config.speed
        )

        # Convert to bytes
        buffer = io.BytesIO()
        wav_array = np.array(wav, dtype=np.float32)
        sf.write(buffer, wav_array, config.sample_rate, format='WAV')
        buffer.seek(0)

        return buffer.read()

    async def get_voices(self) -> List[TTSVoice]:
        """Get Coqui speaker list."""
        await self.ensure_initialized()

        voices = []
        if hasattr(self.tts, 'speakers') and self.tts.speakers:
            for speaker in self.tts.speakers:
                voices.append(TTSVoice(
                    id=speaker,
                    name=speaker.replace("_", " ").title(),
                    language="multi"
                ))
        else:
            voices.append(TTSVoice("default", "Default", "en"))

        return voices

    async def cleanup(self) -> None:
        if hasattr(self, 'tts'):
            del self.tts
            self.tts = None
            self._initialized = False


# =============================================================================
# Piper TTS Backend (CPU-friendly)
# =============================================================================

class PiperTTSBackend(TTSBackend):
    """
    Piper TTS backend - fast, CPU-friendly TTS.

    Good for low-latency, low-resource environments.
    Model: piper-tts voices from https://github.com/rhasspy/piper
    """

    name = "piper"
    supports_streaming = False  # Piper generates all at once
    supports_voices = True
    supported_formats = ["wav"]

    async def initialize(self) -> None:
        """Load Piper voice."""
        # Piper uses ONNX models
        logger.info(f"Loading Piper voice {self.model_name}")

        # Import piper-tts
        from piper import PiperVoice

        self.voice = PiperVoice.load(self.model_name)
        logger.info("Piper voice loaded successfully")

    async def generate(self, text: str, config: TTSConfig) -> bytes:
        """Generate audio using Piper."""
        await self.ensure_initialized()

        import io
        import wave

        # Generate audio
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(config.sample_rate)

            for audio_bytes in self.voice.synthesize_stream_raw(
                text,
                length_scale=1.0 / config.speed
            ):
                wav_file.writeframes(audio_bytes)

        buffer.seek(0)
        return buffer.read()

    async def get_voices(self) -> List[TTSVoice]:
        # Piper voices are loaded at init, only one voice per model
        return [TTSVoice("default", "Piper Voice", "en")]


# =============================================================================
# Kokoro TTS Backend
# =============================================================================

class KokoroTTSBackend(TTSBackend):
    """
    Kokoro TTS backend - high quality Japanese/English TTS.

    Model: hexgrad/Kokoro-82M
    """

    name = "kokoro"
    supports_streaming = True
    supports_voices = True
    supported_formats = ["wav", "opus"]

    async def initialize(self) -> None:
        """Load Kokoro model."""
        logger.info(f"Loading Kokoro TTS model {self.model_name}")

        # Kokoro uses a custom loading process
        # Implementation depends on kokoro-tts package

        logger.info("Kokoro TTS model loaded")

    async def generate(self, text: str, config: TTSConfig) -> bytes:
        """Generate audio using Kokoro."""
        await self.ensure_initialized()
        # Implementation placeholder
        return b""

    async def get_voices(self) -> List[TTSVoice]:
        return [
            TTSVoice("af", "American Female", "en", "female"),
            TTSVoice("af_bella", "Bella", "en", "female"),
            TTSVoice("af_sarah", "Sarah", "en", "female"),
            TTSVoice("am_adam", "Adam", "en", "male"),
            TTSVoice("am_michael", "Michael", "en", "male"),
        ]


# =============================================================================
# Backend Registry
# =============================================================================

TTS_BACKENDS: Dict[str, type] = {
    "qwen3": Qwen3TTSBackend,
    "coqui": CoquiTTSBackend,
    "piper": PiperTTSBackend,
    "kokoro": KokoroTTSBackend,
}


def get_tts_backend_class(backend_name: str) -> type:
    """Get TTS backend class by name."""
    if backend_name not in TTS_BACKENDS:
        raise ValueError(
            f"Unknown TTS backend: {backend_name}. "
            f"Available: {list(TTS_BACKENDS.keys())}"
        )
    return TTS_BACKENDS[backend_name]
```

### 2.1.2 TTS Service (Orchestrator)

**New File:** `app/services/tts_service.py`

```python
"""
TTS Service - Orchestrates TTS backend based on configuration.

Handles backend selection, initialization, and request routing.
"""

import logging
from typing import AsyncGenerator, Dict, Any, Optional, List

from app import config
from app.services.tts_backends import (
    TTSBackend, TTSConfig, TTSVoice,
    get_tts_backend_class
)

logger = logging.getLogger(__name__)


class TTSService:
    """
    TTS orchestration service.

    Loads the configured backend and routes requests to it.
    """

    def __init__(self):
        self._backend: Optional[TTSBackend] = None
        self._backend_name: Optional[str] = None

    def _get_backend(self) -> TTSBackend:
        """Get or create the configured backend."""
        backend_name = config.TTS_BACKEND

        # Reinitialize if backend changed
        if self._backend_name != backend_name:
            if self._backend:
                # Cleanup old backend
                import asyncio
                asyncio.create_task(self._backend.cleanup())

            backend_class = get_tts_backend_class(backend_name)
            self._backend = backend_class(
                model_name=config.TTS_MODEL,
                device=config.TTS_DEVICE
            )
            self._backend_name = backend_name

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

        Yields:
            {"event": "metadata", "data": {...}}
            {"event": "audio", "data": {"chunk": base64, "index": int}}
            {"event": "done", "data": {"total_chunks": int}}
            {"event": "error", "data": {"code": str, "message": str}}
        """
        import base64

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
            "supported_formats": backend.supported_formats
        }

    async def cleanup(self) -> None:
        """Release backend resources."""
        if self._backend:
            await self._backend.cleanup()
            self._backend = None


# Singleton instance
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """Get TTS service singleton."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
```

---

## 3. Phase 1.2: STT Backend Abstraction

### 3.2.1 STT Backend Base Class

**New File:** `app/services/stt_backends.py`

```python
"""
STT Backends - Model-swappable speech-to-text implementations.

Follows the same pattern as image_backends.py and video_backends.py.
Add new STT models by subclassing STTBackend.
"""

import asyncio
import logging
import tempfile
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result from STT transcription."""
    text: str
    language: str
    confidence: float
    duration: float
    segments: Optional[List[Dict]] = None  # Word-level timestamps if available


@dataclass
class STTConfig:
    """Configuration for STT transcription."""
    language: Optional[str] = None  # None = auto-detect
    task: str = "transcribe"  # transcribe or translate
    word_timestamps: bool = False


class STTBackend(ABC):
    """
    Abstract base class for STT backends.

    Subclass this to add support for new STT models.
    """

    name: str = "base"
    supports_streaming: bool = False
    supports_word_timestamps: bool = False
    supported_languages: List[str] = ["en"]

    def __init__(self, model_name: str, device: str = "cuda:0"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self._lock = asyncio.Lock()
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Load model onto device."""
        pass

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        config: STTConfig
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes (wav, mp3, webm, etc.)
            config: Transcription configuration

        Returns:
            TranscriptionResult with text and metadata
        """
        pass

    async def cleanup(self) -> None:
        """Release resources."""
        pass

    async def ensure_initialized(self) -> None:
        """Thread-safe initialization."""
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self.initialize()
                    self._initialized = True


# =============================================================================
# Whisper Backend (OpenAI)
# =============================================================================

class WhisperBackend(STTBackend):
    """
    OpenAI Whisper STT backend.

    Models: tiny, base, small, medium, large, large-v2, large-v3
    VRAM: ~0.5GB (small) to ~10GB (large-v3)
    """

    name = "whisper"
    supports_streaming = False
    supports_word_timestamps = True
    supported_languages = [
        "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
        "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi"
    ]

    async def initialize(self) -> None:
        """Load Whisper model."""
        import whisper

        # Extract model size from model_name (e.g., "openai/whisper-small" -> "small")
        model_size = self.model_name.split("-")[-1] if "-" in self.model_name else self.model_name

        logger.info(f"Loading Whisper model {model_size} on {self.device}")

        self.model = whisper.load_model(model_size, device=self.device)

        logger.info("Whisper model loaded successfully")

    async def transcribe(
        self,
        audio_data: bytes,
        config: STTConfig
    ) -> TranscriptionResult:
        """Transcribe using Whisper."""
        await self.ensure_initialized()

        # Write audio to temp file (Whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            result = self.model.transcribe(
                temp_path,
                language=config.language,
                task=config.task,
                word_timestamps=config.word_timestamps
            )

            # Calculate duration from segments
            duration = 0.0
            if result.get("segments"):
                duration = result["segments"][-1].get("end", 0.0)

            # Extract segments if word timestamps requested
            segments = None
            if config.word_timestamps and result.get("segments"):
                segments = []
                for seg in result["segments"]:
                    if seg.get("words"):
                        segments.extend(seg["words"])

            return TranscriptionResult(
                text=result["text"].strip(),
                language=result.get("language", config.language or "en"),
                confidence=1.0 - result.get("no_speech_prob", 0.0),
                duration=duration,
                segments=segments
            )

        finally:
            os.unlink(temp_path)

    async def cleanup(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None

            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self._initialized = False
            logger.info("Whisper model unloaded")


# =============================================================================
# Faster-Whisper Backend
# =============================================================================

class FasterWhisperBackend(STTBackend):
    """
    Faster-Whisper STT backend (CTranslate2 optimized).

    2-4x faster than OpenAI Whisper with same accuracy.
    Lower VRAM usage.
    """

    name = "faster_whisper"
    supports_streaming = True  # Supports real-time transcription
    supports_word_timestamps = True
    supported_languages = WhisperBackend.supported_languages

    async def initialize(self) -> None:
        """Load Faster-Whisper model."""
        from faster_whisper import WhisperModel

        # Extract model size
        model_size = self.model_name.split("-")[-1] if "-" in self.model_name else self.model_name

        # Map device string
        device = "cuda" if "cuda" in self.device else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        logger.info(f"Loading Faster-Whisper model {model_size} on {device}")

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        logger.info("Faster-Whisper model loaded successfully")

    async def transcribe(
        self,
        audio_data: bytes,
        config: STTConfig
    ) -> TranscriptionResult:
        """Transcribe using Faster-Whisper."""
        await self.ensure_initialized()

        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            segments, info = self.model.transcribe(
                temp_path,
                language=config.language,
                task=config.task,
                word_timestamps=config.word_timestamps
            )

            # Collect segments
            text_parts = []
            word_segments = []
            duration = 0.0

            for segment in segments:
                text_parts.append(segment.text)
                duration = max(duration, segment.end)

                if config.word_timestamps and segment.words:
                    for word in segment.words:
                        word_segments.append({
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        })

            return TranscriptionResult(
                text=" ".join(text_parts).strip(),
                language=info.language,
                confidence=info.language_probability,
                duration=duration,
                segments=word_segments if word_segments else None
            )

        finally:
            os.unlink(temp_path)

    async def cleanup(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
            self._initialized = False


# =============================================================================
# Backend Registry
# =============================================================================

STT_BACKENDS: Dict[str, type] = {
    "whisper": WhisperBackend,
    "faster_whisper": FasterWhisperBackend,
}


def get_stt_backend_class(backend_name: str) -> type:
    """Get STT backend class by name."""
    if backend_name not in STT_BACKENDS:
        raise ValueError(
            f"Unknown STT backend: {backend_name}. "
            f"Available: {list(STT_BACKENDS.keys())}"
        )
    return STT_BACKENDS[backend_name]
```

### 3.2.2 STT Service (Orchestrator)

**New File:** `app/services/stt_service.py`

```python
"""
STT Service - Orchestrates STT backend based on configuration.
"""

import logging
from typing import Dict, Any, Optional

from app import config
from app.services.stt_backends import (
    STTBackend, STTConfig, TranscriptionResult,
    get_stt_backend_class
)

logger = logging.getLogger(__name__)


class STTService:
    """STT orchestration service."""

    def __init__(self):
        self._backend: Optional[STTBackend] = None
        self._backend_name: Optional[str] = None

    def _get_backend(self) -> STTBackend:
        """Get or create the configured backend."""
        backend_name = config.STT_BACKEND

        if self._backend_name != backend_name:
            if self._backend:
                import asyncio
                asyncio.create_task(self._backend.cleanup())

            backend_class = get_stt_backend_class(backend_name)
            self._backend = backend_class(
                model_name=config.STT_MODEL,
                device=config.STT_DEVICE
            )
            self._backend_name = backend_name

        return self._backend

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        word_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Returns dict for API compatibility:
            {
                "text": str,
                "language": str,
                "confidence": float,
                "duration": float,
                "segments": [...] (if word_timestamps=True)
            }
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
            "supported_languages": backend.supported_languages
        }

    async def cleanup(self) -> None:
        if self._backend:
            await self._backend.cleanup()
            self._backend = None


# Singleton
_stt_service: Optional[STTService] = None


def get_stt_service() -> STTService:
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
```

---

## 4. Phase 1.3: Voice Router

### 4.3.1 Voice Settings Service

**New File:** `app/services/voice_settings_service.py`

```python
"""
Voice Settings Service - Manages per-user voice preferences.

Stores settings in user_profiles table.
"""

import logging
from typing import Dict, Any, Optional

from app.services.database import get_database

logger = logging.getLogger(__name__)

DEFAULT_VOICE_SETTINGS = {
    "voice_mode": "disabled",
    "tts_voice": "default",
    "tts_speed": 1.0,
    "tts_format": "opus",
    "auto_play": True,
    "stt_language": "auto"
}


class VoiceSettingsService:
    """Manages voice settings in user profiles."""

    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user's voice settings."""
        db = get_database()

        row = db.execute(
            "SELECT profile_data FROM user_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not row or not row[0]:
            return DEFAULT_VOICE_SETTINGS.copy()

        import json
        profile = json.loads(row[0])
        voice_settings = profile.get("voice_settings", {})

        # Merge with defaults
        return {**DEFAULT_VOICE_SETTINGS, **voice_settings}

    async def update_settings(
        self,
        user_id: int,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's voice settings."""
        db = get_database()

        # Get current profile
        row = db.execute(
            "SELECT profile_data FROM user_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        import json
        if row and row[0]:
            profile = json.loads(row[0])
        else:
            profile = {}

        # Update voice settings
        current_voice = profile.get("voice_settings", {})
        current_voice.update(settings)
        profile["voice_settings"] = current_voice

        # Save
        db.execute(
            """
            INSERT INTO user_profiles (user_id, profile_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                profile_data = excluded.profile_data,
                updated_at = excluded.updated_at
            """,
            (user_id, json.dumps(profile))
        )
        db.commit()

        return {**DEFAULT_VOICE_SETTINGS, **current_voice}


# Singleton
_voice_settings_service: Optional[VoiceSettingsService] = None


def get_voice_settings_service() -> VoiceSettingsService:
    global _voice_settings_service
    if _voice_settings_service is None:
        _voice_settings_service = VoiceSettingsService()
    return _voice_settings_service
```

### 4.3.2 Voice Router

**New File:** `app/routers/voice.py`

```python
"""
Voice Router - TTS and STT API endpoints.
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sse_starlette.sse import EventSourceResponse
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
    text: str = Field(..., max_length=5000)
    voice: Optional[str] = None
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)
    format: Optional[str] = Field(default="opus", pattern="^(opus|mp3|wav)$")


class TranscriptionResponse(BaseModel):
    text: str
    language: str
    confidence: float
    duration: float


class VoiceSettings(BaseModel):
    voice_mode: str = Field(default="disabled")
    tts_voice: str = "default"
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    auto_play: bool = True
    stt_language: str = "auto"


class VoiceCapabilities(BaseModel):
    """Backend capabilities response."""
    tts_enabled: bool
    stt_enabled: bool
    tts_backend: Optional[str]
    stt_backend: Optional[str]
    tts_voices: list
    stt_languages: list


# =============================================================================
# Dependencies
# =============================================================================

async def require_voice_enabled():
    """Check if voice features are enabled."""
    if not config.VOICE_ENABLED:
        raise HTTPException(status_code=503, detail="Voice features are disabled")


# =============================================================================
# TTS Endpoints
# =============================================================================

@router.post("/tts/stream")
async def tts_stream(
    request: TTSRequest,
    user: UserResponse = Depends(require_auth),
    _: None = Depends(require_voice_enabled)
):
    """
    Stream TTS audio for given text.

    Returns Server-Sent Events with audio chunks.
    """
    tts_service = get_tts_service()
    settings_service = get_voice_settings_service()

    # Get user's voice settings
    user_settings = await settings_service.get_settings(user.id)

    # Build config
    tts_config = TTSConfig(
        voice=request.voice or user_settings.get("tts_voice", "default"),
        speed=request.speed or user_settings.get("tts_speed", 1.0),
        format=request.format or "opus",
        sample_rate=24000
    )

    async def event_generator():
        try:
            async for event in tts_service.generate_stream(request.text, tts_config):
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"])
                }
        except Exception as e:
            logger.error(f"TTS stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"code": "stream_error", "message": str(e)})
            }

    return EventSourceResponse(event_generator())


@router.get("/tts/voices")
async def get_voices(
    user: UserResponse = Depends(require_auth),
    _: None = Depends(require_voice_enabled)
):
    """Get available TTS voices from current backend."""
    tts_service = get_tts_service()
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


# =============================================================================
# STT Endpoints
# =============================================================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
    user: UserResponse = Depends(require_auth),
    _: None = Depends(require_voice_enabled)
):
    """Transcribe audio file to text."""
    # Validate file type
    allowed_types = {
        "audio/webm", "audio/wav", "audio/mp3", "audio/mpeg",
        "audio/ogg", "audio/m4a", "audio/x-m4a"
    }
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio format. Allowed: webm, wav, mp3, ogg, m4a"
        )

    # Read and validate size (10MB max)
    content = await audio.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file too large. Maximum size: 10MB"
        )

    stt_service = get_stt_service()

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
    service = get_voice_settings_service()
    updated = await service.update_settings(user.id, settings.model_dump())
    return VoiceSettings(**updated)


# =============================================================================
# Info Endpoints
# =============================================================================

@router.get("/capabilities", response_model=VoiceCapabilities)
async def get_capabilities(user: UserResponse = Depends(require_auth)):
    """Get voice backend capabilities."""
    tts_info = None
    stt_info = None
    tts_voices = []
    stt_languages = []

    if config.VOICE_ENABLED:
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
        tts_enabled=config.VOICE_ENABLED and tts_info is not None,
        stt_enabled=config.VOICE_ENABLED and stt_info is not None,
        tts_backend=tts_info["name"] if tts_info else None,
        stt_backend=stt_info["name"] if stt_info else None,
        tts_voices=tts_voices,
        stt_languages=stt_languages
    )
```

---

## 5. Phase 1.4: Frontend Integration

### 5.4.1 Voice Manager (JavaScript)

**New File:** `static/js/voice.js`

```javascript
/**
 * Voice Manager - Handles TTS playback and STT recording.
 *
 * Integrates with the chat UI to provide voice input/output.
 */

class VoiceManager {
    constructor() {
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isPlaying = false;
        this.audioQueue = [];
        this.settings = {
            voiceMode: 'disabled',
            ttsVoice: 'default',
            ttsSpeed: 1.0,
            autoPlay: true,
            sttLanguage: 'auto'
        };
        this.capabilities = null;
    }

    /**
     * Initialize voice manager - load settings and check capabilities.
     */
    async initialize() {
        try {
            // Load capabilities
            const capResp = await fetch('/api/voice/capabilities', {
                credentials: 'include'
            });
            if (capResp.ok) {
                this.capabilities = await capResp.json();
            }

            // Load user settings
            const settingsResp = await fetch('/api/voice/settings', {
                credentials: 'include'
            });
            if (settingsResp.ok) {
                this.settings = await settingsResp.json();
            }

            // Initialize AudioContext on user interaction
            document.addEventListener('click', () => this._initAudioContext(), { once: true });

            console.log('Voice manager initialized', {
                capabilities: this.capabilities,
                settings: this.settings
            });

        } catch (error) {
            console.error('Failed to initialize voice manager:', error);
        }
    }

    _initAudioContext() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    }

    /**
     * Check if TTS is available and enabled.
     */
    isTTSEnabled() {
        return this.capabilities?.tts_enabled &&
               ['tts_only', 'conversation'].includes(this.settings.voiceMode);
    }

    /**
     * Check if STT is available and enabled.
     */
    isSTTEnabled() {
        return this.capabilities?.stt_enabled &&
               ['transcribe_only', 'conversation'].includes(this.settings.voiceMode);
    }

    /**
     * Speak text using TTS streaming.
     */
    async speak(text) {
        if (!this.isTTSEnabled()) {
            console.warn('TTS not enabled');
            return;
        }

        this._initAudioContext();

        try {
            const response = await fetch('/api/voice/tts/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    text: text,
                    voice: this.settings.ttsVoice,
                    speed: this.settings.ttsSpeed,
                    format: 'opus'
                })
            });

            if (!response.ok) {
                throw new Error(`TTS request failed: ${response.status}`);
            }

            // Process SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            await this._handleTTSEvent(data);
                        } catch (e) {
                            console.error('Failed to parse TTS event:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('TTS error:', error);
            throw error;
        }
    }

    async _handleTTSEvent(event) {
        switch (event.event) {
            case 'metadata':
                console.log('TTS metadata:', event.data);
                break;

            case 'audio':
                // Decode base64 audio chunk and queue for playback
                const audioData = atob(event.data.chunk);
                const audioArray = new Uint8Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                    audioArray[i] = audioData.charCodeAt(i);
                }
                await this._playAudioChunk(audioArray.buffer);
                break;

            case 'done':
                console.log('TTS complete:', event.data);
                break;

            case 'error':
                console.error('TTS error:', event.data);
                break;
        }
    }

    async _playAudioChunk(audioBuffer) {
        try {
            const decodedAudio = await this.audioContext.decodeAudioData(audioBuffer);
            const source = this.audioContext.createBufferSource();
            source.buffer = decodedAudio;
            source.connect(this.audioContext.destination);
            source.start();
        } catch (error) {
            console.error('Audio playback error:', error);
        }
    }

    /**
     * Start recording audio for STT.
     */
    async startRecording() {
        if (!this.isSTTEnabled()) {
            console.warn('STT not enabled');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.start(100); // Collect in 100ms chunks
            this.isRecording = true;

            console.log('Recording started');

        } catch (error) {
            console.error('Failed to start recording:', error);
            throw error;
        }
    }

    /**
     * Stop recording and transcribe.
     */
    async stopRecording() {
        if (!this.mediaRecorder || !this.isRecording) {
            return null;
        }

        return new Promise((resolve, reject) => {
            this.mediaRecorder.onstop = async () => {
                try {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

                    // Transcribe
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.webm');
                    if (this.settings.sttLanguage !== 'auto') {
                        formData.append('language', this.settings.sttLanguage);
                    }

                    const response = await fetch('/api/voice/transcribe', {
                        method: 'POST',
                        credentials: 'include',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Transcription failed: ${response.status}`);
                    }

                    const result = await response.json();
                    resolve(result);

                } catch (error) {
                    reject(error);
                } finally {
                    // Cleanup
                    this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    this.isRecording = false;
                }
            };

            this.mediaRecorder.stop();
        });
    }

    /**
     * Update voice settings.
     */
    async updateSettings(settings) {
        try {
            const response = await fetch('/api/voice/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                this.settings = await response.json();
            }

            return this.settings;

        } catch (error) {
            console.error('Failed to update voice settings:', error);
            throw error;
        }
    }

    /**
     * Get available TTS voices.
     */
    async getVoices() {
        try {
            const response = await fetch('/api/voice/tts/voices', {
                credentials: 'include'
            });

            if (response.ok) {
                return await response.json();
            }

            return [];

        } catch (error) {
            console.error('Failed to get voices:', error);
            return [];
        }
    }
}

// Export singleton
window.voiceManager = new VoiceManager();
```

---

## 6. Database Schema

### 6.1 Migration 011: Voice Settings

**New File:** `app/services/migrations/011_voice_settings.py`

```python
"""
Migration 011: Voice Settings

Adds voice-related columns to support TTS/STT preferences.
Note: Voice settings are stored in user_profiles.profile_data JSON,
this migration adds the voice_enabled global flag.
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


def run_migration(db_path: str) -> bool:
    """Execute migration."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if already applied
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'voice_enabled' in columns:
            logger.info("Migration 011 already applied")
            return True

        # Add voice_enabled flag to users (admin can disable per-user)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN voice_enabled BOOLEAN DEFAULT 1
        """)

        conn.commit()
        logger.info("Migration 011 completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration 011 failed: {e}")
        return False
    finally:
        conn.close()
```

---

## 7. Configuration

### 7.1 Config Updates

**Update File:** `app/config.py`

Add the following configuration:

```python
# =============================================================================
# Voice Configuration
# =============================================================================

# Global enable/disable
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "false").lower() == "true"

# TTS Configuration
TTS_BACKEND = os.getenv("TTS_BACKEND", "qwen3")  # qwen3, coqui, piper, kokoro
TTS_MODEL = os.getenv("TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B")
TTS_DEVICE = os.getenv("TTS_DEVICE", "cuda:1")

# STT Configuration
STT_BACKEND = os.getenv("STT_BACKEND", "faster_whisper")  # whisper, faster_whisper
STT_MODEL = os.getenv("STT_MODEL", "small")  # tiny, base, small, medium, large
STT_DEVICE = os.getenv("STT_DEVICE", "cuda:1")

# Validation
if VOICE_ENABLED:
    if TTS_BACKEND not in ["qwen3", "coqui", "piper", "kokoro"]:
        raise ValueError(f"Invalid TTS_BACKEND: {TTS_BACKEND}")
    if STT_BACKEND not in ["whisper", "faster_whisper"]:
        raise ValueError(f"Invalid STT_BACKEND: {STT_BACKEND}")
```

### 7.2 Environment Variables

Add to `.env.example`:

```bash
# =============================================================================
# Voice Features (TTS/STT)
# =============================================================================

# Enable voice features (default: false)
VOICE_ENABLED=false

# TTS Backend: qwen3, coqui, piper, kokoro
TTS_BACKEND=qwen3
TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B
TTS_DEVICE=cuda:1

# STT Backend: whisper, faster_whisper
STT_BACKEND=faster_whisper
STT_MODEL=small
STT_DEVICE=cuda:1
```

---

## 8. API Reference

### 8.1 TTS Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/voice/tts/stream` | Stream TTS audio (SSE) |
| GET | `/api/voice/tts/voices` | List available voices |

### 8.2 STT Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/voice/transcribe` | Transcribe audio to text |

### 8.3 Settings Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/voice/settings` | Get user voice settings |
| PUT | `/api/voice/settings` | Update user voice settings |
| GET | `/api/voice/capabilities` | Get backend capabilities |

---

## 9. Adding New Models

### 9.1 Adding a New TTS Backend

1. Create a new class in `app/services/tts_backends.py`:

```python
class MyNewTTSBackend(TTSBackend):
    """My new TTS backend."""

    name = "my_new_tts"
    supports_streaming = True
    supports_voices = True
    supported_formats = ["wav", "mp3"]

    async def initialize(self) -> None:
        # Load your model
        pass

    async def generate(self, text: str, config: TTSConfig) -> bytes:
        # Generate audio
        pass

    async def get_voices(self) -> List[TTSVoice]:
        # Return available voices
        pass
```

2. Register in `TTS_BACKENDS` dict:

```python
TTS_BACKENDS = {
    # ... existing backends
    "my_new_tts": MyNewTTSBackend,
}
```

3. Use via environment:

```bash
TTS_BACKEND=my_new_tts
TTS_MODEL=my-model-name
```

### 9.2 Adding a New STT Backend

Same pattern - subclass `STTBackend` and register in `STT_BACKENDS`.

---

## 10. Testing Requirements

### 10.1 Unit Tests

**New File:** `tests/test_voice_backends.py`

```python
"""Test voice backend implementations."""

import pytest
from app.services.tts_backends import TTSConfig, Qwen3TTSBackend
from app.services.stt_backends import STTConfig, WhisperBackend


class TestTTSBackends:
    """Test TTS backend implementations."""

    @pytest.fixture
    def tts_config(self):
        return TTSConfig(voice="default", speed=1.0, format="wav")

    async def test_qwen3_initialization(self):
        """Test Qwen3 backend initializes correctly."""
        backend = Qwen3TTSBackend("Qwen/Qwen3-TTS-12Hz-0.6B", "cpu")
        await backend.initialize()
        assert backend._initialized
        await backend.cleanup()

    async def test_qwen3_generate(self, tts_config):
        """Test Qwen3 generates audio."""
        backend = Qwen3TTSBackend("Qwen/Qwen3-TTS-12Hz-0.6B", "cpu")
        audio = await backend.generate("Hello world", tts_config)
        assert isinstance(audio, bytes)
        assert len(audio) > 0


class TestSTTBackends:
    """Test STT backend implementations."""

    async def test_whisper_initialization(self):
        """Test Whisper backend initializes correctly."""
        backend = WhisperBackend("small", "cpu")
        await backend.initialize()
        assert backend._initialized
        await backend.cleanup()
```

### 10.2 Integration Tests

- Test TTS streaming end-to-end
- Test STT transcription with various audio formats
- Test voice settings persistence
- Test backend swapping via config

### 10.3 Manual Testing Checklist

- [ ] TTS generates audio with each backend
- [ ] STT transcribes audio with each backend
- [ ] Voice settings persist across sessions
- [ ] Backend can be swapped without restart (lazy loading)
- [ ] GPU memory is released on cleanup
- [ ] Frontend plays streamed audio correctly
- [ ] Recording and transcription flow works

---

## Implementation Checklist

- [ ] Create `app/services/tts_backends.py`
- [ ] Create `app/services/tts_service.py`
- [ ] Create `app/services/stt_backends.py`
- [ ] Create `app/services/stt_service.py`
- [ ] Create `app/services/voice_settings_service.py`
- [ ] Create `app/routers/voice.py`
- [ ] Create `static/js/voice.js`
- [ ] Create `app/services/migrations/011_voice_settings.py`
- [ ] Update `app/config.py` with voice settings
- [ ] Update `app/main.py` to register voice router
- [ ] Update `.env.example` with voice variables
- [ ] Create `tests/test_voice_backends.py`
- [ ] Update frontend to integrate voice UI

---

*End of Voice Build Plan v2.0*
