# PeanutChat Voice & Admin Portal Build Plan

## Overview

This document outlines the implementation plan for two major features:
1. **Voice Integration** - TTS (Qwen3-TTS) + STT (Whisper) with three operating modes
2. **Admin Portal** - User management, theme management, and access control

---

## Feature 1: Voice Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend                                   │
├──────────────────┬──────────────────┬───────────────────────────────┤
│  Audio Recorder  │  Audio Player    │  Voice Settings UI            │
│  (MediaRecorder) │  (Web Audio API) │  (Mode toggle, voice select)  │
└────────┬─────────┴────────▲─────────┴───────────────────────────────┘
         │                  │
         │ Audio Blob       │ Audio Chunks (streaming)
         ▼                  │
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend API                                  │
├──────────────────┬──────────────────┬───────────────────────────────┤
│  POST /voice/    │  SSE /voice/tts  │  GET /voice/settings          │
│  transcribe      │  /stream         │  PUT /voice/settings          │
└────────┬─────────┴────────▲─────────┴───────────────────────────────┘
         │                  │
         ▼                  │
┌─────────────────┐ ┌──────┴──────────┐
│   STT Service   │ │   TTS Service   │
│   (Whisper)     │ │   (Qwen3-TTS)   │
│   GPU 1 (16GB)  │ │   GPU 1 (16GB)  │
└─────────────────┘ └─────────────────┘
```

### Voice Modes

| Mode | STT | TTS | Description |
|------|-----|-----|-------------|
| `transcribe_only` | ✓ | ✗ | Voice input → text, model responds with text |
| `tts_only` | ✗ | ✓ | Text input, model response → audio |
| `conversation` | ✓ | ✓ | Full voice conversation |

### Hardware Allocation Plan

```
V100 32GB (Primary)     V100 16GB (Secondary)
├── Chat Model          ├── Qwen3-TTS-0.6B (~1.2GB)
│   (7B-30B range)      ├── Whisper-small (~0.5GB)
│                       └── ~14GB headroom
```

### Implementation Tasks

#### Phase 1: Backend Services

##### 1.1 TTS Service (`app/services/tts_service.py`)
```python
# Key components:
- QwenTTSService class
- Model loading (lazy, configurable GPU)
- generate_speech(text, voice_config) -> audio bytes
- stream_speech(text, voice_config) -> AsyncGenerator[bytes]
- Voice configuration (speed, pitch, voice_id)
- 12Hz tokenizer for ultra-low latency streaming
```

**Tasks:**
- [ ] Install qwen-tts package and dependencies
- [ ] Create TTS service with model loading
- [ ] Implement streaming audio generation
- [ ] Add voice configuration options
- [ ] GPU memory management (load/unload)
- [ ] Audio format conversion (wav, mp3, opus)

##### 1.2 STT Service (`app/services/stt_service.py`)
```python
# Key components:
- WhisperSTTService class
- Model selection (tiny, small, medium)
- transcribe(audio_bytes) -> TranscriptionResult
- Language detection
- Timestamp support (optional)
```

**Tasks:**
- [ ] Install faster-whisper or whisper.cpp
- [ ] Create STT service with model loading
- [ ] Implement transcription endpoint
- [ ] Add language detection
- [ ] GPU/CPU fallback support
- [ ] Audio preprocessing (format conversion, noise reduction)

##### 1.3 Voice Router (`app/routers/voice.py`)
```python
# Endpoints:
POST /api/voice/transcribe
  - Input: audio file (webm, wav, mp3)
  - Output: { "text": str, "language": str, "confidence": float }

GET /api/voice/tts/stream
  - Input: text (query param), voice_config
  - Output: SSE stream of audio chunks (base64 encoded)

POST /api/voice/tts/generate
  - Input: { "text": str, "voice": str, "format": str }
  - Output: audio file

GET /api/voice/settings
PUT /api/voice/settings
  - Voice mode, default voice, auto-play preference
