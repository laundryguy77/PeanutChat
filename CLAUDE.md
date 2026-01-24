# PeanutChat - Claude Code Project Guide

## Project Overview
PeanutChat is a FastAPI-based AI chat application that integrates with Ollama for LLM interactions. It features authentication, knowledge base management, MCP (Model Context Protocol) tools, memory/conversation persistence, and user profiles.

## Tech Stack
- **Backend:** Python 3, FastAPI
- **LLM:** Ollama (local)
- **Database:** SQLite (`peanutchat.db`)
- **Frontend:** Static HTML/JS served by FastAPI

## Project Structure
```
app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── routers/             # API route handlers
│   ├── auth.py, chat.py, commands.py, knowledge.py
│   ├── mcp.py, memory.py, models.py, settings.py, user_profile.py
├── services/            # Business logic
│   ├── ollama.py, auth_service.py, conversation_store.py
│   ├── knowledge_base.py, memory_service.py, mcp_client.py
│   ├── memory_extractor.py, profile_extractor.py
│   └── image_backends.py, video_backends.py, tool_executor.py
├── models/              # Pydantic schemas
├── middleware/          # Request middleware
└── tools/               # Tool definitions for LLM
static/                  # Frontend HTML/JS/CSS
```

## Service Management (Passwordless Sudo)
The following commands are available without password for user `tech`:

```bash
# Service control
sudo systemctl start peanutchat
sudo systemctl stop peanutchat
sudo systemctl restart peanutchat
sudo systemctl status peanutchat
sudo systemctl cat peanutchat.service
sudo systemctl enable peanutchat
sudo systemctl disable peanutchat

# View logs
sudo journalctl -u peanutchat -f      # Follow live logs
sudo journalctl -u peanutchat -n 50   # Last 50 lines
```

## Running Locally
```bash
# Activate virtual environment
source venv/bin/activate

# Run directly
python run.py

# Or via start script
./start_peanutchat.sh
```

## Dependencies
- Ollama service must be running (`ollama.service`)
- Python virtual environment at `./venv/`
- Environment variables in `.env`

---

## Key Systems Architecture

### Memory System

The memory system provides persistent, semantic memory storage for user information.

**Files:**
- `app/services/memory_service.py` - Core business logic
- `app/services/memory_store.py` - Database persistence
- `app/services/memory_extractor.py` - Auto-extraction from responses
- `app/services/embedding_service.py` - Vector embeddings
- `app/routers/memory.py` - REST API endpoints

**Flow:**
```
User Message → Extract Search Terms (LLM) → Query Memories (Semantic Search)
                                                    ↓
                                         Inject into System Prompt
                                                    ↓
Model Response → Extract Memories (Auto) → Store with Embeddings
```

**Features:**
- Two-phase retrieval: LLM extracts search terms, then semantic similarity search
- Semantic duplicate detection (cosine similarity > 0.85)
- Source tagging: `explicit` (user asked) vs `inferred` (model proactive)
- Auto-extraction from model responses via `[MEMORY]` tags
- Categories: `personal`, `preference`, `topic`, `instruction`, `general`

**Configuration:**
- `KB_EMBEDDING_MODEL` - Embedding model (default: `nomic-embed-text`)
- Memory similarity threshold: 0.4 for retrieval, 0.85 for duplicates

---

### Profile System

User profiles store persistent preferences and personal information.

**Files:**
- `app/services/user_profile_service.py` - Business logic + mode security
- `app/services/user_profile_store.py` - Database persistence
- `app/services/profile_extractor.py` - Auto-extraction from responses
- `app/routers/user_profile.py` - REST API endpoints

**Features:**
- Auto-save with 2-second debounce
- Profile sections: identity, communication, technical, persona_preferences, etc.
- Auto-extraction via `[PROFILE]` tags for non-tool models

---

### Three-Tier Mode System

Content gating with session-scoped unlocks for safety.

**Tiers:**
1. **Normal Mode** - Default, SFW content only
2. **Uncensored Mode** (Tier 1) - Requires passcode, persists to database
3. **Full Unlock Mode** (Tier 2) - Requires `/full_unlock` command, session-only

**Security Features:**
- Rate limiting: 5 attempts per 5 minutes (PasscodeRateLimiter)
- Session-scoped unlocks (in-memory, cleared on restart)
- X-Session-ID validation for gated endpoints
- Automatic cleanup on mode disable

**Files:**
- `app/services/user_profile_service.py` - Mode logic + rate limiter
- `app/services/user_profile_store.py` - Persistence + session tracking
- `app/routers/user_profile.py` - API endpoints
- `app/routers/commands.py` - Avatar endpoints with session gating

---

### Chat Streaming System

SSE-based streaming with thinking mode support.

**Files:**
- `app/routers/chat.py` - Main chat endpoint
- `app/services/ollama.py` - Ollama API integration
- `static/js/chat.js` - Frontend SSE handling

**Features:**
- Real-time token streaming via Server-Sent Events
- Thinking mode with soft/hard limits (3000/30000 tokens)
- Tool execution with follow-up responses
- Context window compaction for long conversations
- Stream cleanup in finally blocks (prevents resource leaks)

**Context Metadata:**
Each message stores debugging context:
- `thinking_content` - Model's internal reasoning
- `memories_used` - Retrieved memories for this response
- `tools_available` - Tools the model had access to

Frontend displays this in an expandable "Context" section per message.

---

### System Prompt Builder

Assembles the full context sent to the model.

**File:** `app/services/system_prompt_builder.py`

**Assembly Order:**
1. Base identity (persona name, core behavior)
2. User greeting (if name known)
3. Memory context (retrieved memories)
4. Profile context (user preferences)
5. Tool instructions (when to use/not use tools)
6. Response guidelines (format, behavior)

**Sanitization:**
- Truncates content to prevent prompt injection
- Removes system-like markers (`[SYSTEM]`, `[INSTRUCTION]`)
- Blocks instruction override patterns
- Strips control characters

---

### UI-Backend Sync

Frontend state management and error handling.

**Files:**
- `static/js/app.js` - Main application controller
- `static/js/chat.js` - Chat UI management
- `static/js/profile.js` - Profile management
- `static/js/settings.js` - Settings modal

**Features:**
- Toast notifications for user feedback
- Race condition handling (restore state on error)
- Response validation for API calls
- Error boundaries in SSE handler

---

## Configuration Reference

Key environment variables in `.env`:

```bash
# Required
ADULT_PASSCODE=         # Passcode for uncensored mode
JWT_SECRET=             # JWT signing secret

# Optional
OLLAMA_BASE_URL=http://localhost:11434
KB_EMBEDDING_MODEL=nomic-embed-text
THINKING_TOKEN_LIMIT_INITIAL=3000
THINKING_TOKEN_LIMIT_FOLLOWUP=2000
THINKING_HARD_LIMIT_INITIAL=30000
THINKING_HARD_LIMIT_FOLLOWUP=20000
CHAT_REQUEST_TIMEOUT=300
```

---

## MCP Tool Documentation
Reference implementations for MCP tools are in:
- `mcp_tool_documentation/image_gen/` - Image generation MCP server
- `mcp_tool_documentation/video_gen/` - Video generation MCP server
