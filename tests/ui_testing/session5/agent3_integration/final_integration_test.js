const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_int3_${TIMESTAMP}`;
// Password needs: min 12 chars, upper, lower, digit, special
const TEST_PASS = 'TestPass123!@#';

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
    log('PEANUTCHAT INTEGRATION TEST - FINAL - AGENT 3');
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

        // Fill registration with correct placeholders
        await page.fill('input[placeholder="Choose a username"]', TEST_USER);
        await page.fill('input[placeholder*="12 chars"]', TEST_PASS);
        await page.fill('input[placeholder="Confirm your password"]', TEST_PASS);
        log(`Filled registration form for: ${TEST_USER}`);
        await screenshot(page, 'A1c_register_filled');

        // Click the Create Account submit button
        await page.click('#auth-modal button.w-full:has-text("Create Account")');
        await page.waitForTimeout(3000);
        await screenshot(page, 'A1d_after_register');
        log('✅ Registration complete');

        // A2. Verify logged in status
        log('\n--- A2: VERIFY LOGIN STATUS ---');
        const userInfo = await page.isVisible('#user-info');
        log(`User info visible: ${userInfo}`);
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
        await page.fill('textarea', 'Hello! This is my first message for integration testing. Can you help me?');
        await screenshot(page, 'A4a_message_typed');
        
        await page.click('#send-btn');
        log('Message sent, waiting for AI response...');
        await page.waitForTimeout(20000);
        await screenshot(page, 'A4b_after_response');
        
        const messageCount = await page.$$eval('[data-message-id]', msgs => msgs.length).catch(() => 0);
        log(`Messages after first exchange: ${messageCount}`);

        // A5. Open Settings
        log('\n--- A5: OPEN SETTINGS ---');
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        await screenshot(page, 'A5_settings_opened');

        // A6. Change theme
        log('\n--- A6: CHANGE THEME ---');
        const themeBtns = await page.$$('.theme-btn');
        log(`Found ${themeBtns.length} theme buttons`);
        
        await page.click('.theme-btn:has-text("Midnight")');
        await page.waitForTimeout(500);
        log('✅ Selected Midnight theme');
        await screenshot(page, 'A6_theme_changed');

        // A7. Explore profile/model settings
        log('\n--- A7: PROFILE & MODEL SETTINGS ---');
        const styleSelect = await page.$('select#communication-style');
        if (styleSelect) {
            const options = await styleSelect.$$eval('option', opts => opts.map(o => o.value));
            log(`Communication styles: ${options.join(', ')}`);
            await styleSelect.selectOption('professional');
            log('✅ Set style to professional');
        }
        
        const modelSelect = await page.$('select#model-select');
        if (modelSelect) {
            const models = await modelSelect.$$eval('option', opts => opts.map(o => ({ value: o.value, text: o.textContent.trim() })));
            log(`Available models: ${JSON.stringify(models)}`);
        }
        await screenshot(page, 'A7_profile_settings');

        // A8. Save and close settings
        log('\n--- A8: SAVE AND CLOSE SETTINGS ---');
        await page.click('button:has-text("Save Settings")');
        await page.waitForTimeout(1000);
        log('Settings saved');
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        await screenshot(page, 'A8_settings_closed');

        // A9. Continue chatting
        log('\n--- A9: CONTINUE CHATTING ---');
        await page.fill('textarea', 'Thanks! What is 2+2? Keep it brief.');
        await page.click('#send-btn');
        await page.waitForTimeout(15000);
        await screenshot(page, 'A9_continued_chat');

        // A10. Logout
        log('\n--- A10: LOGOUT ---');
        await page.click('#logout-btn');
        await page.waitForTimeout(2000);
        await screenshot(page, 'A10_logged_out');

        // A11. Login again
        log('\n--- A11: LOGIN AGAIN ---');
        await page.click('button:has-text("Sign In")').catch(() => {});
        await page.waitForTimeout(500);
        
        await page.fill('input[placeholder="Enter your username"]', TEST_USER);
        await page.fill('input[placeholder="Enter your password"]', TEST_PASS);
        await screenshot(page, 'A11a_login_filled');
        
        await page.click('#auth-modal button.w-full:has-text("Sign In")');
        await page.waitForTimeout(2000);
        await screenshot(page, 'A11b_logged_in_again');
        log('✅ Re-logged in');

        // ==================== SECTION B: SETTINGS PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION B: SETTINGS PERSISTENCE');
        log('='.repeat(60));

        log('\n--- B: VERIFY THEME PERSISTENCE ---');
        const htmlTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
        log(`Data-theme after re-login: ${htmlTheme}`);
        
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        
        // Find active theme
        const activeThemeBtns = await page.$$('.theme-btn');
        for (const btn of activeThemeBtns) {
            const isActive = await btn.evaluate(el => el.classList.contains('border-primary') || el.classList.contains('active'));
            if (isActive) {
                const text = await btn.textContent();
                log(`Active theme: ${text.trim()}`);
                break;
            }
        }
        await screenshot(page, 'B_theme_persistence');
        await page.keyboard.press('Escape');

        // ==================== SECTION C: CONVERSATION PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION C: CONVERSATION PERSISTENCE');
        log('='.repeat(60));

        log('\n--- C: VERIFY CONVERSATION HISTORY ---');
        const conversations = await page.$$('#conversation-list > div, #conversation-list .conversation-item');
        log(`Conversations in sidebar: ${conversations.length}`);
        
        // Click on a conversation to load it
        if (conversations.length > 0) {
            await conversations[0].click();
            await page.waitForTimeout(1000);
        }
        
        const messagesNow = await page.$$eval('[data-message-id], .message', msgs => msgs.length).catch(() => 0);
        log(`Messages currently displayed: ${messagesNow}`);
        await screenshot(page, 'C_conversation_persistence');

        // ==================== SECTION D: PROFILE EFFECTS ====================
        log('\n' + '='.repeat(60));
        log('SECTION D: PROFILE EFFECTS');
        log('='.repeat(60));

        log('\n--- D: CHANGE COMMUNICATION STYLE ---');
        await page.click('#settings-btn');
        await page.waitForTimeout(1000);
        
        const styleSelectD = await page.$('select#communication-style');
        if (styleSelectD) {
            await styleSelectD.selectOption('friendly');
            log('Changed communication style to friendly');
        }
        
        await page.click('button:has-text("Save Settings")');
        await page.waitForTimeout(500);
        await page.keyboard.press('Escape');
        await screenshot(page, 'D1_style_changed');

        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);
        await page.fill('textarea', 'Hey! What\'s up? Can you respond in a super casual and friendly way?');
        await page.click('#send-btn');
        await page.waitForTimeout(15000);
        await screenshot(page, 'D2_casual_response');

        // ==================== SECTION E: MODEL SWITCH MID-CONVERSATION ====================
        log('\n' + '='.repeat(60));
        log('SECTION E: MODEL SWITCH MID-CONVERSATION');
        log('='.repeat(60));

        log('\n--- E: MODEL SWITCH TEST ---');
        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);
        
        const currentModel = await page.$eval('select#model-select', el => el.value).catch(() => 'unknown');
        log(`Current model: ${currentModel}`);
        
        const availableModels = await page.$$eval('select#model-select option', opts => 
            opts.map(o => ({ value: o.value, text: o.textContent.trim() }))
        ).catch(() => []);
        log(`Available models: ${JSON.stringify(availableModels)}`);
        await screenshot(page, 'E1_before_model_switch');

        await page.fill('textarea', 'Tell me a short joke.');
        await page.click('#send-btn');
        await page.waitForTimeout(12000);
        await screenshot(page, 'E2_first_model_response');

        if (availableModels.length > 1) {
            const newModel = availableModels.find(m => m.value !== currentModel)?.value;
            if (newModel) {
                await page.selectOption('select#model-select', newModel);
                log(`Switched to model: ${newModel}`);
                await page.waitForTimeout(500);
            }
        }
        await screenshot(page, 'E3_model_switched');

        await page.fill('textarea', 'Tell me another joke, this time about computers!');
        await page.click('#send-btn');
        await page.waitForTimeout(12000);
        await screenshot(page, 'E4_second_model_response');

        // ==================== SECTION F: MULTI-FEATURE FLOW ====================
        log('\n' + '='.repeat(60));
        log('SECTION F: MULTI-FEATURE FLOW');
        log('='.repeat(60));

        log('\n--- F: THINKING MODE TEST ---');
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

        await page.click('#new-chat-btn');
        await page.waitForTimeout(500);

        await page.fill('textarea', 'Explain recursion in programming with a simple example.');
        await page.click('#send-btn');
        
        await page.waitForTimeout(3000);
        await screenshot(page, 'F2_processing');
        
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
