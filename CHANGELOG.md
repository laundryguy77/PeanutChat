# Changelog

All notable changes to PeanutChat are documented in this file.

---

## [2026-01-25] - Voice Integration & Admin Portal

### Voice System (TTS/STT)

**Model-Swappable Architecture**
- Added abstract `TTSBackend` and `STTBackend` base classes
- TTS backends: Edge-TTS, Piper, Coqui, Kokoro
- STT backends: Whisper, Faster-Whisper, Vosk
- Backend selection via environment variables (`TTS_BACKEND`, `STT_BACKEND`)
- Lazy model loading to conserve GPU memory

**Voice Services**
- `tts_service.py` - TTS orchestration with streaming support
- `stt_service.py` - STT orchestration with language detection
- `voice_settings_service.py` - Per-user voice preferences
- Voice modes: disabled, transcribe_only, tts_only, conversation

**Voice API Endpoints**
- `POST /api/voice/tts/stream` - Stream TTS audio (SSE)
- `POST /api/voice/transcribe` - Transcribe audio to text
- `GET /api/voice/tts/voices` - List available voices
- `GET/PUT /api/voice/settings` - User voice settings
- `GET /api/voice/capabilities` - Backend capabilities

### Admin Portal

**User Management**
- Create, edit, delete users via web UI
- Password reset functionality
- Activate/deactivate user accounts
- Mode restrictions (normal_only, no_full_unlock)
- Per-user voice enable/disable

**Feature Flag System**
- Global feature defaults in `feature_flags` table
- Per-user overrides in `user_feature_overrides` table
- Features: web_search, memory, tts, stt, image_gen, video_gen, knowledge_base

**Dashboard & Audit**
- System statistics (users, conversations, messages)
- Admin audit log for all administrative actions
- Filterable by admin, action type, date range

**Admin API Endpoints**
- `GET/POST /api/admin/users` - List/create users
- `PATCH/DELETE /api/admin/users/{id}` - Update/delete user
- `POST /api/admin/users/{id}/reset-password` - Reset password
- `GET/PATCH /api/admin/features` - Feature flag management
- `PUT /api/admin/users/{id}/features/{key}` - User feature override
- `GET /api/admin/audit-log` - View audit log
- `GET /api/admin/dashboard` - System statistics

**Admin Setup**
- `scripts/create_admin.py` - CLI script to create admin users
- Interactive and command-line modes
- Promote existing users to admin

### Database Migrations

- Migration 011: Voice settings (`voice_enabled` column on users)
- Migration 012: Admin features (`is_admin`, `is_active`, `mode_restriction` columns; feature tables)

### New Files

**Voice System**
- `app/services/tts_backends.py` - TTS backend implementations
- `app/services/stt_backends.py` - STT backend implementations
- `app/services/tts_service.py` - TTS orchestration
- `app/services/stt_service.py` - STT orchestration
- `app/services/voice_settings_service.py` - Voice settings
- `app/routers/voice.py` - Voice API router

**Admin System**
- `app/services/admin_service.py` - Admin business logic
- `app/services/feature_service.py` - Feature flag management
- `app/routers/admin.py` - Admin API router
- `static/admin.html` - Admin portal UI
- `static/js/admin.js` - Admin panel JavaScript
- `scripts/create_admin.py` - Admin user creation script

### Configuration Changes

New environment variables:
```bash
# Voice Features
VOICE_ENABLED=false
TTS_BACKEND=edge
TTS_MODEL=default
STT_BACKEND=faster_whisper
STT_MODEL=small
```

---

## [2026-01-24] - UI/Backend Sync & System Improvements

### UI-Backend Sync Fixes

**Error Handling & User Feedback**
- Added `showToast()` method to `chat.js` for visual error/success notifications
- Fixed silent error handling in `regenerateResponse()` and `saveEdit()` - now shows user feedback
- Added response validation for fork/edit API calls
- Added error boundaries in SSE handler for malformed JSON

**Race Condition Fixes**
- Fixed race condition in `sendMessage()` - stores original message/images before clearing
- Restores input state on error so users don't lose their message

**Stream Cleanup**
- Fixed stream cleanup in regenerate endpoint - stream now properly tracked and closed
- Added `regen_stream` variable with try/finally cleanup pattern
- Matches cleanup pattern used in main chat endpoint

### Profile Persistence Fixes

