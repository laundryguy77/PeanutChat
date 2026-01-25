# PeanutChat UI Testing Findings: Authentication & Sidebar

**Test Date:** January 25, 2025  
**Tester:** Automated UI Testing Agent  
**Browser:** Chromium (headless via Playwright)  
**Viewport:** 1440x900

---

## A. REGISTRATION FLOW

### Initial Auth Modal
**Screenshot:** `01_initial_auth_modal.png`

**Observed:**
- Auth modal appears automatically on page load (unauthenticated state)
- Modal centered on dark backdrop overlay
- Title "Sign In" at top
- Two tabs: "Sign In" (active, highlighted with underline) and "Create Account"
- Sign In form visible by default with:
  - Username field (placeholder: "Enter your username")
  - Password field (placeholder: "Enter your password")
  - "Sign In" button (blue, full width)

**Source Code Reference:**
- Modal structure: `index.html` lines 155-230 (auth modal div)
- Tab switching logic: Likely in separate JS file

### Create Account Tab
**Screenshot:** `02_create_account_tab.png`

**Observed:**
- Clicking "Create Account" tab switches form
- Title changes to "Create Account"
- Form fields:
  - Username (placeholder: "Choose a username")
  - Email (optional) (placeholder: "Enter your email")
  - Password (placeholder: "Min 12 chars, upper, lower, digit, special")
  - Confirm Password (placeholder: "Confirm your password")
- "Create Account" button (blue, full width)

**Source Code Reference:**
- Registration endpoint: `auth.py` line 57-84 (`register` function)
- Password requirements: Shown in placeholder, validated server-side

### Validation - Empty Form
**Screenshot:** `03_registration_validation_empty.png`

**Observed:**
- Error message displayed in red banner: "Please enter username and password"
- Error appears above form fields
- Form fields remain empty

**Status:** ✅ PASS - Validation message displayed correctly

### Validation - Password Mismatch
**Screenshot:** `04_registration_password_mismatch.png`

**Observed:**
- Error message: "Passwords do not match"
- Username filled: "testuser_auth1_1769370807572"
- Password fields filled (masked)
- Email left empty (optional)

**Status:** ✅ PASS - Client-side validation catches password mismatch before API call

### Successful Registration
**Screenshot:** `05_post_registration.png`

**Observed:**
- Modal closes after successful registration
- User automatically logged in
- Main chat interface visible
- Sidebar shows:
  - User info at bottom: "testuser_auth1_1769..." with "Logged in" status
  - Logout icon visible
- Welcome message: "Welcome to PeanutChat"
- Model selector shows: "ministral-3:latest (tools, vision)"

**Source Code Reference:**
- `auth.js` lines 88-109: `register()` method calls API and stores user
- `auth.js` line 103: `markSessionActive()` sets sessionStorage marker

**Status:** ✅ PASS - Registration completes and auto-login works

---

## B. LOGIN FLOW

### After Logout - Login Form
**Screenshot:** `07_login_form.png`

**Observed:**
- Auth modal reappears after logout
- Sign In tab active
- Same form as initial load

### Validation - Empty Login
**Screenshot:** `08_login_validation_empty.png`

**Observed:**
- No visible error message for empty submission
- Form validation should trigger

**Note:** Screenshot shows form unchanged - may need to verify if HTML5 validation is used

### Invalid Credentials
**Screenshot:** `09_login_invalid_credentials.png`

**Observed:**
- Error message: "Invalid username or password"
- Red error banner displayed
- Username shows entered value: "nonexistent_user"
- Password field masked

**Source Code Reference:**
- `auth.py` lines 89-113: `login` endpoint returns 401 with "Invalid username or password" detail

**Status:** ✅ PASS - Correct error message displayed

### Successful Login
**Screenshot:** `10_successful_login.png`

**Observed:**
- Modal closes
- User logged in with test user
- Main interface visible
- Same state as post-registration

**Status:** ✅ PASS - Login flow works correctly

---

## C. SESSION HANDLING

**Observations:**
1. Session uses HTTP-only cookies (`auth.py` line 44-52)
2. `sessionStorage` marker tracks browser tab sessions (`auth.js` line 11)
3. New tabs require re-authentication (security feature)
4. Token refresh runs every 20 minutes (`auth.js` line 58)

**Source Code Reference:**
- Session marker: `auth.js` line 11 (`SESSION_MARKER_KEY`)
- Tab detection: `auth.js` lines 22-35

**Status:** ✅ Working as designed - Security-conscious session handling

---

## D. LOGOUT FLOW

### Before Logout
**Screenshot:** `18_before_logout.png` (not captured due to test timeout)

### After Logout
**Screenshot:** `06_after_logout.png`

**Observed:**
- Auth modal reappears
- All user data cleared from UI
- Sidebar shows empty state
- No conversations visible

**Source Code Reference:**
- `auth.js` lines 142-157: `logout()` clears session and notifies listeners
- `auth.py` lines 130-140: Blacklists token and deletes cookie

