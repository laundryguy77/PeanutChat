/**
 * PeanutChat UI Testing - Error States & Edge Cases (v2)
 * Agent 2 - Session 4
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOTS_DIR = './screenshots';
const timestamp = Date.now();
const TEST_USER = `testuser_error2_${timestamp}`;
const TEST_PASS = 'TestPass123!';

// Ensure screenshots directory exists
if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function screenshot(page, name) {
    const filepath = path.join(SCREENSHOTS_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: true });
    console.log(`📸 Screenshot: ${name}.png`);
    return filepath;
}

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
    console.log('🚀 Starting Error States & Edge Cases Tests');
    console.log(`Test User: ${TEST_USER}`);
    
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();
    page.setDefaultTimeout(60000); // 60 second timeout
    
    const findings = [];
    
    try {
        // ==========================================
        // REGISTRATION & LOGIN
        // ==========================================
        console.log('\n📝 Step 1: Navigate to app...');
        await page.goto(BASE_URL, { waitUntil: 'networkidle' });
        await delay(2000);
        await screenshot(page, '00_initial_page');
        
        // Debug: print page content
        const pageTitle = await page.title();
        console.log(`Page title: ${pageTitle}`);
        
        // Check what's visible
        console.log('\n📝 Step 2: Checking page elements...');
        const bodyText = await page.locator('body').textContent();
        console.log(`Body contains login text: ${bodyText.includes('Login') || bodyText.includes('Sign in')}`);
        console.log(`Body contains register text: ${bodyText.includes('Register') || bodyText.includes('Create')}`);
        
        // Try to find registration form
        const registerTab = page.locator('text=Register, text=Create account, text=Sign up, #register-tab, [data-tab="register"]').first();
        console.log(`Register tab visible: ${await registerTab.isVisible().catch(() => false)}`);
        
        if (await registerTab.isVisible().catch(() => false)) {
            console.log('Clicking register tab...');
            await registerTab.click();
            await delay(1000);
            await screenshot(page, '01_register_form');
        }
        
        // Look for registration fields
        const usernameField = page.locator('input[name="username"], input[id*="username"], input[placeholder*="sername"]').first();
        const passwordField = page.locator('input[type="password"]').first();
        
        if (await usernameField.isVisible().catch(() => false)) {
            console.log('Found username field, filling registration...');
            await usernameField.fill(TEST_USER);
            await passwordField.fill(TEST_PASS);
            
            // Look for confirm password
            const confirmField = page.locator('input[name="confirm"], input[id*="confirm"], input[placeholder*="onfirm"]').first();
            if (await confirmField.isVisible().catch(() => false)) {
                await confirmField.fill(TEST_PASS);
            }
            
            await screenshot(page, '02_filled_registration');
            
            // Submit
            const submitBtn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Register"), button:has-text("Create"), button:has-text("Sign up")').first();
            if (await submitBtn.isVisible().catch(() => false)) {
                console.log('Submitting registration...');
                await submitBtn.click();
                await delay(3000);
                await screenshot(page, '03_after_registration');
            }
        } else {
            console.log('No registration form found, trying login...');
            // Maybe already need login
            await screenshot(page, '02_login_form');
        }
        
        // ==========================================
        // A. EMPTY STATES
        // ==========================================
        console.log('\n📋 A. Testing Empty States...');
        await delay(2000);
        await screenshot(page, 'A1_empty_conversation_state');
        findings.push({
            test: 'A1 - Empty Conversation State',
            status: 'CAPTURED',
            notes: 'Captured initial state after authentication'
        });
        
        // Look for sidebar/settings
        const settingsBtn = page.locator('[aria-label="Settings"], button:has-text("Settings"), .settings-btn').first();
        if (await settingsBtn.isVisible().catch(() => false)) {
            await settingsBtn.click();
            await delay(500);
            await screenshot(page, 'A2_settings_panel');
            await page.keyboard.press('Escape');
        }
        
        // ==========================================
        // B. LONG INPUT HANDLING
        // ==========================================
        console.log('\n📋 B. Testing Long Input Handling...');
        
        const messageInput = page.locator('#message-input, textarea').first();
        if (await messageInput.isVisible().catch(() => false)) {
            const longMessage = 'X'.repeat(5000);
            console.log(`Filling ${longMessage.length} character message...`);
            await messageInput.fill(longMessage);
            await delay(500);
            await screenshot(page, 'B1_long_input_textarea');
            
            const inputValue = await messageInput.inputValue();
            findings.push({
                test: 'B1 - Long Input Textarea',
                status: inputValue.length >= 5000 ? 'PASS' : 'TRUNCATED',
                notes: `Textarea contains ${inputValue.length} chars`
            });
            
            // Try sending
            const sendBtn = page.locator('#send-btn, button[type="submit"]').first();
            if (await sendBtn.isVisible().catch(() => false)) {
                await sendBtn.click();
                await delay(5000);
                await screenshot(page, 'B2_long_message_result');
                findings.push({
                    test: 'B2 - Long Message Send',
                    status: 'CAPTURED',
                    notes: 'Attempted to send 5000 char message'
                });
            }
        }
        
        // ==========================================
        // C. SPECIAL CHARACTERS / XSS
        // ==========================================
        console.log('\n📋 C. Testing XSS Prevention...');
        
        if (await messageInput.isVisible().catch(() => false)) {
            await messageInput.fill('');
            await delay(300);
            
            const xssPayload = '<script>alert("xss")</script>';
            await messageInput.fill(xssPayload);
            await screenshot(page, 'C1_xss_input');
            
            const sendBtn = page.locator('#send-btn, button[type="submit"]').first();
            if (await sendBtn.isVisible().catch(() => false)) {
                await sendBtn.click();
                await delay(3000);
                await screenshot(page, 'C2_xss_after_send');
            }
            
            // Check for unescaped script
            const html = await page.content();
            const hasRawScript = html.includes('<script>alert');
            findings.push({
                test: 'C1 - XSS Prevention',
                status: hasRawScript ? 'FAIL - VULNERABLE' : 'PASS - SAFE',
                notes: hasRawScript ? 'Raw script tag found in HTML!' : 'Script tags properly escaped or removed'
            });
        }
        
        // ==========================================
        // D. MOBILE VIEWPORT
        // ==========================================
        console.log('\n📋 D. Testing Mobile Viewport...');
        
        await page.setViewportSize({ width: 375, height: 667 });
        await delay(500);
        await screenshot(page, 'D1_mobile_viewport');
        findings.push({
            test: 'D1 - Mobile Viewport',
            status: 'CAPTURED',
            notes: 'Resized to 375x667 iPhone SE dimensions'
        });
        
        // Check for hamburger menu
        const hamburger = page.locator('[aria-label="Menu"], .hamburger, #menu-toggle, button:has(.material-symbols-outlined:text("menu"))').first();
        if (await hamburger.isVisible({ timeout: 2000 }).catch(() => false)) {
            await hamburger.click();
            await delay(500);
            await screenshot(page, 'D2_mobile_menu_open');
            findings.push({
                test: 'D2 - Mobile Menu',
                status: 'CAPTURED',
                notes: 'Hamburger menu found and opened'
            });
            await page.keyboard.press('Escape');
        } else {
            findings.push({
                test: 'D2 - Mobile Menu',
                status: 'NOT_FOUND',
                notes: 'No hamburger menu visible on mobile'
            });
        }
        
        // Reset viewport
        await page.setViewportSize({ width: 1280, height: 800 });
        await delay(500);
        
        // ==========================================
        // E. KEYBOARD NAVIGATION
        // ==========================================
        console.log('\n📋 E. Testing Keyboard Navigation...');
        
        // Tab through elements
        await page.keyboard.press('Tab');
        await delay(200);
        await screenshot(page, 'E1_tab_focus_1');
        
        for (let i = 0; i < 5; i++) {
            await page.keyboard.press('Tab');
            await delay(150);
        }
        await screenshot(page, 'E2_tab_focus_5');
        
        findings.push({
            test: 'E1 - Keyboard Navigation',
            status: 'CAPTURED',
            notes: 'Captured tab navigation through UI'
        });
        
        // Test Enter to send
        await messageInput.focus();
        await messageInput.fill('Enter key test');
        await page.keyboard.press('Enter');
        await delay(1000);
        await screenshot(page, 'E3_enter_key_submit');
        findings.push({
            test: 'E2 - Enter Key Submit',
            status: 'CAPTURED',
            notes: 'Tested Enter key submission'
        });
        
        // ==========================================
        // F. API ERROR STATES
        // ==========================================
        console.log('\n📋 F. Testing API Error States...');
        
        // Block API calls
        await page.route('**/api/chat/**', route => route.abort('failed'));
        
        await messageInput.fill('Trigger network error');
        const sendBtn = page.locator('#send-btn, button[type="submit"]').first();
        if (await sendBtn.isVisible().catch(() => false)) {
            await sendBtn.click();
        }
        await delay(3000);
        await screenshot(page, 'F1_network_error');
        
        // Check for error indication
        const errorToast = await page.locator('.bg-red-600, [role="alert"], .error, .toast-error').first().isVisible().catch(() => false);
        findings.push({
            test: 'F1 - Network Error',
            status: errorToast ? 'PASS - Error Shown' : 'NEEDS_REVIEW',
            notes: `Error toast visible: ${errorToast}`
        });
        
        await page.unroute('**/api/chat/**');
        
        // ==========================================
        // G. SESSION HANDLING
        // ==========================================
        console.log('\n📋 G. Testing Session Handling...');
        
        await screenshot(page, 'G1_before_refresh');
        await page.reload({ waitUntil: 'networkidle' });
        await delay(2000);
        await screenshot(page, 'G2_after_refresh');
        
        const stillLoggedIn = await messageInput.isVisible().catch(() => false);
        findings.push({
            test: 'G1 - Session After Refresh',
            status: stillLoggedIn ? 'PASS' : 'FAIL',
            notes: `Session maintained after refresh: ${stillLoggedIn}`
        });
        
        // ==========================================
        // GENERATE REPORT
        // ==========================================
        console.log('\n📊 Generating Report...');
        
        let report = `# PeanutChat UI Testing - Error States & Edge Cases
## Session 4 - Agent 2

**Test User:** ${TEST_USER}
**Date:** ${new Date().toISOString()}

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | ${findings.length} |
| Passed/Captured | ${findings.filter(f => f.status.includes('PASS') || f.status === 'CAPTURED').length} |
| Failed | ${findings.filter(f => f.status.includes('FAIL')).length} |
| Needs Review | ${findings.filter(f => f.status.includes('REVIEW') || f.status === 'NOT_FOUND').length} |

---

## Detailed Findings

`;

        for (const f of findings) {
            const emoji = f.status.includes('FAIL') ? '❌' : 
                          f.status.includes('REVIEW') || f.status === 'NOT_FOUND' ? '⚠️' : '✅';
            report += `### ${emoji} ${f.test}\n`;
            report += `- **Status:** ${f.status}\n`;
            report += `- **Notes:** ${f.notes}\n\n`;
        }

        report += `---

## Screenshots

`;
        const screenshots = fs.readdirSync(SCREENSHOTS_DIR).filter(f => f.endsWith('.png')).sort();
        for (const ss of screenshots) {
            report += `- \`${ss}\`\n`;
        }

        report += `

---

## Code Analysis

### XSS Protection (from chat.js)
- Uses **DOMPurify** for HTML sanitization
- FORBID_TAGS: script, iframe, object, embed, form, input, textarea
- FORBID_ATTR: onerror, onload, onmouseover, onfocus, onblur
- \`escapeHtml()\` function for safe text rendering

### Session Management (from auth.js)
- Uses \`sessionStorage\` marker for tab detection
- Cookie + session marker combo for authentication
- Token auto-refresh every 20 minutes
- New tabs require re-login (security feature)

### Error Handling
- \`showToast()\` for user notifications
- Types: error (red), success (green), warning (yellow), info (blue)
- AbortController for cancellable requests

---

## Recommendations

1. **Long Input**: Add client-side character limit indicator
2. **Mobile**: Ensure all touch targets are ≥44px
3. **Accessibility**: Add skip-to-content link
4. **Error States**: Show more context in error messages
5. **Network Errors**: Implement retry mechanism with backoff
`;

        fs.writeFileSync('findings.md', report);
        console.log('✅ Report saved to findings.md');
        
    } catch (error) {
        console.error('❌ Test error:', error.message);
        await screenshot(page, 'ERROR_state');
        
        // Still generate partial report
        fs.writeFileSync('findings.md', `# Error During Testing\n\nError: ${error.message}\n\nPartial findings: ${JSON.stringify(findings, null, 2)}`);
    } finally {
        await browser.close();
        console.log('\n✅ Browser closed');
    }
}

runTests().catch(console.error);
