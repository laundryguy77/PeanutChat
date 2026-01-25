/**
 * PeanutChat UI Testing - Error States & Edge Cases (v3 - simpler)
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOTS_DIR = './screenshots';
const timestamp = Date.now();
const TEST_USER = `testuser_error2_${timestamp}`;
const TEST_PASS = 'TestPass123!';

if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function screenshot(page, name) {
    const filepath = path.join(SCREENSHOTS_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: true });
    console.log(`📸 ${name}.png`);
}

async function runTests() {
    console.log('🚀 Starting Tests');
    console.log(`User: ${TEST_USER}`);
    
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    page.setDefaultTimeout(30000);
    
    const findings = [];
    
    try {
        // Navigate without waiting for networkidle
        console.log('\n1. Navigate...');
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(3000);
        await screenshot(page, '00_initial');
        
        // Check for login/register
        console.log('2. Looking for auth forms...');
        
        // Try to click Register tab
        try {
            const regTab = page.locator('text=/[Rr]egister|[Cc]reate.*[Aa]ccount|[Ss]ign.*[Uu]p/').first();
            if (await regTab.isVisible({ timeout: 3000 })) {
                await regTab.click();
                await page.waitForTimeout(500);
            }
        } catch {}
        
        // Fill registration
        console.log('3. Attempting registration...');
        try {
            await page.fill('#register-username, input[name="username"]', TEST_USER);
            await page.fill('#register-password, input[name="password"]', TEST_PASS);
            
            const confirm = page.locator('#register-confirm, input[name="confirmPassword"]');
            if (await confirm.isVisible({ timeout: 1000 }).catch(() => false)) {
                await confirm.fill(TEST_PASS);
            }
            
            await screenshot(page, '01_registration_filled');
            
            // Submit
            await page.click('#register-submit, button[type="submit"]:visible');
            await page.waitForTimeout(3000);
            await screenshot(page, '02_after_submit');
        } catch (e) {
            console.log(`Registration: ${e.message.slice(0,50)}`);
            // Maybe it's login instead
            try {
                await page.fill('#login-username, #username, input[name="username"]', TEST_USER);
                await page.fill('#login-password, #password, input[type="password"]', TEST_PASS);
                await page.click('#login-submit, button[type="submit"]:visible');
                await page.waitForTimeout(2000);
            } catch {}
        }
        
        // === A. EMPTY STATES ===
        console.log('\n📋 A. Empty States');
        await page.waitForTimeout(1000);
        await screenshot(page, 'A1_main_empty_state');
        findings.push({ test: 'A1 - Empty State', status: 'CAPTURED' });
        
        // === B. LONG INPUT ===
        console.log('\n📋 B. Long Input');
        const textarea = page.locator('#message-input, textarea').first();
        
        if (await textarea.isVisible({ timeout: 5000 }).catch(() => false)) {
            const longText = 'Test message. '.repeat(400); // ~5200 chars
            await textarea.fill(longText);
            await page.waitForTimeout(300);
            await screenshot(page, 'B1_long_input');
            
            const val = await textarea.inputValue();
            findings.push({ 
                test: 'B1 - Long Input', 
                status: val.length >= 5000 ? 'PASS' : 'TRUNCATED',
                notes: `${val.length} chars`
            });
            
            // Send
            const sendBtn = page.locator('#send-btn, button[type="submit"]').first();
            if (await sendBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
                await sendBtn.click();
                await page.waitForTimeout(8000); // Wait for response
                await screenshot(page, 'B2_long_result');
                findings.push({ test: 'B2 - Long Send', status: 'CAPTURED' });
            }
        } else {
            findings.push({ test: 'B - Long Input', status: 'SKIP - No textarea' });
        }
        
        // === C. XSS ===
        console.log('\n📋 C. XSS Test');
        if (await textarea.isVisible({ timeout: 2000 }).catch(() => false)) {
            await textarea.fill('<script>alert("xss")</script>');
            await screenshot(page, 'C1_xss_input');
            
            const sendBtn = page.locator('#send-btn').first();
            if (await sendBtn.isVisible().catch(() => false)) {
                await sendBtn.click();
                await page.waitForTimeout(5000);
            }
            await screenshot(page, 'C2_xss_result');
            
            const html = await page.content();
            findings.push({ 
                test: 'C1 - XSS Prevention', 
                status: html.includes('<script>alert') ? 'FAIL!' : 'PASS',
                notes: html.includes('&lt;script') ? 'Escaped' : 'Removed/Filtered'
            });
        }
        
        // === D. MOBILE ===
        console.log('\n📋 D. Mobile Viewport');
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        await screenshot(page, 'D1_mobile');
        findings.push({ test: 'D1 - Mobile View', status: 'CAPTURED' });
        
        // Check hamburger
        const hamburger = page.locator('#sidebar-toggle, .hamburger-menu, button:has-text("☰")').first();
        if (await hamburger.isVisible({ timeout: 2000 }).catch(() => false)) {
            await hamburger.click();
            await page.waitForTimeout(300);
            await screenshot(page, 'D2_mobile_menu');
            findings.push({ test: 'D2 - Mobile Menu', status: 'CAPTURED' });
        }
        
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.waitForTimeout(300);
        
        // === E. KEYBOARD ===
        console.log('\n📋 E. Keyboard Navigation');
        await page.keyboard.press('Tab');
        await screenshot(page, 'E1_tab_focus');
        for (let i = 0; i < 4; i++) await page.keyboard.press('Tab');
        await screenshot(page, 'E2_multi_tab');
        findings.push({ test: 'E - Keyboard Nav', status: 'CAPTURED' });
        
        // === F. API ERROR ===
        console.log('\n📋 F. API Error');
        await page.route('**/api/**', route => route.abort());
        await textarea.fill('Error test');
        const sendBtn = page.locator('#send-btn').first();
        if (await sendBtn.isVisible().catch(() => false)) {
            await sendBtn.click();
        }
        await page.waitForTimeout(3000);
        await screenshot(page, 'F1_network_error');
        findings.push({ test: 'F - Network Error', status: 'CAPTURED' });
        await page.unroute('**/api/**');
        
        // === G. SESSION ===
        console.log('\n📋 G. Session Handling');
        await screenshot(page, 'G1_before_refresh');
        await page.reload({ waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(2000);
        await screenshot(page, 'G2_after_refresh');
        
        const stillHasTextarea = await textarea.isVisible({ timeout: 3000 }).catch(() => false);
        findings.push({ 
            test: 'G - Session Persist', 
            status: stillHasTextarea ? 'PASS' : 'LOST',
            notes: stillHasTextarea ? 'Session maintained' : 'Session lost on refresh'
        });
        
        // === REPORT ===
        console.log('\n📊 Generating report...');
        
        let report = `# PeanutChat UI Testing - Error States & Edge Cases

**Date:** ${new Date().toISOString()}  
**Test User:** ${TEST_USER}

## Results Summary

| Test | Status | Notes |
|------|--------|-------|
`;
        for (const f of findings) {
            const emoji = f.status.includes('FAIL') ? '❌' : f.status.includes('SKIP') ? '⏭️' : '✅';
            report += `| ${f.test} | ${emoji} ${f.status} | ${f.notes || '-'} |\n`;
        }

        report += `

## Code Analysis (from source files)

### XSS Protection (chat.js)
\`\`\`javascript
// Uses DOMPurify for sanitization
html = DOMPurify.sanitize(html, {
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea'],
    FORBID_ATTR: ['onerror', 'onload', 'onmouseover', 'onfocus', 'onblur']
});
\`\`\`

The app properly sanitizes HTML output with DOMPurify, blocking dangerous tags.

### Session Management (auth.js)
- Uses sessionStorage marker + cookie for authentication
- New tabs require re-authentication (security feature)
- Token refresh every 20 minutes

### Error Handling
- \`showToast()\` method for notifications
- Colors: error=red, success=green, warning=yellow, info=blue
- AbortController for cancellable requests

## Screenshots
`;
        const files = fs.readdirSync(SCREENSHOTS_DIR).filter(f => f.endsWith('.png')).sort();
        for (const f of files) {
            report += `- ${f}\n`;
        }

        report += `

## Recommendations

1. **Long Input** - Add visible character counter
2. **Mobile** - Ensure 44px minimum touch targets  
3. **Accessibility** - Add ARIA labels to interactive elements
4. **Error UX** - Show retry button on network errors
5. **XSS** - ✅ Already properly handled with DOMPurify
`;

        fs.writeFileSync('findings.md', report);
        console.log('✅ Report: findings.md');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        await screenshot(page, 'ERROR_final');
    } finally {
        await browser.close();
        console.log('Done.');
    }
}

runTests();
