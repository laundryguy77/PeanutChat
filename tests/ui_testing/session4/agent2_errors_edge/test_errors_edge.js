/**
 * PeanutChat UI Testing - Error States & Edge Cases
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

async function runTests() {
    console.log('🚀 Starting Error States & Edge Cases Tests');
    console.log(`Test User: ${TEST_USER}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();
    page.setDefaultTimeout(300000);
    
    const findings = [];
    
    try {
        // ==========================================
        // REGISTRATION & LOGIN
        // ==========================================
        console.log('\n📝 Registering test user...');
        await page.goto(BASE_URL);
        await page.waitForLoadState('networkidle');
        
        // Check if we need to register
        const registerLink = page.locator('text=Create account');
        if (await registerLink.isVisible({ timeout: 5000 }).catch(() => false)) {
            await registerLink.click();
            await page.waitForTimeout(500);
        }
        
        // Fill registration form
        await page.fill('#register-username', TEST_USER);
        await page.fill('#register-password', TEST_PASS);
        await page.fill('#register-confirm', TEST_PASS);
        await page.click('#register-submit');
        await page.waitForTimeout(2000);
        
        await screenshot(page, '00_registered');
        
        // ==========================================
        // A. EMPTY STATES
        // ==========================================
        console.log('\n📋 A. Testing Empty States...');
        
        // A1: Empty Conversation State
        await page.waitForTimeout(1000);
        await screenshot(page, 'A1_empty_conversation_state');
        findings.push({
            test: 'A1 - Empty Conversation State',
            status: 'CAPTURED',
            notes: 'New user sees welcome screen with no conversations'
        });
        
        // A2: Empty Memory State - Open settings/memory panel if exists
        const settingsBtn = page.locator('button:has(.material-symbols-outlined:text("settings")), #settings-btn, [aria-label="Settings"]');
        if (await settingsBtn.first().isVisible({ timeout: 3000 }).catch(() => false)) {
            await settingsBtn.first().click();
            await page.waitForTimeout(500);
            await screenshot(page, 'A2_settings_panel');
            
            // Look for memory tab
            const memoryTab = page.locator('text=Memory, text=Memories, button:has-text("Memory")').first();
            if (await memoryTab.isVisible({ timeout: 2000 }).catch(() => false)) {
                await memoryTab.click();
                await page.waitForTimeout(500);
                await screenshot(page, 'A2_empty_memory_state');
                findings.push({
                    test: 'A2 - Empty Memory State',
                    status: 'CAPTURED',
                    notes: 'Memory panel shows empty state for new user'
                });
            }
            
            // Close settings
            const closeBtn = page.locator('button:has-text("Close"), .close-btn, [aria-label="Close"]').first();
            if (await closeBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
                await closeBtn.click();
            } else {
                await page.keyboard.press('Escape');
            }
        }
        
        // A3: Check for knowledge base in sidebar
        const kbBtn = page.locator('text=Knowledge, #knowledge-btn, [aria-label*="Knowledge"]').first();
        if (await kbBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
            await kbBtn.click();
            await page.waitForTimeout(500);
            await screenshot(page, 'A3_empty_knowledge_base');
            findings.push({
                test: 'A3 - Empty Knowledge Base',
                status: 'CAPTURED',
                notes: 'Knowledge base shows empty state'
            });
            await page.keyboard.press('Escape');
        } else {
            findings.push({
                test: 'A3 - Empty Knowledge Base',
                status: 'NOT_FOUND',
                notes: 'Knowledge base button not visible in UI'
            });
        }
        
        // ==========================================
        // B. LONG INPUT HANDLING
        // ==========================================
        console.log('\n📋 B. Testing Long Input Handling...');
        
        // Generate 5000+ character message
        const longMessage = 'This is a test message with many characters. '.repeat(150);
        console.log(`Long message length: ${longMessage.length} chars`);
        
        const messageInput = page.locator('#message-input, textarea[placeholder*="message"], textarea').first();
        await messageInput.waitFor({ state: 'visible', timeout: 5000 });
        
        // Type the long message
        await messageInput.fill(longMessage);
        await page.waitForTimeout(500);
        await screenshot(page, 'B1_long_input_textarea');
        
        // Check textarea state
        const textareaValue = await messageInput.inputValue();
        findings.push({
            test: 'B1 - Long Input Textarea',
            status: textareaValue.length >= 5000 ? 'PASS' : 'PARTIAL',
            notes: `Textarea accepted ${textareaValue.length} characters`
        });
        
        // Try to send the long message
        const sendBtn = page.locator('#send-btn, button:has-text("Send"), button[type="submit"]').first();
        if (await sendBtn.isVisible()) {
            await sendBtn.click();
            await page.waitForTimeout(3000);
            await screenshot(page, 'B2_long_message_sent');
            findings.push({
                test: 'B2 - Long Message Send',
                status: 'CAPTURED',
                notes: 'Long message was submitted to the system'
            });
        }
        
        // Wait for any response
        await page.waitForTimeout(5000);
        await screenshot(page, 'B3_long_message_result');
        
        // ==========================================
        // C. SPECIAL CHARACTERS / XSS
        // ==========================================
        console.log('\n📋 C. Testing Special Characters & XSS...');
        
        // Clear and send XSS attempt
        await messageInput.fill('');
        const xssPayload = '<script>alert("xss")</script>';
        await messageInput.fill(xssPayload);
        await screenshot(page, 'C1_xss_input');
        
        await sendBtn.click();
        await page.waitForTimeout(3000);
        await screenshot(page, 'C2_xss_after_send');
        
        // Check if script tags are visible as text (escaped) or not at all
        const pageContent = await page.content();
        const hasUnescapedScript = pageContent.includes('<script>alert');
        const hasEscapedScript = pageContent.includes('&lt;script&gt;') || 
                                  pageContent.includes('&lt;script>');
        
        findings.push({
            test: 'C1 - XSS Prevention',
            status: hasUnescapedScript ? 'FAIL - XSS VULNERABLE' : 'PASS',
            notes: hasEscapedScript ? 'Script tags properly escaped' : 'Script tags filtered out or escaped'
        });
        
        // Test other special characters
        const specialChars = '< > & " \' \\ / { } [ ] | ; : @ # $ % ^ * ( ) ! ~ `';
        await messageInput.fill(specialChars);
        await screenshot(page, 'C3_special_chars_input');
        await sendBtn.click();
        await page.waitForTimeout(2000);
        await screenshot(page, 'C4_special_chars_result');
        findings.push({
            test: 'C2 - Special Characters',
            status: 'CAPTURED',
            notes: 'Tested various special characters handling'
        });
        
        // ==========================================
        // D. MOBILE VIEWPORT
        // ==========================================
        console.log('\n📋 D. Testing Mobile Viewport...');
        
        // Resize to mobile
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        await screenshot(page, 'D1_mobile_main_interface');
        findings.push({
            test: 'D1 - Mobile Main Interface',
            status: 'CAPTURED',
            notes: 'Viewport resized to 375x667 (iPhone SE)'
        });
        
        // Check if sidebar is hidden or has hamburger menu
        const sidebar = page.locator('#sidebar, .sidebar, nav').first();
        const sidebarVisible = await sidebar.isVisible().catch(() => false);
        const hamburger = page.locator('button:has(.material-symbols-outlined:text("menu")), .hamburger, #menu-toggle').first();
        const hasHamburger = await hamburger.isVisible({ timeout: 2000 }).catch(() => false);
        
        findings.push({
            test: 'D2 - Mobile Sidebar Behavior',
            status: 'CAPTURED',
            notes: `Sidebar visible: ${sidebarVisible}, Hamburger menu: ${hasHamburger}`
        });
        
        // If hamburger exists, test it
        if (hasHamburger) {
            await hamburger.click();
            await page.waitForTimeout(500);
            await screenshot(page, 'D2_mobile_sidebar_open');
            
            // Try to close
            await hamburger.click().catch(() => page.keyboard.press('Escape'));
            await page.waitForTimeout(300);
            await screenshot(page, 'D3_mobile_sidebar_closed');
        }
        
        // Test input on mobile
        await messageInput.fill('Mobile test message');
        await screenshot(page, 'D4_mobile_input');
        
        // Reset viewport
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.waitForTimeout(500);
        
        // ==========================================
        // E. KEYBOARD NAVIGATION
        // ==========================================
        console.log('\n📋 E. Testing Keyboard Navigation...');
        
        // Focus on page start
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);
        await screenshot(page, 'E1_first_tab_focus');
        
        // Tab through several elements
        for (let i = 0; i < 5; i++) {
            await page.keyboard.press('Tab');
            await page.waitForTimeout(200);
        }
        await screenshot(page, 'E2_after_several_tabs');
        
        // Check if focus indicators are visible
        const focusedEl = await page.evaluate(() => {
            const el = document.activeElement;
            const styles = window.getComputedStyle(el);
            return {
                tag: el.tagName,
                id: el.id,
                outline: styles.outline,
                boxShadow: styles.boxShadow,
                hasFocusRing: styles.outline !== 'none' || styles.boxShadow !== 'none'
            };
        });
        
        findings.push({
            test: 'E1 - Keyboard Navigation',
            status: 'CAPTURED',
            notes: `Focus indicators present: ${focusedEl.hasFocusRing}, Current element: ${focusedEl.tag}#${focusedEl.id}`
        });
        
        // Test Enter key on message input
        await messageInput.focus();
        await messageInput.fill('Enter key test');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1000);
        await screenshot(page, 'E3_enter_key_send');
        findings.push({
            test: 'E2 - Enter Key Submit',
            status: 'CAPTURED',
            notes: 'Tested Enter key behavior on message input'
        });
        
        // Test Shift+Enter for newline
        await messageInput.fill('Line 1');
        await page.keyboard.press('Shift+Enter');
        await page.keyboard.type('Line 2');
        await screenshot(page, 'E4_shift_enter_newline');
        findings.push({
            test: 'E3 - Shift+Enter Newline',
            status: 'CAPTURED',
            notes: 'Tested Shift+Enter for multiline input'
        });
        await messageInput.fill(''); // Clear
        
        // ==========================================
        // F. API ERROR STATES
        // ==========================================
        console.log('\n📋 F. Testing API Error States...');
        
        // Intercept network to simulate error
        await page.route('**/api/chat/**', route => {
            route.abort('failed');
        });
        
        await messageInput.fill('This should trigger network error');
        await sendBtn.click();
        await page.waitForTimeout(3000);
        await screenshot(page, 'F1_network_error');
        
        // Check for error toast
        const errorToast = page.locator('.toast, [role="alert"], .error-message, .bg-red-600').first();
        const toastVisible = await errorToast.isVisible({ timeout: 2000 }).catch(() => false);
        
        findings.push({
            test: 'F1 - Network Error Handling',
            status: toastVisible ? 'PASS' : 'NEEDS_REVIEW',
            notes: `Error toast visible: ${toastVisible}`
        });
        
        // Remove route intercept
        await page.unroute('**/api/chat/**');
        
        // ==========================================
        // G. SESSION HANDLING
        // ==========================================
        console.log('\n📋 G. Testing Session Handling...');
        
        // First, send a message so we have something in conversation
        await messageInput.fill('Message before refresh');
        await sendBtn.click();
        await page.waitForTimeout(3000);
        await screenshot(page, 'G1_before_refresh');
        
        // Reload page
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);
        await screenshot(page, 'G2_after_refresh');
        
        // Check if we're still logged in
        const isLoggedIn = await page.locator('#message-input, textarea').first().isVisible({ timeout: 5000 }).catch(() => false);
        findings.push({
            test: 'G1 - Session Persistence After Refresh',
            status: isLoggedIn ? 'PASS' : 'FAIL',
            notes: `User session maintained: ${isLoggedIn}`
        });
        
        // Check if conversation was restored
        const messageList = page.locator('#message-list, .messages, .chat-messages').first();
        const hasMessages = await messageList.locator('.flex.gap-4, .message').count() > 0;
        findings.push({
            test: 'G2 - Conversation Recovery',
            status: 'CAPTURED',
            notes: `Messages visible after refresh: ${hasMessages}`
        });
        
        // Test new tab behavior (session isolation)
        const newContext = await browser.newContext();
        const newPage = await newContext.newPage();
        newPage.setDefaultTimeout(300000);
        await newPage.goto(BASE_URL);
        await newPage.waitForLoadState('networkidle');
        await screenshot(newPage, 'G3_new_tab_session');
        
        // Check if new tab requires login
        const newTabRequiresLogin = await newPage.locator('#login-form, text=Login, text=Sign in').first().isVisible({ timeout: 3000 }).catch(() => false);
        findings.push({
            test: 'G3 - New Tab Session',
            status: newTabRequiresLogin ? 'SECURE' : 'SHARED_SESSION',
            notes: `New tab requires login: ${newTabRequiresLogin}`
        });
        
        await newContext.close();
        
        // ==========================================
        // Generate Report
        // ==========================================
        console.log('\n📊 Generating findings report...');
        
        let report = `# PeanutChat UI Testing - Error States & Edge Cases
## Session 4 - Agent 2
Test User: ${TEST_USER}
Date: ${new Date().toISOString()}

---

## Summary
Total Tests: ${findings.length}
`;
        
        const passed = findings.filter(f => f.status === 'PASS' || f.status === 'CAPTURED' || f.status === 'SECURE').length;
        const failed = findings.filter(f => f.status.includes('FAIL')).length;
        const review = findings.filter(f => f.status === 'NEEDS_REVIEW' || f.status === 'NOT_FOUND').length;
        
        report += `
- ✅ Passed/Captured: ${passed}
- ❌ Failed: ${failed}
- ⚠️ Needs Review: ${review}

---

## Detailed Findings

`;
        
        // Group by category
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
            const categoryFindings = findings.filter(f => f.test.startsWith(prefix));
            if (categoryFindings.length > 0) {
                report += `### ${title}\n\n`;
                report += `| Test | Status | Notes |\n`;
                report += `|------|--------|-------|\n`;
                for (const f of categoryFindings) {
                    const statusEmoji = f.status.includes('FAIL') ? '❌' : 
                                        f.status === 'NEEDS_REVIEW' ? '⚠️' : '✅';
                    report += `| ${f.test} | ${statusEmoji} ${f.status} | ${f.notes} |\n`;
                }
                report += '\n';
            }
        }
        
        report += `
---

## Screenshots

All screenshots saved to \`./screenshots/\` directory:
`;
        const screenshots = fs.readdirSync(SCREENSHOTS_DIR).filter(f => f.endsWith('.png'));
        for (const ss of screenshots.sort()) {
            report += `- ${ss}\n`;
        }
        
        report += `
---

## Key Observations

### XSS Protection
Based on source code analysis (chat.js), the application uses DOMPurify for sanitization:
- FORBID_TAGS includes: script, iframe, object, embed, form, input, textarea
- FORBID_ATTR includes: onerror, onload, onmouseover, onfocus, onblur
- Has escapeHtml() function for user content in context sections

### Session Handling
Based on auth.js analysis:
- Uses sessionStorage marker (peanutchat_session_active) for tab detection
- New tabs require re-authentication even if cookie is valid
- Token refresh every 20 minutes

### Error Handling
- showToast() method for user notifications
- Abort controller for cancellable requests
- Network error handling with fallback messages

---

## Recommendations

1. **Long Input**: Verify server-side validation of message length
2. **Mobile**: Test touch gestures and swipe interactions
3. **Accessibility**: Add more ARIA labels for screen readers
4. **Error States**: Consider more descriptive error messages for network issues
`;
        
        fs.writeFileSync('findings.md', report);
        console.log('✅ Report saved to findings.md');
        
    } catch (error) {
        console.error('❌ Test error:', error);
        await screenshot(page, 'ERROR_state');
        throw error;
    } finally {
        await browser.close();
        console.log('\n✅ Tests completed');
    }
}

runTests().catch(console.error);
