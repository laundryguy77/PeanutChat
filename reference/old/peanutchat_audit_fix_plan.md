# PeanutChat Audit & Fix Implementation Plan

## Overview
Fix critical issues identified in audit: model filtering, capability exposure, authentication gaps, and UI improvements.

## User Decisions
- **Auth**: Require login to chat (all conversations user-scoped)
- **UI**: Icon badges for capabilities (wrench/eye/brain icons)
- **Scope**: Full implementation (all 4 phases)

---

## Phase 1: Model Filtering & Capability Detection

### 1.1 Backend - Ollama Service Enhancement
**File:** `app/services/ollama.py`

Added new method to fetch chat-capable models with capabilities:

```python
async def get_chat_models_with_capabilities(self) -> List[Dict[str, Any]]:
    """Get only chat-capable models with their capabilities."""
    response = await self.client.get(f"{self.base_url}/api/tags")
    all_models = response.json().get("models", [])

    chat_models = []
    for model in all_models:
        model_name = model.get("name", "")

        # Get detailed info including capabilities
        show_response = await self.client.post(
            f"{self.base_url}/api/show",
            json={"name": model_name}
        )
        info = show_response.json()

        capabilities = info.get("capabilities", [])
        family = model.get("details", {}).get("family", "").lower()

        # Skip embedding-only models
        if "bert" in family:
            continue
        if "completion" not in capabilities:
            if "embed" in model_name.lower():
                continue
            if capabilities:
                continue

        chat_models.append({
            "name": model_name,
            "capabilities": capabilities,
            "supports_tools": "tools" in capabilities,
            "supports_vision": "vision" in capabilities,
            "supports_thinking": "thinking" in capabilities,
        })

    return chat_models
```

### 1.2 Backend - Models Router Update
**File:** `app/routers/models.py`

Updated `/api/models` endpoint to use new filtering method and return capabilities.

---

## Phase 2: Frontend Capability Display

### 2.1 Model Dropdown Enhancement
**File:** `static/js/app.js`

Updated `loadModels()` to:
- Display capability text in dropdown: `model (tools, vision, think)`
- Store capabilities object for selected model in app state
- Update header indicators when model changes via `updateCapabilityIndicators()`

### 2.2 Capability Indicators in Chat Header
**File:** `static/index.html`

Added capability badges next to model selector:
```html
<div id="model-capabilities" class="flex items-center gap-1">
  <span id="cap-tools" class="hidden" title="Tools available">
    <span class="material-symbols-outlined text-sm text-green-400">build</span>
  </span>
  <span id="cap-vision" class="hidden" title="Vision capable">
    <span class="material-symbols-outlined text-sm text-blue-400">visibility</span>
  </span>
  <span id="cap-thinking" class="hidden" title="Extended thinking">
    <span class="material-symbols-outlined text-sm text-purple-400">psychology</span>
  </span>
</div>
```

---

## Phase 3: Authentication Fixes (Required Login)

### 3.1 Require Auth on All Chat Endpoints
**File:** `app/routers/chat.py`

Added `require_auth` dependency to all chat endpoints:
```python
from app.middleware.auth import require_auth
from app.models.auth_schemas import UserResponse

@router.post("")
async def chat(request: Request, user: UserResponse = Depends(require_auth)):
    tool_executor.set_current_user(user.id)
    # ... existing code
```

Protected endpoints:
- `POST /api/chat` - main chat
- `GET /api/chat/conversations` - list (filter by user_id)
- `POST /api/chat/conversations` - create (associate with user_id)
- `GET/DELETE/PATCH /api/chat/conversations/{id}` - verify ownership
- All message operations

### 3.2 Set Tool Executor User Context
**File:** `app/routers/chat.py` (in `chat()` and `regenerate_response()`)

```python
tool_executor.set_current_user(user.id)
```

### 3.3 User-Scoped Conversations
**File:** `app/services/conversation_store.py`

Added `user_id` field to Conversation dataclass and filter methods:
```python
@dataclass
class Conversation:
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    user_id: Optional[int] = None  # NEW
    # ...

def list_for_user(self, user_id: int) -> List[Dict]:
    """List conversations for specific user"""
    return [c for c in self._cache.values()
            if c.user_id == user_id or c.user_id is None]
```

### 3.4 Frontend Auth Integration
**Files:** `static/js/app.js`, `static/js/chat.js`

Added `credentials: 'include'` to all fetch calls to send auth cookies.

---

## Phase 4: Code Cleanup

### 4.1 Removed Dead Code
- `app/routers/chat.py:311-318` - Video generation SSE events
- `app/services/ollama.py:14` - Unused `_vision_models_cache`
- `app/tools/definitions.py:76-78` - Unused `is_vision` parameter

### 4.2 Fixed Deprecation Warnings
- `app/services/auth_service.py:35` - Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)`

---

## Implementation Summary

### Files Modified

| File | Changes |
|------|---------|
| `app/services/ollama.py` | Added `get_chat_models_with_capabilities()`, removed `_vision_models_cache` |
| `app/routers/models.py` | Updated `/api/models` to use filtered list with capabilities |
| `app/routers/chat.py` | Added auth to all endpoints, set tool_executor user, removed video code |
| `app/services/conversation_store.py` | Added `user_id` field, `list_for_user()`, ownership verification |
| `app/services/auth_service.py` | Fixed `datetime.utcnow()` deprecation |
| `app/tools/definitions.py` | Removed unused `is_vision` parameter |
| `static/js/app.js` | Capability badges, `updateCapabilityIndicators()`, credentials in fetch |
| `static/js/chat.js` | Added `credentials: 'include'` to all fetch calls |
| `static/index.html` | Added capability indicator elements in header |

### Ollama API Capability Detection

| Field | Purpose |
|-------|---------|
| `capabilities` | Array: `["completion", "vision", "tools", "thinking"]` |
| `details.family` | Model family (e.g., "llama", "nomic-bert", "qwen2") |

| Feature | Detection Method | Reliability |
|---------|------------------|-------------|
| Chat/Completion | `"completion" in capabilities` | High |
| Vision | `"vision" in capabilities` | High |
| Tools | `"tools" in capabilities` | High |
| Thinking | `"thinking" in capabilities` | High |
| Embedding Model | NO completion OR family contains "bert" | Medium |

### Migration Notes

#### Existing Conversations
Existing JSON conversations lack `user_id`. Legacy conversations (with `user_id=None`) are visible to all users until claimed.

#### API Breaking Changes
- `/api/models` response includes new capability fields
- `/api/chat/*` endpoints now require auth header
- Frontend sends `credentials: 'include'` with all requests

### Testing Checklist

- [ ] Embedding models filtered from dropdown
- [ ] Capability icons display correctly
- [ ] Unauthenticated requests return 401
- [ ] Conversations scoped to logged-in user
- [ ] Knowledge base search works for authenticated users
- [ ] Thinking mode toggle respects model capability
- [ ] Tool calls only attempted on tool-capable models

---

## Post-Implementation

**Restart required:** Run `sudo systemctl restart peanutchat` to apply changes.
