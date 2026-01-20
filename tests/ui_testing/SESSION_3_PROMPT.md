# SESSION 3: Profile, Memory & Knowledge Base Testing

## Session Overview
Test profile management, adult mode/onboarding, memory system, knowledge base, and settings parameters.

## Pre-Session Checklist
- Sessions 1-2 completed
- App running: `sudo systemctl status peanutchat`
- Prepare test files for knowledge base upload

---

## AGENT 1: User Profile Forms & Inputs
**Directory**: `tests/ui_testing/session3/agent1_profile/`
**Focus**: Profile section, form inputs, relationship metrics

### Prompt for Agent 1:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is USER PROFILE UI.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent1_profile/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_profile1_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. PROFILE SECTION LOCATION
Read /static/js/profile.js for profile rendering.
- Open Settings modal
- Screenshot profile section (#profile-section)
- Document section position in modal

B. PROFILE INPUT FIELDS
Read profile.js for field structure.
Verify and screenshot each field:
- Preferred Name input (#profile-name)
- Assistant Name input (#profile-assistant-name)
- Communication Style dropdown (#profile-style)
- Response Length dropdown (#profile-length)

C. COMMUNICATION STYLE DROPDOWN
- Click dropdown
- Screenshot all options:
  * candid_direct
  * quirky_imaginative
  * nerdy_exploratory
  * sarcastic_dry
  * empathetic_supportive
- Select each, screenshot

D. RESPONSE LENGTH DROPDOWN
- Click dropdown
- Screenshot options:
  * brief
  * adaptive
  * detailed
- Test selection

E. RELATIONSHIP METRICS DISPLAY
Read profile.js for metrics rendering.
Screenshot metrics section:
- Satisfaction Level
- Trust Level
- Interaction Count
- Relationship Stage (badge with color)

F. RELATIONSHIP STAGE BADGE
- Screenshot stage badge
- Note color coding
- Document what stages exist (from code)
- What colors map to what stages?

G. PROFILE INPUT VALIDATION
- Clear preferred name, try to save
- Screenshot any validation
- Enter very long name (100+ chars)
- Enter special characters
- Screenshot behaviors

H. PROFILE SAVE FLOW
- Make changes to profile fields
- Click Save Settings button
- Screenshot save process
- Verify API call made (PUT /api/profile)
- Screenshot success/error feedback

I. PROFILE LOAD ON OPEN
- Close settings
- Reopen settings
- Verify profile data loads correctly
- Screenshot populated fields

J. EXPORT PROFILE BUTTON
Read profile.js for export logic.
- Find export button
- Click it
- Screenshot any confirmation
- Verify file download (peanutchat_profile.json)
- Open downloaded file, verify content

K. RESET PROFILE BUTTON
- Find reset profile button
- Click it
- Screenshot confirmation dialog
- Message should mention preserving identity
- Cancel the reset
- Screenshot unchanged state

OUTPUT: Create findings.md with:
- Profile form inventory
- Dropdown options documentation
- Metrics display analysis
- Validation behaviors
- Export/reset flow documentation
```

---

## AGENT 2: Adult Mode & Onboarding Flows
**Directory**: `tests/ui_testing/session3/agent2_adult_mode/`
**Focus**: Adult mode unlock, full unlock flow, onboarding questions

### Prompt for Agent 2:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is ADULT MODE & ONBOARDING.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent2_adult_mode/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_adult2_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. UNCENSORED MODE BUTTON
Read /static/js/profile.js for adult mode logic.
- Open Settings > Profile section
- Find Uncensored Mode toggle button
- Screenshot button (lock icon state)
- Note: Should show lock icon when disabled

B. PASSCODE MODAL
Read /static/index.html for #adult-mode-modal.
- Click uncensored mode button
- Screenshot passcode modal
- Verify elements:
  * Passcode input (#adult-passcode, 4 digits, numeric)
  * Error display area (#adult-mode-error)
  * Cancel button
  * Unlock button

C. WRONG PASSCODE
- Enter wrong passcode (e.g., 1234)
- Click Unlock
- Screenshot error message (red styling)
- Verify error says invalid passcode

D. CORRECT PASSCODE
Read /app/services/auth_service.py for ADULT_PASSCODE = "6060".
- Enter 6060
- Click Unlock
- Screenshot success state
- Modal should close
- Button should now show lock_open icon

E. ADULT MODE EFFECTS
- After unlock, screenshot model selector
- Check if previously hidden models now appear
- Look for models with: uncensored, abliterated, nsfw
- Screenshot model list differences

F. DISABLE ADULT MODE
- Find disable mechanism
- Click to disable
- Screenshot confirmation/result
- Verify lock icon returns
- Verify models list filters again

G. FULL UNLOCK COMMAND
Read /static/js/chat.js for /full_unlock handling.
- With adult mode enabled
- Type /full_unlock enable in chat
- Screenshot command response
- Verify onboarding modal opens (#full-unlock-modal)

H. ONBOARDING MODAL STRUCTURE
Read /static/index.html lines 783-827.
- Screenshot full unlock modal
- Verify elements:
  * Gradient icon (pink-purple)
  * Title "Full Unlock"
  * Progress indicator
  * Intro text (flirty narrative)
  * Questions container (#onboarding-questions)
  * Skip button
  * Next button

I. ONBOARDING QUESTIONS
Read /app/routers/user_profile.py lines 223-493 for question definitions.
- Screenshot first section questions
- Document question types:
  * Enum (dropdown/radio)
  * Boolean (yes/no)
  * Multi-select (checkboxes)
  * Text (free input)
- Test conditional questions (depend_on logic)

J. ONBOARDING NAVIGATION
- Answer questions
- Click Next
- Screenshot next section
- Test Skip button (closes without saving?)
- Navigate through all 5 sections if possible

K. FULL UNLOCK DISABLE
- After enabling, type /full_unlock disable
- Screenshot result
- Verify session unlock removed

L. SESSION-SCOPED BEHAVIOR
Read auth_service.py for session scoping.
- Enable full unlock
- Refresh page
- Is full unlock still active? (should reset)
- Screenshot behavior

OUTPUT: Create findings.md with:
- Adult mode unlock flow
- Passcode modal behavior
- Onboarding question inventory
- Conditional question logic
- Session scoping verification
- Two-tier system documentation
```

---

## AGENT 3: Memory Management UI
**Directory**: `tests/ui_testing/session3/agent3_memory/`
**Focus**: Memory display, CRUD operations, categories

### Prompt for Agent 3:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is MEMORY MANAGEMENT.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent3_memory/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_mem3_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MEMORY SECTION LOCATION
Read /static/index.html lines 494-535.
- Open Settings modal
- Scroll to Memory section
- Screenshot full section

B. MEMORY STATS DISPLAY
- Screenshot stats:
  * Memory count (#memory-count)
  * Category count (#memory-categories)
- Verify numbers format correctly

C. EMPTY MEMORY STATE
- With new user, screenshot empty state
- Verify message: "No memories yet..."
- Screenshot expandable details element

D. VIEW ALL MEMORIES
- Click "View all memories" details element
- Screenshot expanded memory list
- Verify scrollable container (max-height: 256px)

E. CREATE MEMORIES VIA CHAT
Read /app/services/memory_service.py for memory creation.
- Chat about personal preferences
- AI should infer and store memories
- Return to settings
- Screenshot new memories appearing

F. MEMORY CARD DISPLAY
Read /static/js/memory.js for card rendering.
- Screenshot individual memory card
- Verify elements:
  * Content text
  * Category icon and label
  * Source (You asked / Learned)
  * Date
  * Importance flag (if >= 8: yellow "Important")
  * Delete button (hover-only)

G. MEMORY CATEGORIES
Document and screenshot each category:
- personal (person icon)
- preference (favorite icon)
- topic (topic icon)
- instruction (rule icon)
- general (memory icon)

H. DELETE SINGLE MEMORY
- Hover over memory card
- Screenshot delete button appearance (red on hover)
- Click delete
- Screenshot confirmation dialog
- Confirm delete
- Verify memory removed from list

I. CLEAR ALL MEMORIES
- Find "Clear all memories" button (red text)
- Click it
- Screenshot confirmation: "Clear ALL memories? This cannot be undone."
- Cancel first, verify unchanged
- Then confirm, verify all cleared

J. MEMORY PERSISTENCE
- Create memories
- Close settings
- Reopen settings
- Verify memories still there
- Logout, login again
- Verify memories persist

K. MEMORY SEARCH (if available)
- Check if search functionality exists in UI
- Test search if present
- Screenshot results

OUTPUT: Create findings.md with:
- Memory section element inventory
- Category icon mapping
- Memory card structure
- CRUD operation flows
- Persistence verification
- Any UI bugs or missing elements
```

---

## AGENT 4: Knowledge Base Upload & Management
**Directory**: `tests/ui_testing/session3/agent4_knowledge/`
**Focus**: Document upload, management, search

### Prompt for Agent 4:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is KNOWLEDGE BASE.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent4_knowledge/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_kb4_{timestamp}
4. Prepare test files:
   - small_doc.txt (< 1MB, some text)
   - code_sample.py (Python code)
   - test.pdf (if available)
   - large_file.txt (> 150MB for limit testing)

INVESTIGATION TASKS - Screenshot everything:

A. KNOWLEDGE BASE SECTION
Read /static/index.html lines 429-466.
- Open Settings modal
- Screenshot Knowledge Base section
- Verify section title and icon

B. STATS DISPLAY
- Screenshot stats cards:
  * Document count (#kb-doc-count)
  * Chunk count (#kb-chunk-count)
- Verify initial state (0 documents, 0 chunks)

C. UPLOAD AREA STYLING
Read /static/js/knowledge.js for upload logic.
- Screenshot upload area (#kb-upload-area)
- Verify dashed border
- Check icon and text
- Verify accepted file types listed

D. CLICK TO UPLOAD
- Click upload area
- Screenshot file picker dialog
- Verify file type filters in picker
- Select small_doc.txt
- Screenshot upload in progress

E. UPLOAD PROGRESS DISPLAY
Read knowledge.js for progress UI.
- Screenshot progress indicator (#kb-upload-progress)
- Status text (#kb-upload-status)
- Spinning icon
- Verify "Uploading X/Y: filename" format

F. UPLOAD COMPLETION
- Wait for upload to finish
- Screenshot success state
- Verify document appears in list
- Verify stats update (1 document, N chunks)

G. DOCUMENT LIST DISPLAY
Read knowledge.js lines 109-142.
- Screenshot document list (#kb-documents)
- Verify each document shows:
  * File type icon (PDF, text, code)
  * Filename (truncated with tooltip)
  * Chunk count
  * Delete button (hover-only)

H. MULTIPLE FILE UPLOAD
- Upload 3 different files at once
- Screenshot sequential upload process
- Verify all appear in list
- Check stats accumulate correctly

I. DRAG AND DROP UPLOAD
- Drag file onto upload area
- Screenshot drag-over state (border-primary, bg-primary/10)
- Drop file
- Verify upload starts

J. DELETE DOCUMENT
- Hover over document
- Screenshot delete button (red on hover)
- Click delete
- Screenshot confirmation dialog
- Confirm delete
- Verify document removed
- Verify stats decrease

K. FILE SIZE LIMIT
Read knowledge.js for 150MB limit.
- Try uploading large_file.txt (> 150MB)
- Screenshot error alert
- Verify file rejected gracefully

L. FILE TYPE DETECTION
Upload different types and verify icons:
- .pdf → PDF icon
- .txt → text icon
- .py, .js → code icon
- Screenshot each

M. DUPLICATE UPLOAD
- Upload same file twice
- Screenshot behavior
- Should return "duplicate" status
- Verify no duplicate entry in list

OUTPUT: Create findings.md with:
- Upload flow documentation
- Stats update verification
- File type handling
- Size limit enforcement
- Delete flow
- Drag-drop behavior
- Any bugs or improvements needed
```

---

## AGENT 5: Settings Parameters (Sliders & Toggles)
**Directory**: `tests/ui_testing/session3/agent5_parameters/`
**Focus**: Model parameters, compaction settings, range inputs

### Prompt for Agent 5:
```
You are a UI tester for PeanutChat using Playwright + Chromium. Your focus is SETTINGS PARAMETERS.

SETUP:
1. Create test directory: /home/user/PeanutChat/tests/ui_testing/session3/agent5_parameters/
2. App URL: http://localhost:8000
3. Create unique test user: testuser_params5_{timestamp}

INVESTIGATION TASKS - Screenshot everything:

A. MODEL PARAMETERS SECTION
Read /static/index.html lines 537-601.
- Open Settings modal
- Scroll to Model Parameters section
- Screenshot full section

B. TEMPERATURE SLIDER
- Locate #temperature slider
- Screenshot with value display (#temp-value)
- Verify range: 0 to 2, step 0.1
- Default: 0.7
- Slide to min, screenshot
- Slide to max, screenshot
- Verify value display updates

C. TOP P SLIDER
- Locate #top-p slider
- Screenshot with value display (#topp-value)
- Verify range: 0 to 1, step 0.05
- Default: 0.9
- Test full range
- Screenshot min and max values

D. TOP K SLIDER
- Locate #top-k slider
- Screenshot with value display (#topk-value)
- Verify range: 1 to 100, step 1
- Default: 40
- Test extremes

E. CONTEXT LENGTH SLIDER
- Locate #num-ctx slider
- Screenshot with value display (#ctx-value)
- Verify range: 1024 to 32768, step 1024
- Default: 4096
- Test sliding behavior
- Format: shows number with commas?

F. REPEAT PENALTY SLIDER
- Locate #repeat-penalty slider
- Screenshot with value display (#repeat-value)
- Verify range: 1 to 2, step 0.1
- Default: 1.1

G. SLIDER TOOLTIPS
- Hover over info icons (if present)
- Screenshot any tooltip explanations
- Document what each parameter does

H. CONTEXT COMPACTION SECTION
Read index.html lines 604-664.
- Screenshot compaction settings section
- Verify header and description

I. COMPACTION TOGGLE
- Locate #compaction-enabled checkbox
- Screenshot enabled state (default)
- Toggle off
- Screenshot disabled state
- Verify child settings become disabled (opacity 0.5)

J. COMPACTION BUFFER SLIDER
- Locate #compaction-buffer slider
- Screenshot with value (#buffer-value)
- Verify range: 5 to 30, step 5
- Default: 15%
- Test when compaction disabled (should be grayed out)

K. COMPACTION THRESHOLD SLIDER
- Locate #compaction-threshold slider
- Verify range: 50 to 90, step 5
- Default: 70%
- Screenshot value

L. PROTECTED MESSAGES SLIDER
- Locate #compaction-protected slider
- Verify range: 4 to 12, step 1
- Default: 6
- Screenshot value

M. SAVE PARAMETERS
- Change multiple parameters
- Click Save Settings
- Screenshot any feedback
- Verify API call (PUT /api/settings)
- Close and reopen modal
- Verify values persisted

N. PARAMETER EFFECTS
- Set temperature to max (2.0)
- Send chat message
- Observe response randomness
- Set to min (0.0)
- Compare responses
- Document observations

O. COMPACTION IN ACTION
- Enable compaction with low threshold (50%)
- Have long conversation
- Monitor context gauge
- Screenshot when compaction triggers
- Check for any status updates

OUTPUT: Create findings.md with:
- Complete slider inventory
- Range/step/default verification
- Toggle behavior documentation
- Parameter persistence
- Compaction observation
- Any UI bugs or inconsistencies
```

---

## Session 3 Execution Command

```
I need you to run 5 UI testing agents in parallel for PeanutChat Session 3.

Create the test directory structure first, then spawn these 5 agents simultaneously:

1. Agent 1 - User profile forms & inputs (profile section, relationship metrics)
2. Agent 2 - Adult mode & onboarding flows (unlock, full unlock, questions)
3. Agent 3 - Memory management UI (display, CRUD, categories)
4. Agent 4 - Knowledge base upload & management (documents, search)
5. Agent 5 - Settings parameters (sliders, compaction, toggles)

Each agent should:
- Create unique test user
- Use Playwright + Chromium
- Screenshot EVERY interaction
- Read source code to understand expected behavior
- Document findings in their agent directory
- Focus on INVESTIGATION, not fixes

The app is running at http://localhost:8000
```