- Added `setupFormEventListeners()` for change detection on all profile inputs
- Added visible Save button that appears when changes detected
- Implemented auto-save with 2-second debounce
- Fixed in-memory cache updates for all profile fields (was only updating some)
- Added `forceReload` parameter to `init()` for fresh data on modal open
- Settings modal now forces profile reload when opened

### Mode System Security

**Rate Limiting**
- Added `PasscodeRateLimiter` class (5 attempts / 5 minute lockout)
- Prevents brute-force attacks on adult mode passcode

**Session Security**
- Fixed `disable_adult_mode()` to clear all session unlocks
- Added X-Session-ID header validation to `enable_section` endpoint
- Added session verification to avatar endpoints (generate, select, regenerate)
- Avatar operations now require both Tier 1 and Tier 2 unlock

### Thinking Mode Improvements

**Soft/Hard Limit System**
- Changed from immediate break at soft limit to warning + continue
- Soft limits (warning only): 3000 tokens initial, 2000 tokens followup
- Hard limits (break stream): 30000 tokens initial, 20000 tokens followup
- Model can now complete extended thinking for complex problems
- Added configurable environment variables for all limits

### System Prompt Improvements

**Tool Instructions**
- Added "When NOT to Use Tools" section to prevent unnecessary tool calls
- Added "Never mix tool syntax into responses" rule
- Clearer guidance on when to respond directly vs use tools

**Response Guidelines**
- Streamlined PROFILE_INSTRUCTIONS from 15 to 6 lines
- Added Format section (default 1-3 paragraphs, expand if needed)
- Added Behavior section (stay in character, proactive)
- Updated base identity to emphasize conciseness

### Memory System Improvements

**Source Tagging**
- Added `source` parameter to `add_memory` tool definition
- Model can now specify `explicit` when user directly asked to remember
- Tool executor uses provided source, defaults to `inferred`
- Enables filtering user-requested vs proactively stored memories

**Semantic Duplicate Detection**
- Replaced exact string match with cosine similarity check
- Threshold 0.85 catches semantically similar memories
- Returns existing memory content in duplicate error for transparency
- Prevents memory bloat from similar entries

**Automatic Memory Extraction**
- New `memory_extractor.py` service (similar to profile_extractor.py)
- Parses `[MEMORY]` structured tags from model responses
- Parses `[REMEMBER]` simple tags
- Implicit extraction for non-tool models (name/preference acknowledgments)
- Integrated into chat flow for both regular and followup responses

### Context Debugging

**Backend Changes**
- Message SSE events now include full metadata object
- Metadata contains: `thinking_content`, `memories_used`, `tools_available`
- Applied to all endpoints: regular chat, followup, and regenerate

**Frontend Changes**
- Context section created immediately when message completes (during streaming)
- Replaces streaming thinking container with unified context section
- Context section expanded by default for easier debugging
- Shows three panels:
  - Model Reasoning (pink) - thinking/reasoning tokens
  - Memories Used (purple) - retrieved memories with categories
  - Tools Available (green) - tools the model had access to
- Persists with each message for historical debugging

---

## File Changes Summary

### Modified Files
- `app/config.py` - Added thinking hard limits
- `app/routers/chat.py` - Stream cleanup, metadata events, memory extraction
- `app/routers/commands.py` - Session validation for avatars
- `app/routers/user_profile.py` - Session header validation
- `app/services/memory_service.py` - Semantic duplicate detection
- `app/services/system_prompt_builder.py` - Improved prompts
- `app/services/tool_executor.py` - Source parameter support
- `app/services/user_profile_service.py` - Rate limiter, session cleanup
- `app/services/user_profile_store.py` - Architecture documentation
- `app/tools/definitions.py` - Source parameter in add_memory tool
- `static/js/app.js` - Race condition fix
- `static/js/chat.js` - Toast notifications, context section, SSE handling
- `static/js/profile.js` - Auto-save, change detection, Save button
- `static/js/settings.js` - Force reload profile on modal open

### New Files
- `app/services/memory_extractor.py` - Automatic memory extraction from responses

---

## Configuration Changes

New environment variables (optional):
```bash
THINKING_HARD_LIMIT_INITIAL=30000
THINKING_HARD_LIMIT_FOLLOWUP=20000
```

---

## Migration Notes

No database migrations required. All changes are backwards compatible.
