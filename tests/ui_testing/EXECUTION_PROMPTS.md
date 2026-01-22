# PeanutChat UI Testing - Execution Prompts

Copy-paste these prompts into separate Claude Code sessions.
Run sessions sequentially (1 -> 2 -> 3 -> 4).
Each session spawns 3 parallel agents (reduced from 5 for LLM request management).

## Timeout Configuration (CRITICAL)
All agents MUST use these Playwright timeout settings:
```python
page.set_default_timeout(300000)  # 5 min for LLM responses
page.set_default_navigation_timeout(120000)  # 2 min for page loads
```

---

# SESSION 1 PROMPT

```
I need you to run 3 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8000
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Set page.set_default_timeout(300000) for LLM response waits
- Set page.set_default_navigation_timeout(120000) for page loads
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Wait for LLM responses to complete before sending new messages
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session1/{agent1_auth_sidebar,agent2_themes_settings,agent3_models_gauges}/

Then spawn ALL 3 agents in parallel (single message, 3 Task tool calls):

AGENT 1 - Authentication & Sidebar
Directory: tests/ui_testing/session1/agent1_auth_sidebar/
Code to read: /static/js/auth.js, /static/index.html (lines 155-230, 725-781), /app/routers/auth.py
Test: Registration flow, Login flow, Session handling, Logout flow, Sidebar structure, New Chat button, Conversation list, Search filtering, Rename/Delete modals. Screenshot all states.

AGENT 2 - Themes & Settings Modal
Directory: tests/ui_testing/session1/agent2_themes_settings/
Code to read: /static/index.html (lines 375-674), /static/js/settings.js, /static/css/styles.css
Test: Theme selector (4 themes), Theme persistence, Settings modal open/close, All 8 sections exist, Section navigation, Form fields, Save button. Screenshot each theme and section.

AGENT 3 - Models & Capability Gauges
Directory: tests/ui_testing/session1/agent3_models_gauges/
Code to read: /static/index.html (lines 246-301), /static/js/app.js, /app/routers/models.py
Test: Model dropdown, Capability icons (#cap-tools, #cap-vision, #cap-thinking), Context gauge, VRAM gauge (if GPU), Model switching, Tooltips. Screenshot all model states.
```

---

# SESSION 2 PROMPT

```
I need you to run 3 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8000
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Set page.set_default_timeout(300000) for LLM response waits
- Set page.set_default_navigation_timeout(120000) for page loads
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Wait for LLM responses to complete before sending new messages
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session2/{agent1_messaging_streaming,agent2_edit_fork_regen,agent3_attachments_thinking}/

Then spawn ALL 3 agents in parallel (single message, 3 Task tool calls):

AGENT 1 - Messaging & Streaming
Directory: tests/ui_testing/session2/agent1_messaging_streaming/
Code to read: /static/js/chat.js, /static/index.html (lines 305-360)
Test: Input area, Textarea auto-resize, Send button states, User/Assistant message styling, Markdown rendering, Code blocks, Streaming indicators, Typing indicator, Long response handling. Screenshot message types and streaming states.

AGENT 2 - Edit, Fork & Regenerate
Directory: tests/ui_testing/session2/agent2_edit_fork_regen/
Code to read: /static/js/chat.js, /static/index.html (lines 685-710)
Test: Edit button (user messages only), Edit modal with radio options, Edit in-place flow, Fork conversation flow, Regenerate button (assistant messages), Cancel operations. Screenshot modal and conversation states.

AGENT 3 - Attachments & Thinking Mode
Directory: tests/ui_testing/session2/agent3_attachments_thinking/
Code to read: /static/js/chat.js, /static/index.html (lines 316-340)
Test: Tools menu, File/image inputs, Image preview, File badges, Multiple attachments, Send with attachments, Thinking toggle, Thinking display during response, Thought process collapsible, Context section. Screenshot all attachment and thinking states.
```

---

# SESSION 3 PROMPT

