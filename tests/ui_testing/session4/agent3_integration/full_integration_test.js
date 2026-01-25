const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_int3_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const findings = [];
let screenshotCount = 0;

function log(msg) {
    const entry = `[${new Date().toISOString()}] ${msg}`;
    console.log(entry);
    findings.push(entry);
}

async function screenshot(page, name) {
    screenshotCount++;
    const filename = `${String(screenshotCount).padStart(2, '0')}_${name}.png`;
    const filepath = path.join(SCREENSHOT_DIR, filename);
    await page.screenshot({ path: filepath, fullPage: true });
    log(`📸 Screenshot: ${filename}`);
    return filename;
}

async function waitForResponse(page, timeout = 30000) {
    // Wait for a response message to appear (streaming completion)
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        const streamingEl = await page.$('.streaming, .typing-indicator, [data-streaming="true"]');
        if (!streamingEl) {
            // Check if there are messages
            const msgs = await page.$$('.message, .chat-message, [data-role="assistant"]');
            if (msgs.length > 0) {
                await page.waitForTimeout(2000); // Give it time to finish
                return true;
            }
        }
        await page.waitForTimeout(500);
    }
    return false;
}

async function runTests() {
    log('='.repeat(60));
    log('PEANUTCHAT INTEGRATION TEST - AGENT 3');
    log(`Test User: ${TEST_USER}`);
    log('='.repeat(60));

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    page.setDefaultTimeout(300000);

    try {
        // ==================== SECTION A: COMPLETE USER JOURNEY ====================
        log('\n' + '='.repeat(60));
        log('SECTION A: COMPLETE USER JOURNEY');
        log('='.repeat(60));

        // A1. Navigate and Register
        log('\n--- A1: REGISTER NEW USER ---');
        await page.goto(BASE_URL);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2000);
        await screenshot(page, 'A1a_initial_page');

        // Click "Create Account" tab in auth modal
        const createAccountTab = await page.$('button:has-text("Create Account")');
        if (createAccountTab) {
            await createAccountTab.click();
            await page.waitForTimeout(500);
            log('Switched to Create Account tab');
        }
        await screenshot(page, 'A1b_register_tab');

        // Fill registration form
        const registerInputs = await page.$$('#auth-modal input');
        log(`Found ${registerInputs.length} inputs in auth modal`);
        
        // Find username and password fields in registration
        const regUsername = await page.$('#register-username') || await page.$('input[placeholder*="username" i]');
        const regPassword = await page.$('#register-password') || await page.$('input[type="password"]:nth-of-type(1)');
        const regConfirm = await page.$('#register-confirm') || await page.$('input[type="password"]:nth-of-type(2)');

        // Try to fill based on visible inputs in register form
        const visibleInputs = await page.$$('#register-form input:visible, #auth-modal input:visible');
        log(`Found ${visibleInputs.length} visible inputs`);
        
        for (const input of visibleInputs) {
            const type = await input.getAttribute('type');
            const placeholder = await input.getAttribute('placeholder') || '';
            const name = await input.getAttribute('name') || '';
            const id = await input.getAttribute('id') || '';
            
            if (placeholder.toLowerCase().includes('username') || name.includes('username') || id.includes('username')) {
                await input.fill(TEST_USER);
                log(`Filled username: ${TEST_USER}`);
            } else if (type === 'password' && (placeholder.toLowerCase().includes('confirm') || name.includes('confirm') || id.includes('confirm'))) {
                await input.fill(TEST_PASS);
                log('Filled confirm password');
            } else if (type === 'password') {
                await input.fill(TEST_PASS);
                log('Filled password');
            }
        }
        await screenshot(page, 'A1c_register_filled');

        // Click Create Account submit button
        const registerSubmit = await page.$('#auth-modal button:has-text("Create Account")');
        if (registerSubmit) {
            const btns = await page.$$('#auth-modal button:has-text("Create Account")');
            // Click the submit button (usually the second one if there's also a tab)
            if (btns.length >= 2) {
                await btns[1].click();
            } else if (btns.length === 1) {
                await btns[0].click();
            }
            await page.waitForTimeout(3000);
            log('Clicked register submit');
        }
        await screenshot(page, 'A1d_after_register');

        // A2. Login (if registration redirected to login)
        log('\n--- A2: LOGIN ---');
        
        // Check if we need to login
        const loginTab = await page.$('button:has-text("Sign In")');
        if (loginTab) {
            await loginTab.click();
            await page.waitForTimeout(500);
        }

        const loginUsername = await page.$('#login-username') || await page.$('#auth-modal input[placeholder*="username" i]');
        const loginPassword = await page.$('#login-password') || await page.$('#auth-modal input[type="password"]');
        
        if (loginUsername && loginPassword) {
            await loginUsername.fill(TEST_USER);
            await loginPassword.fill(TEST_PASS);
            await screenshot(page, 'A2a_login_filled');
            
            const signInBtn = await page.$$('#auth-modal button:has-text("Sign In")');
            // Click submit button (usually second button if there are tabs)
            const submitBtn = signInBtn.length >= 2 ? signInBtn[1] : signInBtn[0];
            if (submitBtn) {
                await submitBtn.click();
                await page.waitForTimeout(3000);
                log('Login submitted');
            }
        }
        await screenshot(page, 'A2b_after_login');

        // Verify logged in
        const userInfo = await page.$('#user-info');
        const isLoggedIn = userInfo ? await userInfo.isVisible() : false;
        log(`Logged in status: ${isLoggedIn}`);
        
        // A3. Create new conversation
        log('\n--- A3: CREATE NEW CONVERSATION ---');
        const newChatBtn = await page.$('#new-chat-btn');
        if (newChatBtn) {
            await newChatBtn.click();
            await page.waitForTimeout(1000);
            log('Clicked New Chat button');
        }
        await screenshot(page, 'A3_new_conversation');

        // A4. Send first message
        log('\n--- A4: SEND FIRST MESSAGE ---');
        const messageInput = await page.$('textarea#message-input, textarea, input[type="text"]#message-input');
        if (messageInput) {
            await messageInput.fill('Hello! This is my first message for integration testing. What can you do?');
            await screenshot(page, 'A4a_message_typed');
            
            // Find and click send button or press Enter
            const sendBtn = await page.$('button[type="submit"]:has(.material-symbols-outlined)') || 
                           await page.$('button:has-text("arrow_upward")');
            if (sendBtn) {
                await sendBtn.click();
            } else {
                await messageInput.press('Enter');
            }
            log('Message sent, waiting for AI response...');
            await page.waitForTimeout(15000); // Wait for AI response
            await screenshot(page, 'A4b_after_response');
            log('First message exchange completed');
        } else {
            log('❌ Message input not found');
        }

        // A5. Open Settings
        log('\n--- A5: OPEN SETTINGS ---');
        const settingsBtn = await page.$('#settings-btn');
        if (settingsBtn) {
            await settingsBtn.click();
            await page.waitForTimeout(1000);
            log('Settings panel opened');
        }
        await screenshot(page, 'A5_settings_opened');

        // A6. Change theme
        log('\n--- A6: CHANGE THEME ---');
        // Look for theme buttons
        const themeBtns = await page.$$('.theme-btn');
        log(`Found ${themeBtns.length} theme buttons`);
        
        // Try to click "Midnight" or a different theme
        const midnightBtn = await page.$('.theme-btn:has-text("Midnight")');
        const forestBtn = await page.$('.theme-btn:has-text("Forest")');
        
        if (midnightBtn) {
            await midnightBtn.click();
            log('Selected Midnight theme');
            await page.waitForTimeout(500);
        } else if (forestBtn) {
            await forestBtn.click();
            log('Selected Forest theme');
            await page.waitForTimeout(500);
        }
        await screenshot(page, 'A6_theme_changed');

        // A7. Configure profile
        log('\n--- A7: CONFIGURE PROFILE ---');
        // Look for profile tab in settings
        const profileTab = await page.$('[data-tab="profile"], button:has-text("Profile")');
        if (profileTab) {
            await profileTab.click();
            await page.waitForTimeout(500);
            log('Profile tab opened');
        }

        // Look for profile settings like display name, communication style, etc.
        const displayNameInput = await page.$('input[name="display_name"], input#display-name');
        if (displayNameInput) {
            await displayNameInput.fill('Integration Tester');
            log('Set display name');
        }

        // Communication style selector
        const styleSelect = await page.$('select[name="communication_style"], select#communication-style');
        if (styleSelect) {
            await styleSelect.selectOption('formal');
            log('Set communication style to formal');
        }
        await screenshot(page, 'A7_profile_configured');

        // A8. Save and close settings
        log('\n--- A8: CLOSE SETTINGS ---');
        const saveBtn = await page.$('button:has-text("Save Settings")');
        if (saveBtn) {
            await saveBtn.click();
            await page.waitForTimeout(1000);
            log('Settings saved');
        }
        
        // Close settings modal
        const closeBtn = await page.$('#settings-modal button:has-text("close"), #settings-modal .close-btn');
        if (closeBtn) {
            await closeBtn.click();
            await page.waitForTimeout(500);
        } else {
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
        }
        await screenshot(page, 'A8_settings_closed');

        // A9. Continue chatting
        log('\n--- A9: CONTINUE CHATTING ---');
        const msgInput2 = await page.$('textarea#message-input, textarea');
        if (msgInput2) {
            await msgInput2.fill('Thanks! Can you summarize our conversation so far?');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(15000);
            log('Continued conversation');
        }
        await screenshot(page, 'A9_continued_chat');

        // A10. Logout
        log('\n--- A10: LOGOUT ---');
        const logoutBtn = await page.$('#logout-btn');
        if (logoutBtn) {
            await logoutBtn.click();
            await page.waitForTimeout(2000);
            log('Logged out');
        }
        await screenshot(page, 'A10_logged_out');

        // A11. Login again
        log('\n--- A11: LOGIN AGAIN ---');
        // Auth modal should appear
        await page.waitForTimeout(1000);
        
        const loginUsername2 = await page.$('#login-username') || await page.$('#auth-modal input[placeholder*="username" i]');
        const loginPassword2 = await page.$('#login-password') || await page.$('#auth-modal input[type="password"]');
        
        if (loginUsername2 && loginPassword2) {
            await loginUsername2.fill(TEST_USER);
            await loginPassword2.fill(TEST_PASS);
            
            const signInBtns = await page.$$('#auth-modal button:has-text("Sign In")');
            const submitBtn = signInBtns.length >= 2 ? signInBtns[1] : signInBtns[0];
            if (submitBtn) {
                await submitBtn.click();
                await page.waitForTimeout(3000);
            }
            log('Re-logged in');
        }
        await screenshot(page, 'A11_logged_in_again');

        // ==================== SECTION B: SETTINGS PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION B: SETTINGS PERSISTENCE');
        log('='.repeat(60));

        log('\n--- B: VERIFY THEME PERSISTENCE ---');
        const bodyClasses = await page.evaluate(() => document.body.className);
        const htmlClasses = await page.evaluate(() => document.documentElement.className);
        const htmlDataTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
        
        log(`Body classes: ${bodyClasses}`);
        log(`HTML classes: ${htmlClasses}`);
        log(`Data-theme attribute: ${htmlDataTheme}`);

        const bgColor = await page.evaluate(() => window.getComputedStyle(document.body).backgroundColor);
        log(`Background color after re-login: ${bgColor}`);
        
        // Verify by opening settings and checking which theme is selected
        const settingsBtnB = await page.$('#settings-btn');
        if (settingsBtnB) {
            await settingsBtnB.click();
            await page.waitForTimeout(1000);
            
            // Check which theme button has the "active" class
            const activeTheme = await page.$('.theme-btn.active, .theme-btn[data-active="true"], .theme-btn.border-primary');
            if (activeTheme) {
                const activeText = await activeTheme.textContent();
                log(`Active theme in settings: ${activeText.trim()}`);
            }
            
            await page.keyboard.press('Escape');
        }
        await screenshot(page, 'B_theme_persistence');

        // ==================== SECTION C: CONVERSATION PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION C: CONVERSATION PERSISTENCE');
        log('='.repeat(60));

        log('\n--- C: VERIFY CONVERSATION HISTORY ---');
        const conversationList = await page.$('#conversation-list');
        if (conversationList) {
            const conversations = await conversationList.$$('.conversation-item, [data-conversation-id]');
            log(`Found ${conversations.length} conversations in sidebar`);
            
            // Get conversation titles
            for (let i = 0; i < Math.min(3, conversations.length); i++) {
                const title = await conversations[i].textContent();
                log(`  Conversation ${i + 1}: ${title.substring(0, 50).trim()}...`);
            }
        }

        // Check message area for loaded messages
        const messages = await page.$$('.message, .chat-message, [data-role]');
        log(`Found ${messages.length} messages in current view`);
        await screenshot(page, 'C_conversation_persistence');

        // ==================== SECTION D: PROFILE EFFECTS ====================
        log('\n' + '='.repeat(60));
        log('SECTION D: PROFILE EFFECTS');
        log('='.repeat(60));

        log('\n--- D: CHANGE COMMUNICATION STYLE & TEST ---');
        const settingsBtnD = await page.$('#settings-btn');
        if (settingsBtnD) {
            await settingsBtnD.click();
            await page.waitForTimeout(1000);
        }
        await screenshot(page, 'D1_settings_for_profile');

        // Find and change communication style
        const styleSelectD = await page.$('select[name="communication_style"], select#communication-style, #style-select');
        if (styleSelectD) {
            const options = await styleSelectD.$$eval('option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
            log(`Available communication styles: ${JSON.stringify(options)}`);
            
            // Change to "casual" or "friendly" if available
            const casualOpt = options.find(o => o.value === 'casual' || o.value === 'friendly');
            if (casualOpt) {
                await styleSelectD.selectOption(casualOpt.value);
                log(`Changed style to: ${casualOpt.value}`);
            }
        }

        // Save settings
        const saveBtnD = await page.$('button:has-text("Save Settings")');
        if (saveBtnD) {
            await saveBtnD.click();
            await page.waitForTimeout(1000);
        }
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        await screenshot(page, 'D2_style_changed');

        // Send message to test new style
        const msgInputD = await page.$('textarea#message-input, textarea');
        if (msgInputD) {
            await msgInputD.fill('Hey! What\'s up? Can you give me a super casual response?');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(15000);
        }
        await screenshot(page, 'D3_response_with_casual_style');

        // ==================== SECTION E: MODEL SWITCH MID-CONVERSATION ====================
        log('\n' + '='.repeat(60));
        log('SECTION E: MODEL SWITCH MID-CONVERSATION');
        log('='.repeat(60));

        log('\n--- E: START NEW CONVERSATION ---');
        const newChatBtnE = await page.$('#new-chat-btn');
        if (newChatBtnE) {
            await newChatBtnE.click();
            await page.waitForTimeout(1000);
        }
        await screenshot(page, 'E1_new_conversation');

        // Send initial message with current model
        const msgInputE1 = await page.$('textarea#message-input, textarea');
        if (msgInputE1) {
            await msgInputE1.fill('Tell me a short programming joke.');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(12000);
        }
        await screenshot(page, 'E2_first_model_response');

        // Find and change model
        log('\n--- E: SWITCH MODEL ---');
        const modelSelector = await page.$('select#model-select, select[name="model"], #model-selector');
        if (modelSelector) {
            const models = await modelSelector.$$eval('option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
            log(`Available models: ${JSON.stringify(models)}`);
            
            // Select a different model
            if (models.length > 1) {
                await modelSelector.selectOption(models[1].value);
                log(`Switched to model: ${models[1].text}`);
            }
        } else {
            // Check in settings
            const settingsBtnE = await page.$('#settings-btn');
            if (settingsBtnE) {
                await settingsBtnE.click();
                await page.waitForTimeout(1000);
                
                const modelSelectInSettings = await page.$('select#model-select, select[name="model"]');
                if (modelSelectInSettings) {
                    const models = await modelSelectInSettings.$$eval('option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
                    log(`Available models in settings: ${JSON.stringify(models)}`);
                    
                    if (models.length > 1) {
                        await modelSelectInSettings.selectOption(models[1].value);
                        log(`Switched to model: ${models[1].text}`);
                        
                        const saveBtnE = await page.$('button:has-text("Save Settings")');
                        if (saveBtnE) await saveBtnE.click();
                    }
                }
                await page.keyboard.press('Escape');
            }
        }
        await screenshot(page, 'E3_model_switched');

        // Continue conversation with new model
        const msgInputE2 = await page.$('textarea#message-input, textarea');
        if (msgInputE2) {
            await msgInputE2.fill('Now tell me an AI joke. Keep it short and punny!');
            await page.keyboard.press('Enter');
            await page.waitForTimeout(12000);
        }
        await screenshot(page, 'E4_second_model_response');

        // ==================== SECTION F: MULTI-FEATURE FLOW ====================
        log('\n' + '='.repeat(60));
        log('SECTION F: MULTI-FEATURE FLOW (THINKING MODE)');
        log('='.repeat(60));

        log('\n--- F: ENABLE THINKING MODE ---');
        // Open settings to find thinking mode
        const settingsBtnF = await page.$('#settings-btn');
        if (settingsBtnF) {
            await settingsBtnF.click();
            await page.waitForTimeout(1000);
        }

        // Look for thinking mode toggle/checkbox
        const thinkingToggle = await page.$('input[name="thinking"], input#thinking-mode, #enable-thinking');
        const thinkingCheckbox = await page.$('input[type="checkbox"][name*="thinking"]');
        
        if (thinkingToggle) {
            const isChecked = await thinkingToggle.isChecked();
            if (!isChecked) {
                await thinkingToggle.click();
                log('Enabled thinking mode');
            }
        } else if (thinkingCheckbox) {
            await thinkingCheckbox.check();
            log('Enabled thinking mode checkbox');
        } else {
            log('⚠️ Thinking mode toggle not found');
        }
        
        // Save settings
        const saveBtnF = await page.$('button:has-text("Save Settings")');
        if (saveBtnF) {
            await saveBtnF.click();
            await page.waitForTimeout(1000);
        }
        await page.keyboard.press('Escape');
        await screenshot(page, 'F1_thinking_mode_enabled');

        // Start new conversation for clean test
        const newChatBtnF = await page.$('#new-chat-btn');
        if (newChatBtnF) {
            await newChatBtnF.click();
            await page.waitForTimeout(1000);
        }

        // Send complex question
        log('\n--- F: SEND COMPLEX QUESTION ---');
        const msgInputF = await page.$('textarea#message-input, textarea');
        if (msgInputF) {
            await msgInputF.fill('Explain the philosophical implications of artificial consciousness. Can machines truly think? Consider both materialist and dualist perspectives in your response.');
            await page.keyboard.press('Enter');
            
            // Quick screenshot while potentially processing/thinking
            await page.waitForTimeout(3000);
            await screenshot(page, 'F2_during_processing');
            
            // Wait for full response
            await page.waitForTimeout(25000);
        }
        await screenshot(page, 'F3_thinking_response_complete');

        // ==================== FINAL SUMMARY ====================
        log('\n' + '='.repeat(60));
        log('TEST EXECUTION COMPLETE');
        log('='.repeat(60));
        log(`Total screenshots: ${screenshotCount}`);
        log(`Test user: ${TEST_USER}`);
        log(`Final URL: ${page.url()}`);

    } catch (error) {
        log(`❌ ERROR: ${error.message}`);
        log(`Stack: ${error.stack}`);
        await screenshot(page, 'ERROR_state');
        throw error;
    } finally {
        await browser.close();
    }

    return findings;
}

runTests().then(findings => {
    const report = findings.join('\n');
    fs.writeFileSync('test_output.log', report);
    console.log('\n✅ Test complete. Output saved to test_output.log');
}).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
});
