PeanutChat Audit Remediation Plan

 Issue Verification Summary

 27 Valid Issues | 12 Resolved | 1 New Issue Discovered

 Resolved Issues (No Action Required)

 - ✅ Models filtering (backend filters embedding models)
 - ✅ Chat endpoint auth (require_auth added)
 - ✅ List conversations auth (user scoping added)
 - ✅ Conversation user isolation (user_id field added)
 - ✅ Knowledge base user context (set_current_user called)
 - ✅ Browse website in system prompt (frontend updated)
 - ✅ Video generation code removed
 - ✅ _vision_models_cache removed
 - ✅ Tool capability indicators in UI (icons added)
 - ✅ Script loading order (correct)
 - ✅ Clipboard API (modern API with fallback)
 - ✅ Ollama endpoint configurable via env

 ---
 Phase 1: Critical Security Fixes

 Priority: CRITICAL | Estimated Files: 4 | Can Block Production

 Context for Executor

 You are fixing critical security vulnerabilities in PeanutChat, a FastAPI +
 vanilla JS chat application. These issues could allow unauthorized access or
 data exposure.

 Files to Modify

 - app/main.py - CORS configuration
 - app/routers/auth.py - Cookie security
 - app/config.py - JWT secret validation
 - app/routers/chat.py - Legacy endpoint auth

 Tasks

 1.1 Fix CORS Configuration

 File: app/main.py:19-25
 Problem: allow_origins=["*"] with allow_credentials=True allows any site to
 make authenticated requests.
 Fix:
 # Add to config.py
 CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")

 # In main.py
 app.add_middleware(
     CORSMiddleware,
     allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"]
 else [],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
 )

 1.2 Fix Cookie Security

 File: app/routers/auth.py:32-39 and 63-70
 Problem: secure=False hardcoded - cookies sent over HTTP.
 Fix:
 # Add to config.py
 COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

 # In auth.py (both locations)
 response.set_cookie(
     key="access_token",
     value=access_token,
     httponly=True,
     secure=COOKIE_SECURE,  # From config
     samesite="lax",
     max_age=60 * 60 * 24
 )

 1.3 Add JWT Secret Startup Warning

 File: app/config.py:60 and app/main.py
 Problem: Default JWT_SECRET used without warning.
 Fix:
 # In config.py after JWT_SECRET definition
 if JWT_SECRET == "change-this-in-production-use-a-long-random-string":
     import warnings
     warnings.warn("⚠️  Using default JWT_SECRET - set JWT_SECRET env var for 
 production!", stacklevel=2)

 # Or in main.py startup event
 @app.on_event("startup")
 async def startup_warning():
     if config.JWT_SECRET ==
 "change-this-in-production-use-a-long-random-string":
         logger.warning("⚠️  SECURITY: Using default JWT_SECRET! Set 
 JWT_SECRET environment variable.")

 1.4 Add Auth to Legacy Endpoints

 File: app/routers/chat.py:716-733
 Problem: /history GET and DELETE endpoints have no authentication.
 Fix:
 @router.get("/history")
 async def get_chat_history(request: Request, user: UserResponse = 
 Depends(require_auth)):
     """Get chat history for current session (legacy)"""
     conv_id = request.headers.get("X-Conversation-ID", "default")
     conv = conversation_store.get(conv_id, user_id=user.id)  # Add user 
 verification
     ...

 @router.delete("/history")
 async def clear_chat_history(request: Request, user: UserResponse = 
 Depends(require_auth)):
     """Clear chat history for current session (legacy)"""
     conv_id = request.headers.get("X-Conversation-ID")
     # Verify ownership before delete
     ...

 Verification Commands

 # Test CORS - should reject unknown origins
 curl -H "Origin: http://evil.com" -I http://localhost:8080/api/models

 # Test cookie secure flag in response headers
 curl -v -X POST http://localhost:8080/api/auth/login -d
 '{"username":"test","password":"test"}'

 # Test JWT warning appears in logs on startup
 grep -i "jwt_secret" logs/app.log

 # Test legacy endpoints require auth
 curl http://localhost:8080/api/chat/history  # Should return 401

 ---
 Phase 2: Concurrency & Data Integrity Fixes

 Priority: CRITICAL | Estimated Files: 3
 Decision: FULL ASYNC CONVERSION

 Context for Executor

 PeanutChat is a FastAPI chat application at /home/tech/PeanutChat/. It uses
 threading.Lock() in ConversationStore but FastAPI is async - this causes race
  conditions. You must convert ConversationStore to use asyncio.Lock and
 update all 27 call sites.

 Files to Modify

 1. app/services/conversation_store.py - Convert to async
 2. app/routers/chat.py - 26 call sites to await
 3. app/services/tool_executor.py - 1 call site to await

 Task 2.1: Convert ConversationStore to Async

 File: /home/tech/PeanutChat/app/services/conversation_store.py

 Step 1: Change import at top of file:
 # Change this line (around line 2-5):
 import threading

 # To:
 import asyncio

 Step 2: In __init__ (around line 76), change:
 self._lock = threading.Lock()
 # To:
 self._lock = asyncio.Lock()

 Step 3: Convert these methods to async (add async keyword and change with 
 self._lock: to async with self._lock:):

 | Method            | Line ~ | Change
   |
 |-------------------|--------|-----------------------------------------------
 --|
 | create()          | 97     | Add async def, use async with self._lock:
   |
 | add_message()     | 175    | Add async def, use async with self._lock:
   |
 | update_message()  | 204    | Add async def, use async with self._lock:
   |
 | fork_at_message() | 224    | Add async def, use async with self._lock:
   |
 | delete()          | 284    | Add async def, use async with self._lock:
   |
 | rename()          | 296    | Add async def, use async with self._lock:
   |
 | clear_messages()  | ~310   | Add async def, use async with self._lock:
   |
 | _save()           | ~350   | Add async def (internal, called with lock
 held) |

 Keep synchronous (read-only, no lock):
 - get() - just reads from cache
 - list_conversations() - read-only
 - list_for_user() - read-only
 - get_messages_for_api() - read-only
 - search_conversations() - read-only

 Task 2.2: Update All 26 Call Sites in chat.py

 File: /home/tech/PeanutChat/app/routers/chat.py

 Add await to each of these lines:

 | Line | Current Code
             | Change To                                                   |
 |------|---------------------------------------------------------------------
 ------------|-------------------------------------------------------------|
 | 126  | conv = conversation_store.create(model=settings.model, 
 user_id=user.id)         | conv = await conversation_store.create(...)
           |
 | 136  | conv = conversation_store.create(model=settings.model, 
 user_id=user.id)         | conv = await conversation_store.create(...)
           |
 | 203  | user_msg = conversation_store.add_message(conv_id, role="user", ...)
             | user_msg = await conversation_store.add_message(...)        |
 | 317  | assistant_msg = conversation_store.add_message(conv_id, 
 role="assistant", ...)  | assistant_msg = await 
 conversation_store.add_message(...)   |
 | 391  | followup_msg = conversation_store.add_message(conv_id, 
 role="assistant", ...)   | followup_msg = await 
 conversation_store.add_message(...)    |
 | 407  | assistant_msg = conversation_store.add_message(conv_id, 
 role="assistant", ...)  | assistant_msg = await 
 conversation_store.add_message(...)   |
 | 458  | conv = conversation_store.create(model=settings.model, 
 user_id=user.id)         | conv = await conversation_store.create(...)
           |
 | 478  | if conversation_store.delete(conv_id):
             | if await conversation_store.delete(conv_id):                |
 | 494  | if conversation_store.rename(conv_id, request.title):
             | if await conversation_store.rename(conv_id, request.title): |
 | 506  | if conversation_store.clear_messages(conv_id):
             | if await conversation_store.clear_messages(conv_id):        |
 | 523  | msg = conversation_store.update_message(conv_id, msg_id, 
 request.content)       | msg = await conversation_store.update_message(...)
         |
 | 541  | new_conv = conversation_store.fork_at_message(conv_id, msg_id, 
 request.content) | new_conv = await conversation_store.fork_at_message(...)
   |
 | 676  | assistant_msg = conversation_store.add_message(conv_id, 
 role="assistant", ...)  | assistant_msg = await 
 conversation_store.add_message(...)   |
 | 731  | conversation_store.clear_messages(conv_id)
             | await conversation_store.clear_messages(conv_id)            |

 CRITICAL - Lines 593-595: There's direct _lock access that must change:
 # Current (lines 593-595):
 with conversation_store._lock:
     conv.messages = conv.messages[:msg_index]
     conversation_store._save(conv)

 # Change to:
 async with conversation_store._lock:
     conv.messages = conv.messages[:msg_index]
     await conversation_store._save(conv)

 No changes needed for these (read-only methods stay sync):
 - Lines 132, 465, 475, 491, 503, 520, 538, 561, 720: .get() calls
 - Lines 165, 608, 723: .get_messages_for_api() calls
 - Line 451: .list_for_user() call

 Task 2.3: Update tool_executor.py

 File: /home/tech/PeanutChat/app/services/tool_executor.py

 Line 502 - search_conversations() is read-only, no change needed.

 Task 2.4: Improve Load Error Handling

 File: /home/tech/PeanutChat/app/services/conversation_store.py (around line
 80-89)

 Replace _load_all() method:
 def _load_all(self):
     """Load all conversations into cache"""
     failed_files = []
     for file_path in self.storage_dir.glob("*.json"):
         try:
             with open(file_path) as f:
                 data = json.load(f)
                 conv = Conversation.from_dict(data)
                 self._cache[conv.id] = conv
         except json.JSONDecodeError as e:
             logger.error(f"Corrupt JSON in {file_path}: {e}")
             failed_files.append(file_path)
             # Move to backup
             backup_path = file_path.with_suffix('.json.corrupt')
             file_path.rename(backup_path)
             logger.warning(f"Moved corrupt file to {backup_path}")
         except Exception as e:
             logger.error(f"Error loading conversation {file_path}: {e}")
             failed_files.append(file_path)

     if failed_files:
         logger.warning(f"Failed to load {len(failed_files)} conversations")

 Verification Commands

 cd /home/tech/PeanutChat

 # Test async lock is used
 grep -n "asyncio.Lock" app/services/conversation_store.py

 # Verify all add_message calls are awaited
 grep -n "await conversation_store.add_message" app/routers/chat.py | wc -l
 # Should return 5

 # Test app starts
 source venv/bin/activate && python -c "from app.main import app; print('OK')"

 # Test concurrent requests (run multiple times quickly)
 for i in {1..5}; do curl -s -X POST http://localhost:8080/api/chat -d
 '{"message":"hi"}' & done
 wait

 ---
 Phase 3: Frontend UX & Code Quality

 Priority: HIGH | Estimated Files: 5

 Context for Executor

 PeanutChat is a FastAPI + vanilla JavaScript chat application at
 /home/tech/PeanutChat/. This phase fixes frontend UX issues and adds token
 refresh. Prerequisite: Phase 1 must be complete (for config.COOKIE_SECURE).

 Files to Modify

 1. /home/tech/PeanutChat/static/js/app.js - Filter models, add error
 boundary, fix capability loading order
 2. /home/tech/PeanutChat/static/js/chat.js - Remove 9 console.log statements
 3. /home/tech/PeanutChat/static/js/knowledge.js - Parallel file uploads
 4. /home/tech/PeanutChat/static/js/auth.js - Token refresh mechanism
 5. /home/tech/PeanutChat/app/routers/auth.py - Backend refresh endpoint

 Tasks

 3.1 Filter Embedding Models from Dropdown

 File: /home/tech/PeanutChat/static/js/app.js around lines 391-439 (loadModels
  function)
 Problem: Users can select embedding models (nomic-embed-text,
 snowflake-arctic-embed) which cannot chat.
 Fix:
 async loadModels() {
     try {
         const response = await fetch('/api/models');
         const data = await response.json();

         // Filter out embedding models
         const chatModels = data.models.filter(model => {
             const name = model.name.toLowerCase();
             return !name.includes('embed') &&
                    !name.includes('nomic') &&
                    !name.includes('snowflake');
         });

         chatModels.forEach(model => {
             // ... existing rendering code
         });
     } catch (error) {
         console.error('Failed to load models:', error);
         this.showError('Failed to load models. Check Ollama connection.');
     }
 }

 3.2 Load Capabilities Before Model Selection

 File: static/js/app.js:81-89 (initializeApp)
 Problem: Users don't see capabilities until after selecting model.
 Fix:
 async initializeApp() {
     this.isAuthenticated = true;
     try {
         // Load capabilities FIRST, then models can display them
         await Promise.all([
             this.loadModelCapabilities(),
             this.settingsManager.loadSettings()
         ]);
         await this.loadModels();  // Now has capability data available
         await this.loadConversations();
         this.setupEventListeners();
     } catch (error) {
         console.error('Initialization failed:', error);
         this.showError('Failed to initialize app. Please refresh.');
     }
 }

 3.3 Add Global Error Handler

 File: static/js/app.js (add new method)
 Problem: Network failures crash the app silently.
 Fix:
 // Add to PeanutChatApp class
 showError(message) {
     // Create toast notification
     const toast = document.createElement('div');
     toast.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2
  rounded shadow-lg z-50';
     toast.textContent = message;
     document.body.appendChild(toast);
     setTimeout(() => toast.remove(), 5000);
 }

 // Add global error handler in constructor or init
 window.addEventListener('unhandledrejection', (event) => {
     console.error('Unhandled promise rejection:', event.reason);
     this.showError('An error occurred. Please try again.');
 });

 3.4 Remove Debug Console.log Statements

 File: /home/tech/PeanutChat/static/js/chat.js
 Problem: Debug logging in production code.

 Lines to DELETE (remove these entire lines):

 | Line | Code to Remove
                                                     |
 |------|---------------------------------------------------------------------
 ----------------------------------------------------|
 | 193  | console.log('Creating action buttons for message:', { role, msgId, 
 contentPreview: messageContent?.substring(0, 30) }); |
 | 201  | console.log('User copy button clicked!');
                                                     |
 | 226  | console.log('Assistant copy button clicked!');
                                                     |
 | 239  | console.log('Regenerate button clicked!', msgId);
                                                     |
 | 534  | console.log('regenerateResponse called with messageId:', messageId);
                                                     |
 | 536  | console.log('Blocked: already streaming');
                                                     |
 | 541  | console.log('Conversation ID:', convId);
                                                     |
 | 543  | console.log('Blocked: no conversation ID');
                                                     |
 | 548  | console.log('Fetching regenerate endpoint...');
                                                     |

 Total: 9 lines to remove. Just delete each line entirely.

 3.5 Parallel File Uploads

 File: /home/tech/PeanutChat/static/js/knowledge.js around lines 159-208
 Problem: Files upload sequentially - slow for multiple files.
 Fix:
 async uploadFiles(files) {
     const progressDiv = document.getElementById('kb-upload-progress');
     if (progressDiv) progressDiv.classList.remove('hidden');

     // Upload all files in parallel
     const uploadPromises = Array.from(files).map(async (file, i) => {
         const formData = new FormData();
         formData.append('file', file);

         try {
             const response = await fetch('/api/knowledge/upload', {
                 method: 'POST',
                 credentials: 'include',
                 body: formData
             });
             return { file: file.name, success: response.ok };
         } catch (error) {
             return { file: file.name, success: false, error };
         }
     });

     const results = await Promise.all(uploadPromises);
     // Update UI with results
 }

 3.6 Add Token Refresh Mechanism (Frontend + Backend)

 Decision: INCLUDE REFRESH ENDPOINT

 Backend File: /home/tech/PeanutChat/app/routers/auth.py

 Add these imports at top if not present:
 import jwt
 from app import config

 Add this endpoint after the existing /logout endpoint (around line 75):
 @router.post("/refresh")
 async def refresh_token(request: Request, response: Response):
     """Refresh the access token using existing valid token"""
     token = request.cookies.get("access_token")
     if not token:
         raise HTTPException(status_code=401, detail="No token provided")

     try:
         # Verify current token is valid (not expired)
         payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
         user_id = payload.get("sub")
         username = payload.get("username")

         # Issue new token with fresh expiration
         new_token = auth_service.create_access_token({
             "sub": str(user_id),
             "username": username
         })

         response.set_cookie(
             key="access_token",
             value=new_token,
             httponly=True,
             secure=config.COOKIE_SECURE,  # From Phase 1
             samesite="lax",
             max_age=60 * 60 * 24  # 24 hours
         )
         return {"message": "Token refreshed"}
     except jwt.ExpiredSignatureError:
         raise HTTPException(status_code=401, detail="Token expired - please 
 login again")
     except jwt.InvalidTokenError:
         raise HTTPException(status_code=401, detail="Invalid token")

 Frontend File: /home/tech/PeanutChat/static/js/auth.js

 Step 1: Add refreshInterval to constructor (line 6-10):
 class AuthManager {
     constructor() {
         this.user = null;
         this.token = null;
         this.onAuthChange = null;
         this.refreshInterval = null;  // ADD THIS LINE
     }

 Step 2: Add these three new methods after the init() method (after line 32):
     /**
      * Start periodic token refresh
      */
     startTokenRefresh() {
         // Stop any existing interval first
         this.stopTokenRefresh();
         // Refresh token every 20 minutes (token expires in 24 hours)
         this.refreshInterval = setInterval(() => this.refreshToken(), 20 * 60
  * 1000);
     }

     /**
      * Stop periodic token refresh
      */
     stopTokenRefresh() {
         if (this.refreshInterval) {
             clearInterval(this.refreshInterval);
             this.refreshInterval = null;
         }
     }

     /**
      * Refresh the access token
      */
     async refreshToken() {
         try {
             const response = await fetch('/api/auth/refresh', {
                 method: 'POST',
                 credentials: 'include'
             });
             if (!response.ok) {
                 console.warn('Token refresh failed, logging out');
                 this.stopTokenRefresh();
                 await this.logout();
             }
         } catch (error) {
             console.error('Token refresh error:', error);
         }
     }

 Step 3: In the register() method (around line 59-60), add
 startTokenRefresh():
         const data = await response.json();
         this.user = data.user;
         this.token = data.access_token;
         this.startTokenRefresh();  // ADD THIS LINE
         this.notifyAuthChange();
         return data;

 Step 4: In the login() method (around line 81-84), add startTokenRefresh():
         const data = await response.json();
         this.user = data.user;
         this.token = data.access_token;
         this.startTokenRefresh();  // ADD THIS LINE
         this.notifyAuthChange();
         return data;

 Step 5: In the logout() method (around line 91), add stopTokenRefresh():
     async logout() {
         this.stopTokenRefresh();  // ADD THIS LINE AT START
         try {
             await fetch('/api/auth/logout', {

 Step 6: In the init() method, start refresh if already logged in (around line
  24):
             if (response.ok) {
                 this.user = await response.json();
                 this.startTokenRefresh();  // ADD THIS LINE
                 this.notifyAuthChange();
                 return true;
             }

 Step 7: In deleteAccount() method (around line 147), add stopTokenRefresh():
     async deleteAccount() {
         this.stopTokenRefresh();  // ADD THIS LINE AT START
         const response = await fetch('/api/auth/account', {

 Verification Commands

 # Test embedding models filtered
 curl http://localhost:8080/api/models | jq '.models[].name' | grep -i embed
 # Should return empty

 # Test error handling - stop Ollama and try to load models
 sudo systemctl stop ollama
 # UI should show error toast, not crash

 # Check no console.log in production
 grep -n "console.log" static/js/chat.js
 # Should return nothing or only wrapped in DEBUG

 ---
 Phase 4: Dependency & Schema Cleanup

 Priority: HIGH | Estimated Files: 2
 Decision: REMOVE TTS COLUMNS WITH MIGRATION

 Context for Executor

 PeanutChat is a FastAPI chat application at /home/tech/PeanutChat/. TTS/STT
 features were removed but dependencies remain, causing ~10GB+ container
 images. Database schema also has dead TTS columns. This phase has NO 
 dependencies and can run in parallel with Phases 5 and 6.

 Files to Modify

 1. /home/tech/PeanutChat/requirements.txt - Remove unused dependencies
 2. /home/tech/PeanutChat/app/services/database.py - Add migration to remove
 TTS columns

 Tasks

 4.1 Remove Unused Dependencies

 File: /home/tech/PeanutChat/requirements.txt around lines 15-23
 Problem: Heavy ML libraries for removed TTS/STT feature.
 Remove these lines:
 nemo_toolkit[asr]>=2.0.0
 soundfile>=0.12.0
 silentcipher>=1.0.0
 moshi>=0.1.0
 Keep: tokenizers and huggingface_hub may be needed for embeddings.

 4.2 Add Migration to Remove TTS Columns

 File: /home/tech/PeanutChat/app/services/database.py
 Problem: Dead columns in user_settings table: tts_enabled, tts_speaker,
 tts_temperature, tts_topk.

 Add new migration after existing migrations:
 def _migrate_004_remove_tts_columns(self):
     """Remove deprecated TTS columns from user_settings"""
     # SQLite doesn't support DROP COLUMN directly, so we need to recreate the
  table
     self.execute("""
         CREATE TABLE IF NOT EXISTS user_settings_new (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER UNIQUE NOT NULL,
             theme TEXT DEFAULT 'dark',
             created_at TEXT NOT NULL,
             updated_at TEXT NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users(id)
         )
     """)

     # Copy data (excluding TTS columns)
     self.execute("""
         INSERT INTO user_settings_new (id, user_id, theme, created_at, 
 updated_at)
         SELECT id, user_id, theme, created_at, updated_at FROM user_settings
     """)

     # Drop old table and rename new one
     self.execute("DROP TABLE user_settings")
     self.execute("ALTER TABLE user_settings_new RENAME TO user_settings")

     logger.info("Migration 004: Removed deprecated TTS columns from 
 user_settings")

 Update _run_migrations() to include migration 004:
 def _run_migrations(self):
     """Run all database migrations"""
     self._migrate_001_create_users()
     self._migrate_002_create_user_settings()
     self._migrate_003_create_knowledge_base()
     self._migrate_004_remove_tts_columns()  # Add this

 Note: Also remove the TTS column definitions from
 _migrate_002_create_user_settings() so new installations don't create them.

 Verification Commands

 # Test app still works after dependency removal
 pip install -r requirements.txt
 python -c "from app.main import app; print('OK')"

 # Check container size reduction
 docker build -t peanutchat:slim .
 docker images peanutchat:slim --format "{{.Size}}"

 ---
 Phase 5: Configuration & Deployment Fixes

 Priority: MEDIUM | Estimated Files: 4

 Context for Executor

 PeanutChat is a FastAPI application at /home/tech/PeanutChat/. This phase
 fixes configuration and deployment issues. This phase has NO dependencies and
  can run in parallel with Phases 4 and 6.

 Files to Modify

 1. /home/tech/PeanutChat/app/tools/definitions.py - Use is_vision parameter
 2. /home/tech/PeanutChat/app/services/auth_service.py - Fix deprecated
 datetime
 3. /home/tech/PeanutChat/peanutchat.service - Parameterize paths
 4. /home/tech/PeanutChat/start_peanutchat.sh - Add error handling

 Tasks

 5.1 Fix is_vision Parameter in Tool Definitions

 File: /home/tech/PeanutChat/app/tools/definitions.py around lines 76-78
 Problem: get_tools_for_model() ignores capabilities, returns all tools
 regardless.

 Current code:
 def get_tools_for_model():
     """Get available tools for tool-capable models"""
     return ALL_TOOLS

 Replace with:
 def get_tools_for_model(supports_tools: bool = True, supports_vision: bool = 
 False) -> List[Dict]:
     """Get available tools filtered by model capabilities"""
     if not supports_tools:
         return []

     tools = ALL_TOOLS.copy()

     # Filter vision-only tools if model doesn't support vision
     if not supports_vision:
         tools = [t for t in tools if t.get('name') != 'analyze_image']

     return tools

 5.2 Parameterize Service File

 File: /home/tech/PeanutChat/peanutchat.service
 Problem: Hardcoded /home/tech/PeanutChat paths not portable.

 Replace entire file with:
 [Unit]
 Description=PeanutChat AI Chat Service
 After=network.target ollama.service
 Wants=ollama.service

 [Service]
 Type=simple
 User=tech
 WorkingDirectory=/home/tech/PeanutChat
 ExecStart=/home/tech/PeanutChat/venv/bin/python3 /home/tech/PeanutChat/run.py
 Restart=on-failure
 RestartSec=5
 Environment="PATH=/home/tech/PeanutChat/venv/bin:/usr/local/bin:/usr/bin:/bin
 "

 [Install]
 WantedBy=multi-user.target

 Note: Paths remain hardcoded but are now clearly visible. For portability,
 create an install script that generates this file.

 5.3 Add Shell Script Error Handling

 File: /home/tech/PeanutChat/start_peanutchat.sh
 Problem: No set -e, silent failures possible.

 Replace entire file with:
 #!/bin/bash
 set -euo pipefail

 SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
 cd "$SCRIPT_DIR"

 if [ ! -d "venv" ]; then
     echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"
     echo "Run: python3 -m venv venv && source venv/bin/activate && pip 
 install -r requirements.txt"
     exit 1
 fi

 echo "Starting PeanutChat from $SCRIPT_DIR..."
 source venv/bin/activate
 exec python3 run.py

 5.4 Fix Deprecated datetime.utcnow()

 File: /home/tech/PeanutChat/app/services/auth_service.py around line 76
 Problem: datetime.utcnow() deprecated in Python 3.12.

 Step 1: Check imports at top of file, ensure timezone is imported:
 from datetime import datetime, timezone

 Step 2: Find and replace (around line 76):
 # Current:
 created_at = datetime.utcnow().isoformat()

 # Change to:
 created_at = datetime.now(timezone.utc).isoformat()

 Verification Commands

 # Test shell script error handling
 bash -x start_peanutchat.sh
 # Should fail gracefully if venv missing

 # Test service file
 systemctl --user daemon-reload
 systemctl --user start peanutchat
 systemctl --user status peanutchat

 ---
 Phase 6: Low Priority Cleanup

 Priority: LOW | Estimated Files: 3

 Context for Executor

 PeanutChat is a FastAPI application at /home/tech/PeanutChat/. This phase
 addresses minor code quality issues. This phase has NO dependencies and can 
 run in parallel with Phases 4 and 5.

 Files to Modify

 1. /home/tech/PeanutChat/static/js/settings.js - Fix useless check
 2. /home/tech/PeanutChat/app/services/database.py - Add TODO for unused
 tables
 3. /home/tech/PeanutChat/app/services/knowledge_store.py - Add TODO for
 embedding storage

 Tasks

 6.1 Fix Useless knowledgeManager Check

 File: /home/tech/PeanutChat/static/js/settings.js around lines 183-185
 Problem: typeof knowledgeManager !== 'undefined' check is always true because
  knowledgeManager is a global defined at bottom of knowledge.js.

 Current code:
 if (typeof knowledgeManager !== 'undefined') {
     knowledgeManager.init();
 }

 Replace with (just call init directly):
 knowledgeManager.init();

 Or if you want to keep defensive check, use a proper initialized flag:
 if (knowledgeManager && !knowledgeManager.initialized) {
     knowledgeManager.init();
     knowledgeManager.initialized = true;
 }

 6.2 Add TODO Comments for Technical Debt

 These are documentation-only changes to flag known issues for future cleanup.

 File: /home/tech/PeanutChat/app/services/database.py
 At the top of _migrate_002_create_user_settings() (around line 146), add
 comment:
 def _migrate_002_create_user_settings(self):
     """Create user settings table

     NOTE: This migration creates TTS columns that are no longer used.
     Phase 4 migration (_migrate_004_remove_tts_columns) removes them.
     """

 File: /home/tech/PeanutChat/app/services/knowledge_store.py
 In the add_chunk() method (around line 88), add comment above the embedding
 line:
 def add_chunk(self, document_id: str, chunk_index: int, content: str, 
 embedding: List[float]) -> str:
     chunk_id = str(uuid.uuid4())
     # TODO: Consider using BLOB for embeddings instead of JSON string.
     # JSON works but is less efficient for large datasets with many vectors.
     embedding_json = json.dumps(embedding)

 Verification Commands

 # Verify no runtime errors
 python -c "from app.services.database import get_database; db = 
 get_database(); print('OK')"

 ---
 Execution Order

 | Phase | Parallel Safe | Dependencies
    | Est. Changes |
 |-------|---------------|----------------------------------------------------
 ---|--------------|
 | 1     | No            | None
    | 4 files      |
 | 2     | No            | Phase 1 (auth.py config import)
    | 3+ files     |
 | 3     | No            | Phase 1 (COOKIE_SECURE), Phase 2 (async
 conversation) | 5 files      |
 | 4     | Yes           | None
    | 2 files      |
 | 5     | Yes           | None
    | 4 files      |
 | 6     | Yes           | None
    | 3 files      |

 Recommended execution sequence:
 1. Phase 1 - Critical security fixes (CORS, cookies, JWT, legacy auth)
 2. Phase 2 - Async conversion (depends on Phase 1 config changes)
 3. Phase 3 - Frontend fixes (depends on Phase 1 for config, Phase 2 for async
  calls)
 4. Phases 4, 5, 6 - Can run in parallel after Phase 3

 Alternative parallel groups (if sessions can coordinate):
 - Session A: Phase 1 → Phase 2 → Phase 3 (sequential, main path)
 - Session B: Phase 4 (can start immediately, no dependencies)
 - Session C: Phase 5 (can start immediately, no dependencies)
 - Session D: Phase 6 (can start immediately, lowest priority)

 ---
 Files Reference

 | File                               | Phases | Notes
                |
 |------------------------------------|--------|------------------------------
 ---------------|
 | app/main.py                        | 1      | CORS, startup warning
                |
 | app/config.py                      | 1, 5   | CORS_ORIGINS, COOKIE_SECURE
                |
 | app/routers/auth.py                | 1, 3   | Cookie security, refresh
 endpoint           |
 | app/routers/chat.py                | 1, 2   | Legacy auth, async
 conversation calls       |
 | app/services/conversation_store.py | 2      | Full async conversion
                |
 | app/services/auth_service.py       | 5      | datetime.utcnow fix
                |
 | app/tools/definitions.py           | 5      | is_vision filtering
                |
 | app/services/database.py           | 4      | TTS column migration
                |
 | app/services/knowledge_store.py    | 6      | Documentation only
                |
 | static/js/app.js                   | 3      | Model filtering, error
 handling, init order |
 | static/js/chat.js                  | 3      | Remove console.log
                |
 | static/js/auth.js                  | 3      | Token refresh mechanism
                |
 | static/js/knowledge.js             | 3      | Parallel uploads
                |
 | static/js/settings.js              | 6      | Fix useless check
                |
 | requirements.txt                   | 4      | Remove TTS deps
                |
 | peanutchat.service                 | 5      | Parameterize paths
                |
 | start_peanutchat.sh                | 5      | Error handling
                |

 ---
 Quick Reference: Issue Count by Severity

 | Severity | Count | Phases  |
 |----------|-------|---------|
 | Critical | 5     | 1, 2    |
 | High     | 8     | 2, 3, 4 |
 | Medium   | 9     | 3, 5, 6 |
 | Low      | 5     | 5, 6    |
 | Total    | 27    |         |
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

