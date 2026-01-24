# SESSION 4: MCP, Models & Edge Cases Testing

## Session Overview
Test MCP server management, model switching, error states, and cross-feature integration.

## Pre-Session Checklist
- Sessions 1-3 completed
- App running: `sudo systemctl status peanutchat`
- Ollama running with multiple models
- (Optional) MCP server available for testing

## IMPORTANT: Timeout Configuration
All agents MUST configure these timeouts for LLM response handling:
```python
page.set_default_timeout(300000)  # 5 minutes for LLM responses
page.set_default_navigation_timeout(120000)  # 2 minutes for page loads
```

---

## AGENT 1: MCP Servers & Model Switching
**Directory**: `tests/ui_testing/session4/agent1_mcp_models/`
**Focus**: MCP server management, model dropdown, capabilities

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MCP & MODEL SWITCHING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent1_mcp_models/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_mcp1_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. MCP SECTION
Read /static/index.html lines 468-492.
- Open Settings modal
- Screenshot MCP Servers section (#mcp-servers)
- Screenshot empty state

B. ADD MCP SERVER
Read /static/js/mcp.js for add flow.
- Click "Add MCP Server" button
- Screenshot modal (#mcp-add-modal)
- Verify: Name input, Command input, Args input
- Test Cancel closes modal

C. ADD VALID SERVER
Read /app/services/mcp_client.py for allowed commands.
- Enter: Name "Test", Command "node", Args ""
- Click Add Server
- Screenshot server in list

D. SERVER LIST ITEM
- Screenshot: Status dot, Name, Command, Toggle, Delete
- Test toggle connect/disconnect
- Screenshot connected (green) vs disconnected (gray) states

E. DELETE SERVER
- Hover over server, screenshot delete button
- Click delete, screenshot confirmation
- Confirm, verify removed

F. INVALID COMMAND
Read mcp_client.py lines 23-47 for allowlist.
- Try command "bash" (not allowed)
- Screenshot error

G. MODEL DROPDOWN
Read /static/js/app.js for model loading.
- Screenshot model selector (#model-select)
- Click to expand, screenshot all models
- Note model count

H. MODEL SWITCHING
- Select different model
- Screenshot capability icons update
- Wait for any API calls (up to 5 min)
- Verify POST /api/models/select

I. CAPABILITY ICONS
- Test model with tools (#cap-tools green)
- Test model with vision (#cap-vision blue)
- Test model with thinking (#cap-thinking purple)
- Screenshot each capability state

J. ADULT MODE FILTERING
- Count models without adult mode
- Enable adult mode (passcode 6060)
- Recount models
- Screenshot difference

K. RAPID SWITCHING
- Switch models quickly
- Screenshot any race conditions
- Verify final state correct

OUTPUT: Create findings.md with MCP and model switching documentation.
```

---

## AGENT 2: Error States & Edge Cases
**Directory**: `tests/ui_testing/session4/agent2_errors_edge/`
**Focus**: Error handling, edge cases, graceful degradation

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is ERROR STATES.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent2_errors_edge/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_error2_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. NETWORK DISCONNECTION
- Send message
- Simulate network disconnect (dev tools)
- Screenshot error handling
- How does UI indicate failure?

B. AUTHENTICATION EXPIRY
Read /static/js/auth.js for token refresh.
- Delete access_token cookie
- Try to send message
- Screenshot auth error
- Does it redirect to login?

C. EMPTY STATES
- New user: screenshot empty conversation list
- Screenshot empty memory state
- Screenshot empty KB state

D. VERY LONG INPUT
- Paste 10,000+ character message
- Screenshot textarea behavior
- Send, screenshot any truncation/error

E. XSS ATTEMPT
- Send: <script>alert('xss')</script>
- Screenshot rendering (should be escaped)
- Verify safe handling

F. RAPID INTERACTIONS
- Click send button repeatedly
- Screenshot double-send prevention
- Click "New Chat" rapidly
- Screenshot any issues

G. MODAL CONFLICTS
- Open settings modal
- Try to open another modal
- Screenshot behavior
- Test ESC key handling

H. MOBILE VIEWPORT
- Set viewport to 375x667 (iPhone)
- Screenshot full app
- Test major interactions
- Document responsive issues

I. KEYBOARD NAVIGATION
- Tab through all interactive elements
- Screenshot focus indicators
- Document accessibility gaps

J. CLIPBOARD OPERATIONS
- Test paste into textarea
- Test copy from messages
- Screenshot clipboard feedback

K. PAGE REFRESH DURING STREAM
- Start streaming response
- Refresh page
- Screenshot state after refresh
- Is conversation preserved?

OUTPUT: Create findings.md with error states and edge case documentation.
```

---

## AGENT 3: Integration Testing
**Directory**: `tests/ui_testing/session4/agent3_integration/`
**Focus**: Cross-feature interactions, end-to-end flows

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is INTEGRATION TESTING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session4/agent3_integration/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_integ3_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. COMPLETE USER JOURNEY
Document full flow:
1. Fresh registration
2. First chat message (wait up to 5 min)
3. Configure profile
4. Upload knowledge document
5. Chat that uses KB (wait up to 5 min)
6. View memories created
7. Change theme
8. Logout
9. Login again
10. Verify all state preserved

B. KNOWLEDGE + CHAT
- Upload technical document
- Ask question about content (wait up to 5 min)
- Screenshot response
- Verify KB was searched

C. MEMORY + CHAT
- Chat about preferences (wait up to 5 min)
- Check memories created
- New conversation
- Chat referencing preferences (wait up to 5 min)
- Screenshot memory being used

D. PROFILE + CHAT
- Set communication style to "sarcastic_dry"
- Save, chat (wait up to 5 min)
- Change to "empathetic_supportive"
- Compare responses

E. THINKING + TOOLS
- Enable thinking mode
- Ask question requiring tools (wait up to 5 min)
- Screenshot thinking + tool display

F. MODEL SWITCH + CONTINUITY
- Conversation with model A
- Switch to model B
- Continue conversation (wait up to 5 min)
- Screenshot differences

G. COMPACTION + HISTORY
- Set low threshold (50%)
- Build long conversation (multiple waits, up to 5 min each)
- Observe compaction
- Screenshot before/after

H. SETTINGS PERSISTENCE
Change all settings:
- Profile, Theme, Persona, Parameters, Compaction
- Save, refresh
- Verify each persists

I. CONVERSATION FORK
- Create conversation A
- Fork at message 3
- Edit in fork
- Verify A unaffected
- Screenshot conversation list

J. FULL APP TOUR
Screenshot comprehensive tour:
1. Auth screen
2. Empty dashboard
3. Active conversation
4. Settings modal (each section)
5. Each theme
6. Error states

OUTPUT: Create findings.md with integration test documentation and screenshot catalog.
```

---

## Session 4 Execution Command

```
I need you to run 3 UI testing agents in parallel for PeanutChat Session 4.

Create the test directory structure first, then spawn these 3 agents simultaneously:

1. Agent 1 - MCP Servers & Model Switching (MCP management, model dropdown)
2. Agent 2 - Error States & Edge Cases (error handling, accessibility)
3. Agent 3 - Integration Testing (end-to-end flows, cross-feature)

Each agent should:
- Create unique test user
- Use Playwright + Chromium
- Set page.set_default_timeout(300000) for LLM responses
- Set page.set_default_navigation_timeout(120000) for page loads
- Screenshot EVERY interaction
- Wait for LLM responses to complete before next action (up to 5 min)
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes

The app is running at http://localhost:8000
```
