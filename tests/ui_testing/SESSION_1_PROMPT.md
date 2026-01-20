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

## IMPORTANT: Parallel Execution Instructions
Run ALL 5 agents in parallel using a SINGLE message with 5 Task tool calls.
Each agent creates its own test user to avoid conflicts.

---

## AGENT 1: Authentication Flows
**Directory**: `tests/ui_testing/session1/agent1_auth/`
**Focus**: Login, Register, Logout, Session Handling

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is AUTHENTICATION.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent1_auth/
2. Install playwright if needed: pip install playwright && playwright install chromium
3. App URL: http://localhost:8000

INVESTIGATION TASKS - Screenshot everything:

A. REGISTRATION FLOW
Read /static/js/auth.js and /static/index.html (lines 725-781) to understand expected behavior.
- Screenshot the auth modal on page load (#auth-modal)
- Test "Create Account" tab navigation
- Verify form fields exist: #register-username, #register-email, #register-password, #register-confirm
- Test client-side validation:
  * Username < 3 chars should show error in #register-error
  * Password < 6 chars should show error
  * Password mismatch should show error
- Screenshot each validation error state
- Test successful registration with unique user (testuser_auth1_{timestamp})
- Screenshot the post-login state (modal should close, sidebar shows username)

B. LOGIN FLOW
- Logout first
- Screenshot login form (#login-username, #login-password)
- Test empty field validation
- Test wrong credentials (should show error in #auth-error)
- Screenshot error state (red background styling)
- Test successful login
- Verify #user-info shows with correct username

C. SESSION HANDLING
Read /static/js/auth.js lines 11-46 for session marker logic.
- Verify sessionStorage has 'peanutchat_session_active' after login
- Open new tab (simulate) - code says new tabs should require re-login
- Screenshot the new tab behavior
- Test logout clears session marker

D. LOGOUT FLOW
- Find #logout-btn in sidebar
- Screenshot before logout (user info visible)
- Click logout
- Screenshot after logout (auth modal should reappear)
- Verify cookie is cleared

E. UI ELEMENT VERIFICATION
Compare index.html elements against what appears in screenshots:
- Auth modal styling matches CSS (bg-background-dark, rounded-2xl)
- Tab underline indicator on active tab
- Error message red styling (bg-red-500/20, border-red-500/50)
- Button hover states

OUTPUT: Create findings.md with:
- All screenshots with descriptions
- Code expectation vs actual behavior
- Any discrepancies found
- Element IDs that exist in code but not in UI or vice versa
```

---

## AGENT 2: Sidebar & Conversation Management
**Directory**: `tests/ui_testing/session1/agent2_sidebar/`
**Focus**: Sidebar navigation, conversation list, search

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is SIDEBAR & CONVERSATIONS.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent2_sidebar/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_sidebar2_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. SIDEBAR STRUCTURE
Read /static/index.html lines 155-230 for sidebar HTML structure.
- Screenshot full sidebar layout
- Verify elements exist:
  * Logo "PeanutChat" at top
  * "New Chat" button (#new-chat-btn)
  * Search bar with clear button
  * Conversation list (#conversation-list)
  * User info section (#user-info)
  * Settings button (#settings-btn)
  * Logout button (#logout-btn)

B. NEW CHAT FUNCTIONALITY
- Screenshot empty state
- Click "New Chat" button
- Screenshot result (should create new conversation)
- Verify conversation appears in list
- Check title defaults to "New Chat"

C. CONVERSATION LIST
Read /static/js/app.js for conversation loading logic.
- Create 3+ conversations by sending messages
- Screenshot conversation list with multiple items
- Verify each shows: title, timestamp
- Test conversation selection (click to switch)
- Screenshot active vs inactive conversation styling

D. SEARCH FUNCTIONALITY
- Screenshot search input
- Enter search term matching one conversation
- Screenshot filtered results
- Test clear button (X) functionality
- Verify search is real-time filtering

E. CONVERSATION CONTEXT MENU
Read index.html for rename/delete functionality.
- Right-click or find context menu trigger
- Screenshot context menu if exists
- Test rename functionality (#rename-modal)
- Screenshot rename modal (input, cancel, save buttons)
- Test delete with confirmation

F. RESPONSIVE BEHAVIOR
- Resize viewport to mobile width (< 768px)
- Screenshot sidebar behavior
- Check if sidebar collapses or overlays

OUTPUT: Create findings.md with:
- All screenshots with descriptions
- Sidebar element inventory (what's in code vs what's visible)
- Interaction flows documented
- Any missing or broken elements
```

---

## AGENT 3: Theme Switching & Visual Appearance
**Directory**: `tests/ui_testing/session1/agent3_themes/`
**Focus**: Theme system, visual consistency, CSS variables

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is THEMES & VISUALS.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent3_themes/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_theme3_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. THEME BUTTON DISCOVERY
Read /static/index.html lines 399-420 for theme selector HTML.
- Open Settings modal
- Screenshot theme selector section
- Verify 4 theme buttons exist: dark, light, midnight, forest
- Each has data-theme attribute
- Verify gradient preview boxes

B. DEFAULT DARK THEME
Read /static/css/styles.css for CSS variable definitions.
- Screenshot default dark theme state
- Capture:
  * Header/nav colors
  * Sidebar background
  * Chat area background
  * Button colors
  * Text colors
- Document CSS variables in use (--color-background, --color-surface, etc.)

C. LIGHT THEME TESTING
- Click light theme button
- Screenshot FULL page in light theme
- Verify class changes (removes 'dark' from html element)
- Compare all major areas for contrast/readability
- Check text visibility

D. MIDNIGHT THEME TESTING
- Click midnight theme button
- Screenshot FULL page
- Verify data-theme="midnight" applied
- Document color differences from dark

E. FOREST THEME TESTING
- Click forest theme button
- Screenshot FULL page
- Verify data-theme="forest" applied
- Document green-tinted styling

F. THEME PERSISTENCE
- Set theme to forest
- Close settings
- Refresh page
- Screenshot after refresh
- Verify theme persisted in localStorage
- Read localStorage.getItem('theme')

G. ACTIVE THEME INDICATOR
- Screenshot each theme button's active state
- Verify active shows: border-primary + bg-primary/10 styling
- Test rapid switching between themes

H. VISUAL CONSISTENCY CHECK
For each theme, verify:
- Modal backgrounds match theme
- Input field styling
- Button states (hover, active, disabled)
- Scrollbar styling
- Icon colors

OUTPUT: Create findings.md with:
- Screenshot comparison table (4 themes x key areas)
- CSS variable mapping per theme
- Any visual bugs or inconsistencies
- Contrast/accessibility observations
```

---

## AGENT 4: Settings Modal Navigation & Structure
**Directory**: `tests/ui_testing/session1/agent4_settings/`
**Focus**: Settings modal sections, navigation, form structure

### Prompt for Agent 4:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is SETTINGS MODAL.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent4_settings/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_settings4_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MODAL OPEN/CLOSE
Read /static/js/settings.js for modal behavior.
- Screenshot settings button (#settings-btn)
- Click to open modal
- Screenshot full modal (#settings-modal)
- Test close via X button (#close-settings)
- Test close via clicking outside modal (backdrop)
- Test close via Escape key

B. SECTION INVENTORY
Read /static/index.html lines 375-674 for all sections.
Verify these sections exist and screenshot each:
1. User Profile (#profile-section)
2. Theme Selector
3. Persona Input (#persona-input)
4. Knowledge Base (#kb-upload-area)
5. MCP Servers (#mcp-servers)
6. Memory Section
7. Model Parameters (sliders)
8. Context Compaction Settings

C. SECTION HEADERS & ICONS
- Screenshot each section header
- Verify Material Symbols icons render correctly
- Check section descriptions are visible

D. PERSONA INPUT
- Screenshot persona textarea
- Verify placeholder text
- Enter test persona
- Screenshot with content
- Check character handling (special chars, long text)

E. KNOWLEDGE BASE SECTION
- Screenshot upload area (dashed border)
- Verify document count (#kb-doc-count) display
- Verify chunk count (#kb-chunk-count) display
- Screenshot document list container

F. MCP SERVERS SECTION
- Screenshot server list area
- Verify "Add MCP Server" button visible
- Screenshot empty state message if no servers

G. MEMORY SECTION
- Screenshot memory stats
- Verify memory count (#memory-count) display
- Verify category count (#memory-categories)
- Test expandable "View all memories" details element
- Screenshot expanded state

H. MODEL PARAMETERS SECTION
Verify all sliders exist (read index.html lines 537-601):
- Temperature (#temperature) - range 0-2, step 0.1
- Top P (#top-p) - range 0-1, step 0.05
- Top K (#top-k) - range 1-100, step 1
- Context Length (#num-ctx) - range 1024-32768, step 1024
- Repeat Penalty (#repeat-penalty) - range 1-2, step 0.1
Screenshot each slider with value display

I. CONTEXT COMPACTION SECTION
Read index.html lines 604-664.
- Screenshot compaction settings
- Verify toggle (#compaction-enabled)
- Test toggle enables/disables child settings
- Screenshot disabled state (opacity change)

J. SAVE BUTTON
- Screenshot sticky save button (#save-settings)
- Verify it's at bottom of modal
- Test click behavior (should call settings API)

OUTPUT: Create findings.md with:
- Complete section inventory with screenshots
- Missing elements (code says exist, UI doesn't show)
- Extra elements (UI shows, not in code)
- Form field validation behaviors
```

---

## AGENT 5: Model Selector & Capability Indicators
**Directory**: `tests/ui_testing/session1/agent5_models/`
**Focus**: Model dropdown, capability icons, usage gauges

### Prompt for Agent 5:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MODEL SELECTOR & GAUGES.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session1/agent5_models/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_models5_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MODEL SELECTOR LOCATION
Read /static/index.html lines 246-264 for header structure.
- Screenshot header area
- Locate model selector dropdown (#model-select)
- Verify green status dot indicator
- Screenshot dropdown in closed state

B. DROPDOWN CONTENTS
Read /static/js/app.js for model loading logic.
- Click to open dropdown
- Screenshot all available models
- Note which models are listed
- Check for adult/uncensored model filtering (should be hidden by default)

C. MODEL SWITCHING
- Select a different model
- Screenshot dropdown with new selection
- Verify UI updates (capability icons change)
- Check API call made (POST /api/models/select)

D. CAPABILITY INDICATORS
Read index.html lines 255-261 for capability icons.
- Screenshot #model-capabilities container
- Test models with different capabilities:
  * Find model with tools support (#cap-tools - build icon, green)
  * Find model with vision support (#cap-vision - visibility icon, blue)
  * Find model with thinking support (#cap-thinking - psychology icon, purple)
- Screenshot each capability state
- Verify icons have correct tooltips

E. CONTEXT GAUGE
Read index.html lines 268-283 for context gauge.
- Screenshot context window gauge (#context-gauge)
- Verify gauge components:
  * Memory icon
  * Background bar (gray-700)
  * Fill bar (primary color)
  * Label showing percentage (#context-label)
- Send messages to see gauge fill
- Screenshot gauge at different fill levels

F. VRAM GAUGE
Read index.html lines 285-301 for VRAM gauge.
- Screenshot VRAM gauge container (#vram-gauge-container)
- Note: Only visible if GPU detected
- If visible:
  * Verify developer_board icon
  * Check fill bar (#vram-gauge)
  * Check label (#vram-label)
- If hidden, document why (no GPU)

G. CAPABILITY ICON TOOLTIPS
- Hover each capability icon
- Screenshot tooltip displays
- Verify tooltip text matches:
  * Tools: "Tools available (web search, knowledge base)"
  * Vision: "Vision capable (can analyze images)"
  * Thinking: "Extended thinking mode"

H. MODEL FILTERING TEST
Read /app/routers/models.py lines 55-94 for filtering logic.
- Screenshot model list in normal mode
- Note any models containing: uncensored, abliterated, nsfw, adult, xxx
- If none visible, that's expected (adult_mode=false filter)

I. GAUGE ANIMATION
- Trigger context usage change (send long message)
- Observe gauge animation
- Verify transition (duration-300 class)
- Screenshot before/after states

OUTPUT: Create findings.md with:
- Model selector element inventory
- Capability indicator states documented
- Gauge behavior documentation
- Model filtering observations
- Any UI bugs or inconsistencies
```

---

## Session 1 Execution Command

In your Claude Code session, execute this to run all 5 agents in parallel:

```
I need you to run 5 UI testing agents in parallel for PeanutChat Session 1.

Create the test directory structure first, then spawn these 5 agents simultaneously using the Task tool:

1. Agent 1 - Authentication testing (auth flows, login/register/logout)
2. Agent 2 - Sidebar & conversation management testing
3. Agent 3 - Theme switching & visual appearance testing
4. Agent 4 - Settings modal structure testing
5. Agent 5 - Model selector & capability indicators testing

Each agent should:
- Create unique test user with pattern: testuser_{area}_{agent_num}_{timestamp}
- Use Playwright + Chromium
- Take screenshots of EVERY interaction
- Read the source code to understand expected behavior
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes

The app is running at http://localhost:8000
```
