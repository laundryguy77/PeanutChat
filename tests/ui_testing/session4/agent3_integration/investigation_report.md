# Submit Button Timeout Investigation Report

**Date:** 2026-01-25  
**Test:** agent3_integration / final_integration_test.js  
**Issue:** Timeout waiting for `button[type="submit"]` selector at "A4: SEND FIRST MESSAGE" step

---

## Executive Summary

**Root Cause:** Test selector mismatch - the test uses `button[type="submit"]` but the actual send button in PeanutChat does NOT have `type="submit"` attribute.

**Is this a real UI bug?** ❌ **NO** - This is a **test selector issue**, not a UI bug. The send button works correctly for real users.

---

## Evidence Reviewed

### Screenshots Analysis

| Screenshot | Description | Observation |
|------------|-------------|-------------|
| `07_A4a_message_typed.png` | State before send attempt | Message text visible in input field. Blue circular send button (↑) visible and appears enabled. UI looks normal. |
| `08_ERROR_state.png` | Error state after timeout | Identical to previous - UI still functional, button still visible. Test timed out, but UI didn't break. |

Both screenshots show:
- Message text typed: "Hello! This is my first message for integration testing. Can you help me?"
- Circular blue send button with up-arrow icon (↑) is **clearly visible and enabled**
- No visual indication of any UI problem

### Test Log Analysis

From `test_output.log`:
```
[2026-01-25T20:29:41.177Z] ❌ ERROR: page.click: Timeout 60000ms exceeded.
Call log:
  - waiting for locator('button[type="submit"]')
```

The test waited 60 seconds for a selector that **does not exist** in the DOM.

### Frontend Code Analysis

**File:** `/home/tech/projects/PeanutChat/static/index.html` (line 378)

```html
<button class="flex items-center justify-center size-10 bg-primary..." 
        id="send-btn" 
        title="Send">
    <span class="material-symbols-outlined text-[20px]">arrow_upward</span>
</button>
```

**Key finding:** The send button:
- ✅ Has `id="send-btn"`
- ✅ Is visible and styled properly
- ❌ Does **NOT** have `type="submit"` attribute

**File:** `/home/tech/projects/PeanutChat/static/js/app.js` (line 1101)

```javascript
document.getElementById('send-btn')?.addEventListener('click', () => {
    // Send message logic
});
```

The button is controlled via JavaScript click listener on `#send-btn`, NOT via form submission.

### Test File Analysis

**File:** `final_integration_test.js` (line 96)

```javascript
await page.click('button[type="submit"]');
```

The test incorrectly assumes the send button has `type="submit"`.

---

## Root Cause Analysis

### Why the test fails:
1. The test uses selector `button[type="submit"]`
2. PeanutChat's send button has `id="send-btn"` but no `type` attribute
3. The button is not inside a `<form>` element - it uses JavaScript click handlers
4. Playwright waits 60 seconds for a non-existent element, then times out

### Why users are NOT affected:
1. The actual button (`#send-btn`) is visible and clickable
2. The JavaScript click handler works correctly
3. Messages send successfully when users click the button
4. The UI is fully functional

---

## Classification

| Aspect | Status |
|--------|--------|
| **Real UI Bug** | ❌ No |
| **Test Infrastructure Issue** | ✅ Yes |
| **User Impact** | None |
| **Priority** | Low (test-only fix needed) |

---

## Recommended Fix

### Option 1: Fix the test selector (Recommended)

**File:** `final_integration_test.js` (line 96)

```javascript
// BEFORE (incorrect):
await page.click('button[type="submit"]');

// AFTER (correct):
await page.click('#send-btn');
```

Also update any other occurrences in the test file that reference `button[type="submit"]` for sending messages (line 96 in the send message context).

**Note:** Some `button[type="submit"]` selectors in the test file are for OTHER forms (login/register modals) where `type="submit"` IS correct. Only the chat send action needs fixing.

### Option 2: Add type="submit" to the button (Not recommended)

**File:** `/home/tech/projects/PeanutChat/static/index.html` (line 378)

```html
<button type="submit" id="send-btn" ...>
```

**Why not recommended:**
- The button is not inside a `<form>` element
- Adding `type="submit"` without a form could cause unexpected behavior
- The current implementation with JavaScript handlers is correct

---

## Verification Steps

After applying Option 1 fix, re-run the test:

```bash
cd /home/tech/projects/PeanutChat/tests/ui_testing/session4/agent3_integration/
node final_integration_test.js
```

The "A4: SEND FIRST MESSAGE" step should now pass.

---

## Conclusion

This is a **test selector bug**, not a PeanutChat UI bug. The application's send button works correctly for all users. The test simply used the wrong CSS selector to find the button.

**Action Required:** Update the test file to use `#send-btn` selector instead of `button[type="submit"]` for the message send action.
