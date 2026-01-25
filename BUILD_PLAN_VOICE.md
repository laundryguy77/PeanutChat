# PeanutChat Voice Integration Build Plan

## Document Information
- **Feature:** Voice Integration (TTS + STT)
- **Version:** 1.1 (Audited)
- **Last Updated:** 2026-01-25
- **Status:** Planning (Audit Complete)

---

## Audit Summary

This document has been audited by 3 independent agents for:
1. **Technical Accuracy** - Code patterns, file locations, method signatures
2. **Completeness** - Missing steps, edge cases, error handling
3. **Integration** - Fit with existing codebase patterns

### Critical Corrections Applied

| Issue | Original | Corrected |
|-------|----------|-----------|
| Database access | `get_db_connection()` | `get_database()` (DatabaseService) |
| Auth pattern | localStorage tokens | httpOnly cookies with `credentials: 'include'` |
| SSE HTTP method | GET for TTS stream | POST (matches chat.py pattern) |
| Migration number | 003 | 011 (after existing 010) |
| Tool names | `browse_url` | `browse_website` |
| Tool names | `query_memories` | `query_memory` |
| Tool names | `generate_image` | `image` |

---

## Executive Summary

This document provides a complete implementation guide for adding voice capabilities to PeanutChat:
- **TTS (Text-to-Speech):** Qwen3-TTS for streaming audio generation
- **STT (Speech-to-Text):** Whisper for voice transcription

### Voice Modes
| Mode | STT | TTS | Description |
|------|-----|-----|-------------|
| `disabled` | No | No | No voice features (default) |
| `transcribe_only` | Yes | No | Voice input, text responses |
| `tts_only` | No | Yes | Text input, voice responses |
| `conversation` | Yes | Yes | Full voice-to-voice chat |

---

## Table of Contents