```

**Tasks:**
- [ ] Create voice router with authentication
- [ ] Implement transcription endpoint
- [ ] Implement TTS streaming endpoint
- [ ] Implement TTS batch generation endpoint
- [ ] Add voice settings endpoints
- [ ] Rate limiting for voice endpoints

#### Phase 2: Database Schema

##### 2.1 Voice Settings Table
```sql
CREATE TABLE voice_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    voice_mode TEXT DEFAULT 'disabled',  -- disabled, transcribe_only, tts_only, conversation
    tts_voice TEXT DEFAULT 'default',
    tts_speed REAL DEFAULT 1.0,
    auto_play BOOLEAN DEFAULT true,
    stt_language TEXT DEFAULT 'auto',  -- auto-detect or specific language
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**Tasks:**
- [ ] Add migration for voice_settings table
- [ ] Create VoiceSettings Pydantic model
- [ ] Add to database initialization

#### Phase 3: Frontend Integration

##### 3.1 Voice UI Components (`static/js/voice.js`)
```javascript
// Key components:
- VoiceManager class
- AudioRecorder (MediaRecorder API)
- AudioPlayer (Web Audio API for streaming)
- Push-to-talk button
- Voice activity detection (optional)
- Waveform visualization (optional)
```

**Tasks:**
- [ ] Create VoiceManager class
- [ ] Implement audio recording with MediaRecorder
- [ ] Implement streaming audio playback
- [ ] Add microphone button to input area
- [ ] Visual feedback (recording indicator, speaking indicator)
- [ ] Voice settings panel in settings modal

##### 3.2 Chat Integration
```javascript
// Modify chat.js:
- Add voice mode state
- Intercept send for transcribe mode
- Subscribe to TTS stream for responses
- Queue management for audio playback
```

**Tasks:**
- [ ] Add voice mode toggle to chat UI
- [ ] Integrate transcription with message sending
- [ ] Add TTS streaming to message display
- [ ] Audio queue for sequential playback
- [ ] Interrupt handling (stop TTS on new message)

##### 3.3 Settings Integration
```html
<!-- Voice settings section in settings modal -->
<div id="voice-settings">
  <h3>Voice Settings</h3>
  <select id="voice-mode">...</select>
  <select id="tts-voice">...</select>
  <input type="range" id="tts-speed">
  <input type="checkbox" id="auto-play">
</div>
```

**Tasks:**
- [ ] Add voice settings section to settings modal
- [ ] Voice mode selector
- [ ] TTS voice selector (load available voices)
- [ ] Speed/pitch controls
- [ ] Auto-play toggle

#### Phase 4: Configuration

##### 4.1 Environment Variables
```bash
# Voice settings
VOICE_ENABLED=true
TTS_MODEL=Qwen3-TTS-12Hz-0.6B
TTS_DEVICE=cuda:1  # Secondary GPU
STT_MODEL=whisper-small
STT_DEVICE=cuda:1
VOICE_MAX_AUDIO_LENGTH=60  # seconds
VOICE_SAMPLE_RATE=24000
```

**Tasks:**
- [ ] Add voice config to app/config.py
- [ ] Document in .env.example
- [ ] Add to CLAUDE.md

---

