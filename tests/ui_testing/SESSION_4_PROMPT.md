# SESSION 4: MCP, Models & Edge Cases Testing

## Session Overview
Test MCP server management, model switching, context compaction behavior, error states, and cross-feature integration.

## Pre-Session Checklist
- Sessions 1-3 completed
- App running: `sudo systemctl status peanutchat`
- Ollama running with multiple models
- (Optional) MCP server available for testing

---

## AGENT 1: MCP Server Management
**Directory**: `tests/ui_testing/session4/agent1_mcp/`
**Focus**: MCP server list, add/remove, connect/disconnect

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MCP SERVER MANAGEMENT.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent1_mcp/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_mcp1_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MCP SECTION LOCATION
Read /static/index.html lines 468-492.
- Open Settings modal
- Scroll to MCP Servers section
- Screenshot full section
- Verify extension icon and title

B. EMPTY SERVER LIST
- Screenshot empty state (no servers)
- Verify description text about MCP

C. ADD SERVER BUTTON
Read /static/js/mcp.js for add flow.
- Find "Add MCP Server" button
- Screenshot button
- Click to open add modal

D. ADD SERVER MODAL
Read mcp.js for modal structure.
- Screenshot #mcp-add-modal
- Verify elements:
  * Title "Add MCP Server"
  * Server Name input (#mcp-server-name)
  * Command input (#mcp-server-command)
  * Arguments input (#mcp-server-args)
  * Helper text about MCP
  * Cancel button (#mcp-modal-cancel)
  * Add Server button (#mcp-modal-save)
  * Close button (#mcp-modal-close)

E. FORM PLACEHOLDERS
- Screenshot input placeholders:
  * "e.g., Filesystem, Database"
  * "e.g., npx, python, node"
  * "e.g., -y @modelcontextprotocol/server-filesystem /home/user"

F. CANCEL ADD MODAL
- Fill some fields
- Click Cancel
- Verify modal closes
- Reopen, verify fields cleared

G. ADD VALID SERVER
Read /app/services/mcp_client.py for allowed commands.
- Enter: Name: "Test Server", Command: "node", Args: ""
- Click Add Server
- Screenshot result
- Verify server appears in list

H. SERVER LIST ITEM
- Screenshot server list item
- Verify elements:
  * Connection status dot (green=connected, gray=disconnected)
  * Server name
  * Command display
  * Toggle button (play/stop icon)
  * Delete button (hover-only)

I. CONNECTION STATUS INDICATOR
- Screenshot disconnected state (gray dot)
- Click connect (play_arrow icon)
- Screenshot connecting state
- Screenshot connected state (green glowing dot)

J. TOGGLE CONNECTION
- If connected, click toggle (stop icon, red)
- Screenshot disconnecting
- Screenshot disconnected state
- Toggle back to connect
- Verify state changes

K. DELETE SERVER
- Hover over server item
- Screenshot delete button appearance
- Click delete
- Screenshot confirmation dialog
- Cancel first
- Then confirm delete
- Verify server removed from list

L. ADD INVALID COMMAND
Read mcp_client.py lines 23-47 for allowlist.
- Try adding server with command: "bash" (not allowed)
- Screenshot error response
- Try command: "rm" (not allowed)
- Document which commands are rejected

M. MULTIPLE SERVERS
- Add 3+ different servers
- Screenshot list with multiple items
- Verify scrolling (max-height: 48)
- Test individual connections

N. CONNECTION ERROR HANDLING
- Add server with bad command/args
- Try to connect
- Screenshot error state/message
- How does UI show connection failed?

O. MCP TOOLS (after connection)
Read /app/routers/mcp.py line 219-224.
- With server connected
- Check if tools appear anywhere
- Screenshot any tool listing

OUTPUT: Create findings.md with:
- MCP section element inventory
- Add server flow documentation
- Connection state management
- Error handling observations
- Command validation behavior
- Any bugs or missing features
```

---

## AGENT 2: Model Listing & Switching
**Directory**: `tests/ui_testing/session4/agent2_model_switch/`
**Focus**: Model dropdown, switching, capability updates

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MODEL SWITCHING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent2_model_switch/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_model2_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MODEL DROPDOWN INVENTORY
Read /static/js/app.js for model loading.
- Screenshot model dropdown (#model-select)
- Click to expand
- Screenshot all available models
- Document each model name

B. CURRENT MODEL INDICATOR
- Note which model shows as selected
- Screenshot green status dot
- Verify current model via GET /api/models/current

C. SWITCH TO DIFFERENT MODEL
- Select different model from dropdown
- Screenshot during switch
- Verify POST /api/models/select called
- Screenshot after switch complete
- Verify dropdown shows new selection

D. CAPABILITY UPDATES
Read /app/routers/models.py for capabilities.
- Note current model capabilities
- Switch to model with different capabilities
- Screenshot #model-capabilities changing
- Document which icons appear/disappear

E. TOOLS CAPABILITY
- Find model that supports tools
- Switch to it
- Verify #cap-tools (build icon) appears
- Screenshot green icon with tooltip

F. VISION CAPABILITY
- Find model that supports vision
- Switch to it
- Verify #cap-vision (visibility icon) appears
- Screenshot blue icon with tooltip

G. THINKING CAPABILITY
- Find model that supports thinking
- Switch to it
- Verify #cap-thinking (psychology icon) appears
- Screenshot purple icon with tooltip

H. NO CAPABILITIES
- Find model with no special capabilities
- Switch to it
- Verify all capability icons hidden
- Screenshot empty capabilities area

I. MODEL DURING CHAT
- Start streaming response
- Try to switch models
- Screenshot behavior
- Is dropdown disabled during stream?

J. MODEL PERSISTENCE
- Select specific model
- Refresh page
- Verify same model selected after reload
- Is it stored per-user?

K. ADULT MODE MODEL FILTERING
Read models.py lines 55-94.
- Without adult mode: count models
- Enable adult mode
- Recount models
- Screenshot difference
- Verify uncensored/nsfw models now visible

L. MODEL SWITCH DURING CONVERSATION
- Have active conversation with model A
- Switch to model B
- Send message
- Does response come from model B?
- Is there any indicator in UI?

M. OLLAMA CONNECTIVITY
- What happens if Ollama is down?
- Try to load models
- Screenshot error handling
- How does UI recover?

N. RAPID MODEL SWITCHING
- Switch models rapidly (click different models quickly)
- Screenshot any race conditions
- Verify final state is correct

OUTPUT: Create findings.md with:
- Model inventory
- Capability mapping per model
- Switch flow documentation
- Filtering behavior
- Persistence verification
- Error handling
- Any bugs or race conditions
```

---

## AGENT 3: Context Compaction Behavior
**Directory**: `tests/ui_testing/session4/agent3_compaction/`
**Focus**: Context gauge, compaction triggers, summarization

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is CONTEXT COMPACTION.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent3_compaction/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_compact3_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. CONTEXT GAUGE BASELINE
Read /static/index.html lines 268-283.
- Screenshot context gauge at conversation start
- Verify gauge elements:
  * Memory icon
  * Background bar (gray)
  * Fill bar (primary color)
  * Label showing percentage

B. GAUGE FILL PROGRESSION
- Send short message
- Screenshot gauge
- Send longer message
- Screenshot gauge increase
- Document fill rate estimation

C. LOW CONTEXT STATE
- New conversation
- Screenshot gauge at ~0-10%
- Label should show low percentage

D. MEDIUM CONTEXT STATE
- Build conversation to ~50%
- Screenshot gauge
- Observe fill animation (transition-all duration-300)

E. HIGH CONTEXT STATE
- Build conversation to ~70%+
- Screenshot gauge
- This should approach compaction threshold

F. COMPACTION SETTINGS VERIFY
Read /static/index.html lines 604-664.
- Open Settings
- Screenshot compaction settings
- Note current values:
  * Enabled: true/false
  * Buffer: default 15%
  * Threshold: default 70%
  * Protected messages: default 6

G. MANUAL THRESHOLD TEST
- Set threshold to 50%
- Save settings
- Build conversation until gauge hits 50%
- Screenshot when compaction triggers

H. COMPACTION IN ACTION
Read /app/services/compaction_service.py.
- When compaction triggers, observe:
  * Any status indicator?
  * How does conversation change?
  * Are old messages summarized?
- Screenshot before/after compaction

I. PROTECTED MESSAGES
- Set protected messages to minimum (4)
- Trigger compaction
- Verify most recent 4 messages preserved
- Screenshot message history

J. COMPACTION DISABLED
- Disable compaction toggle
- Build long conversation
- Verify gauge fills past threshold
- No compaction should trigger
- Screenshot at high fill level

K. SUMMARY BUFFER EFFECT
- Set buffer to max (30%)
- Trigger compaction
- Observe how much context freed
- Screenshot gauge after compaction

L. CONTEXT OVERFLOW
- Disable compaction
- Exceed context limit
- Screenshot any error/warning
- How does UI handle overflow?

M. VRAM GAUGE (if GPU)
- Screenshot VRAM gauge (#vram-gauge-container)
- If hidden, note no GPU detected
- If visible:
  * Observe during model usage
  * Screenshot fill levels

N. GAUGE ANIMATION
- Observe gauge transition effect
- Screenshot during fill change
- Verify smooth animation

OUTPUT: Create findings.md with:
- Context gauge behavior documentation
- Compaction trigger observation
- Threshold testing results
- Protected message verification
- Summary buffer effect
- Error handling for overflow
- Any bugs or unexpected behavior
```

---

## AGENT 4: Error States & Edge Cases
**Directory**: `tests/ui_testing/session4/agent4_errors/`
**Focus**: Error handling, edge cases, graceful degradation

### Prompt for Agent 4:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is ERROR STATES.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent4_errors/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_error4_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. NETWORK DISCONNECTION
- Send message
- Simulate network disconnect (dev tools)
- Screenshot error handling
- How does UI indicate failure?
- Any retry mechanism?

B. SERVER DOWN
- Stop peanutchat service
- Try to use app
- Screenshot error states
- Restart service
- Screenshot recovery

C. AUTHENTICATION EXPIRY
Read /static/js/auth.js for token refresh.
- Manually delete access_token cookie
- Try to send message
- Screenshot auth error
- Does it redirect to login?

D. INVALID API RESPONSES
- What if API returns 500?
- Screenshot error display
- Does UI show user-friendly message?

E. EMPTY STATE HANDLING
- New user, empty conversation list
- Screenshot empty state
- New user, no memories
- Screenshot empty memory state
- New user, no knowledge docs
- Screenshot empty KB state

F. VERY LONG INPUT
- Paste 10,000+ character message
- Screenshot textarea behavior
- Try to send
- Screenshot any truncation/error

G. SPECIAL CHARACTERS
- Send message with: <script>alert('xss')</script>
- Screenshot rendering (should be escaped)
- Send: ' OR 1=1 --
- Screenshot handling

H. RAPID INTERACTIONS
- Click send button repeatedly
- Screenshot behavior
- Does it prevent double-send?
- Click "New Chat" rapidly
- Screenshot any issues

I. CONCURRENT OPERATIONS
- Start file upload
- While uploading, try other operations
- Screenshot any conflicts

J. MODAL CONFLICTS
- Open settings modal
- Try to open another modal
- Screenshot behavior
- ESC key handling with multiple modals?

K. BROWSER BACK/FORWARD
- Navigate through conversations
- Use browser back button
- Screenshot behavior
- Does state preserve?

L. PAGE REFRESH DURING OPERATION
- Start streaming response
- Refresh page
- Screenshot state after refresh
- Is conversation preserved?

M. MOBILE VIEWPORT
- Set viewport to 375x667 (iPhone)
- Screenshot full app
- Test all major interactions
- Document responsive issues

N. ZOOM LEVELS
- Test at 50% zoom
- Test at 200% zoom
- Screenshot UI at extremes
- Note any overflow issues

O. KEYBOARD NAVIGATION
- Tab through all interactive elements
- Screenshot focus indicators
- Can you use app without mouse?
- Document accessibility gaps

P. CLIPBOARD OPERATIONS
- Test paste into textarea
- Test copy from messages
- Screenshot clipboard feedback

OUTPUT: Create findings.md with:
- Error state catalog with screenshots
- Edge case behaviors
- Recovery mechanisms
- Responsive design issues
- Accessibility gaps
- Security handling
- Recommendations
```

---

## AGENT 5: Cross-Feature Integration Testing
**Directory**: `tests/ui_testing/session4/agent5_integration/`
**Focus**: Feature interactions, end-to-end flows

### Prompt for Agent 5:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is INTEGRATION TESTING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent5_integration/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_integ5_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. COMPLETE USER JOURNEY
Document full flow with screenshots:
1. Fresh registration
2. First chat message
3. Configure profile
4. Upload knowledge document
5. Chat that uses KB search
6. View memories created
7. Change theme
8. Logout
9. Login again
10. Verify all state preserved

B. KNOWLEDGE + CHAT INTEGRATION
- Upload technical document
- Ask question about document content
- Screenshot response
- Verify KB was searched (tool indicator?)
- Does response reference document?

C. MEMORY + CHAT INTEGRATION
- Chat about preferences
- Wait for AI to learn
- Check memories created
- New conversation
- Chat referencing past preferences
- Screenshot memory being used

D. PROFILE + CHAT INTEGRATION
- Set communication style to "sarcastic_dry"
- Save settings
- Chat and observe response style
- Change to "empathetic_supportive"
- Compare responses
- Screenshot differences

E. THINKING + TOOLS INTEGRATION
- Enable thinking mode
- Ask question requiring web search
- Screenshot thinking + tool call display
- How do they interact visually?

F. MODEL SWITCH + CHAT CONTINUITY
- Have conversation with model A
- Note response style
- Switch to model B
- Continue conversation
- Screenshot any differences
- Is context preserved?

G. ADULT MODE + PROFILE FLOW
- Enable adult mode (passcode)
- Run full unlock onboarding
- Configure sensitive sections
- Verify chat behavior changes
- Screenshot differences

H. MCP + CHAT INTEGRATION
- Connect MCP server
- Chat to trigger MCP tool
- Screenshot tool execution
- How does UI show MCP tool results?

I. COMPACTION + CONVERSATION HISTORY
- Build long conversation
- Trigger compaction
- Scroll back in history
- How do summarized messages appear?
- Screenshot before/after

J. MULTI-FEATURE STRESS TEST
Simultaneously active:
- Streaming response
- File attachment
- Thinking mode
- Screenshot complex state
- Any performance issues?

K. SETTINGS SAVE VERIFICATION
Change all settings:
- Profile fields
- Theme
- Persona
- Model parameters
- Compaction settings
Save and verify each persists

L. CONVERSATION FORK + EDIT TREE
- Create conversation A
- Fork at message 3 → conversation B
- Edit message 2 in B
- Verify A unaffected
- Screenshot conversation list

M. SESSION BOUNDARIES
- Login session A
- Open new tab
- Verify session handling
- Both tabs functional?
- State synchronization?

N. EXPORT/IMPORT CYCLE
- Populate profile
- Export profile
- Reset profile
- Verify reset
- (Import if available)
- Screenshot each step

O. FULL APP TOUR
Create comprehensive screenshot tour:
1. Landing/Auth screen
2. Empty dashboard
3. Active conversation
4. Settings modal (each section)
5. Profile section
6. Knowledge section
7. Memory section
8. MCP section
9. Each theme
10. Error states

OUTPUT: Create findings.md with:
- User journey documentation
- Integration point analysis
- Cross-feature bugs
- State management observations
- Performance notes
- Comprehensive screenshot catalog
```

---

## Session 4 Execution Command

```
I need you to run 5 UI testing agents in parallel for PeanutChat Session 4.

Create the test directory structure first, then spawn these 5 agents simultaneously:

1. Agent 1 - MCP server management (add/remove, connect/disconnect)
2. Agent 2 - Model listing & switching (dropdown, capabilities)
3. Agent 3 - Context compaction behavior (gauge, triggers, summarization)
4. Agent 4 - Error states & edge cases (error handling, graceful degradation)
5. Agent 5 - Cross-feature integration testing (end-to-end flows)

Each agent should:
- Create unique test user
- Use Playwright + Chromium
- Screenshot EVERY interaction
- Read source code to understand expected behavior
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes

The app is running at http://localhost:8080
```