1. [Hardware Requirements](#1-hardware-requirements)
2. [Phase 1.1: TTS Backend](#2-phase-11-tts-backend)
3. [Phase 1.2: STT Backend](#3-phase-12-stt-backend)
4. [Phase 1.3: Frontend Integration](#4-phase-13-frontend-integration)
5. [Database Schema](#5-database-schema)
6. [Configuration](#6-configuration)
7. [API Reference](#7-api-reference)
8. [Error Handling](#8-error-handling)
9. [Testing Requirements](#9-testing-requirements)

---

## 1. Hardware Requirements

### GPU Allocation
| GPU | VRAM | Workload |
|-----|------|----------|
| V100 32GB | Primary | Chat model (7B-30B) |
| V100 16GB | Secondary | TTS (~1.2GB) + STT (~0.5GB) |

### Model Specifications
| Model | Size | VRAM | Purpose |
|-------|------|------|---------|
| Qwen3-TTS-12Hz-0.6B | 0.6B | ~1.2GB | Text-to-speech |
| Whisper-small | 244M | ~0.5GB | Speech-to-text |

---

## 2. Phase 1.1: TTS Backend

### 2.1.1 TTS Service

**New File:** `app/services/tts_service.py`

```python
"""
TTS Service - Qwen3-TTS text-to-speech generation.

Provides streaming audio generation with configurable voice settings.
"""

import logging
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)


@dataclass
class TTSConfig:
    """Configuration for TTS generation."""
    voice: str = "default"
    speed: float = 1.0
    format: str = "opus"  # opus, mp3, wav
    sample_rate: int = 24000


class QwenTTSService:
    """
    Qwen3-TTS streaming text-to-speech service.

    Uses the secondary GPU for inference to avoid competing
    with the main chat model.
    """

    def __init__(self):
        self.model = None
        self.device = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self, model_name: str, device: str = "cuda:1"):
        """
        Load TTS model onto specified device.

        Args:
            model_name: Hugging Face model ID (e.g., "Qwen/Qwen3-TTS-12Hz-0.6B")
            device: CUDA device for inference
        """
        async with self._lock:
            if self._initialized:
                return

            try:
                # Import here to avoid loading on startup if disabled
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer

                logger.info(f"Loading TTS model {model_name} on {device}")

                self.device = device
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map=device
                )

                self._initialized = True
                logger.info("TTS model loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load TTS model: {e}")
                raise

    async def generate_stream(
        self,
        text: str,
        config: Optional[TTSConfig] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream audio chunks for given text.

        Args:
            text: Text to convert to speech
            config: TTS configuration options

        Yields:
            {
                "event": "audio" | "metadata" | "done" | "error",
                "data": {...}
            }
        """
        if not self._initialized:
            yield {"event": "error", "data": {"code": "not_initialized", "message": "TTS service not initialized"}}
            return

        config = config or TTSConfig()

        try:
            # Yield metadata first
            yield {
                "event": "metadata",
                "data": {
                    "sample_rate": config.sample_rate,
                    "format": config.format,
                    "voice": config.voice
                }
            }

            # Generate audio in chunks
            chunk_index = 0
            async for audio_chunk in self._generate_audio(text, config):
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

        except asyncio.CancelledError:
            logger.info("TTS generation cancelled")
            raise
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            yield {"event": "error", "data": {"code": "generation_failed", "message": str(e)}}

    async def _generate_audio(
        self,
        text: str,
        config: TTSConfig
    ) -> AsyncGenerator[bytes, None]:
        """Internal audio generation - implement based on Qwen3-TTS API."""
        # This is a placeholder - actual implementation depends on
        # Qwen3-TTS specific API
        import torch

        # Tokenize input
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        # Generate in chunks (streaming)
        # Actual implementation will depend on model's streaming capabilities
        with torch.no_grad():
            # Placeholder for actual generation
            pass

        # Yield audio chunks
        # Each chunk should be ~100-200ms of audio
        yield b""  # Placeholder

    async def cleanup(self):
        """Release GPU memory."""
        async with self._lock:
            if self.model is not None:
                del self.model
                self.model = None

                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                self._initialized = False
                logger.info("TTS model unloaded")


# Singleton instance
_tts_service: Optional[QwenTTSService] = None

def get_tts_service() -> QwenTTSService:
    """Get TTS service singleton."""
    global _tts_service
    if _tts_service is None:
        _tts_service = QwenTTSService()
    return _tts_service
```

### 2.1.2 Voice Router

**New File:** `app/routers/voice.py`

```python
"""
Voice Router - TTS and STT API endpoints.

Provides voice transcription and text-to-speech capabilities.
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from app.middleware.auth import get_current_user, require_auth
from app.models.auth_schemas import UserResponse
from app.services.tts_service import get_tts_service, TTSConfig
from app.services.stt_service import get_stt_service
from app.services.voice_settings_service import get_voice_settings_service
from app import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])


# =============================================================================
# Pydantic Models
# =============================================================================

class TTSRequest(BaseModel):
    """Request body for TTS generation."""
    text: str = Field(..., max_length=5000)
    voice: Optional[str] = None
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)
    format: Optional[str] = Field(default="opus", pattern="^(opus|mp3|wav)$")


class TranscriptionResponse(BaseModel):
    """Response from STT transcription."""
    text: str
    language: str
    confidence: float
    duration: float


class VoiceSettings(BaseModel):
    """User voice settings."""
    voice_mode: str = Field(default="disabled", pattern="^(disabled|transcribe_only|tts_only|conversation)$")
    tts_voice: str = "default"
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    auto_play: bool = True
    stt_language: str = "auto"


# =============================================================================
# Dependency
# =============================================================================

async def require_voice_enabled():
    """Dependency that checks if voice features are enabled."""
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

    Events:
    - metadata: {sample_rate, format, voice}
    - audio: {chunk: base64, index: int}
    - done: {total_chunks: int}
    - error: {code, message}
    """
    tts_service = get_tts_service()

    # Get user's voice settings
    settings_service = get_voice_settings_service()
    user_settings = await settings_service.get_settings(user.id)

    # Build config from request + user defaults
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
    """
    Transcribe audio file to text.

    Accepts: webm, wav, mp3, ogg, m4a
    Max size: 10MB
    Max duration: 60 seconds
    """
    # Validate file type
    allowed_types = {"audio/webm", "audio/wav", "audio/mp3", "audio/mpeg",
                    "audio/ogg", "audio/m4a", "audio/x-m4a"}
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: webm, wav, mp3, ogg, m4a"
        )

    # Validate file size (10MB)
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
```

---

## 3. Phase 1.2: STT Backend

### 3.2.1 STT Service

**New File:** `app/services/stt_service.py`

```python
"""
STT Service - Whisper speech-to-text transcription.

Provides audio transcription with language detection.
"""

import logging
import asyncio
import tempfile
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WhisperSTTService:
    """
    Whisper speech-to-text service.

    Uses the secondary GPU alongside TTS service.
    """

    def __init__(self):
        self.model = None
        self.device = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self, model_size: str = "small", device: str = "cuda:1"):
        """
        Load Whisper model.

        Args:
            model_size: tiny, base, small, medium, large
            device: CUDA device for inference
        """
        async with self._lock:
            if self._initialized:
                return

            try:
                import whisper
                import torch

                logger.info(f"Loading Whisper {model_size} on {device}")

                self.device = device
                self.model = whisper.load_model(model_size, device=device)

                self._initialized = True
                logger.info("Whisper model loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes
            language: Optional language code (e.g., "en", "es")

        Returns:
            {
                "text": str,
                "language": str,
                "confidence": float,
                "duration": float
            }
        """
        if not self._initialized:
            raise RuntimeError("STT service not initialized")

        # Write to temp file (Whisper expects file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            f.write(audio_data)

        try:
            # Run transcription in thread pool to not block
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                temp_path,
                language
            )
            return result

        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _transcribe_sync(
        self,
        audio_path: str,
        language: Optional[str]
    ) -> Dict[str, Any]:
        """Synchronous transcription (runs in thread pool)."""
        import whisper

        options = {}
        if language:
            options["language"] = language

        result = self.model.transcribe(audio_path, **options)

        # Calculate confidence from segments
        segments = result.get("segments", [])
        if segments:
            avg_confidence = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments)
            confidence = 1.0 - avg_confidence  # Higher = more confident
        else:
            confidence = 0.0

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "confidence": confidence,
            "duration": result.get("duration", 0.0)
        }

    async def cleanup(self):
        """Release GPU memory."""
        async with self._lock:
            if self.model is not None:
                del self.model
                self.model = None

                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                self._initialized = False
                logger.info("Whisper model unloaded")


# Singleton
_stt_service: Optional[WhisperSTTService] = None

def get_stt_service() -> WhisperSTTService:
    """Get STT service singleton."""
    global _stt_service
    if _stt_service is None:
        _stt_service = WhisperSTTService()
    return _stt_service
```

---

## 4. Phase 1.3: Frontend Integration

### 4.3.1 Voice Manager

**New File:** `static/js/voice.js`

```javascript
/**
 * VoiceManager - Handles TTS playback and STT recording.
 *
 * Integrates with chat.js for voice-enabled conversations.
 */

class VoiceManager {
    constructor() {
        this.mode = 'disabled';  // disabled, transcribe_only, tts_only, conversation
        this.settings = null;
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioQueue = [];
        this.isPlaying = false;
        this.isRecording = false;

        // Event callbacks
        this.onTranscription = null;
        this.onPlaybackStart = null;
        this.onPlaybackEnd = null;
        this.onError = null;
    }

    /**
     * Initialize voice features.
     */
    async init() {
        try {
            // Load user settings
            await this.loadSettings();

            // Initialize audio context (must be after user interaction)
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            console.log('VoiceManager initialized');
        } catch (error) {
            console.error('VoiceManager init failed:', error);
            this.onError?.('Failed to initialize voice features');
        }
    }

    /**
     * Load voice settings from server.
     */
    async loadSettings() {
        try {
            const response = await fetch('/api/voice/settings', {
                credentials: 'include'  // Use httpOnly cookies
            });

            if (response.ok) {
                this.settings = await response.json();
                this.mode = this.settings.voice_mode;
            }
        } catch (error) {
            console.error('Failed to load voice settings:', error);
        }
    }

    /**
     * Check if STT is enabled for current mode.
     */
    get sttEnabled() {
        return this.mode === 'transcribe_only' || this.mode === 'conversation';
    }

    /**
     * Check if TTS is enabled for current mode.
     */
    get ttsEnabled() {
        return this.mode === 'tts_only' || this.mode === 'conversation';
    }

    // =========================================================================
    // Recording (STT)
    // =========================================================================

    /**
     * Start recording audio from microphone.
     */
    async startRecording() {
        if (!this.sttEnabled) {
            this.onError?.('Voice input is not enabled');
            return false;
        }

        if (this.isRecording) {
            return false;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    this.audioChunks.push(e.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());

                // Create blob from chunks
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

                // Send for transcription
                await this._transcribe(audioBlob);
            };

            this.mediaRecorder.start(100);  // Collect chunks every 100ms
            this.isRecording = true;

            return true;

        } catch (error) {
            console.error('Failed to start recording:', error);

            if (error.name === 'NotAllowedError') {
                this.onError?.('Microphone permission denied. Please enable in browser settings.');
            } else {
                this.onError?.('Failed to access microphone');
            }

            return false;
        }
    }

    /**
     * Stop recording and transcribe.
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
        }
    }

    /**
     * Cancel recording without transcribing.
     */
    cancelRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.ondataavailable = null;
            this.mediaRecorder.onstop = null;
            this.mediaRecorder.stop();
            this.audioChunks = [];
            this.isRecording = false;
        }
    }

    /**
     * Send audio to STT endpoint.
     */
    async _transcribe(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const response = await fetch('/api/voice/transcribe', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Transcription failed');
            }

            const result = await response.json();
            this.onTranscription?.(result.text);

        } catch (error) {
            console.error('Transcription error:', error);
            this.onError?.(error.message);
        }
    }

    // =========================================================================
    // Playback (TTS)
    // =========================================================================

    /**
     * Queue text for TTS playback.
     */
    async speak(text) {
        if (!this.ttsEnabled) {
            return;
        }

        // Add to queue
        this.audioQueue.push(text);

        // Start playback if not already playing
        if (!this.isPlaying) {
            await this._processQueue();
        }
    }

    /**
     * Process TTS queue sequentially.
     */
    async _processQueue() {
        if (this.audioQueue.length === 0) {
            this.isPlaying = false;
            this.onPlaybackEnd?.();
            return;
        }

        this.isPlaying = true;
        this.onPlaybackStart?.();

        const text = this.audioQueue.shift();

        try {
            await this._playTTS(text);
        } catch (error) {
            console.error('TTS playback error:', error);
            this.onError?.(error.message);
        }

        // Process next item
        await this._processQueue();
    }

    /**
     * Stream and play TTS audio.
     */
    async _playTTS(text) {
        return new Promise((resolve, reject) => {
            const audioChunks = [];
            let sampleRate = 24000;

            // Use POST for SSE (matches chat.py pattern)
            fetch('/api/voice/tts/stream', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            }).then(response => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                const processStream = async () => {
                    while (true) {
                        const { done, value } = await reader.read();

                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || '';

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = JSON.parse(line.slice(6));

                                if (data.sample_rate) {
                                    sampleRate = data.sample_rate;
                                }

                                if (data.chunk) {
                                    const chunk = Uint8Array.from(atob(data.chunk), c => c.charCodeAt(0));
                                    audioChunks.push(chunk);
                                }
                            }

                            if (line.startsWith('event: done')) {
                                // All chunks received, play audio
                                await this._playAudioChunks(audioChunks, sampleRate);
                                resolve();
                                return;
                            }

                            if (line.startsWith('event: error')) {
                                const errorData = JSON.parse(lines[lines.indexOf(line) + 1]?.slice(6) || '{}');
                                reject(new Error(errorData.message || 'TTS error'));
                                return;
                            }
                        }
                    }
                };

                processStream().catch(reject);
            }).catch(reject);
        });
    }

    /**
     * Play collected audio chunks.
     */
    async _playAudioChunks(chunks, sampleRate) {
        if (chunks.length === 0) return;

        // Combine chunks
        const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
        const combined = new Uint8Array(totalLength);
        let offset = 0;
        for (const chunk of chunks) {
            combined.set(chunk, offset);
            offset += chunk.length;
        }

        // Decode and play
        const audioBuffer = await this.audioContext.decodeAudioData(combined.buffer);
        const source = this.audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.audioContext.destination);

        return new Promise(resolve => {
            source.onended = resolve;
            source.start(0);
        });
    }

    /**
     * Stop current playback and clear queue.
     */
    stopPlayback() {
        this.audioQueue = [];
        // Note: stopping current playback would require tracking active source
    }

    // =========================================================================
    // Cleanup
    // =========================================================================

    /**
     * Clean up resources.
     */
    cleanup() {
        this.cancelRecording();
        this.stopPlayback();

        if (this.audioContext && this.audioContext.state !== 'closed') {
            this.audioContext.close();
        }
    }
}

// Export for use in other modules
window.VoiceManager = VoiceManager;
```

### 4.3.2 Chat Integration

Add to `static/js/chat.js`:

```javascript
// In ChatManager constructor, add:
constructor() {
    // ... existing code ...
    this.voiceManager = null;
}

// Add method to initialize voice:
async initVoice() {
    if (window.VoiceManager) {
        this.voiceManager = new VoiceManager();
        await this.voiceManager.init();

        // Set up callbacks
        this.voiceManager.onTranscription = (text) => {
            // Put transcribed text in input
            const input = document.getElementById('messageInput');
            if (input) {
                input.value = text;
                input.focus();
            }
        };

        this.voiceManager.onError = (message) => {
            this.showToast(message, 'error');
        };
    }
}

// Add to processAssistantMessage or similar:
// When assistant message is complete:
if (this.voiceManager?.ttsEnabled && !isThinking) {
    await this.voiceManager.speak(messageContent);
}
```

---

## 5. Database Schema

### Migration 011

**Location:** `app/services/database.py`

Add method `_migration_011_voice_settings`:

```python
def _migration_011_voice_settings(self):
    """Add voice settings to user_settings table."""

    # Add voice columns to existing user_settings table
    columns_to_add = [
        ("voice_mode", "TEXT", "'disabled'"),
        ("tts_voice", "TEXT", "'default'"),
        ("tts_speed", "REAL", "1.0"),
        ("auto_play", "INTEGER", "1"),
        ("stt_language", "TEXT", "'auto'")
    ]

    for col_name, col_type, default in columns_to_add:
        try:
            self.execute(f"""
                ALTER TABLE user_settings
                ADD COLUMN {col_name} {col_type} DEFAULT {default}
            """)
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                raise

    logger.info("Migration 011 complete: voice settings columns added")
```

---

## 6. Configuration

### Environment Variables

Add to `app/config.py`:

```python
# Voice Configuration
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "false").lower() == "true"

# TTS Configuration
TTS_MODEL = os.getenv("TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B")
TTS_DEVICE = os.getenv("TTS_DEVICE", "cuda:1")

# STT Configuration
STT_MODEL = os.getenv("STT_MODEL", "small")  # tiny, base, small, medium
STT_DEVICE = os.getenv("STT_DEVICE", "cuda:1")

# Voice Limits
VOICE_MAX_AUDIO_LENGTH = int(os.getenv("VOICE_MAX_AUDIO_LENGTH", "60"))  # seconds
VOICE_MAX_TTS_LENGTH = int(os.getenv("VOICE_MAX_TTS_LENGTH", "5000"))  # characters

# Timeouts
VOICE_TRANSCRIBE_TIMEOUT = int(os.getenv("VOICE_TRANSCRIBE_TIMEOUT", "30"))
VOICE_TTS_TIMEOUT = int(os.getenv("VOICE_TTS_TIMEOUT", "60"))
```

### .env.example

```bash
# Voice Features
VOICE_ENABLED=false

# TTS (Text-to-Speech)
TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B
TTS_DEVICE=cuda:1

# STT (Speech-to-Text)
STT_MODEL=small
STT_DEVICE=cuda:1

# Limits
VOICE_MAX_AUDIO_LENGTH=60
VOICE_MAX_TTS_LENGTH=5000
```

---

## 7. API Reference

### Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/voice/tts/stream` | Stream TTS audio | Yes |
| POST | `/api/voice/transcribe` | Transcribe audio | Yes |
| GET | `/api/voice/settings` | Get voice settings | Yes |
| PUT | `/api/voice/settings` | Update voice settings | Yes |

### POST /api/voice/tts/stream

**Request:**
```json
{
  "text": "Hello world",
  "voice": "default",
  "speed": 1.0,
  "format": "opus"
}
```

**Response (SSE):**
```
event: metadata
data: {"sample_rate": 24000, "format": "opus", "voice": "default"}

event: audio
data: {"chunk": "base64...", "index": 0}

event: audio
data: {"chunk": "base64...", "index": 1}

event: done
data: {"total_chunks": 2}
```

### POST /api/voice/transcribe

**Request:** multipart/form-data with `audio` file

**Response:**
```json
{
  "text": "Hello world",
  "language": "en",
  "confidence": 0.95,
  "duration": 1.5
}
```

**Errors:**
| Code | Description |
|------|-------------|
| 400 | Invalid audio format |
| 413 | Audio file too large (>10MB) |
| 500 | Transcription failed |
| 503 | Voice features disabled |

---

## 8. Error Handling

### STT Errors

| Error | HTTP Code | User Message |
|-------|-----------|--------------|
| Invalid format | 400 | "Unsupported audio format. Use webm, wav, or mp3." |
| File too large | 413 | "Audio file too large. Maximum 10MB." |
| Audio too short | 400 | "Recording too short. Please record at least 0.5 seconds." |
| Transcription failed | 500 | "Failed to transcribe audio. Please try again." |
| Service unavailable | 503 | "Voice features are currently unavailable." |

### TTS Errors

| Error | Handling |
|-------|----------|
| Text too long | Truncate to 5000 chars with warning |
| Stream disconnected | Auto-reconnect up to 3 times |
| Model unavailable | Skip TTS, show text-only response |
| Generation timeout | Cancel and show error toast |

### Reconnection Strategy

```javascript
// SSE reconnection with exponential backoff
const reconnect = async (attempt = 0) => {
    if (attempt >= 3) {
        showError("Voice unavailable. Falling back to text mode.");
        return;
    }

    const delay = Math.pow(2, attempt) * 1000;  // 1s, 2s, 4s
    await sleep(delay);

    try {
        await connect();
    } catch (e) {
        await reconnect(attempt + 1);
    }
};
```

---

## 9. Testing Requirements

### Unit Tests

```python
# tests/test_voice_services.py

async def test_tts_config_validation():
    """Verify TTSConfig validates speed range."""

async def test_stt_language_detection():
    """Verify Whisper detects language correctly."""

async def test_voice_settings_persistence():
    """Verify settings save and load correctly."""

async def test_disabled_mode_rejects_requests():
    """Verify endpoints return 503 when VOICE_ENABLED=false."""
```

### Integration Tests

```python
# tests/test_voice_integration.py

async def test_full_conversation_flow():
    """Test: record -> transcribe -> chat -> TTS -> playback."""

async def test_mode_switching():
    """Verify mode changes take effect immediately."""

async def test_concurrent_requests():
    """Verify multiple users can use voice simultaneously."""
```

### Performance Targets

| Metric | Target |
|--------|--------|
| STT latency | < 2x audio duration |
| TTS first chunk | < 500ms |
| Memory per stream | < 50MB |
| Concurrent streams | 5 TTS + 10 STT |

---

## Implementation Phases

### Phase 1.1: TTS Backend
- [ ] Create `app/services/tts_service.py`
- [ ] Add Qwen3-TTS model loading
- [ ] Implement streaming generation
- [ ] Add to `app/routers/voice.py`

### Phase 1.2: STT Backend
- [ ] Create `app/services/stt_service.py`
- [ ] Add Whisper model loading
- [ ] Implement transcription
- [ ] Add endpoint to voice router

### Phase 1.3: Frontend Integration
- [ ] Create `static/js/voice.js`
- [ ] Add recording UI
- [ ] Add playback queue
- [ ] Integrate with chat.js
- [ ] Add voice settings to settings modal

---

*End of Voice Build Plan*
