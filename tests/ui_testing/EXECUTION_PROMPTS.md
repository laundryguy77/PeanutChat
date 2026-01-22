# PeanutChat UI Testing - Execution Prompts

Copy-paste these prompts into separate Claude Code sessions.
Run sessions sequentially (1 → 2 → 3 → 4).
Each session spawns 5 parallel agents.

---

# SESSION 1 PROMPT

```
I need you to run 5 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8080
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session1/{agent1_auth,agent2_sidebar,agent3_themes,agent4_settings,agent5_models}/

Then spawn ALL 5 agents in parallel (single message, 5 Task tool calls):

AGENT 1 - Authentication Testing
Directory: tests/ui_testing/session1/agent1_auth/
Code to read: /static/js/auth.js, /static/index.html (lines 725-781), /app/routers/auth.py
Test: Registration flow (form validation, error states, success), Login flow (credentials, errors), Session handling (sessionStorage marker, new tab detection), Logout flow (button, state clearing). Screenshot all modals, error messages, success states.

AGENT 2 - Sidebar & Conversations
Directory: tests/ui_testing/session1/agent2_sidebar/
Code to read: /static/index.html (lines 155-230), /static/js/app.js
Test: Sidebar structure (logo, buttons, user info), New Chat button, Conversation list (create, select, scroll), Search filtering, Rename modal (#rename-modal), Delete confirmation. Screenshot all states.

AGENT 3 - Themes & Visuals
Directory: tests/ui_testing/session1/agent3_themes/
Code to read: /static/index.html (lines 399-420), /static/css/styles.css
Test: Theme selector (4 buttons: dark, light, midnight, forest), Each theme applied to full page, Theme persistence in localStorage, Active theme indicator styling, CSS variable changes per theme. Screenshot full page in each theme.

AGENT 4 - Settings Modal Structure
Directory: tests/ui_testing/session1/agent4_settings/
Code to read: /static/index.html (lines 375-674), /static/js/settings.js
Test: Modal open/close (button, X, backdrop, ESC), All 8 sections exist (Profile, Theme, Persona, KB, MCP, Memory, Parameters, Compaction), Section headers and icons, Save button behavior. Screenshot each section.

AGENT 5 - Model Selector & Gauges
Directory: tests/ui_testing/session1/agent5_models/
Code to read: /static/index.html (lines 246-301), /static/js/app.js, /app/routers/models.py
Test: Model dropdown (#model-select), Capability icons (#cap-tools, #cap-vision, #cap-thinking), Context gauge (#context-gauge), VRAM gauge (if GPU), Tooltips on hover, Model switching updates capabilities. Screenshot all states.
```

---

# SESSION 2 PROMPT

```
I need you to run 5 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8080
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session2/{agent1_messaging,agent2_streaming,agent3_edit_fork,agent4_attachments,agent5_thinking}/

Then spawn ALL 5 agents in parallel (single message, 5 Task tool calls):

AGENT 1 - Message Sending & Display
Directory: tests/ui_testing/session2/agent1_messaging/
Code to read: /static/js/chat.js, /static/index.html (lines 305-360)
Test: Input area (#message-input, #send-btn), Textarea auto-resize, Send button states, User message bubble styling, Assistant message styling, Message actions (copy, edit), Markdown rendering (bold, italic, code blocks, lists, tables, blockquotes), Code block copy button, Scroll behavior. Screenshot each message type and markdown element.

AGENT 2 - Streaming & Indicators
Directory: tests/ui_testing/session2/agent2_streaming/
Code to read: /static/js/chat.js (search "stream")
Test: Typing indicator during response, Token-by-token rendering, Streaming interruption handling, Send button disabled during stream, Long response handling, Error mid-stream recovery, Stream completion (indicator disappears, actions appear). Take screenshots every 2 seconds during streaming.

AGENT 3 - Edit, Fork, Regenerate
Directory: tests/ui_testing/session2/agent3_edit_fork/
Code to read: /static/js/chat.js, /static/index.html (lines 685-710)
Test: Edit button on user messages only, Edit modal (#edit-modal with radio options), Edit in-place flow, Fork conversation flow (creates new conversation), Regenerate button on assistant messages, Regenerate replaces response, Cancel operations. Screenshot modal and conversation states.

AGENT 4 - File & Image Attachments
Directory: tests/ui_testing/session2/agent4_attachments/
Code to read: /static/js/chat.js, /static/index.html (lines 316-340)
Test: Tools menu (#tools-menu), File input (#file-upload, #image-upload), Image preview in #image-previews, File badge in #file-previews, Multiple file attachment, Remove individual attachment, Send with attachments, File size limit (25MB), Drag and drop upload. Screenshot previews and states.

AGENT 5 - Thinking Mode
Directory: tests/ui_testing/session2/agent5_thinking/
Code to read: /static/js/chat.js (search "thinking"), /static/index.html (lines 330-336)
Test: Thinking toggle (#thinking-checkbox in tools menu), Mode indicator when enabled, Thinking display during response (collapsible details, spinning icon), Thought process content, Auto-collapse after completion, Context section (Model Reasoning, Memories Used, Tools Available), Thinking + tools interaction. Screenshot all thinking states.
```

