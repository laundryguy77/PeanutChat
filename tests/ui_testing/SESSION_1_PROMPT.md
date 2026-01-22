# SESSION 1: Foundation & Navigation Testing

## Session Overview
Test the foundational UI elements: authentication, navigation, visual themes, settings modal structure, and model indicators.

## Pre-Session Setup
```bash
# Ensure app is running
sudo systemctl status peanutchat
# Start if needed
sudo systemctl start peanutchat
```

## IMPORTANT: Timeout Configuration
All agents MUST configure these timeouts for LLM response handling:
```python
page.set_default_timeout(300000)  # 5 minutes for LLM responses
page.set_default_navigation_timeout(120000)  # 2 minutes for page loads
```

## IMPORTANT: Parallel Execution Instructions
Run ALL 3 agents in parallel using a SINGLE message with 3 Task tool calls.
Each agent creates its own test user to avoid conflicts.

---

## AGENT 1: Authentication & Sidebar
**Directory**: `tests/ui_testing/session1/agent1_auth_sidebar/`
**Focus**: Login, Register, Logout, Session Handling, Sidebar Navigation

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is AUTHENTICATION & SIDEBAR.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent1_auth_sidebar/
2. Install playwright if needed: pip install playwright && playwright install chromium
3. App URL: http://localhost:8000
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. REGISTRATION FLOW
Read /static/js/auth.js and /static/index.html (lines 725-781) to understand expected behavior.
- Screenshot the auth modal on page load (#auth-modal)
- Test "Create Account" tab navigation
- Verify form fields exist: #register-username, #register-email, #register-password, #register-confirm
- Test client-side validation (username < 3 chars, password < 6 chars, mismatch)
- Screenshot each validation error state
- Test successful registration with unique user (testuser_auth1_{timestamp})
- Screenshot the post-login state

B. LOGIN FLOW
- Logout first, screenshot login form
- Test empty field validation, wrong credentials
- Screenshot error states (red background styling)
- Test successful login, verify #user-info shows username

C. SESSION HANDLING
Read /static/js/auth.js lines 11-46 for session marker logic.
- Verify sessionStorage has 'peanutchat_session_active' after login
- Test new tab behavior (should require re-login)
- Test logout clears session marker

D. LOGOUT FLOW
- Find #logout-btn in sidebar
- Screenshot before/after logout
- Verify cookie is cleared, auth modal reappears

E. SIDEBAR STRUCTURE
Read /static/index.html lines 155-230 for sidebar HTML structure.
- Screenshot full sidebar layout
- Verify elements: Logo, New Chat button, Search bar, Conversation list, User info, Settings/Logout buttons

F. CONVERSATION MANAGEMENT
- Test New Chat button creates conversation
- Create 3+ conversations, screenshot list
- Test conversation selection, search filtering
- Test rename modal (#rename-modal), delete confirmation

G. RESPONSIVE BEHAVIOR
- Resize viewport to mobile width (< 768px)
- Screenshot sidebar behavior

OUTPUT: Create findings.md with all screenshots and observations.
```

---

## AGENT 2: Themes & Settings Modal
**Directory**: `tests/ui_testing/session1/agent2_themes_settings/`
**Focus**: Theme switching, Settings modal structure and navigation

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is THEMES & SETTINGS.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent2_themes_settings/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_themes2_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. THEME BUTTON DISCOVERY
Read /static/index.html lines 399-420 for theme selector HTML.
- Open Settings modal
- Screenshot theme selector section
- Verify 4 theme buttons: dark, light, midnight, forest
- Each has data-theme attribute and gradient preview

B. THEME TESTING (ALL 4)
Read /static/css/styles.css for CSS variable definitions.
For EACH theme:
- Click theme button
- Screenshot FULL page
- Document colors: Header, Sidebar, Chat area, Buttons, Text
- Verify data-theme attribute applied

C. THEME PERSISTENCE
- Set theme to forest
- Refresh page
- Screenshot after refresh
- Verify theme persisted in localStorage

D. ACTIVE THEME INDICATOR
- Screenshot each theme button's active state
- Verify active shows: border-primary + bg-primary/10 styling

E. SETTINGS MODAL OPEN/CLOSE
Read /static/js/settings.js for modal behavior.
- Click #settings-btn, screenshot modal
- Test close via X button (#close-settings)
- Test close via backdrop click
- Test close via Escape key

F. SECTION INVENTORY
Read /static/index.html lines 375-674 for all sections.
Screenshot and verify these 8 sections exist:
1. User Profile (#profile-section)
2. Theme Selector
3. Persona Input (#persona-input)
4. Knowledge Base (#kb-upload-area)
5. MCP Servers (#mcp-servers)
6. Memory Section
7. Model Parameters (sliders)
8. Context Compaction Settings

G. FORM FIELDS & SAVE
- Screenshot each section's form fields
- Test persona textarea input
- Test Save button (#save-settings) behavior

OUTPUT: Create findings.md with theme comparison screenshots and section inventory.
```

---

## AGENT 3: Models & Capability Gauges
**Directory**: `tests/ui_testing/session1/agent3_models_gauges/`
**Focus**: Model selector, capability icons, usage gauges

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MODELS & GAUGES.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent3_models_gauges/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_models3_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. MODEL SELECTOR LOCATION
Read /static/index.html lines 246-264 for header structure.
- Screenshot header area
- Locate model selector dropdown (#model-select)
- Verify green status dot indicator
- Screenshot dropdown closed state

B. DROPDOWN CONTENTS
Read /static/js/app.js for model loading logic.
- Click to open dropdown
- Screenshot all available models
- Note which models are listed
- Check for adult/uncensored model filtering (hidden by default)

C. MODEL SWITCHING
- Select a different model
- Screenshot new selection
- Verify capability icons update
- Note: Wait for any LLM calls to complete (up to 5 min timeout)

D. CAPABILITY INDICATORS
Read index.html lines 255-261 for capability icons.
- Screenshot #model-capabilities container
- Test models with different capabilities:
  * #cap-tools (build icon, green) - tools support
  * #cap-vision (visibility icon, blue) - vision support
  * #cap-thinking (psychology icon, purple) - thinking support
- Screenshot each capability state
- Verify tooltips on hover

E. CONTEXT GAUGE
Read index.html lines 268-283 for context gauge.
- Screenshot context gauge (#context-gauge)
- Verify components: Memory icon, Background bar, Fill bar, Label
- Send messages to see gauge fill (wait for responses)
- Screenshot gauge at different fill levels

F. VRAM GAUGE
Read index.html lines 285-301 for VRAM gauge.
- Screenshot VRAM gauge container (#vram-gauge-container)
- Note: Only visible if GPU detected
- If visible: Verify icon, fill bar, label
- If hidden: Document why

G. GAUGE ANIMATION
- Trigger context usage change (send message, wait for response)
- Observe gauge animation (transition duration-300)
- Screenshot before/after states

OUTPUT: Create findings.md with model inventory, capability states, and gauge documentation.
```

---

## Session 1 Execution Command

In your Claude Code session, execute this to run all 3 agents in parallel:

```
I need you to run 3 UI testing agents in parallel for PeanutChat Session 1.

Create the test directory structure first, then spawn these 3 agents simultaneously using the Task tool:

1. Agent 1 - Authentication & Sidebar testing (auth flows, sidebar navigation)
2. Agent 2 - Themes & Settings Modal testing (4 themes, 8 sections)
3. Agent 3 - Models & Capability Gauges testing (model selector, gauges)

Each agent should:
- Create unique test user with pattern: testuser_{area}_{agent_num}_{timestamp}
- Use Playwright + Chromium
- Set page.set_default_timeout(300000) for LLM responses
- Set page.set_default_navigation_timeout(120000) for page loads
- Take screenshots of EVERY interaction
- Read the source code to understand expected behavior
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes
- Wait for LLM responses before sending new messages

The app is running at http://localhost:8000
```
