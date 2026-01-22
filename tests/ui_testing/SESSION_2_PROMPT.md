# SESSION 2: Core Chat Features Testing

## Session Overview
Test the chat interface: messaging, streaming, message manipulation, file attachments, and thinking mode.

## Pre-Session Checklist
- Session 1 completed
- App running: `sudo systemctl status peanutchat`
- Ollama running with at least one model

## IMPORTANT: Timeout Configuration
All agents MUST configure these timeouts for LLM response handling:
```python
page.set_default_timeout(300000)  # 5 minutes for LLM responses
page.set_default_navigation_timeout(120000)  # 2 minutes for page loads
```

---

## AGENT 1: Messaging & Streaming
**Directory**: `tests/ui_testing/session2/agent1_messaging_streaming/`
**Focus**: Input area, message display, streaming responses

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MESSAGING & STREAMING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent1_messaging_streaming/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_msg1_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. INPUT AREA STRUCTURE
Read /static/index.html lines 305-360 for input structure.
- Screenshot input area (#input-container)
- Verify: Tools button (#tools-btn), Message textarea (#message-input), Send button (#send-btn)
- Screenshot placeholder text

B. TEXTAREA BEHAVIOR
Read /static/js/chat.js for textarea handling.
- Type short message, screenshot
- Type multiline message (Shift+Enter), screenshot
- Test auto-resize (min 48px, max 200px)
- Very long message scrolling test

C. SEND BUTTON STATES
- Screenshot default, enabled (with text), disabled (empty), loading states
- Click send, observe loading state

D. MESSAGE DISPLAY
- Send message, wait for response (up to 5 min)
- Screenshot user message bubble (blue, right-aligned)
- Screenshot assistant message (gray, left-aligned, AI badge)
- Verify message actions (copy, edit on user, regenerate on assistant)

E. MARKDOWN RENDERING
Test each element (wait for response each time):
- **Bold**, *Italic*, `inline code`
- Code blocks with syntax highlighting
- Bullet lists, Numbered lists
- Headers, Links, Tables, Blockquotes
- Screenshot each rendered element

F. STREAMING INDICATORS
- Send message requesting long response
- Screenshot IMMEDIATELY when streaming starts
- Capture typing indicator, token-by-token rendering
- Screenshot at intervals during stream
- Screenshot completion (indicator disappears, actions appear)

G. STREAMING BEHAVIOR
- Test send button disabled during stream
- Test scroll keeps up with content
- If possible, test interruption mid-stream

OUTPUT: Create findings.md with message rendering and streaming documentation.
```

---

## AGENT 2: Edit, Fork & Regenerate
**Directory**: `tests/ui_testing/session2/agent2_edit_fork_regen/`
**Focus**: Message editing, conversation forking, response regeneration

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MESSAGE MANIPULATION.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent2_edit_fork_regen/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_edit2_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. EDIT BUTTON DISCOVERY
Read /static/js/chat.js for edit functionality.
- Send message, wait for response
- Hover over USER message, screenshot edit button
- Verify edit button ONLY on user messages (not assistant)

B. EDIT MODAL
Read /static/index.html lines 685-710 for edit modal.
- Click edit button
- Screenshot edit modal (#edit-modal)
- Verify: Textarea with content, Radio buttons (Edit in place/Fork), Cancel, Save

C. EDIT IN-PLACE FLOW
- Select "Edit in place"
- Modify message text
- Click Save, wait for new response (up to 5 min)
- Screenshot result - original updated, subsequent regenerated

D. FORK CONVERSATION FLOW
- Build conversation with 3+ messages
- Edit middle message, select "Fork conversation"
- Save, screenshot result
- Verify: New conversation created, check conversation list

E. REGENERATE BUTTON
- Find regenerate button on ASSISTANT message
- Screenshot button location
- Click, wait for regeneration (up to 5 min)
- Screenshot: Old replaced with new

F. REGENERATE VARIATIONS
- Test on latest message
- Test on older message in conversation
- Screenshot each behavior

G. CANCEL OPERATIONS
- Open edit modal, make changes, Cancel
- Screenshot: Original unchanged
- Start regenerate, try to cancel

H. VALIDATION
- Try empty edit
- Try very long edit (10000+ chars)
- Screenshot any errors

OUTPUT: Create findings.md with edit/fork/regenerate flow documentation.
```

---

## AGENT 3: Attachments & Thinking Mode
**Directory**: `tests/ui_testing/session2/agent3_attachments_thinking/`
**Focus**: File uploads, image attachments, thinking mode toggle

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is ATTACHMENTS & THINKING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent3_attachments_thinking/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_attach3_{timestamp}
4. Create test files: test_image.png (small image), test_doc.txt (text), test_code.py (Python)
5. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. TOOLS MENU
Read /static/index.html lines 316-340 for tools menu.
- Screenshot tools button (#tools-btn)
- Click to open menu (#tools-menu)
- Screenshot: "Add files" option, "Thinking mode" checkbox

B. FILE/IMAGE INPUTS
- Locate #image-upload (accept="image/*")
- Locate #file-upload (multiple types)
- Document accepted file types

C. IMAGE UPLOAD
- Upload test_image.png
- Screenshot preview in #image-previews
- Verify: Thumbnail, Remove button (X)

D. FILE UPLOAD
- Upload test_doc.txt
- Screenshot badge in #file-previews
- Verify: File icon, Filename, Close button
- Test code file icon accuracy

E. MULTIPLE ATTACHMENTS
- Attach 3+ files
- Screenshot grid layout
- Test removing individual files

F. SEND WITH ATTACHMENTS
- Attach file + type message
- Send, wait for response (up to 5 min)
- Screenshot how attachments appear in message

G. THINKING MODE TOGGLE
Read /static/js/chat.js for thinking display.
- Open tools menu
- Screenshot thinking checkbox (#thinking-checkbox)
- Enable, screenshot indicator
- Disable, verify indicator gone

H. THINKING IN ACTION
- Enable thinking mode
- Send complex question
- Screenshot DURING thinking: spinning icon, "Thinking...", collapsible details
- Screenshot thought process content

I. THINKING COLLAPSE
Read /static/js/chat.js for auto-collapse.
- During thinking: expanded
- After complete: auto-collapse
- Screenshot both states
- Test manual expand/collapse

J. WITHOUT THINKING
- Disable thinking mode
- Send same question
- Verify no thinking section

K. CONTEXT SECTION
After response, check for:
- Model Reasoning (primary color)
- Memories Used (purple)
- Tools Available (green)
- Screenshot each if present

OUTPUT: Create findings.md with attachment handling and thinking mode documentation.
```

---

## Session 2 Execution Command

```
I need you to run 3 UI testing agents in parallel for PeanutChat Session 2.

Create the test directory structure first, then spawn these 3 agents simultaneously:

1. Agent 1 - Messaging & Streaming (input area, message display, streaming)
2. Agent 2 - Edit, Fork & Regenerate (message manipulation flows)
3. Agent 3 - Attachments & Thinking Mode (file uploads, thinking display)

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