**Status:** ✅ PASS - Logout clears all state correctly

---

## E. SIDEBAR STRUCTURE

### Full Sidebar Layout
**Screenshot:** `11_sidebar_full.png`

**Observed Elements:**

| Element | Location | ID/Class | Present |
|---------|----------|----------|---------|
| Logo | Top left | `.font-display` | ✅ "PeanutChat" |
| Collapse Button | Top right (header) | `#sidebar-collapse-btn` | ✅ |
| New Chat Button | Below header | `#new-chat-btn` | ✅ Blue button |
| Search Input | Below New Chat | `#conversation-search` | ✅ "Search conversations..." |
| Conversation List | Middle area | `#conversation-list` | ✅ Shows "No conversations yet" |
| User Info | Bottom | `#user-info` | ✅ Username + "Logged in" |
| Logout Button | Bottom (next to user) | `#logout-btn` | ✅ Icon button |
| Settings Button | Very bottom | `#settings-btn` | ✅ "Settings" + "Preferences & Config" |

**Source Code Reference:**
- Sidebar: `index.html` lines 163-229
- User info: `index.html` lines 207-218

**Status:** ✅ PASS - All sidebar elements present and positioned correctly

---

## F. CONVERSATION MANAGEMENT

### New Conversation
**Screenshot:** `12_new_conversation.png`

**Observed:**
- Clicking "New Chat" creates empty conversation
- Conversation not yet named (no messages sent)
- Main area shows welcome screen

### Conversation with Message
**Screenshot:** `13_conversation_with_message.png`

**Observed:**
- User message displayed on right side (blue bubble)
- Message text: "Hello, this is test conversation 1"
- AI response area shows "PeanutChat AI" with typing indicator
- Timestamp visible: "02:54 PM"

### Multiple Conversations
**Screenshot:** `14_multiple_conversations.png`

**Observed:**
- Sidebar shows "TODAY" date header
- Three conversations listed:
  1. "Test conversation 2 mess..." (truncated)
  2. "Hello, this is test convers..." (truncated)
  3. (Currently active - not in list view)
- AI generating response (3 dots animation)
- "Stop" button visible during generation
- Context usage: 3%

**Status:** ✅ PASS - Multiple conversations create and display correctly

### Search Filtering
**Screenshot:** `15_search_filter.png`

**Observed:**
- Search input shows "test" with clear (X) button
- Conversations filtered - showing matching results
- Both visible conversations match "test" query
- Real-time filtering (no submit needed)

**Source Code Reference:**
- Search input: `index.html` line 193
- Filter logic: Likely in main.js

**Status:** ✅ PASS - Search filtering works

### Conversation Actions (Hover Menu)
**Screenshot:** `16_context_menu.png`

**Observed:**
- Hovering over conversation shows inline action icons
- Edit (pencil) icon visible
- Delete (trash) icon visible
- NOT a traditional right-click context menu - inline hover icons

**Note:** Test attempted to click "Rename" option but failed because the UI uses inline icons, not a dropdown menu

**Discrepancy:** Test script expected a traditional context menu (`text=Rename`), but UI uses hover icons

---

## Summary of Findings

### ✅ Working Correctly

1. Auth modal shows on unauthenticated load
2. Tab switching between Sign In / Create Account
3. Registration form validation (empty, password mismatch)
4. Successful registration with auto-login
5. Login validation (invalid credentials error)
6. Successful login
7. Logout clears session properly
8. All sidebar elements present
9. New conversation creation
10. Message sending and display
11. Conversation list with date grouping
12. Search filtering

### ⚠️ Observations/Notes

1. **Conversation actions** use inline hover icons, not a traditional context menu
2. **Session handling** requires re-auth on new tabs (by design)
3. **Password requirements** shown in placeholder only - no visible validator

### ❌ Issues Found

1. **Empty login validation** - No visible error message displayed (may rely on HTML5 validation)

---

## Screenshots Index

| File | Description |
|------|-------------|
| `01_initial_auth_modal.png` | Initial page load with auth modal |
| `02_create_account_tab.png` | Create Account form |
| `03_registration_validation_empty.png` | Empty form validation |
| `04_registration_password_mismatch.png` | Password mismatch validation |
| `05_post_registration.png` | Post-registration state |
| `06_after_logout.png` | After logout |
| `07_login_form.png` | Login form |
| `08_login_validation_empty.png` | Empty login attempt |
| `09_login_invalid_credentials.png` | Invalid credentials error |
| `10_successful_login.png` | Successful login state |
| `11_sidebar_full.png` | Full sidebar layout |
| `12_new_conversation.png` | New conversation created |
| `13_conversation_with_message.png` | Conversation with message |
| `14_multiple_conversations.png` | Multiple conversations list |
| `15_search_filter.png` | Search filtering |
| `16_context_menu.png` | Hover action icons |
