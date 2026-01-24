# CONSOLIDATION SESSION PROMPT

Copy this into a Claude Code session after all 4 testing sessions complete.

---

```
I need you to consolidate findings from 20 UI testing agents into actionable reports.

Base directory: /home/user/PeanutChat/tests/ui_testing/

## STEP 1: Read All Findings

Read all findings.md files from these directories:

Session 1:
- session1/agent1_auth/findings.md
- session1/agent2_sidebar/findings.md
- session1/agent3_themes/findings.md
- session1/agent4_settings/findings.md
- session1/agent5_models/findings.md

Session 2:
- session2/agent1_messaging/findings.md
- session2/agent2_streaming/findings.md
- session2/agent3_edit_fork/findings.md
- session2/agent4_attachments/findings.md
- session2/agent5_thinking/findings.md

Session 3:
- session3/agent1_profile/findings.md
- session3/agent2_adult_mode/findings.md
- session3/agent3_memory/findings.md
- session3/agent4_knowledge/findings.md
- session3/agent5_parameters/findings.md

Session 4:
- session4/agent1_mcp/findings.md
- session4/agent2_model_switch/findings.md
- session4/agent3_compaction/findings.md
- session4/agent4_errors/findings.md
- session4/agent5_integration/findings.md

## STEP 2: Create CONSOLIDATED_REPORT.md

Create tests/ui_testing/CONSOLIDATED_REPORT.md with this structure:

# PeanutChat UI Testing - Consolidated Report

## Executive Summary
- Total issues found: X
- Critical: X | High: X | Medium: X | Low: X
- Areas most affected: [list]
- Recommended priority order for fixes

## 1. CRITICAL ISSUES (Severity: Critical)
Features broken, unusable, or security concerns.
For each:
- **Issue**: [description]
- **Location**: [feature area]
- **Evidence**: [screenshot path]
- **Code Reference**: [file:line]
- **Reproduction**: [steps]
- **Agent Source**: [which agent found it]

## 2. FUNCTIONAL DISCREPANCIES (Severity: High)
Code says one thing, UI does another.
For each:
- **Issue**: [description]
- **Expected (from code)**: [what code defines]
- **Actual (from UI)**: [what screenshot shows]
- **Code Reference**: [file:line]
- **Screenshot**: [path]

## 3. MISSING UI ELEMENTS (Severity: High)
Code defines elements that don't appear in UI.
For each:
- **Element**: [ID or description]
- **Defined In**: [file:line]
- **Expected Location**: [where it should appear]
- **Screenshot Showing Absence**: [path]

## 4. ORPHAN UI ELEMENTS (Severity: Medium)
UI shows elements with no code backing or dead functionality.
For each:
- **Element**: [description]
- **Location**: [where in UI]
- **Screenshot**: [path]
- **Expected Code**: [where code should be]

## 5. VISUAL/STYLING BUGS (Severity: Medium)
Layout issues, styling inconsistencies, responsive problems.
For each:
- **Issue**: [description]
- **Affected Area**: [component/page]
- **Screenshot**: [path]
- **CSS Reference**: [file:line if applicable]

## 6. UX CONCERNS (Severity: Medium)
Confusing flows, poor feedback, unclear states.
For each:
- **Concern**: [description]
- **User Impact**: [how it affects users]
- **Current Flow**: [what happens now]
- **Screenshot**: [path]

## 7. ERROR HANDLING GAPS (Severity: Medium)
Missing error states, poor error messages, unhandled edge cases.
For each:
- **Scenario**: [what triggers it]
- **Current Behavior**: [what happens]
- **Expected Behavior**: [what should happen]
- **Screenshot**: [path]

## 8. EDGE CASE FAILURES (Severity: Low)
Unusual inputs, boundary conditions, race conditions.
For each:
- **Case**: [description]
- **Input/Condition**: [what was tested]
- **Result**: [what happened]
- **Screenshot**: [path]

## 9. OBSERVATIONS (Severity: Info)
Not bugs, but noteworthy findings, patterns, or improvement opportunities.

## 10. TESTING GAPS
Areas that couldn't be fully tested and why.

---

## STEP 3: Create ISSUE_MATRIX.md

Create tests/ui_testing/ISSUE_MATRIX.md:

# Issue Matrix by Feature Area

| Feature Area | Critical | High | Medium | Low | Total |
|--------------|----------|------|--------|-----|-------|
| Authentication | | | | | |
| Sidebar/Navigation | | | | | |
| Themes | | | | | |
| Settings Modal | | | | | |
| Model Selector | | | | | |
| Chat/Messaging | | | | | |
| Streaming | | | | | |
| Edit/Fork/Regenerate | | | | | |
| Attachments | | | | | |
| Thinking Mode | | | | | |
| User Profile | | | | | |
| Adult Mode | | | | | |
| Memory System | | | | | |
| Knowledge Base | | | | | |
| Parameters/Sliders | | | | | |
| MCP Servers | | | | | |
| Context Compaction | | | | | |
| Error Handling | | | | | |
| **TOTAL** | | | | | |

## Issue Type Distribution

| Issue Type | Count | % of Total |
|------------|-------|------------|
| Functional Discrepancy | | |
| Missing Element | | |
| Orphan Element | | |
| Visual Bug | | |
| UX Concern | | |
| Error Handling Gap | | |
| Edge Case Failure | | |

---

## STEP 4: Create SCREENSHOT_INDEX.md

Create tests/ui_testing/SCREENSHOT_INDEX.md:

# Screenshot Index

Organized catalog of all captured screenshots.

## Session 1: Foundation & Navigation

### Agent 1 - Authentication
| Screenshot | Description | Issue Reference |
|------------|-------------|-----------------|
| [path] | [what it shows] | [issue # if applicable] |

### Agent 2 - Sidebar
...

(Continue for all 20 agents)

---

## STEP 5: Create PRIORITY_FIXES.md

Create tests/ui_testing/PRIORITY_FIXES.md:

# Priority Fix List

Ordered by impact and effort.

## Immediate (Fix This Week)
Issues blocking core functionality.

| # | Issue | Severity | Effort | Files to Modify |
|---|-------|----------|--------|-----------------|
| 1 | | | | |

## Short-Term (Fix This Sprint)
High-impact issues that should be addressed soon.

| # | Issue | Severity | Effort | Files to Modify |
|---|-------|----------|--------|-----------------|

## Medium-Term (Backlog)
Important but not urgent.

| # | Issue | Severity | Effort | Files to Modify |
|---|-------|----------|--------|-----------------|

## Low Priority (Nice to Have)
Minor improvements when time permits.

| # | Issue | Severity | Effort | Files to Modify |
|---|-------|----------|--------|-----------------|

---

## STEP 6: Create VERIFICATION_CHECKLIST.md

Create tests/ui_testing/VERIFICATION_CHECKLIST.md:

# Post-Fix Verification Checklist

Use this to verify fixes after implementation.

## Critical Issues
- [ ] Issue #1: [description] - Retest: [specific steps]
- [ ] Issue #2: ...

## High Priority Issues
- [ ] Issue #X: [description] - Retest: [specific steps]

(Continue for all issues)

---

## OUTPUT SUMMARY

When complete, you should have created:
1. CONSOLIDATED_REPORT.md - Main findings document
2. ISSUE_MATRIX.md - Feature × severity breakdown
3. SCREENSHOT_INDEX.md - Organized screenshot catalog
4. PRIORITY_FIXES.md - Prioritized fix list
5. VERIFICATION_CHECKLIST.md - Post-fix testing guide

Report completion with:
- Total issues found by severity
- Top 5 most affected areas
- Recommended first fixes
```

---

## After Consolidation

Once you have the consolidated reports, your options:

| Next Step | Command |
|-----------|---------|
| Review reports | Read the .md files |
| Start fixing | Create fix sessions based on PRIORITY_FIXES.md |
| Deep dive | Re-run specific agents with more focus |
| Share findings | Reports are ready for stakeholder review |
