const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = './screenshots';
fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1440, height: 900 }
    });
    const page = await context.newPage();
    
    console.log('Starting PeanutChat UI Tests - Auth & Sidebar');
    
    // A. REGISTRATION FLOW
    console.log('\n=== A. REGISTRATION FLOW ===');
    
    // 1. Initial page load - auth modal
    await page.goto('http://localhost:8080');
    await delay(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_initial_auth_modal.png') });
    console.log('Screenshot: 01_initial_auth_modal.png - Initial auth modal');
    
    // 2. Click Create Account tab
    await page.click('text=Create Account');
    await delay(500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_create_account_tab.png') });
    console.log('Screenshot: 02_create_account_tab.png - Create Account tab');
    
    // 3. Check form fields exist
    const usernameInput = await page.$('#register-username');
    const passwordInput = await page.$('#register-password');
    const confirmInput = await page.$('#register-confirm');
    const emailInput = await page.$('#register-email');
    console.log('Form fields exist:', {
        username: !!usernameInput,
        password: !!passwordInput,
        confirm: !!confirmInput,
        email: !!emailInput
    });
    
    // 4. Test validation - empty submit
    await page.click('#register-btn');
    await delay(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_registration_validation_empty.png') });
    console.log('Screenshot: 03_registration_validation_empty.png - Empty form validation');
    
    // 5. Test password mismatch validation
    const timestamp = Date.now();
    await page.fill('#register-username', `testuser_auth1_${timestamp}`);
    await page.fill('#register-password', 'TestPass123!');
    await page.fill('#register-confirm', 'DifferentPass456!');
    await page.click('#register-btn');
    await delay(500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_registration_password_mismatch.png') });
    console.log('Screenshot: 04_registration_password_mismatch.png - Password mismatch');
    
    // 6. Successful registration
    await page.fill('#register-confirm', 'TestPass123!');
    await page.click('#register-btn');
    await delay(2000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_post_registration.png') });
    console.log('Screenshot: 05_post_registration.png - Post registration state');
    
    // B. LOGIN FLOW (after logout)
    console.log('\n=== B. LOGIN FLOW ===');
    
    // Check if we're logged in
    const userInfo = await page.$('#user-info:not(.hidden)');
    if (userInfo) {
        console.log('User logged in, attempting logout');
        // Click logout
        await page.click('#logout-btn');
        await delay(1000);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_after_logout.png') });
        console.log('Screenshot: 06_after_logout.png - After logout');
    }
    
    // Wait for auth modal
    await page.waitForSelector('#auth-modal', { timeout: 5000 }).catch(() => {});
    await delay(500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_login_form.png') });
    console.log('Screenshot: 07_login_form.png - Login form');
    
    // Test login validation - empty
    await page.click('#login-btn');
    await delay(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_login_validation_empty.png') });
    console.log('Screenshot: 08_login_validation_empty.png - Empty login validation');
    
    // Test invalid credentials
    await page.fill('#login-username', 'nonexistent_user');
    await page.fill('#login-password', 'wrongpassword');
    await page.click('#login-btn');
    await delay(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_login_invalid_credentials.png') });
    console.log('Screenshot: 09_login_invalid_credentials.png - Invalid credentials');
    
    // Login with created user
    await page.fill('#login-username', `testuser_auth1_${timestamp}`);
    await page.fill('#login-password', 'TestPass123!');
    await page.click('#login-btn');
    await delay(2000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_successful_login.png') });
    console.log('Screenshot: 10_successful_login.png - Successful login');
    
    // E. SIDEBAR STRUCTURE
    console.log('\n=== E. SIDEBAR STRUCTURE ===');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_sidebar_full.png') });
    console.log('Screenshot: 11_sidebar_full.png - Full sidebar');
    
    // Document sidebar elements
    const logo = await page.$('.font-display:has-text("PeanutChat")');
    const newChatBtn = await page.$('#new-chat-btn');
    const searchInput = await page.$('#conversation-search');
    const conversationList = await page.$('#conversation-list');
    const settingsBtn = await page.$('#settings-btn');
    const logoutBtn = await page.$('#logout-btn');
    
    console.log('Sidebar elements:', {
        logo: !!logo,
        newChatBtn: !!newChatBtn,
        searchInput: !!searchInput,
        conversationList: !!conversationList,
        settingsBtn: !!settingsBtn,
        logoutBtn: !!logoutBtn
    });
    
    // F. CONVERSATION MANAGEMENT
    console.log('\n=== F. CONVERSATION MANAGEMENT ===');
    
    // Create new conversation
    await page.click('#new-chat-btn');
    await delay(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_new_conversation.png') });
    console.log('Screenshot: 12_new_conversation.png - New conversation');
    
    // Send a message to name the conversation
    await page.fill('#message-input', 'Hello, this is test conversation 1');
    await page.click('#send-btn');
    await delay(3000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '13_conversation_with_message.png') });
    console.log('Screenshot: 13_conversation_with_message.png - Conversation with message');
    
    // Create more conversations
    for (let i = 2; i <= 3; i++) {
        await page.click('#new-chat-btn');
        await delay(500);
        await page.fill('#message-input', `Test conversation ${i} message`);
        await page.click('#send-btn');
        await delay(2000);
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '14_multiple_conversations.png') });
    console.log('Screenshot: 14_multiple_conversations.png - Multiple conversations');
    
    // Test search
    await page.fill('#conversation-search', 'test');
    await delay(500);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '15_search_filter.png') });
    console.log('Screenshot: 15_search_filter.png - Search filter');
    
    // Clear search
    await page.fill('#conversation-search', '');
    await delay(300);
    
    // Test rename modal (right-click on conversation)
    const firstConv = await page.$('#conversation-list button[data-id]');
    if (firstConv) {
        await firstConv.click({ button: 'right' });
        await delay(500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '16_context_menu.png') });
        console.log('Screenshot: 16_context_menu.png - Context menu');
        
        // Click rename if visible
        const renameOption = await page.$('text=Rename');
        if (renameOption) {
            await renameOption.click();
            await delay(500);
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, '17_rename_modal.png') });
            console.log('Screenshot: 17_rename_modal.png - Rename modal');
            // Press Escape to close
            await page.keyboard.press('Escape');
        }
    }
    
    // D. LOGOUT FLOW
    console.log('\n=== D. LOGOUT FLOW ===');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '18_before_logout.png') });
    console.log('Screenshot: 18_before_logout.png - Before logout');
    
    await page.click('#logout-btn');
    await delay(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '19_after_final_logout.png') });
    console.log('Screenshot: 19_after_final_logout.png - After final logout');
    
    console.log('\n=== Tests Complete ===');
    await browser.close();
}

runTests().catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
});
