# SESSION 3: Profile, Memory & Knowledge Testing

## Session Overview
Test user profile management, memory system, knowledge base uploads, and model parameter settings.

## Pre-Session Checklist
- Session 2 completed
- App running: `sudo systemctl status peanutchat`
- Ollama running with at least one model

## IMPORTANT: Timeout Configuration
All agents MUST configure these timeouts for LLM response handling:
```python
page.set_default_timeout(300000)  # 5 minutes for LLM responses
page.set_default_navigation_timeout(120000)  # 2 minutes for page loads
```

---

## AGENT 1: User Profile & Adult Mode
**Directory**: `tests/ui_testing/session3/agent1_profile_adult/`
**Focus**: Profile inputs, relationship metrics, uncensored mode

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is PROFILE & ADULT MODE.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent1_profile_adult/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_profile1_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. PROFILE SECTION
Read /static/js/profile.js and /app/routers/user_profile.py.
- Open Settings modal
- Screenshot profile section (#profile-section)
- Verify input fields: Preferred name, Assistant name

B. PROFILE DROPDOWNS
- Screenshot communication style dropdown (5 options)
- Screenshot response length dropdown (3 options)
- Test selecting each option

C. RELATIONSHIP METRICS
Read /app/routers/user_profile.py for metrics.
- Screenshot relationship metrics display
- Verify: Satisfaction, Trust, Interaction count, Stage badge
- Note: May need chat interactions to populate

D. EXPORT/RESET BUTTONS
- Screenshot Export profile button
- Test export (should download JSON)
- Screenshot Reset profile button
- Test reset with confirmation dialog

E. UNCENSORED MODE TOGGLE
Read /static/js/profile.js and index.html (lines 783-827).
- Find uncensored mode button (lock icon)
- Screenshot locked state
- Click to show passcode modal (#adult-mode-modal)

F. PASSCODE MODAL
- Screenshot passcode modal
- Test wrong passcode, screenshot error
- Test correct passcode "6060"
- Screenshot unlocked state
- Verify model list changes

G. FULL UNLOCK COMMANDS
- Test /full_unlock enable command in chat (wait for response, up to 5 min)
- Screenshot onboarding modal (#full-unlock-modal)
- Document question types: enum, boolean, multi-select, text
- Screenshot conditional questions
- Test /full_unlock disable
- Verify session-scoped (reset on refresh)

OUTPUT: Create findings.md with profile forms and adult mode documentation.
```

---

## AGENT 2: Memory & Knowledge Base
**Directory**: `tests/ui_testing/session3/agent2_memory_knowledge/`
**Focus**: Memory management, knowledge base uploads

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MEMORY & KNOWLEDGE BASE.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent2_memory_knowledge/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_memory2_{timestamp}
4. Create test files: test_kb.txt (text content), test_kb.pdf (if available)
5. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. MEMORY SECTION
Read /static/js/memory.js and /static/index.html (lines 494-535).
- Open Settings modal
- Screenshot memory section
- Verify stats: #memory-count, #memory-categories

B. MEMORY EMPTY STATE
- Screenshot empty state message
- Verify "View all memories" details element

C. POPULATE MEMORIES
- Have chat conversation mentioning preferences (wait for responses, up to 5 min each)
- Wait for memories to be created
- Screenshot memory cards: content, category icon, source, date, importance

D. MEMORY CATEGORIES
Verify category icons:
- Personal, Preference, Topic, Instruction, General
- Screenshot each category type if present

E. MEMORY MANAGEMENT
- Test delete single memory (hover button)
- Screenshot confirmation
- Test clear all memories
- Screenshot confirmation dialog

F. KNOWLEDGE BASE SECTION
Read /static/js/knowledge.js and /static/index.html (lines 429-466).
- Screenshot KB section
- Verify stats: #kb-doc-count, #kb-chunk-count

G. KB UPLOAD AREA
- Screenshot upload area (#kb-upload-area) with dashed border
- Test click-to-upload flow
- Screenshot upload progress

H. KB DOCUMENT LIST
- Upload test_kb.txt
- Screenshot document in #kb-documents
- Verify file type icon (text icon)
- Screenshot delete hover button

I. KB FILE HANDLING
- Test delete document with confirmation
- Test drag-drop upload (screenshot border change)
- Document file size limit (150MB)
- Test duplicate upload handling

OUTPUT: Create findings.md with memory and knowledge base documentation.
```

---

## AGENT 3: Parameters & Compaction
**Directory**: `tests/ui_testing/session3/agent3_parameters_compaction/`
**Focus**: Model parameter sliders, context compaction settings

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is PARAMETERS & COMPACTION.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent3_parameters_compaction/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_params3_{timestamp}
4. CRITICAL: Set page.set_default_timeout(300000) and page.set_default_navigation_timeout(120000)

INVESTIGATION TASKS - Screenshot everything:

A. MODEL PARAMETERS SECTION
Read /static/index.html lines 537-601.
- Open Settings modal
- Screenshot Model Parameters section

B. PARAMETER SLIDERS
Test each slider:
1. Temperature (#temperature) - range 0-2, step 0.1
2. Top P (#top-p) - range 0-1, step 0.05
3. Top K (#top-k) - range 1-100, step 1
4. Context Length (#num-ctx) - range 1024-32768, step 1024
5. Repeat Penalty (#repeat-penalty) - range 1-2, step 0.1

For each:
- Screenshot at default value
- Screenshot at min value
- Screenshot at max value
- Verify value display updates

C. CONTEXT COMPACTION SECTION
Read /static/index.html lines 604-664.
- Screenshot compaction settings
- Locate toggle (#compaction-enabled)

D. COMPACTION TOGGLE
- Screenshot toggle OFF state
- Enable toggle
- Screenshot toggle ON state
- Verify child settings become enabled

E. COMPACTION SLIDERS
When enabled, test:
- Buffer slider
- Threshold slider
- Protected messages slider
- Screenshot each with value display

F. DISABLED STATE
- Disable compaction toggle
- Screenshot disabled child settings (opacity 0.5)
- Verify sliders not interactive when disabled

G. CONTEXT GAUGE BEHAVIOR
Read /static/index.html lines 268-283.
- Screenshot context gauge (#context-gauge) at different levels
- Send messages to fill context (wait for responses, up to 5 min each)
- Screenshot gauge at: 0%, ~50%, 70%+

H. COMPACTION TRIGGER
- Set threshold to 50%
- Build conversation until past threshold
- Observe any compaction behavior
- Screenshot gauge changes

I. SAVE PERSISTENCE
- Change multiple settings
- Click Save
- Refresh page
- Verify settings persisted

OUTPUT: Create findings.md with parameter sliders and compaction settings documentation.
```

---

## Session 3 Execution Command

```
I need you to run 3 UI testing agents in parallel for PeanutChat Session 3.

Create the test directory structure first, then spawn these 3 agents simultaneously:

1. Agent 1 - User Profile & Adult Mode (profile forms, uncensored mode)
2. Agent 2 - Memory & Knowledge Base (memory cards, KB uploads)
3. Agent 3 - Parameters & Compaction (sliders, context management)

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