---

# SESSION 3 PROMPT

```
I need you to run 5 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8080
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session3/{agent1_profile,agent2_adult_mode,agent3_memory,agent4_knowledge,agent5_parameters}/

Then spawn ALL 5 agents in parallel (single message, 5 Task tool calls):

AGENT 1 - User Profile UI
Directory: tests/ui_testing/session3/agent1_profile/
Code to read: /static/js/profile.js, /app/routers/user_profile.py
Test: Profile section (#profile-section), Input fields (preferred name, assistant name), Dropdowns (communication style with 5 options, response length with 3 options), Relationship metrics display (satisfaction, trust, interaction count, stage badge), Export profile button (downloads JSON), Reset profile button (confirmation dialog). Screenshot all fields and states.

AGENT 2 - Adult Mode & Onboarding
Directory: tests/ui_testing/session3/agent2_adult_mode/
Code to read: /static/js/profile.js, /app/routers/user_profile.py (lines 223-493), /static/index.html (lines 783-827)
Test: Uncensored mode button (lock icon), Passcode modal (#adult-mode-modal), Wrong passcode error, Correct passcode "6060" unlocks, Model list changes after unlock, /full_unlock enable command, Onboarding modal (#full-unlock-modal), Question types (enum, boolean, multi-select, text), Conditional questions, /full_unlock disable, Session-scoped behavior (reset on refresh). Screenshot all flows.

AGENT 3 - Memory Management
Directory: tests/ui_testing/session3/agent3_memory/
Code to read: /static/js/memory.js, /static/index.html (lines 494-535), /app/routers/memory.py
Test: Memory section location, Stats display (#memory-count, #memory-categories), Empty state message, Expandable "View all memories" details, Memory card structure (content, category icon, source, date, importance flag), Categories (personal, preference, topic, instruction, general with icons), Delete single memory, Clear all memories (confirmation). Screenshot all states.

AGENT 4 - Knowledge Base Upload
Directory: tests/ui_testing/session3/agent4_knowledge/
Code to read: /static/js/knowledge.js, /static/index.html (lines 429-466), /app/routers/knowledge.py
Test: KB section, Stats (#kb-doc-count, #kb-chunk-count), Upload area (#kb-upload-area) with dashed border, Click-to-upload flow, Upload progress display, Document list (#kb-documents), File type icons (PDF, text, code), Delete document (hover button, confirmation), Drag-drop upload (border change), File size limit 150MB, Duplicate upload handling. Create test files to upload.

AGENT 5 - Settings Parameters
Directory: tests/ui_testing/session3/agent5_parameters/
Code to read: /static/index.html (lines 537-664)
Test: Model Parameters section with 5 sliders: Temperature (#temperature, 0-2), Top P (#top-p, 0-1), Top K (#top-k, 1-100), Context Length (#num-ctx, 1024-32768), Repeat Penalty (#repeat-penalty, 1-2). Each slider has value display that updates. Compaction section: Toggle (#compaction-enabled), Buffer slider, Threshold slider, Protected messages slider. Disabled state when toggle off (opacity 0.5). Save persistence. Screenshot all sliders at min/max values.
```

