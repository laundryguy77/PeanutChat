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

async function runTests() {
    log('='.repeat(60));
    log('PEANUTCHAT INTEGRATION TEST v2 - AGENT 3');
    log(`Test User: ${TEST_USER}`);
    log('='.repeat(60));

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    page.setDefaultTimeout(60000);

    try {
        // ==================== SECTION A: COMPLETE USER JOURNEY ====================
        log('\n' + '='.repeat(60));
        log('SECTION A: COMPLETE USER JOURNEY');
        log('='.repeat(60));

        // A1. Navigate and Register
        log('\n--- A1: REGISTER NEW USER ---');
        await page.goto(BASE_URL);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(1500);
        await screenshot(page, 'A1a_initial_page');

        // Click "Create Account" tab
        await page.click('button:has-text("Create Account")');
        await page.waitForTimeout(500);
        await screenshot(page, 'A1b_register_tab');

        // Fill registration - find inputs in visible register form
        await page.fill('input[placeholder="Choose a username"]', TEST_USER);
        await page.fill('input[placeholder="Create a password"]', TEST_PASS);
        await page.fill('input[placeholder="Confirm your password"]', TEST_PASS);
        log(`Filled registration form for: ${TEST_USER}`);
        await screenshot(page, 'A1c_register_filled');

        // Click the Create Account submit button (second button with that text)
        const createBtns = await page.$$('button:has-text("Create Account")');
        if (createBtns.length >= 2) {
            await createBtns[1].click();
        } else {
            await createBtns[0].click();
        }
        await page.waitForTimeout(2000);
        await screenshot(page, 'A1d_after_register');

        // Registration auto-logs in the user
        log('✅ Registration complete - user auto-logged in');

        // A2. Verify logged in status
        log('\n--- A2: VERIFY LOGIN STATUS ---');
        const userDisplayName = await page.textContent('#user-display-name').catch(() => 'N/A');
        log(`User display name: ${userDisplayName}`);
        await screenshot(page, 'A2_logged_in');

        // A3. Create new conversation
        log('\n--- A3: CREATE NEW CONVERSATION ---');
        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);
        log('✅ New chat started');
        await screenshot(page, 'A3_new_conversation');

        // A4. Send first message
        log('\n--- A4: SEND FIRST MESSAGE ---');
        await page.fill('textarea', 'Hello! This is my first message for integration testing. What can you help me with?');
        await screenshot(page, 'A4a_message_typed');
        
        await page.click('button[type="submit"]');
        log('Message sent, waiting for AI response...');
        await page.waitForTimeout(20000); // Wait for AI response
        await screenshot(page, 'A4b_after_response');
        
        // Check if response appeared
        const messageCount = await page.$$eval('.message, [data-role]', msgs => msgs.length).catch(() => 0);
        log(`Messages in view: ${messageCount}`);

        // A5. Open Settings
        log('\n--- A5: OPEN SETTINGS ---');
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        await screenshot(page, 'A5_settings_opened');

        // A6. Change theme
        log('\n--- A6: CHANGE THEME ---');
        // Find theme buttons
        const themeBtns = await page.$$('.theme-btn');
        log(`Found ${themeBtns.length} theme buttons`);
        
        // Click on "Midnight" theme
        await page.click('.theme-btn:has-text("Midnight")');
        await page.waitForTimeout(500);
        log('✅ Selected Midnight theme');
        await screenshot(page, 'A6_theme_changed');

        // A7. Configure profile (look for profile settings)
        log('\n--- A7: EXPLORE PROFILE SETTINGS ---');
        // Look for communication style selector
        const styleSelect = await page.$('select#communication-style');
        if (styleSelect) {
            const options = await styleSelect.$$eval('option', opts => opts.map(o => o.value));
            log(`Communication styles available: ${options.join(', ')}`);
            await styleSelect.selectOption('formal');
            log('✅ Set style to formal');
        } else {
            log('Communication style selector not found in current view');
        }
        
        // Check for model selector in settings
        const modelSelect = await page.$('select#model-select');
        if (modelSelect) {
            const models = await modelSelect.$$eval('option', opts => opts.map(o => o.textContent.trim()));
            log(`Models available: ${models.join(', ')}`);
        }
        await screenshot(page, 'A7_profile_settings');

        // A8. Save and close settings
        log('\n--- A8: SAVE AND CLOSE SETTINGS ---');
        await page.click('button:has-text("Save Settings")');
        await page.waitForTimeout(1000);
        log('Settings saved');
        
        // Close settings modal (press Escape)
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        await screenshot(page, 'A8_settings_closed');

        // A9. Continue chatting
        log('\n--- A9: CONTINUE CHATTING ---');
        await page.fill('textarea', 'Thanks! Tell me a short interesting fact about AI.');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(15000);
        await screenshot(page, 'A9_continued_chat');

        // A10. Logout
        log('\n--- A10: LOGOUT ---');
        await page.click('#logout-btn');
        await page.waitForTimeout(2000);
        await screenshot(page, 'A10_logged_out');

        // A11. Login again
        log('\n--- A11: LOGIN AGAIN ---');
        // Auth modal should appear - click Sign In tab first
        await page.click('button:has-text("Sign In")').catch(() => {});
        await page.waitForTimeout(500);
        
        await page.fill('input[placeholder="Enter your username"]', TEST_USER);
        await page.fill('input[placeholder="Enter your password"]', TEST_PASS);
        await screenshot(page, 'A11a_login_filled');
        
        // Click Sign In submit button
        const signInBtns = await page.$$('button:has-text("Sign In")');
        if (signInBtns.length >= 2) {
            await signInBtns[1].click();
        } else {
            await signInBtns[0].click();
        }
        await page.waitForTimeout(2000);
        await screenshot(page, 'A11b_logged_in_again');
        log('✅ Re-logged in');

        // ==================== SECTION B: SETTINGS PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION B: SETTINGS PERSISTENCE');
        log('='.repeat(60));

        log('\n--- B: VERIFY THEME PERSISTENCE ---');
        const htmlTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
        const bodyClass = await page.evaluate(() => document.body.className);
        log(`Data-theme: ${htmlTheme}`);
        log(`Body classes: ${bodyClass}`);
        
        // Open settings to verify
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        
        // Check which theme button has active styling (border-primary)
        const activeTheme = await page.$eval('.theme-btn.border-primary, .theme-btn.active', el => el.textContent).catch(() => 'unknown');
        log(`Active theme in settings: ${activeTheme}`);
        await screenshot(page, 'B_theme_persistence');
        await page.keyboard.press('Escape');

        // ==================== SECTION C: CONVERSATION PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION C: CONVERSATION PERSISTENCE');
        log('='.repeat(60));

        log('\n--- C: VERIFY CONVERSATION HISTORY ---');
        // Check sidebar for conversation list
        const conversations = await page.$$('#conversation-list > div');
        log(`Conversations in sidebar: ${conversations.length}`);
        
        // Check if messages are loaded
        const messagesNow = await page.$$eval('.message-container, .chat-message, [data-message-id]', msgs => msgs.length).catch(() => 0);
        log(`Messages currently displayed: ${messagesNow}`);
        await screenshot(page, 'C_conversation_persistence');

        // ==================== SECTION D: PROFILE EFFECTS ====================
        log('\n' + '='.repeat(60));
        log('SECTION D: PROFILE EFFECTS');
        log('='.repeat(60));

        log('\n--- D: CHANGE COMMUNICATION STYLE & OBSERVE ---');
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        
        const styleSelectD = await page.$('select#communication-style');
        if (styleSelectD) {
            await styleSelectD.selectOption('casual');
            log('Changed communication style to casual');
        }
        
        await page.click('button:has-text("Save Settings")');
        await page.waitForTimeout(500);
        await page.keyboard.press('Escape');
        await screenshot(page, 'D1_style_changed');

        // Send a message to observe the different response
        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);
        await page.fill('textarea', 'Yo! What\'s the coolest thing about programming? Keep it super chill and casual!');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(15000);
        await screenshot(page, 'D2_casual_response');

        // ==================== SECTION E: MODEL SWITCH MID-CONVERSATION ====================
        log('\n' + '='.repeat(60));
        log('SECTION E: MODEL SWITCH MID-CONVERSATION');
        log('='.repeat(60));

        log('\n--- E: MODEL SWITCH TEST ---');
        // Start fresh conversation
        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);
        
        // Get current model
        const currentModel = await page.$eval('select#model-select', el => el.value).catch(() => 'unknown');
        log(`Current model: ${currentModel}`);
        
        // List available models
        const availableModels = await page.$$eval('select#model-select option', opts => 
            opts.map(o => ({ value: o.value, text: o.textContent.trim() }))
        ).catch(() => []);
        log(`Available models: ${JSON.stringify(availableModels)}`);
        await screenshot(page, 'E1_before_model_switch');

        // Send first message with current model
        await page.fill('textarea', 'Tell me a short programming joke.');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(12000);
        await screenshot(page, 'E2_first_model_response');

        // Switch model if multiple available
        if (availableModels.length > 1) {
            const newModel = availableModels.find(m => m.value !== currentModel)?.value;
            if (newModel) {
                await page.selectOption('select#model-select', newModel);
                log(`Switched to model: ${newModel}`);
                await page.waitForTimeout(500);
            }
        }
        await screenshot(page, 'E3_model_switched');

        // Continue conversation with new model
        await page.fill('textarea', 'Now tell me an AI joke!');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(12000);
        await screenshot(page, 'E4_second_model_response');

        // ==================== SECTION F: MULTI-FEATURE FLOW ====================
        log('\n' + '='.repeat(60));
        log('SECTION F: MULTI-FEATURE FLOW');
        log('='.repeat(60));

        log('\n--- F: THINKING MODE TEST ---');
        // Check if thinking mode is available
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        
        const thinkingCheckbox = await page.$('input#thinking-enabled, input[name*="thinking"]');
        if (thinkingCheckbox) {
            await thinkingCheckbox.check();
            log('Enabled thinking mode');
        } else {
            log('Thinking mode toggle not found');
        }
        
        await page.click('button:has-text("Save Settings")');
        await page.waitForTimeout(500);
        await page.keyboard.press('Escape');
        await screenshot(page, 'F1_thinking_enabled');

        // Start new conversation for complex question
        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);

        // Ask complex question
        await page.fill('textarea', 'Explain the concept of recursion with a practical example. Break it down step by step.');
        await page.click('button[type="submit"]');
        
        // Screenshot while processing
        await page.waitForTimeout(3000);
        await screenshot(page, 'F2_processing');
        
        // Wait for complete response
        await page.waitForTimeout(20000);
        await screenshot(page, 'F3_thinking_response');

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
