# SESSION 2: Core Chat Features Testing

## Session Overview
Test the chat interface: messaging, streaming, message manipulation, file attachments, and thinking mode.

## Pre-Session Checklist
- Session 1 completed
- App running: `sudo systemctl status peanutchat`
- Ollama running with at least one model

---

## AGENT 1: Message Sending & Receiving
**Directory**: `tests/ui_testing/session2/agent1_messaging/`
**Focus**: Input area, message display, send flow

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MESSAGE SENDING & DISPLAY.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent1_messaging/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_msg1_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. INPUT AREA STRUCTURE
Read /static/index.html lines 305-360 for input structure.
- Screenshot the input area (#input-container)
- Verify elements:
  * Tools button (#tools-btn)
  * Message textarea (#message-input)
  * Send button (#send-btn)
- Screenshot placeholder text "Message PeanutChat..."

B. TEXTAREA BEHAVIOR
Read /static/js/chat.js for textarea handling.
- Type short message, screenshot
- Type multiline message (use Shift+Enter or paste), screenshot
- Test auto-resize behavior (field-sizing: content)
- Verify min-height 48px, max-height 200px
- Type extremely long message, verify scrolling within textarea

C. SEND BUTTON STATES
- Screenshot send button in default state
- Type message, screenshot button (should be enabled)
- Clear message, screenshot button (check if disabled when empty)
- Click send, screenshot during sending (should show loading state)

D. USER MESSAGE DISPLAY
Read /static/js/chat.js for message rendering.
- Send a message
- Screenshot user message bubble
- Verify styling:
  * Blue background (primary color)
  * Right-aligned (flex-row-reverse)
  * Rounded corners (rounded-2xl with rounded-tr-sm)
  * Avatar with person icon
- Check whitespace handling (pre-wrap)

E. ASSISTANT MESSAGE DISPLAY
- Wait for response
- Screenshot assistant message
- Verify styling:
  * Gray background with border
  * Left-aligned
  * Avatar with bot icon
  * "AI" badge
  * Message actions (copy button)

F. MESSAGE ACTIONS
- Hover over user message, screenshot action buttons
- Hover over assistant message, screenshot action buttons
- Verify copy button works (check clipboard)
- Find edit button (user messages only)
- Find regenerate button (assistant messages only)

G. MARKDOWN RENDERING
Read /static/js/chat.js for markdown logic (uses marked.js).
Test each markdown element:
- **Bold text** - screenshot
- *Italic text* - screenshot
- `inline code` - screenshot
- Code blocks with syntax highlighting - screenshot
- Bullet lists - screenshot
- Numbered lists - screenshot
- Headers (##, ###) - screenshot
- Links - screenshot
- Tables - screenshot
- Blockquotes - screenshot (styled as info callouts)

H. CODE BLOCK FEATURES
- Send message asking for code example
- Screenshot code block
- Verify syntax highlighting (highlight.js)
- Test copy button on code block
- Screenshot copy success feedback

I. EMPTY STATE
- Start new conversation
- Screenshot chat area before any messages
- Verify welcome/empty state display

J. SCROLL BEHAVIOR
- Send enough messages to require scrolling
- Verify auto-scroll to newest message
- Screenshot scroll position
- Manually scroll up, send new message
- Verify it scrolls back to bottom

OUTPUT: Create findings.md with:
- Input area element inventory
- Message rendering documentation
- Markdown support table
- Scroll behavior observations
- Any UI bugs or rendering issues
```

---

## AGENT 2: Streaming & Typing Indicators
**Directory**: `tests/ui_testing/session2/agent2_streaming/`
**Focus**: SSE streaming, token display, loading states

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is STREAMING RESPONSES.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent2_streaming/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_stream2_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. STREAMING INDICATORS
Read /static/js/chat.js for streaming logic.
- Send a message that will generate long response
- Screenshot IMMEDIATELY when assistant starts responding
- Capture typing indicator state
- Screenshot token-by-token appearance

B. TYPING INDICATOR
Read index.html for typing indicator structure.
- Find typing indicator element
- Screenshot while assistant is "typing"
- Verify indicator disappears when complete
- Test visual pulsing/animation

C. TOKEN STREAMING
- Send "Write a 500 word story" message
- Take multiple screenshots during streaming (every 2 seconds)
- Observe token-by-token rendering
- Verify smooth text appearance (no flicker)
- Check for any dropped tokens or gaps

D. STREAMING INTERRUPTION
- Start receiving a streaming response
- Try clicking "New Chat" or navigating away
- Screenshot behavior
- Does it cleanly abort?
- Any error messages?

E. SEND BUTTON DURING STREAM
- While streaming, try to send another message
- Screenshot send button state
- Is it disabled during stream?
- What happens if you click it?

F. LONG RESPONSE HANDLING
- Request very long response ("Write 1000 words about...")
- Screenshot at intervals
- Verify scroll keeps up with new content
- Check memory usage / performance (browser dev tools)

G. NETWORK LATENCY SIMULATION
- Use browser dev tools to throttle network
- Send message on slow connection
- Screenshot any timeout handling
- Check for retry logic

H. ERROR DURING STREAM
Read /static/js/chat.js for error handling.
- If possible, trigger an error mid-stream
- Screenshot error display
- How does UI recover?
- Is partial message preserved or discarded?

I. MULTIPLE RAPID MESSAGES
- Send message 1
- While streaming, queue message 2
- Screenshot the queue behavior
- How are multiple responses handled?

J. STREAM COMPLETION
- Screenshot exact moment streaming completes
- Verify typing indicator disappears
- Check message actions appear (copy, etc.)
- Send button re-enables

OUTPUT: Create findings.md with:
- Streaming timeline with screenshots
- Performance observations
- Error handling documentation
- Edge case behaviors
- Any rendering bugs during stream
```

---

## AGENT 3: Edit, Fork, & Regenerate Flows
**Directory**: `tests/ui_testing/session2/agent3_edit_fork/`
**Focus**: Message editing, conversation forking, response regeneration

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MESSAGE MANIPULATION.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent3_edit_fork/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_edit3_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. EDIT BUTTON DISCOVERY
Read /static/js/chat.js for edit functionality.
- Send a user message, wait for response
- Hover over USER message
- Screenshot edit button appearance
- Verify edit button ONLY on user messages (not assistant)

B. EDIT MODAL
Read /static/index.html lines 685-710 for edit modal.
- Click edit button
- Screenshot edit modal (#edit-modal)
- Verify elements:
  * Textarea with current message content
  * Radio buttons: "Edit in place" / "Fork conversation"
  * Cancel button
  * Save button
- Screenshot both radio options

C. EDIT IN-PLACE FLOW
- Select "Edit in place" option
- Modify the message text
- Click Save
- Screenshot result
- Verify: original message updated
- Verify: subsequent messages affected (regenerated?)

D. FORK CONVERSATION FLOW
- Send 3+ messages to create history
- Edit middle message, select "Fork conversation"
- Click Save
- Screenshot result
- Verify: new conversation created
- Verify: messages after fork point removed
- Check conversation list for new forked conversation

E. REGENERATE BUTTON
Read /static/js/chat.js for regenerate logic.
- Find regenerate button on ASSISTANT message
- Screenshot button location
- Click regenerate
- Screenshot during regeneration
- Verify: old response replaced with new
- Compare old vs new response

F. REGENERATE ON LATEST MESSAGE
- Send message, get response
- Regenerate immediately
- Screenshot the process
- Verify clean replacement

G. REGENERATE ON OLDER MESSAGE
- Build conversation with 5+ exchanges
- Find regenerate on earlier assistant message
- Click it
- Screenshot behavior
- Are subsequent messages affected?

H. CANCEL OPERATIONS
- Open edit modal, make changes, click Cancel
- Screenshot: original message unchanged
- Start regenerate, try to cancel mid-stream
- Screenshot any cancel mechanism

I. EDIT VALIDATION
- Try to save empty message
- Screenshot any validation error
- Try extremely long edit (10000+ chars)
- Screenshot behavior

J. FORK NAMING
- Fork a conversation
- Check the new conversation's title
- Screenshot conversation list showing both original and fork

OUTPUT: Create findings.md with:
- Edit flow documentation with screenshots
- Fork behavior analysis
- Regenerate mechanics
- Edge cases and error states
- Conversation history integrity observations
```

---

## AGENT 4: File & Image Attachments
**Directory**: `tests/ui_testing/session2/agent4_attachments/`
**Focus**: File upload UI, image preview, attachment handling

### Prompt for Agent 4:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is FILE ATTACHMENTS.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent4_attachments/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_attach4_{timestamp}
4. Create test files:
   - test_image.png (any small image)
   - test_doc.txt (some text content)
   - test_code.py (Python code)
   - test_large.pdf (if available, or create dummy)

INVESTIGATION TASKS - Screenshot everything:

A. TOOLS MENU
Read /static/index.html lines 316-340 for tools menu.
- Screenshot tools button (#tools-btn)
- Click to open menu (#tools-menu)
- Screenshot open menu
- Verify options:
  * "Add files" option
  * "Thinking mode" checkbox

B. FILE INPUT ELEMENTS
Read index.html for hidden inputs.
- Locate #image-upload input (accept="image/*")
- Locate #file-upload input (multiple file types)
- Document accepted file types

C. IMAGE UPLOAD FLOW
- Click "Add files" or trigger image upload
- Select test_image.png
- Screenshot image preview in #image-previews
- Verify preview shows:
  * Thumbnail of image
  * Remove button (X)
- Screenshot preview sizing

D. FILE UPLOAD FLOW
- Upload test_doc.txt
- Screenshot file badge in #file-previews
- Verify badge shows:
  * File type icon
  * Filename
  * Close/remove button
- Test file type icon accuracy (text icon for txt, code icon for py)

E. MULTIPLE FILE ATTACHMENT
- Attach 3+ different files simultaneously
- Screenshot grid layout
- Verify all files show
- Test removing individual files
- Screenshot after removal

F. SEND WITH ATTACHMENTS
- Attach file + type message
- Screenshot input area
- Click send
- Screenshot message display
- How are attachments shown in sent message?

G. IMAGE IN MESSAGE
- Send with image attached
- Screenshot how image appears in user message
- Is it displayed inline?
- Can you click to enlarge?

H. FILE SIZE LIMITS
Read /static/js/knowledge.js for size limits (25MB per file).
- Try uploading file > 25MB
- Screenshot any error message
- Verify graceful handling

I. FILE TYPE RESTRICTIONS
- Try uploading .exe file
- Try uploading random binary
- Screenshot acceptance/rejection
- Document which types are blocked

J. CLEAR ATTACHMENTS
- Attach multiple files
- Find clear/remove mechanism
- Screenshot before and after clearing
- Verify all previews removed

K. DRAG AND DROP
- Test drag-drop image onto chat area
- Screenshot drag-over state (if any visual feedback)
- Screenshot after drop
- Does it add to attachments?

OUTPUT: Create findings.md with:
- Attachment flow documentation
- File type support table
- Preview rendering observations
- Size limit enforcement
- Any bugs in attachment handling
```

---

## AGENT 5: Thinking Mode Toggle & Display
**Directory**: `tests/ui_testing/session2/agent5_thinking/`
**Focus**: Thinking mode UI, thought process display

### Prompt for Agent 5:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is THINKING MODE.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session2/agent5_thinking/
2. App URL: http://localhost:8080
3. Create unique test user: testuser_think5_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. THINKING MODE TOGGLE
Read /static/index.html lines 330-336 for thinking toggle.
- Open tools menu (#tools-menu)
- Screenshot thinking mode checkbox (#thinking-checkbox)
- Verify label "Thinking mode"
- Click to enable
- Screenshot enabled state

B. MODE INDICATOR
- Enable thinking mode
- Screenshot any mode indicator in input area
- Verify visual feedback that thinking is active
- Toggle off, verify indicator disappears

C. THINKING IN ACTION
Read /static/js/chat.js for thinking display (search "thinking").
- With thinking mode ON, send complex question
- Screenshot DURING thinking phase
- Look for:
  * Spinning psychology icon
  * "Thinking..." text
  * Collapsible details element

D. THOUGHT PROCESS DISPLAY
- Wait for thinking to complete
- Screenshot thought process section
- Verify <details> element:
  * Summary shows "Thought process"
  * Content shows thinking tokens
  * Scrollable (max-height: 200px)
  * Primary color styling

E. THINKING COLLAPSE BEHAVIOR
Read /static/js/chat.js for auto-collapse logic.
- During thinking: should be expanded
- After thinking: should auto-collapse
- Screenshot both states
- Test manual expand/collapse

F. THINKING TOKENS STREAMING
- Send another thinking query
- Take screenshots during thinking token stream
- Observe token-by-token thinking display
- Separate from main response display?

G. WITHOUT THINKING MODE
- Disable thinking mode
- Send same complex question
- Screenshot response
- Verify no thinking section appears
- Compare response quality (just observation)

H. MODEL CAPABILITY CHECK
Read /app/routers/models.py for thinking capability.
- Check current model supports thinking (#cap-thinking icon)
- If model doesn't support thinking, what happens?
- Screenshot behavior with non-thinking model

I. CONTEXT SECTION
Read /static/js/chat.js for context display.
After response, check for context section:
- Model Reasoning (primary color)
- Memories Used (purple)
- Tools Available (green)
Screenshot each if present.

J. THINKING + TOOLS
- Enable thinking mode
- Ask question that uses tools (web search)
- Screenshot how thinking interacts with tool calls
- Are they shown separately?

K. LONG THINKING
- Ask very complex question
- Let thinking run long
- Screenshot extended thinking display
- Verify scrolling within thinking container

OUTPUT: Create findings.md with:
- Thinking mode toggle flow
- Visual indicator documentation
- Thinking display mechanics
- Context section analysis
- Model capability requirements
- Any bugs in thinking feature
```

---

## Session 2 Execution Command

```
I need you to run 5 UI testing agents in parallel for PeanutChat Session 2.

Create the test directory structure first, then spawn these 5 agents simultaneously:

1. Agent 1 - Message sending & receiving (input area, message display)
2. Agent 2 - Streaming & typing indicators (SSE streaming, loading states)
3. Agent 3 - Edit, fork, & regenerate flows (message manipulation)
4. Agent 4 - File & image attachments (upload UI, previews)
5. Agent 5 - Thinking mode toggle & display (thought process UI)

Each agent should:
- Create unique test user
- Use Playwright + Chromium
- Screenshot EVERY interaction
- Read source code to understand expected behavior
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes

The app is running at http://localhost:8080
```
