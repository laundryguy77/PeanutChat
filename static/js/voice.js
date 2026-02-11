// Voice Manager - Handles TTS playback and STT recording
export class VoiceManager {
    constructor(app) {
        this.app = app;
        this.settings = {
            voice_mode: 'disabled',
            tts_voice: 'default',
            tts_speed: 1.0,
            auto_play: false,
            stt_language: 'en',
            voice_enabled: false
        };

        // Recording state
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStream = null;

        // Playback state
        this.audioContext = null;
        this.currentSource = null;
        this.isPlaying = false;
        this.audioQueue = [];

        // SSE state
        this.ttsEventSource = null;

        this.init();
    }

    async init() {
        try {
            await this.loadSettings();
            this.setupEventListeners();
            console.log('[Voice] Initialized with settings:', this.settings);
        } catch (error) {
            console.error('[Voice] Failed to initialize:', error);
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/voice/settings', {
                credentials: 'include'
            });
            if (response.ok) {
                this.settings = await response.json();
            }
        } catch (error) {
            console.warn('[Voice] Failed to load settings:', error);
        }
    }

    async saveSettings(newSettings) {
        try {
            const response = await fetch('/api/voice/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(newSettings)
            });
            if (response.ok) {
                const result = await response.json();
                this.settings = { ...this.settings, ...result.settings };
                return true;
            }
        } catch (error) {
            console.error('[Voice] Failed to save settings:', error);
        }
        return false;
    }

    setupEventListeners() {
        // Voice input button
        const voiceBtn = document.getElementById('voice-input-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleRecording());
        }

        // Start voice conversation button (enables conversation mode + auto-play)
        const voiceConversationBtn = document.getElementById('voice-conversation-btn');
        if (voiceConversationBtn) {
            voiceConversationBtn.addEventListener('click', () => this.startVoiceConversation());
        }

        // TTS toggle in tools menu (optional)
        const ttsToggle = document.getElementById('tts-toggle');
        if (ttsToggle) {
            ttsToggle.addEventListener('change', () => {
                const enabled = ttsToggle.checked;
                this.settings.auto_play = enabled;
                this.saveSettings({ auto_play: enabled });
            });
        }
    }

    // ==================== Recording (STT) ====================

    get canRecord() {
        return this.settings.voice_enabled &&
               (this.settings.voice_mode === 'transcribe_only' ||
                this.settings.voice_mode === 'conversation');
    }

    async toggleRecording() {
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startVoiceConversation() {
        // Toggle stop if already recording
        if (this.isRecording) {
            await this.stopRecording();
            return;
        }

        // Reload to ensure we have the latest server flag
        await this.loadSettings();

        if (!this.settings.voice_enabled) {
            this.showToast('Voice features are disabled on the server', 'warning');
            return;
        }

        // Enable "conversation" mode and auto-play for hands-free voice chat
        const ok = await this.saveSettings({
            voice_mode: 'conversation',
            auto_play: true
        });
        if (!ok) {
            this.showToast('Failed to enable voice conversation mode', 'error');
            return;
        }

        // Refresh local settings before recording
        await this.loadSettings();
        await this.startRecording();
    }

    async startRecording() {
        if (!this.canRecord) {
            this.showToast('Voice input is not enabled', 'warning');
            return;
        }

        try {
            this.recordingStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(this.recordingStream, {
                mimeType: this.getSupportedMimeType()
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                await this.processRecording();
            };

            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            this.updateRecordingUI(true);

            console.log('[Voice] Recording started');
        } catch (error) {
            console.error('[Voice] Failed to start recording:', error);
            this.showToast('Failed to access microphone', 'error');
        }
    }

    async stopRecording() {
        if (!this.mediaRecorder || !this.isRecording) return;

        this.mediaRecorder.stop();
        this.isRecording = false;
        this.updateRecordingUI(false);

        // Stop all tracks
        if (this.recordingStream) {
            this.recordingStream.getTracks().forEach(track => track.stop());
            this.recordingStream = null;
        }

        console.log('[Voice] Recording stopped');
    }

    async processRecording() {
        if (this.audioChunks.length === 0) return;

        const audioBlob = new Blob(this.audioChunks, {
            type: this.getSupportedMimeType()
        });
        this.audioChunks = [];

        // Show processing indicator
        this.updateRecordingUI(false, true);

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('language', this.settings.stt_language);

            const response = await fetch('/api/voice/transcribe', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                if (result.text) {
                    // Insert transcribed text into message input
                    const input = document.getElementById('message-input');
                    if (input) {
                        const currentText = input.value;
                        const separator = currentText && !currentText.endsWith(' ') ? ' ' : '';
                        input.value = currentText + separator + result.text;
                        input.dispatchEvent(new Event('input'));
                        input.focus();
                    }
                    console.log('[Voice] Transcription:', result.text);

                    // In conversation mode: auto-send the turn.
                    if (this.settings.voice_mode === 'conversation' && this.app && typeof this.app.sendMessage === 'function') {
                        await this.app.sendMessage();
                    }
                }
            } else {
                const error = await response.json();
                this.showToast(error.detail || 'Transcription failed', 'error');
            }
        } catch (error) {
            console.error('[Voice] Transcription error:', error);
            this.showToast('Failed to transcribe audio', 'error');
        }

        this.updateRecordingUI(false, false);
    }

    getSupportedMimeType() {
        const types = ['audio/webm', 'audio/ogg', 'audio/wav'];
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        return 'audio/webm';
    }

    updateRecordingUI(isRecording, isProcessing = false) {
        const voiceBtn = document.getElementById('voice-input-btn');
        if (!voiceBtn) return;

        const icon = voiceBtn.querySelector('.material-symbols-outlined');

        if (isProcessing) {
            icon.textContent = 'sync';
            icon.classList.add('animate-spin');
            voiceBtn.classList.add('text-yellow-500');
            voiceBtn.classList.remove('text-red-500', 'text-gray-400');
        } else if (isRecording) {
            icon.textContent = 'stop_circle';
            icon.classList.remove('animate-spin');
            voiceBtn.classList.add('text-red-500', 'animate-pulse');
            voiceBtn.classList.remove('text-yellow-500', 'text-gray-400');
        } else {
            icon.textContent = 'mic';
            icon.classList.remove('animate-spin');
            voiceBtn.classList.remove('text-red-500', 'text-yellow-500', 'animate-pulse');
            voiceBtn.classList.add('text-gray-400', 'hover:text-white');
        }
    }

    // ==================== Playback (TTS) ====================

    get canPlayTTS() {
        return this.settings.voice_enabled &&
               (this.settings.voice_mode === 'tts_only' ||
                this.settings.voice_mode === 'conversation');
    }

    async speakText(text, force = false) {
        // Check if TTS is enabled (unless forced via speaker button)
        if (!force && !this.canPlayTTS) {
            console.log('[Voice] TTS not enabled');
            return;
        }

        // Check if voice features are enabled on server (always required)
        if (!this.settings.voice_enabled) {
            console.log('[Voice] Voice features disabled on server');
            this.showToast('Voice features are not enabled on the server', 'warning');
            return;
        }

        if (!text || text.trim().length === 0) {
            return;
        }

        // Clean text - remove markdown, code blocks, etc.
        const cleanText = this.cleanTextForTTS(text);
        if (cleanText.length === 0) return;

        console.log('[Voice] Speaking text:', cleanText.substring(0, 50) + '...');

        try {
            await this.playTTSStream(cleanText);
        } catch (error) {
            console.error('[Voice] TTS playback error:', error);
            this.showToast('Failed to play audio', 'error');
        }
    }

    cleanTextForTTS(text) {
        // Remove code blocks
        text = text.replace(/```[\s\S]*?```/g, 'code block');
        // Remove inline code
        text = text.replace(/`[^`]+`/g, 'code');
        // Remove markdown links, keep text
        text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
        // Remove markdown formatting
        text = text.replace(/[*_~]+/g, '');
        // Remove headers
        text = text.replace(/^#+\s*/gm, '');
        // Remove bullet points
        text = text.replace(/^[-*]\s*/gm, '');
        // Collapse multiple spaces/newlines
        text = text.replace(/\s+/g, ' ');
        return text.trim();
    }

    async playTTSStream(text) {
        // Cancel any existing playback
        this.stopPlayback();

        // Initialize audio context if needed
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        // Resume if suspended (browser autoplay policy)
        if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }

        return new Promise((resolve, reject) => {
            const chunks = [];

            this.ttsEventSource = new EventSource('/api/voice/tts/stream?' + new URLSearchParams({
                text: text,
                voice: this.settings.tts_voice,
                speed: this.settings.tts_speed
            }));

            this.ttsEventSource.addEventListener('audio', (event) => {
                const data = JSON.parse(event.data);
                const chunk = Uint8Array.from(atob(data.chunk), c => c.charCodeAt(0));
                chunks.push(chunk);
            });

            this.ttsEventSource.addEventListener('done', async (event) => {
                this.ttsEventSource.close();
                this.ttsEventSource = null;

                // Combine chunks into single buffer
                const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
                const combined = new Uint8Array(totalLength);
                let offset = 0;
                for (const chunk of chunks) {
                    combined.set(chunk, offset);
                    offset += chunk.length;
                }

                try {
                    await this.playAudioBuffer(combined.buffer);
                    resolve();
                } catch (e) {
                    reject(e);
                }
            });

            this.ttsEventSource.addEventListener('error', (event) => {
                console.error('[Voice] TTS stream error:', event);
                this.ttsEventSource.close();
                this.ttsEventSource = null;
                reject(new Error('TTS stream error'));
            });

            this.ttsEventSource.onerror = (error) => {
                console.error('[Voice] EventSource error:', error);
                this.ttsEventSource.close();
                this.ttsEventSource = null;
                reject(error);
            };
        });
    }

    async playAudioBuffer(arrayBuffer) {
        try {
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);

            this.currentSource = source;
            this.isPlaying = true;

            source.onended = () => {
                this.isPlaying = false;
                this.currentSource = null;
            };

            source.start(0);
        } catch (error) {
            console.error('[Voice] Failed to decode/play audio:', error);
            throw error;
        }
    }

    stopPlayback() {
        if (this.currentSource) {
            try {
                this.currentSource.stop();
            } catch (e) {
                // Ignore if already stopped
            }
            this.currentSource = null;
        }

        if (this.ttsEventSource) {
            this.ttsEventSource.close();
            this.ttsEventSource = null;
        }

        this.isPlaying = false;
    }

    // ==================== Auto-speak Integration ====================

    async autoSpeak(text) {
        if (this.settings.auto_play && this.canPlayTTS) {
            await this.speakText(text);
        }
    }

    // ==================== Utilities ====================

    showToast(message, type = 'error') {
        if (this.app.chatManager) {
            this.app.chatManager.showToast(message, type);
        } else {
            console.log(`[Toast ${type}]: ${message}`);
        }
    }

    cleanup() {
        this.stopRecording();
        this.stopPlayback();

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    }
}

// Global voice manager instance (initialized from app.js)
export let voiceManager = null;

export function initVoiceManager(app) {
    voiceManager = new VoiceManager(app);
    return voiceManager;
}