## Feature 2: Admin Portal

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Admin Portal Frontend                           │
│                      /admin (new page)                               │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│ User Mgmt    │ Theme Mgmt   │ Mode Control │ System Settings       │
│ - List       │ - Create     │ - Restrict   │ - View logs          │
│ - Edit       │ - Edit CSS   │ - Lock users │ - MCP overview       │
│ - Delete     │ - Delete     │              │ - Memory stats       │
└──────────────┴──────────────┴──────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Admin API (/api/admin/*)                        │
│                      Requires is_admin=true                          │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│ /users/*     │ /themes/*    │ /modes/*     │ /system/*             │
└──────────────┴──────────────┴──────────────┴───────────────────────┘
```

### Database Schema Changes

##### Users Table Addition
```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN mode_restriction TEXT DEFAULT NULL;
-- mode_restriction: NULL (no restriction), 'normal_only', 'no_full_unlock'
```

##### Themes Table (New)
```sql
CREATE TABLE themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    css_variables TEXT NOT NULL,  -- JSON blob of CSS custom properties
    is_system BOOLEAN DEFAULT false,  -- Built-in themes can't be deleted
    is_enabled BOOLEAN DEFAULT true,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Default themes
INSERT INTO themes (name, display_name, css_variables, is_system, is_enabled, created_at, updated_at)
VALUES
  ('dark', 'Dark', '{"--bg-primary": "#1a1a2e", ...}', true, true, datetime(), datetime()),
  ('light', 'Light', '{"--bg-primary": "#ffffff", ...}', true, true, datetime(), datetime()),
  ('midnight', 'Midnight', '{"--bg-primary": "#0d1117", ...}', true, true, datetime(), datetime());
```

### Implementation Tasks

#### Phase 1: Backend - Admin Infrastructure

##### 1.1 Admin Middleware (`app/middleware/admin.py`)
```python
# Verify admin status for /api/admin/* routes
async def require_admin(request: Request):
    user = get_current_user(request)
    if not user.is_admin:
        raise HTTPException(403, "Admin access required")
```

**Tasks:**
- [ ] Create admin verification dependency
- [ ] Add is_admin field to users table
- [ ] Update UserResponse schema
- [ ] Create first admin user setup flow

##### 1.2 Admin Router (`app/routers/admin.py`)
```python
# User Management
GET    /api/admin/users              # List all users
GET    /api/admin/users/{id}         # Get user details
PUT    /api/admin/users/{id}         # Update user (profile, restrictions)
DELETE /api/admin/users/{id}         # Delete user
POST   /api/admin/users/{id}/reset-password  # Force password reset
PUT    /api/admin/users/{id}/toggle-active   # Enable/disable account

# Theme Management
GET    /api/admin/themes             # List all themes
POST   /api/admin/themes             # Create theme
PUT    /api/admin/themes/{id}        # Update theme
DELETE /api/admin/themes/{id}        # Delete theme (if not system)
PUT    /api/admin/themes/{id}/toggle # Enable/disable theme

# Mode Restrictions
PUT    /api/admin/users/{id}/mode-restriction
  # Body: { "restriction": "normal_only" | "no_full_unlock" | null }

# System
GET    /api/admin/system/stats       # User count, memory usage, etc.
GET    /api/admin/system/logs        # Recent application logs
GET    /api/admin/mcp/servers        # All MCP servers (all users)
```

**Tasks:**
- [ ] Create admin router with all endpoints
- [ ] Implement user CRUD operations
- [ ] Implement theme CRUD operations
- [ ] Implement mode restriction logic
- [ ] System stats endpoint
- [ ] Log viewing endpoint

##### 1.3 Admin Service (`app/services/admin_service.py`)
```python
class AdminService:
    # User management
    def list_users(filters, pagination) -> List[UserAdminView]
    def get_user_detail(user_id) -> UserDetailView
    def update_user(user_id, updates) -> UserAdminView
    def delete_user(user_id) -> bool
    def set_mode_restriction(user_id, restriction) -> bool

    # Theme management
    def list_themes() -> List[Theme]
    def create_theme(theme_data) -> Theme
    def update_theme(theme_id, updates) -> Theme
    def delete_theme(theme_id) -> bool

    # System
    def get_system_stats() -> SystemStats
    def get_recent_logs(lines=100) -> List[str]
```

**Tasks:**
- [ ] Create AdminService class
- [ ] Implement user management methods
- [ ] Implement theme management methods
- [ ] Implement system stats collection

#### Phase 2: Mode Restriction Enforcement

##### 2.1 Update Profile Service
```python
# In user_profile_service.py
def verify_uncensored_passcode(user_id, passcode, session_id):
    # Check mode restriction BEFORE verifying passcode
    restriction = get_mode_restriction(user_id)
    if restriction == 'normal_only':
        return {"success": False, "error": "Account restricted to normal mode"}
    # ... existing logic

def full_unlock(user_id, session_id):
    restriction = get_mode_restriction(user_id)
    if restriction in ('normal_only', 'no_full_unlock'):
        return {"success": False, "error": "Full unlock not available for this account"}
    # ... existing logic
```

**Tasks:**
- [ ] Add mode_restriction check to passcode verification
- [ ] Add mode_restriction check to full_unlock
- [ ] Update frontend to show restriction messages
- [ ] Add restriction indicator in user profile area

#### Phase 3: Frontend - Admin Portal

##### 3.1 Admin Page (`static/admin.html`)
```html
<!-- Separate admin page, not part of main chat UI -->
<!DOCTYPE html>
<html>
<head>
    <title>PeanutChat Admin</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <nav id="admin-nav">
        <a href="#users">Users</a>
        <a href="#themes">Themes</a>
        <a href="#system">System</a>
    </nav>
    <main id="admin-content">
        <!-- Dynamic content loaded here -->
    </main>
    <script type="module" src="/static/js/admin.js"></script>
</body>
</html>
```

**Tasks:**
- [ ] Create admin.html page
- [ ] Create admin.css styles
- [ ] Add route to serve admin page (admin-only)

##### 3.2 Admin JavaScript (`static/js/admin.js`)
```javascript
// Admin portal application
class AdminPortal {
    constructor() {
        this.currentSection = 'users';
        this.init();
    }

    // User management
    async loadUsers()
    async editUser(userId)
    async deleteUser(userId)
    async setModeRestriction(userId, restriction)

    // Theme management
    async loadThemes()
    async createTheme()
    async editTheme(themeId)
    async deleteTheme(themeId)
    renderThemeEditor()  // CSS variable editor
    previewTheme(cssVars)

    // System
    async loadSystemStats()
    async loadLogs()
}
```

**Tasks:**
- [ ] Create AdminPortal class
- [ ] Implement user list view with search/filter
- [ ] Implement user edit modal
- [ ] Implement theme list view
- [ ] Implement theme editor (CSS variable picker)
- [ ] Implement theme preview
- [ ] Implement system stats dashboard
- [ ] Implement log viewer

##### 3.3 Theme Editor Component
```javascript
// Visual CSS variable editor
class ThemeEditor {
    constructor(theme) {
        this.theme = theme;
        this.variables = this.getDefaultVariables();
    }

    getDefaultVariables() {
        return {
            '--bg-primary': { type: 'color', label: 'Background' },
            '--bg-secondary': { type: 'color', label: 'Secondary BG' },
            '--bg-sidebar': { type: 'color', label: 'Sidebar' },
            '--text-primary': { type: 'color', label: 'Text' },
            '--text-secondary': { type: 'color', label: 'Secondary Text' },
            '--accent': { type: 'color', label: 'Accent' },
            '--border': { type: 'color', label: 'Borders' },
            // ... more variables
        };
    }

    render() // Color picker UI
    preview() // Live preview
    export() // Export CSS
}
```

**Tasks:**
- [ ] Create ThemeEditor component
- [ ] Color picker for each CSS variable
- [ ] Live preview panel
- [ ] Import/export theme JSON
- [ ] Reset to defaults button

#### Phase 4: Initial Admin Setup

##### 4.1 First Admin Creation
```python
# On first run or via CLI command
# python -m app.cli create-admin --username admin --password <password>

# Or environment variable for initial admin
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=<secure_password>
```

**Tasks:**
- [ ] Create CLI command for admin creation
- [ ] Environment variable fallback for first admin
- [ ] Prevent creating admin if one exists (unless forced)

##### 4.2 Admin Link in Main UI
```javascript
// In app.js - show admin link if user is admin
if (user.is_admin) {
    showAdminLink();  // Add link to header/sidebar
}
```

**Tasks:**
- [ ] Check is_admin on login
- [ ] Show admin link in UI for admins
- [ ] Add to user dropdown menu

---

## Implementation Order

### Recommended Sequence

```
Week 1: Admin Portal Foundation
├── Database migrations (is_admin, themes table)
├── Admin middleware and router skeleton
├── User list and basic CRUD
└── First admin setup

Week 2: Admin Portal Complete
├── Theme management backend
├── Theme editor frontend
├── Mode restrictions
└── System stats/logs

Week 3: Voice Backend
├── STT service (Whisper)
├── TTS service (Qwen3-TTS)
├── Voice router
└── Database schema

Week 4: Voice Frontend
├── Audio recording
├── Audio playback
├── Chat integration
└── Settings UI
```

---

## API Schema Reference

### Admin Schemas

```python
# app/models/admin_schemas.py

class UserAdminView(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_admin: bool
    is_active: bool
    mode_restriction: Optional[str]
    created_at: str
    last_login: Optional[str]
    conversation_count: int
    memory_count: int

class UserUpdate(BaseModel):
    email: Optional[str]
    is_admin: Optional[bool]
    is_active: Optional[bool]
    mode_restriction: Optional[Literal['normal_only', 'no_full_unlock', None]]

class ThemeCreate(BaseModel):
    name: str
    display_name: str
    css_variables: Dict[str, str]

class ThemeUpdate(BaseModel):
    display_name: Optional[str]
    css_variables: Optional[Dict[str, str]]
    is_enabled: Optional[bool]

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_conversations: int
    total_memories: int
    disk_usage: Dict[str, int]
    mcp_servers: int
```

### Voice Schemas

```python
# app/models/voice_schemas.py

class VoiceSettings(BaseModel):
    voice_mode: Literal['disabled', 'transcribe_only', 'tts_only', 'conversation']
    tts_voice: str
    tts_speed: float
    auto_play: bool
    stt_language: str

class TranscriptionResult(BaseModel):
    text: str
    language: str
    confidence: float
    duration: float

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str]
    speed: Optional[float]
    format: Literal['wav', 'mp3', 'opus'] = 'opus'
```

---

## Security Considerations

### Admin Portal
- [ ] Admin endpoints behind authentication + is_admin check
- [ ] Rate limiting on sensitive operations
- [ ] Audit logging for all admin actions
- [ ] Cannot delete own admin account
- [ ] Cannot remove last admin
- [ ] Password reset requires confirmation

### Voice
- [ ] Audio file size limits
- [ ] Duration limits on transcription
- [ ] Rate limiting on voice endpoints
- [ ] Sanitize transcribed text before chat
- [ ] No voice access in restricted modes (if applicable)

---

## Testing Plan

### Admin Portal Tests
- [ ] User CRUD operations
- [ ] Mode restriction enforcement
- [ ] Theme CRUD operations
- [ ] Theme CSS validation
- [ ] Admin permission checks
- [ ] Edge cases (last admin, self-delete)

### Voice Tests
- [ ] STT accuracy with various audio formats
- [ ] TTS streaming latency measurement
- [ ] Audio codec compatibility
- [ ] GPU memory management under load
- [ ] Concurrent voice requests
- [ ] Mode switching during active session

---

## Files to Create

### Voice Feature
```
app/
├── services/
│   ├── tts_service.py      (NEW)
│   └── stt_service.py      (NEW)
├── routers/
│   └── voice.py            (NEW)
├── models/
│   └── voice_schemas.py    (NEW)
static/
├── js/
│   └── voice.js            (NEW)
```

### Admin Feature
```
app/
├── services/
│   └── admin_service.py    (NEW)
├── routers/
│   └── admin.py            (NEW)
├── models/
│   └── admin_schemas.py    (NEW)
├── middleware/
│   └── admin.py            (NEW)
static/
├── admin.html              (NEW)
├── css/
│   └── admin.css           (NEW)
├── js/
│   └── admin.js            (NEW)
```

### Files to Modify
```
app/
├── config.py               (voice config, admin config)
├── main.py                 (add routers, serve admin page)
├── services/
│   ├── auth_service.py     (is_admin support)
│   ├── user_profile_service.py (mode restriction checks)
│   └── database.py         (migrations)
├── models/
│   └── auth_schemas.py     (UserResponse with is_admin)
static/
├── js/
│   ├── app.js              (admin link, voice toggle)
│   ├── chat.js             (voice integration)
│   └── settings.js         (voice settings, theme loading)
├── index.html              (voice UI elements)
```

---

## Dependencies to Add

```
# requirements.txt additions

# Voice - TTS
qwen-tts>=0.1.0

# Voice - STT
faster-whisper>=1.0.0
# OR
openai-whisper>=20231117

# Audio processing
soundfile>=0.12.0
librosa>=0.10.0  # optional, for advanced audio processing
```