```
I need you to run 3 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8000
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Set page.set_default_timeout(300000) for LLM response waits
- Set page.set_default_navigation_timeout(120000) for page loads
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Wait for LLM responses to complete before sending new messages
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session3/{agent1_profile_adult,agent2_memory_knowledge,agent3_parameters_compaction}/

Then spawn ALL 3 agents in parallel (single message, 3 Task tool calls):

AGENT 1 - User Profile & Adult Mode
Directory: tests/ui_testing/session3/agent1_profile_adult/
Code to read: /static/js/profile.js, /app/routers/user_profile.py, /static/index.html (lines 783-827)
Test: Profile section inputs, Dropdowns (communication style, response length), Relationship metrics, Export/Reset buttons, Uncensored mode toggle, Passcode modal (6060), /full_unlock commands, Onboarding questions. Screenshot all profile and adult mode states.

AGENT 2 - Memory & Knowledge Base
Directory: tests/ui_testing/session3/agent2_memory_knowledge/
Code to read: /static/js/memory.js, /static/js/knowledge.js, /static/index.html (lines 429-535), /app/routers/memory.py, /app/routers/knowledge.py
Test: Memory stats, Memory cards (content, category, icons), Delete memory, Clear all, KB upload area, Document list, File type icons, Delete document, Upload progress, Drag-drop. Screenshot all memory and KB states.

AGENT 3 - Parameters & Compaction
Directory: tests/ui_testing/session3/agent3_parameters_compaction/
Code to read: /static/index.html (lines 537-664), /app/services/compaction_service.py
Test: All 5 parameter sliders (Temperature, Top P, Top K, Context Length, Repeat Penalty), Value displays, Compaction toggle, Buffer/Threshold/Protected sliders, Disabled state styling, Context gauge fill progression, Save persistence. Screenshot sliders at different values.
```

---

# SESSION 4 PROMPT

```
I need you to run 3 Playwright UI testing agents in parallel for PeanutChat.

App URL: http://localhost:8000
Base directory: /home/user/PeanutChat

CRITICAL RULES FOR ALL AGENTS:
- Use Playwright + Chromium for all testing
- Set page.set_default_timeout(300000) for LLM response waits
- Set page.set_default_navigation_timeout(120000) for page loads
- Create unique test user: testuser_{area}_{agentnum}_{timestamp}
- Screenshot EVERY interaction - screenshots are primary evidence
- Read source code to learn expected behavior (NOT documentation)
- INVESTIGATION ONLY - no fixes, no code changes
- Wait for LLM responses to complete before sending new messages
- Document all findings in findings.md in agent directory

Create directory structure first:
/home/user/PeanutChat/tests/ui_testing/session4/{agent1_mcp_models,agent2_errors_edge,agent3_integration}/

Then spawn ALL 3 agents in parallel (single message, 3 Task tool calls):

AGENT 1 - MCP Servers & Model Switching
Directory: tests/ui_testing/session4/agent1_mcp_models/
Code to read: /static/js/mcp.js, /app/routers/mcp.py, /app/services/mcp_client.py, /app/routers/models.py
Test: MCP section, Add server modal, Server list, Connection status, Toggle connect/disconnect, Delete server, Command allowlist, Model switching, Capability updates, Adult mode model filtering, Rapid switching. Screenshot all MCP and model states.

AGENT 2 - Error States & Edge Cases
Directory: tests/ui_testing/session4/agent2_errors_edge/
Code to read: /static/js/auth.js, /static/js/chat.js
Test: Network disconnect behavior, Auth token expiry, API error handling, Empty states, Very long input (10000+ chars), XSS attempt, Double-click prevention, Mobile viewport (375x667), Keyboard navigation, Clipboard operations. Screenshot all error states.

AGENT 3 - Integration Testing
Directory: tests/ui_testing/session4/agent3_integration/
Code to read: All main files
Test: Complete user journey (register -> chat -> configure -> features -> logout -> login), KB + chat integration, Memory + chat integration, Profile effects on responses, Thinking + tools, Model switch mid-conversation, Settings persistence, Conversation fork tree. Screenshot every journey step.
```

---

## Quick Reference: Agent Responsibilities

| Session | Agent 1 | Agent 2 | Agent 3 |
|---------|---------|---------|---------|
| 1 | Auth + Sidebar | Themes + Settings | Models + Gauges |
| 2 | Messaging + Streaming | Edit/Fork/Regen | Attachments + Thinking |
| 3 | Profile + Adult Mode | Memory + KB | Parameters + Compaction |
| 4 | MCP + Model Switch | Errors + Edge Cases | Integration |

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
