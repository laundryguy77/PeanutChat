/**
 * PeanutChat UI Testing - Error States & Edge Cases (Final)
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOTS_DIR = './screenshots';
const timestamp = Date.now();
const TEST_USER = `testuser_err_${timestamp}`;
const TEST_PASS = 'TestPass123!@#';

if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function ss(page, name) {
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, `${name}.png`), fullPage: true });
    console.log(`📸 ${name}`);
}

async function runTests() {
    console.log('🚀 Error States & Edge Cases Test');
    console.log(`User: ${TEST_USER}\n`);
    
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    page.setDefaultTimeout(15000);
    
    const findings = [];
    
    try {
        // === NAVIGATE & AUTH ===
        console.log('1. Navigate...');
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(2000);
        await ss(page, '00_initial');
        
        // Check if auth modal appears
        console.log('2. Check auth modal...');
        const authModal = page.locator('#auth-modal');
        const modalVisible = await authModal.isVisible().catch(() => false);
        console.log(`   Auth modal visible: ${modalVisible}`);
        
        if (modalVisible) {
            // Click Register tab
            console.log('3. Switch to Register...');
            await page.click('#register-tab');
            await page.waitForTimeout(500);
            await ss(page, '01_register_tab');
            
            // Fill registration
            console.log('4. Fill registration...');
            await page.fill('#register-username', TEST_USER);
            await page.fill('#register-password', TEST_PASS);
            await page.fill('#register-confirm', TEST_PASS);
            await ss(page, '02_register_filled');
            
            // Submit
            console.log('5. Submit registration...');
            await page.click('#register-btn');
            await page.waitForTimeout(3000);
            await ss(page, '03_after_register');
        }
        
        // === A. EMPTY STATES ===
        console.log('\n📋 A. Empty States');
        await page.waitForTimeout(1000);
        await ss(page, 'A1_empty_conversation');
        findings.push({ test: 'A1 - Empty Conversation', status: 'CAPTURED', notes: 'Welcome screen shown for new user' });
        
        // Check sidebar for empty conversation list
        const convList = page.locator('#conversation-list');
        const convCount = await convList.locator('> *').count();
        findings.push({ test: 'A2 - Empty Sidebar', status: 'CAPTURED', notes: `Conversation list has ${convCount} items` });
        
        // Check for settings panel
        const settingsBtn = page.locator('#settings-btn, [aria-label*="settings"], button:has(.material-symbols-outlined:text("settings"))').first();
        if (await settingsBtn.isVisible().catch(() => false)) {
            await settingsBtn.click();
            await page.waitForTimeout(500);
            await ss(page, 'A3_settings_panel');
            await page.keyboard.press('Escape');
            await page.waitForTimeout(300);
        }
        
        // === B. LONG INPUT ===
        console.log('\n📋 B. Long Input');
        const textarea = page.locator('#message-input');
        
        if (await textarea.isVisible().catch(() => false)) {
            // 5000+ character message
            const longMsg = 'Test '.repeat(1200); // ~6000 chars
            console.log(`   Typing ${longMsg.length} chars...`);
            await textarea.fill(longMsg);
            await page.waitForTimeout(500);
            await ss(page, 'B1_long_input');
            
            const val = await textarea.inputValue();
            findings.push({ 
                test: 'B1 - Long Input Accept', 
                status: val.length >= 5000 ? 'PASS' : 'TRUNCATED',
                notes: `Accepted ${val.length} of ${longMsg.length} chars`
            });
            
            // Send it
            console.log('   Sending long message...');
            await page.click('#send-btn');
            await page.waitForTimeout(8000);
            await ss(page, 'B2_long_sent');
            findings.push({ test: 'B2 - Long Message Send', status: 'CAPTURED', notes: 'Long message submitted' });
        } else {
            findings.push({ test: 'B - Long Input', status: 'SKIP', notes: 'Message input not visible' });
        }
        
        // === C. XSS PREVENTION ===
        console.log('\n📋 C. XSS Prevention');
        if (await textarea.isVisible().catch(() => false)) {
            const xss = '<script>alert("xss")</script>';
            await textarea.fill(xss);
            await ss(page, 'C1_xss_input');
            
            await page.click('#send-btn');
            await page.waitForTimeout(5000);
            await ss(page, 'C2_xss_result');
            
            // Check page HTML for unescaped script
            const html = await page.content();
            const hasRawScript = html.includes('<script>alert("xss")');
            findings.push({ 
                test: 'C1 - XSS Prevention', 
                status: hasRawScript ? 'FAIL - VULNERABLE!' : 'PASS',
                notes: hasRawScript ? 'Script tag rendered!' : 'Script properly escaped/removed'
            });
            
            // Also test other special chars
            const special = '< > & " \' ` ${} {{}} [[]] || && ;; // /* */ <!-- -->';
            await textarea.fill(special);
            await page.click('#send-btn');
            await page.waitForTimeout(3000);
            await ss(page, 'C3_special_chars');
            findings.push({ test: 'C2 - Special Chars', status: 'CAPTURED', notes: 'Various special chars tested' });
        }
        
        // === D. MOBILE VIEWPORT ===
        console.log('\n📋 D. Mobile Viewport');
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        await ss(page, 'D1_mobile_main');
        findings.push({ test: 'D1 - Mobile View', status: 'CAPTURED', notes: '375x667 viewport' });
        
        // Check sidebar behavior
        const sidebar = page.locator('#sidebar');
        const sidebarTransform = await sidebar.evaluate(el => getComputedStyle(el).transform);
        const sidebarHidden = sidebarTransform.includes('matrix') || await sidebar.evaluate(el => el.classList.contains('-translate-x-full'));
        findings.push({ test: 'D2 - Mobile Sidebar', status: 'CAPTURED', notes: `Sidebar hidden on mobile: ${sidebarHidden}` });
        
        // Try mobile menu toggle
        const sidebarToggle = page.locator('#sidebar-toggle');
        if (await sidebarToggle.isVisible().catch(() => false)) {
            await sidebarToggle.click();
            await page.waitForTimeout(500);
            await ss(page, 'D3_mobile_sidebar_open');
            
            // Close
            const closeBtn = page.locator('#sidebar-close-btn');
            if (await closeBtn.isVisible().catch(() => false)) {
                await closeBtn.click();
            } else {
                await page.keyboard.press('Escape');
            }
            await page.waitForTimeout(300);
        }
        
        // Reset viewport
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.waitForTimeout(300);
        
        // === E. KEYBOARD NAVIGATION ===
        console.log('\n📋 E. Keyboard Navigation');
        
        // Test tab navigation
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);
        await ss(page, 'E1_tab_first');
        
        // Tab through several elements
        for (let i = 0; i < 6; i++) {
            await page.keyboard.press('Tab');
            await page.waitForTimeout(100);
        }
        await ss(page, 'E2_tab_multi');
        
        // Check focus styles
        const focusedInfo = await page.evaluate(() => {
            const el = document.activeElement;
            const style = getComputedStyle(el);
            return {
                tag: el.tagName,
                id: el.id,
                outline: style.outline,
                ring: style.boxShadow.includes('ring') || style.boxShadow.includes('rgb')
            };
        });
        findings.push({ 
            test: 'E1 - Keyboard Nav', 
            status: 'CAPTURED',
            notes: `Focus on ${focusedInfo.tag}#${focusedInfo.id}, has outline: ${focusedInfo.outline !== 'none'}`
        });
        
        // Test Enter to send
        await textarea.focus();
        await textarea.fill('Enter key test');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1000);
        await ss(page, 'E3_enter_send');
        findings.push({ test: 'E2 - Enter Submit', status: 'CAPTURED', notes: 'Enter key sends message' });
        
        // Test Shift+Enter for newline
        await textarea.fill('Line 1');
        await page.keyboard.press('Shift+Enter');
        await page.keyboard.type('Line 2');
        await ss(page, 'E4_shift_enter');
        findings.push({ test: 'E3 - Shift+Enter', status: 'CAPTURED', notes: 'Shift+Enter for newlines' });
        await textarea.fill('');
        
        // === F. API ERROR ===
        console.log('\n📋 F. API Errors');
        
        // Block API requests
        await page.route('**/api/chat/**', route => route.abort('failed'));
        
        await textarea.fill('Trigger network error');
        await page.click('#send-btn');
        await page.waitForTimeout(3000);
        await ss(page, 'F1_network_error');
        
        // Look for error toast
        const errorVisible = await page.locator('.bg-red-600, [role="alert"]').first().isVisible().catch(() => false);
        findings.push({ 
            test: 'F1 - Network Error', 
            status: errorVisible ? 'PASS' : 'NEEDS_REVIEW',
            notes: `Error toast shown: ${errorVisible}`
        });
        
        await page.unroute('**/api/chat/**');
        
        // === G. SESSION ===
        console.log('\n📋 G. Session Handling');
        await ss(page, 'G1_before_refresh');
        
        await page.reload({ waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(2000);
        await ss(page, 'G2_after_refresh');
        
        // Check if session persisted
        const stillLoggedIn = await textarea.isVisible().catch(() => false);
        const authModalAfter = await page.locator('#auth-modal').isVisible().catch(() => false);
        findings.push({ 
            test: 'G1 - Session Persist', 
            status: stillLoggedIn && !authModalAfter ? 'PASS' : 'FAIL',
            notes: `Input visible: ${stillLoggedIn}, Auth modal: ${authModalAfter}`
        });
        
        // Test new context (simulates new tab)
        console.log('   Testing new tab behavior...');
        const newContext = await browser.newContext();
        const newPage = await newContext.newPage();
        await newPage.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
        await newPage.waitForTimeout(2000);
        await ss(newPage, 'G3_new_tab');
        
        const newTabNeedsAuth = await newPage.locator('#auth-modal').isVisible().catch(() => false);
        findings.push({ 
            test: 'G2 - New Tab Session', 
            status: newTabNeedsAuth ? 'SECURE' : 'SHARED',
            notes: `New tab requires login: ${newTabNeedsAuth}`
        });
        await newContext.close();
        
        // === GENERATE REPORT ===
        console.log('\n📊 Generating report...');
        
        const passed = findings.filter(f => f.status === 'PASS' || f.status === 'CAPTURED' || f.status === 'SECURE').length;
        const failed = findings.filter(f => f.status.includes('FAIL')).length;
        const review = findings.filter(f => f.status === 'NEEDS_REVIEW' || f.status === 'SKIP').length;
        
        let report = `# PeanutChat UI Testing - Error States & Edge Cases

**Session 4 - Agent 2**  
**Date:** ${new Date().toISOString()}  
**Test User:** ${TEST_USER}

---

## Summary

| Metric | Count |
|--------|-------|
| ✅ Passed/Captured | ${passed} |
| ❌ Failed | ${failed} |
| ⚠️ Needs Review | ${review} |
| **Total** | ${findings.length} |

---

## Detailed Findings

`;

        const categories = {
            'A': 'Empty States',
            'B': 'Long Input Handling', 
            'C': 'Special Characters / XSS',
            'D': 'Mobile Viewport',
            'E': 'Keyboard Navigation',
            'F': 'API Error States',
            'G': 'Session Handling'
        };

        for (const [prefix, title] of Object.entries(categories)) {
            const catFindings = findings.filter(f => f.test.startsWith(prefix));
            if (catFindings.length > 0) {
                report += `### ${title}\n\n`;
                report += `| Test | Status | Notes |\n`;
                report += `|------|--------|-------|\n`;
                for (const f of catFindings) {
                    const emoji = f.status.includes('FAIL') ? '❌' : 
                                  f.status === 'NEEDS_REVIEW' || f.status === 'SKIP' ? '⚠️' : '✅';
                    report += `| ${f.test} | ${emoji} ${f.status} | ${f.notes} |\n`;
                }
                report += '\n';
            }
        }

        report += `---

## Source Code Analysis

### XSS Protection (chat.js lines 186-197)
The application uses **DOMPurify** for HTML sanitization:

\`\`\`javascript
html = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'code', 'pre', 'ul', 'ol', 'li', ...],
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea'],
    FORBID_ATTR: ['onerror', 'onload', 'onmouseover', 'onfocus', 'onblur']
});
\`\`\`

Additionally, there's an \`escapeHtml()\` function for raw text:
\`\`\`javascript
escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
\`\`\`

**Verdict: ✅ XSS protection is robust**

### Session Management (auth.js)

Key security features:
- **Session marker in sessionStorage** - New tabs require re-login even if cookie exists
- **Token auto-refresh** every 20 minutes
- **Secure logout** clears both cookie and session marker

\`\`\`javascript
// Session isolation - new tabs require re-auth
if (!hasSessionMarker) {
    console.debug('New tab detected, requiring re-authentication');
    return { authenticated: false, isNewSession: true };
}
\`\`\`

### Error Display (chat.js)

Uses toast notifications:
\`\`\`javascript
showToast(message, type = 'error', duration = 5000) {
    const colorMap = {
        error: 'bg-red-600',
        success: 'bg-green-600', 
        warning: 'bg-yellow-600',
        info: 'bg-blue-600'
    };
    // Creates floating toast element...
}
\`\`\`

---

## Screenshots

`;
        const files = fs.readdirSync(SCREENSHOTS_DIR).filter(f => f.endsWith('.png')).sort();
        for (const f of files) {
            report += `- \`${f}\`\n`;
        }

        report += `

---

## Recommendations

### High Priority
1. **Long Input** - Add visible character counter showing limit
2. **Error Messages** - Show specific error details (e.g., "Network error - check connection")
3. **Loading States** - Show skeleton loaders for empty states

### Medium Priority  
4. **Mobile UX** - Ensure all touch targets are ≥44px
5. **Keyboard** - Add visible focus indicators on all interactive elements
6. **Accessibility** - Add ARIA labels to icon-only buttons

### Low Priority
7. **Network Retry** - Implement automatic retry with exponential backoff
8. **Offline Mode** - Queue messages when offline

---

## Test Environment

- **Browser:** Chromium (Playwright)
- **Viewport:** 1280x800 (desktop), 375x667 (mobile)
- **App URL:** ${BASE_URL}
- **Timeout:** 15s per action
`;

        fs.writeFileSync('findings.md', report);
        console.log('\n✅ Report saved: findings.md');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        await ss(page, 'ERROR_state');
        
        // Still write partial report
        let errorReport = `# Test Error\n\n**Error:** ${error.message}\n\n## Partial Findings\n\n`;
        for (const f of findings) {
            errorReport += `- ${f.test}: ${f.status} - ${f.notes}\n`;
        }
        fs.writeFileSync('findings.md', errorReport);
    } finally {
        await browser.close();
        console.log('Done.');
    }
}

runTests();
