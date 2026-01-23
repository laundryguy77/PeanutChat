# PeanutChat Build Plan and Issue Report

**Generated:** 2026-01-23
**Codebase Version:** Based on commit `abf093d`
**Prepared by:** Code Review Analysis

---

## Executive Summary

This document provides a comprehensive build plan addressing all security vulnerabilities, code quality issues, and technical debt identified in the PeanutChat codebase. Each issue includes:
- Exact file locations and line numbers
- Search patterns to locate relevant code
- Step-by-step remediation instructions
- Testing requirements

---

## Table of Contents

1. [Critical Security Issues](#1-critical-security-issues)
2. [High Priority Issues](#2-high-priority-issues)
3. [Medium Priority Issues](#3-medium-priority-issues)
4. [Low Priority Issues](#4-low-priority-issues)
5. [Code Quality & Technical Debt](#5-code-quality--technical-debt)
6. [Test Coverage Gaps](#6-test-coverage-gaps)
7. [Implementation Order](#7-implementation-order)

---

## 1. Critical Security Issues

### CRIT-001: Hardcoded Adult Content Passcode

**Severity:** CRITICAL
**Type:** Security - Authentication Bypass
**Status:** Open

**Location:**
- File: `app/services/user_profile_service.py`
- Line: 15
- Search: `grep -n "ADULT_PASSCODE" app/services/user_profile_service.py`

**Current Code:**
```python
class UserProfileService:
    """Business logic for user profile operations."""

    ADULT_PASSCODE = "6060"
```

**Problem:**
The passcode for unlocking adult content mode is hardcoded in the source code. Anyone with access to the repository can see the passcode and bypass content gating.

**Remediation Steps:**
1. Add environment variable `ADULT_PASSCODE` to `app/config.py`:
   ```python
   ADULT_PASSCODE = os.getenv("ADULT_PASSCODE", "")
   ```
2. Add startup validation in `app/main.py` to fail if not set:
   ```python
   if not ADULT_PASSCODE:
       logger.error("ADULT_PASSCODE environment variable must be set")
       sys.exit(1)
   ```
3. Update `app/services/user_profile_service.py` to import from config
4. Optionally: Hash the passcode with bcrypt and compare hashes instead of plaintext
5. Add to `.env.example` with placeholder value

**Files to Modify:**
- `app/config.py` - Add ADULT_PASSCODE config
- `app/main.py` - Add startup validation
- `app/services/user_profile_service.py` - Import from config
- `.env.example` - Document the variable

**Testing:**
- Verify app fails to start without ADULT_PASSCODE set
- Verify correct passcode still unlocks adult mode
- Verify wrong passcode fails

---

### CRIT-002: Passcode Leaked in Error Messages

**Severity:** CRITICAL
**Type:** Security - Information Disclosure
**Status:** Open

**Location:**
- File: `app/services/user_profile_service.py`
- Lines: 464, 498, 517
- Search: `grep -n "passcode 6060" app/`

**Current Code (line 464):**
```python
"error": "Adult mode must be enabled first (passcode 6060)"
```

**Additional Occurrences:**
- Line 498: Comment mentioning passcode
- Line 517: Error message with passcode hint

**Related Files with Passcode References:**
- `app/routers/commands.py` lines 76, 350
- `app/routers/user_profile.py` line 105
- `app/services/user_profile_store.py` line 569
- `app/services/database.py` line 379

**Problem:**
Error messages reveal the exact passcode to users, completely defeating the purpose of having a passcode.

**Remediation Steps:**
1. Search all files: `grep -rn "6060" app/`
2. Replace all user-facing error messages:
   - Before: `"Adult mode must be enabled first (passcode 6060)"`
   - After: `"Adult mode must be enabled first via Settings"`
3. Remove passcode hints from API documentation comments (internal docs are OK)
4. Update any test files that reference the hardcoded value

**Files to Modify:**
- `app/services/user_profile_service.py` - Lines 464, 517
- `app/routers/commands.py` - Lines 76, 350
- `app/routers/user_profile.py` - Line 105
- `app/services/user_profile_store.py` - Line 569
- `app/services/database.py` - Line 379

**Testing:**
- Trigger each error condition and verify no passcode in response
- Check API responses for any passcode leakage

---

## 2. High Priority Issues

### HIGH-001: Frontend XSS via Unsanitized Markdown

**Severity:** HIGH
**Type:** Security - Cross-Site Scripting
**Status:** Open

**Location:**
- File: `static/js/chat.js`
- Lines: 33-44 (marked config), 53 (parse call)
- Search: `grep -n "marked\." static/js/chat.js`

**Current Code:**
```javascript
marked.setOptions({
    renderer: renderer,
    highlight: function(code, lang) { ... },
    breaks: true,
    gfm: true
    // NOTE: No sanitization configured!
});

// Line 53
let html = marked.parse(content);
```

**Problem:**
1. Markdown output is rendered as HTML without sanitization
2. marked v12+ removed built-in sanitize option
3. No DOMPurify or similar library is used
4. LLM responses could contain malicious HTML/JS that executes in user's browser
5. Extensive use of `innerHTML` throughout frontend without sanitization

**Remediation Steps:**
1. Add DOMPurify library to `static/index.html`:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js"></script>
   ```
2. Create sanitization wrapper in `static/js/chat.js`:
   ```javascript
   renderMarkdown(content) {
       if (!content || typeof marked === 'undefined') return content || '';
       try {
           let html = marked.parse(content);
           // Sanitize HTML to prevent XSS
           if (typeof DOMPurify !== 'undefined') {
               html = DOMPurify.sanitize(html, {
                   ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li',
                                  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'a',
                                  'table', 'thead', 'tbody', 'tr', 'th', 'td', 'div', 'span', 'img'],
                   ALLOWED_ATTR: ['href', 'src', 'alt', 'class', 'target', 'rel']
               });
           }
           // ... rest of processing
       }
   }
   ```
3. Audit all `innerHTML` assignments for user-controlled content

**Files to Modify:**
- `static/index.html` - Add DOMPurify script
- `static/js/chat.js` - Wrap marked.parse with DOMPurify
- `static/js/memory.js` - Verify escapeHtml usage
- `static/js/knowledge.js` - Verify user content handling

**Testing:**
- Test with markdown containing `<script>alert('xss')</script>`
- Test with markdown containing `<img onerror="alert('xss')">`
- Verify legitimate markdown still renders correctly

---

### HIGH-003: URL Cache Memory Exhaustion (DoS Vulnerability)

**Severity:** HIGH
**Type:** Security - Denial of Service
**Status:** Open

**Location:**
- File: `app/services/tool_executor.py`
- Lines: 23-24 (definition), 365-386 (usage)
- Search: `grep -n "_url_cache\|URL_CACHE" app/services/tool_executor.py`

**Current Code:**
```python
# Line 23-24
_url_cache: Dict[str, Dict[str, Any]] = {}
URL_CACHE_TTL = 300  # 5 minutes

# Line 384-386
if len(_url_cache) > 100:
    oldest_url = min(_url_cache, key=lambda u: _url_cache[u]["timestamp"])
    del _url_cache[oldest_url]
```

**Problem:**
1. Cache stores up to 100 entries with potentially 10KB each = 1MB minimum
2. No memory size limit on cached content
3. Attacker can exhaust memory by requesting unique URLs
4. Global cache shared across all users (no isolation)

**Remediation Steps:**
1. Reduce max entries from 100 to 20
2. Add per-entry size limit (already 10KB, but verify)
3. Add total cache memory limit (e.g., 5MB max)
4. Consider using `functools.lru_cache` or `cachetools.TTLCache` for better memory management
5. Add cache statistics logging for monitoring

**Implementation:**
```python
from cachetools import TTLCache
import sys

# Maximum cache size: 20 entries, 5 minute TTL
URL_CACHE_MAX_ENTRIES = 20
URL_CACHE_TTL = 300
URL_CACHE_MAX_ENTRY_SIZE = 10000  # 10KB per entry

_url_cache: TTLCache = TTLCache(maxsize=URL_CACHE_MAX_ENTRIES, ttl=URL_CACHE_TTL)
```

**Files to Modify:**
- `app/services/tool_executor.py`
- `requirements.txt` (add cachetools if using)

**Testing:**
- Test cache eviction works correctly
- Test cache doesn't exceed memory limits
- Load test with many unique URLs

---

### HIGH-004: Thread-Unsafe Legacy Code Path

**Severity:** HIGH
**Type:** Security - Race Condition
**Status:** Open

**Location:**
- File: `app/services/tool_executor.py`
- Lines: 86-147
- Search: `grep -n "_deprecated_" app/services/tool_executor.py`

**Current Code:**
```python
class ToolExecutor:
    def __init__(self):
        # DEPRECATED: These are kept only for backwards compatibility
        self._deprecated_user_id: Optional[int] = None
        self._deprecated_conv_id: Optional[str] = None
        self._deprecated_image_registry: Dict[str, str] = {}
```

**Problem:**
If `ToolExecutionContext` is not created, the code falls back to instance variables on the singleton `ToolExecutor`. This causes:
1. Race conditions when multiple requests execute concurrently
2. Potential data leakage between users (image registry shared)
3. User ID/conversation ID mixing between requests

**Remediation Steps:**
1. Find all callers that might not create context:
   ```bash
   grep -rn "tool_executor\." app/routers/
   grep -rn "create_context\|set_current" app/routers/
   ```
2. Ensure `create_context()` is called at the start of every request handler that uses tools
3. Add assertion in deprecated methods to fail loudly instead of silently using shared state:
   ```python
   def set_current_user(self, user_id: int):
       ctx = get_current_context()
       if ctx is None:
           raise RuntimeError(
               "ToolExecutionContext not initialized. "
               "Call create_context() before using ToolExecutor."
           )
       ctx.user_id = user_id
   ```
4. Remove deprecated fields after all code paths updated

**Files to Modify:**
- `app/services/tool_executor.py` - Make deprecated methods fail loudly
- `app/routers/chat.py` - Ensure context created
- Any other routers using tool_executor

**Testing:**
- Run concurrent requests and verify no data mixing
- Verify deprecated code path is not exercised
- Add test for race condition scenario

---

### HIGH-005: MCP Command Execution Risk

**Severity:** HIGH
**Type:** Security - Command Injection
**Status:** Open (needs review)

**Location:**
- File: `app/services/mcp_client.py`
- Lines: 23-47
- Search: `grep -n "ALLOWED_MCP_COMMANDS" app/services/mcp_client.py`

**Current Code:**
```python
ALLOWED_MCP_COMMANDS = {
    "node", "npx", "npm",
    "python", "python3", "uvx", "uv",
    "deno",
    # ... specific MCP server binaries
}
```

**Problem:**
While there's an allowlist, allowing general-purpose interpreters (python, node) means:
1. If argument sanitization has gaps, arbitrary code could execute
2. User-controlled MCP server configurations could be exploited
3. Need to verify args are properly validated

**Remediation Steps:**
1. Audit argument validation in `_validate_mcp_server_config()`:
   ```bash
   grep -n "_validate_mcp_server_config\|sanitize.*arg" app/services/mcp_client.py
   ```
2. Consider restricting to specific MCP server binaries only
3. Add path validation (only allow commands from known directories)
4. Log all MCP command executions for audit
5. Add resource limits (already has some, verify completeness)

**Files to Review:**
- `app/services/mcp_client.py` - Full security review

**Testing:**
- Test with malicious argument patterns
- Test path traversal in arguments
- Test shell injection attempts

---

## 3. Medium Priority Issues

### MED-001: Thinking Token Limits Without Timeout

**Severity:** MEDIUM
**Type:** Performance/Resource
**Status:** Open

**Location:**
- File: `app/routers/chat.py`
- Lines: 595-596, 735-736
- Search: `grep -n "thinking.*3000\|thinking.*2000" app/routers/chat.py`

**Current Code:**
```python
# Line 595-596
if thinking_token_count > 3000:
    logger.warning(f"Thinking limit reached ({thinking_token_count} tokens) without content, breaking")

# Line 735-736
if thinking_count > 2000:  # Allow more thinking for complex queries
    logger.warning(f"Thinking limit reached ({thinking_count} tokens), breaking")
```

**Problem:**
1. Magic numbers (3000, 2000) not configurable
2. Token counts don't prevent long-running requests
3. Need timeout protection in addition to token limits

**Remediation Steps:**
1. Move limits to config:
   ```python
   # app/config.py
   THINKING_TOKEN_LIMIT_INITIAL = int(os.getenv("THINKING_TOKEN_LIMIT_INITIAL", "3000"))
   THINKING_TOKEN_LIMIT_FOLLOWUP = int(os.getenv("THINKING_TOKEN_LIMIT_FOLLOWUP", "2000"))
   CHAT_REQUEST_TIMEOUT = int(os.getenv("CHAT_REQUEST_TIMEOUT", "300"))  # 5 minutes
   ```
2. Add request timeout wrapper around chat streaming
3. Consider using `asyncio.timeout()` for hard cutoff

**Files to Modify:**
- `app/config.py` - Add constants
- `app/routers/chat.py` - Import from config, add timeout

**Testing:**
- Test with prompts that generate excessive thinking
- Verify timeout triggers correctly

---

### MED-002: Base64 Decoding Error Handling

**Severity:** MEDIUM
**Type:** Error Handling
**Status:** Open

**Location:**
- File: `app/services/file_processor.py`
- Lines: 70, 111
- Search: `grep -n "b64decode" app/services/file_processor.py`

**Current Code:**
```python
pdf_bytes = base64.b64decode(content_b64)  # Line 70
zip_bytes = base64.b64decode(content_b64)  # Line 111
```

**Problem:**
Invalid base64 input causes `binascii.Error` exception. While caught by outer try/except, the error message may not be user-friendly.

**Remediation Steps:**
1. Add explicit base64 validation:
   ```python
   import binascii

   try:
       pdf_bytes = base64.b64decode(content_b64, validate=True)
   except binascii.Error as e:
       return {
           'name': name,
           'type': 'pdf',
           'error': 'Invalid base64 encoding',
           'content': '[Error: Invalid file encoding]'
       }
   ```

**Files to Modify:**
- `app/services/file_processor.py`
- Other files with base64.b64decode (search results show ~20 locations)

**Testing:**
- Test with invalid base64 input
- Verify error messages are user-friendly

---

### MED-003: Empty API Keys Fail Silently

**Severity:** MEDIUM
**Type:** Configuration
**Status:** Open

**Location:**
- File: `app/config.py`
- Lines: 54, 81
- Search: `grep -n "BRAVE_SEARCH_API_KEY\|HF_TOKEN" app/config.py`

**Current Code:**
```python
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")  # Line 54
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Line 81
```

**Problem:**
Empty API keys cause features to fail silently without clear error messages to users.

**Remediation Steps:**
1. Add feature availability checks:
   ```python
   # app/config.py
   WEB_SEARCH_AVAILABLE = bool(BRAVE_SEARCH_API_KEY)
   VIDEO_GENERATION_AVAILABLE = bool(HF_TOKEN)
   ```
2. Log warnings at startup if keys missing:
   ```python
   # app/main.py
   if not WEB_SEARCH_AVAILABLE:
       logger.warning("BRAVE_SEARCH_API_KEY not set - web search disabled")
   ```
3. Return clear error in tool executor when feature unavailable
4. Update frontend to show disabled state for unavailable features

**Files to Modify:**
- `app/config.py` - Add availability flags
- `app/main.py` - Add startup warnings
- `app/services/tool_executor.py` - Check availability before use
- `static/js/chat.js` - Show feature availability

**Testing:**
- Test with missing API keys
- Verify clear error messages returned
- Verify frontend shows disabled state

---

## 4. Low Priority Issues

### LOW-001: Debug Logging May Leak Sensitive Data

**Severity:** LOW
**Type:** Security - Information Disclosure
**Status:** Open

**Location:**
- Various files in `app/services/`
- Search: `grep -rn "logger.debug.*content\|logger.debug.*url" app/services/`

**Problem:**
Debug logs may include full URL contents, request bodies, or other sensitive data when LOG_LEVEL=DEBUG.

**Remediation Steps:**
1. Audit all debug log statements
2. Truncate sensitive content in logs
3. Add log sanitization helper:
   ```python
   def safe_log(content: str, max_length: int = 100) -> str:
       if len(content) > max_length:
           return content[:max_length] + "...[truncated]"
       return content
   ```

**Testing:**
- Run with DEBUG logging and verify no sensitive data logged

---

### LOW-002: Print Statements in Production Code

**Severity:** LOW
**Type:** Code Quality
**Status:** Open

**Location:**
- File: `app/services/file_processor.py`
- Lines: 69, 71, 74, 79, 84, 85, 98
- Search: `grep -n "print(" app/services/file_processor.py`

**Problem:**
Debug print statements in production code instead of proper logging.

**Remediation Steps:**
1. Replace all `print()` with `logger.debug()`
2. Search for other print statements: `grep -rn "print(" app/`

**Files to Modify:**
- `app/services/file_processor.py`
- Any other files with print statements

---

### LOW-003: Missing Security Headers

**Severity:** LOW
**Type:** Security - Defense in Depth
**Status:** Open

**Location:**
- File: `app/main.py`
- Search: `grep -n "Content-Security-Policy\|X-Frame-Options" app/`

**Problem:**
No security headers configured:
- No Content-Security-Policy (CSP) header
- No X-Frame-Options header
- No X-Content-Type-Options header

**Remediation Steps:**
1. Add security headers middleware to `app/main.py`:
   ```python
   from starlette.middleware import Middleware
   from starlette.middleware.base import BaseHTTPMiddleware

   class SecurityHeadersMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request, call_next):
           response = await call_next(request)
           response.headers["X-Frame-Options"] = "DENY"
           response.headers["X-Content-Type-Options"] = "nosniff"
           response.headers["X-XSS-Protection"] = "1; mode=block"
           response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
           # Add CSP once DOMPurify is in place
           return response

   app.add_middleware(SecurityHeadersMiddleware)
   ```

**Files to Modify:**
- `app/main.py`

**Testing:**
- Verify headers present in all responses
- Test CSP doesn't break legitimate functionality

---

## 5. Code Quality & Technical Debt

### DEBT-001: Large Monolithic Files

**Files Exceeding 500 Lines:**

| File | Lines | Recommendation |
|------|-------|----------------|
| `app/services/tool_executor.py` | 1,485 | Split into: `tools/web_tools.py`, `tools/image_tools.py`, `tools/video_tools.py`, `tools/memory_tools.py` |
| `app/routers/chat.py` | 1,257 | Extract streaming logic to `services/chat_service.py` |
| `app/services/system_prompt_builder.py` | 791 | Consider splitting prompt templates to separate files |
| `app/services/image_backends.py` | 789 | OK for now - contains multiple backend implementations |
| `app/services/conversation_store.py` | 700 | OK - single responsibility |
| `app/services/mcp_client.py` | 677 | OK - single responsibility |
| `app/services/user_profile_store.py` | 670 | OK - single responsibility |

**Remediation Steps for tool_executor.py:**
1. Create `app/tools/` directory
2. Move web search logic to `app/tools/web_tools.py`
3. Move image generation to `app/tools/image_tools.py`
4. Move video generation to `app/tools/video_tools.py`
5. Move memory/knowledge tools to `app/tools/memory_tools.py`
6. Keep `tool_executor.py` as orchestrator that imports and delegates

---

### DEBT-002: TODO Comments (Technical Debt)

**Location:**
- Search: `grep -rn "TODO\|FIXME" app/`

**Current TODOs:**
```
app/services/video_backends.py:152: # TODO: Implement base64 return for video
app/services/knowledge_store.py:89:  # TODO: Consider using BLOB for embeddings instead of JSON string.
```

**Remediation:**
1. **video_backends.py:152** - Implement base64 video return for consistency with image tools
2. **knowledge_store.py:89** - Convert embeddings from JSON string to BLOB for better performance

---

### DEBT-003: Deprecated Code Not Removed

**Location:**
- File: `app/services/tool_executor.py`
- Lines: 86-147
- Search: `grep -n "DEPRECATED\|_deprecated_" app/services/tool_executor.py`

**Remediation:**
After fixing HIGH-004, remove all deprecated code paths entirely.

---

### DEBT-004: Inconsistent Error Response Formats

**Problem:**
Some functions return `{"success": False, "error": "..."}` while others raise exceptions.

**Search:**
```bash
grep -rn '"success": False' app/
grep -rn "raise HTTPException" app/routers/
```

**Remediation:**
1. Standardize on one approach per layer:
   - Services: Return result objects or raise custom exceptions
   - Routers: Catch exceptions and return consistent HTTP responses
2. Create standard response models in `app/models/responses.py`

---

## 6. Test Coverage Gaps

### Current Test Coverage

**Existing Tests:**
- `tests/test_auth_verification.py` - Authentication flow tests
- `tests/test_data_layer.py` - Database and persistence tests

**Missing Test Coverage:**

| Area | Priority | Test File to Create |
|------|----------|---------------------|
| Chat streaming | HIGH | `tests/test_chat.py` |
| Tool execution | HIGH | `tests/test_tool_executor.py` |
| Knowledge base | MEDIUM | `tests/test_knowledge_base.py` |
| User profiles | MEDIUM | `tests/test_user_profiles.py` |
| MCP client | MEDIUM | `tests/test_mcp_client.py` |
| Memory service | LOW | `tests/test_memory_service.py` |
| Rate limiting | HIGH | `tests/test_rate_limiter.py` |
| SSRF protection | HIGH | `tests/test_ssrf_protection.py` |
| XSS protection | HIGH | `tests/test_xss_protection.py` |

### Recommended Tests to Add

**tests/test_xss_protection.py:**
```python
"""Test XSS protection in frontend markdown rendering."""

def test_script_tags_sanitized():
    """Verify <script> tags are removed from markdown output."""

def test_event_handlers_sanitized():
    """Verify onerror/onclick handlers are removed."""

def test_javascript_urls_blocked():
    """Verify javascript: URLs are blocked."""

def test_legitimate_html_preserved():
    """Verify allowed tags (p, strong, em, code) still work."""
```

**tests/test_ssrf_protection.py:**
```python
"""Test SSRF protection in tool_executor."""

def test_blocks_localhost():
    """Verify localhost URLs are blocked."""

def test_blocks_private_ip_ranges():
    """Verify 10.x, 172.16.x, 192.168.x blocked."""

def test_blocks_link_local():
    """Verify 169.254.x.x blocked."""

def test_allows_public_urls():
    """Verify legitimate public URLs work."""
```

**tests/test_rate_limiter.py:**
```python
"""Test rate limiting behavior."""

def test_login_lockout_after_5_failures():
    """Verify account locked after 5 failed attempts."""

def test_lockout_expires_after_15_minutes():
    """Verify lockout expires correctly."""

def test_successful_login_resets_counter():
    """Verify success clears rate limit tracking."""
```

---

## 7. Implementation Order

### Phase 1: Critical Security (Immediate)
1. **CRIT-001**: Remove hardcoded passcode
2. **CRIT-002**: Remove passcode from error messages

### Phase 2: High Priority Security (Week 1)
3. **HIGH-001**: Add DOMPurify for XSS protection in markdown rendering
4. **HIGH-003**: Fix URL cache memory limits
5. **HIGH-004**: Remove thread-unsafe legacy code
6. **HIGH-005**: Audit MCP command execution

### Phase 3: Medium Priority (Week 2)
7. **MED-001**: Configure thinking token limits
8. **MED-002**: Improve base64 error handling
9. **MED-003**: Add API key availability checks

### Phase 4: Test Coverage (Week 3)
10. Add `tests/test_ssrf_protection.py`
11. Add `tests/test_rate_limiter.py`
12. Add `tests/test_tool_executor.py`
13. Add `tests/test_chat.py`
14. Add `tests/test_xss_protection.py` (frontend security)

### Phase 5: Code Quality (Week 4+)
15. **DEBT-001**: Split large files
16. **DEBT-002**: Address TODO comments
17. **DEBT-003**: Remove deprecated code
18. **DEBT-004**: Standardize error responses
19. **LOW-001**: Audit debug logging
20. **LOW-002**: Replace print statements
21. **LOW-003**: Add security headers middleware

---

## Appendix: Search Commands Reference

```bash
# Find all security-related issues
grep -rn "ADULT_PASSCODE\|6060" app/
grep -rn "_url_cache\|_deprecated_" app/services/
grep -rn "ALLOWED_MCP_COMMANDS" app/services/

# Find all TODO/FIXME comments
grep -rn "TODO\|FIXME\|HACK\|XXX" app/

# Find all print statements
grep -rn "print(" app/

# Find all base64 decode calls
grep -rn "b64decode" app/

# Find rate limiting code
grep -rn "rate.*limit\|lockout" app/

# Find SSRF protection
grep -rn "_is_private_ip\|private.*ip" app/

# Count lines in large files
wc -l app/services/*.py app/routers/*.py | sort -rn | head -20

# Frontend XSS-related searches
grep -rn "innerHTML" static/js/
grep -rn "marked\." static/js/
grep -rn "DOMPurify\|sanitize\|escapeHtml" static/js/

# Find test files
find tests -name "*.py" -type f

# Find test files
find tests -name "*.py" -type f
```

---

## Verification Checklist

After implementing fixes, verify:

- [ ] App fails to start without ADULT_PASSCODE env var
- [ ] No passcode appears in any API error response
- [ ] DOMPurify sanitizes markdown output (test with `<script>` tags)
- [ ] URL cache limited to 20 entries max
- [ ] ToolExecutor fails loudly without context
- [ ] MCP commands properly validated
- [ ] Thinking limits configurable via env
- [ ] Invalid base64 returns friendly error
- [ ] Missing API keys show clear warnings
- [ ] All tests pass
- [ ] No print statements in app/ directory
- [ ] No hardcoded secrets in codebase
- [ ] Frontend innerHTML assignments use escaped/sanitized content
- [ ] Security headers (X-Frame-Options, X-Content-Type-Options) present in responses

---

*End of Build Plan*