---

# SESSION 4 PROMPT

```
I need you to run 5 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8080
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session4/{agent1_mcp,agent2_model_switch,agent3_compaction,agent4_errors,agent5_integration}/

Then spawn ALL 5 agents in parallel (single message, 5 Task tool calls):

AGENT 1 - MCP Server Management
Directory: tests/ui_testing/session4/agent1_mcp/
Code to read: /static/js/mcp.js, /app/routers/mcp.py, /app/services/mcp_client.py (lines 23-47 for allowlist)
Test: MCP section (#mcp-servers), Empty state, Add Server button → modal (#mcp-add-modal), Form fields (name, command, args), Cancel modal, Add valid server (command: "node"), Server list item structure (status dot, name, command, toggle, delete), Connection status (gray=disconnected, green=connected), Toggle connect/disconnect, Delete server (confirmation), Invalid command rejection (check allowlist). Screenshot all states.

AGENT 2 - Model Switching
Directory: tests/ui_testing/session4/agent2_model_switch/
Code to read: /static/js/app.js, /app/routers/models.py
Test: Model dropdown inventory, Current model indicator, Switch models (POST /api/models/select), Capability icons update per model (#cap-tools, #cap-vision, #cap-thinking), Model with no capabilities, Model switching during chat, Model persistence after refresh, Adult mode filtering (more models visible when enabled), Rapid model switching (race conditions?). Screenshot capability changes.

AGENT 3 - Context Compaction
Directory: tests/ui_testing/session4/agent3_compaction/
Code to read: /static/index.html (lines 268-283, 604-664), /app/services/compaction_service.py
Test: Context gauge (#context-gauge) fill progression, Gauge at 0%, 50%, 70%+ states, Compaction settings (threshold, buffer, protected), Set threshold to 50%, Build conversation until compaction triggers, Observe compaction behavior (messages summarized?), Protected messages preserved, Compaction disabled behavior (fills past threshold), VRAM gauge if GPU present. Screenshot gauge at intervals.

AGENT 4 - Error States & Edge Cases
Directory: tests/ui_testing/session4/agent4_errors/
Code to read: /static/js/auth.js, /static/js/chat.js
Test: Network disconnect during chat, Server down behavior, Auth token expiry (delete cookie), API 500 response handling, Empty states (no conversations, no memories, no KB), Very long input (10000+ chars), XSS attempt (<script> tag), Double-click prevention on buttons, Mobile viewport (375x667), Keyboard navigation (tab through elements), Clipboard operations. Screenshot all error states.

AGENT 5 - Integration Testing
Directory: tests/ui_testing/session4/agent5_integration/
Code to read: All main files
Test: Complete user journey (register → chat → configure → use features → logout → login), KB + chat integration (upload doc, query it), Memory + chat integration (preferences learned and used), Profile + chat (communication style affects responses), Thinking + tools together, Model switch during conversation, Settings save and persistence, Conversation fork tree, Session boundaries (new tabs). Screenshot every step of journeys.
```

---

## Quick Reference: Agent Responsibilities

| Session | Agent 1 | Agent 2 | Agent 3 | Agent 4 | Agent 5 |
|---------|---------|---------|---------|---------|---------|
| 1 | Auth flows | Sidebar | Themes | Settings modal | Models/gauges |
| 2 | Messaging | Streaming | Edit/fork | Attachments | Thinking mode |
| 3 | Profile forms | Adult mode | Memory | Knowledge base | Parameters |
| 4 | MCP servers | Model switch | Compaction | Errors/edge | Integration |

## Output Structure

Each agent creates in their directory:
- `findings.md` - Full investigation report
- `screenshots/` - All captured screenshots with descriptive names
- Any logs or raw data

## No-Fix Rule

Agents MUST NOT:
- Modify any source code
- Create "fixes" for found issues
- Make assumptions about bugs
- Write to files outside their test directory

Agents MUST:
- Document exactly what they observe
- Include screenshot evidence
- Reference source code line numbers
- Note discrepancies between code and UI
