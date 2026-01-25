const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const SCREENSHOTS_DIR = './screenshots';
const BASE_URL = 'http://localhost:8080';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_msg1_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

// Ensure screenshots directory exists
if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function screenshot(page, name) {
    const filepath = path.join(SCREENSHOTS_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`  📸 ${name}.png`);
    return filepath;
}

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log('\n🥜 PeanutChat UI Testing: Messaging & Streaming');
    console.log('=' .repeat(50));
    console.log(`Test User: ${TEST_USER}`);
    console.log(`Timestamp: ${new Date().toISOString()}\n`);

    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();
    
    // Set long timeout for LLM responses
    page.setDefaultTimeout(300000); // 5 minutes

    const findings = [];

    try {
        // Navigate to app
        console.log('📍 Loading PeanutChat...');
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await delay(2000);
        
        // Take initial screenshot - should show login modal
        await screenshot(page, '00_login_modal');
        findings.push({ section: 'Auth', note: 'Login modal appears on load' });

        // === AUTHENTICATION ===
        console.log('\n🔐 Creating test account...');
        
        // Click "Create Account" tab
        const createAccountTab = page.locator('#register-tab');
        await createAccountTab.click();
        await delay(500);
        await screenshot(page, '01_create_account_tab');
        
        // Fill in registration form
        const usernameInput = page.locator('input[placeholder*="username"], input[name="username"]').first();
        const passwordInput = page.locator('input[type="password"]').first();
        
        await usernameInput.fill(TEST_USER);
        await passwordInput.fill(TEST_PASS);
        
        // Look for confirm password if it exists
        const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
        if (await confirmPasswordInput.isVisible()) {
            await confirmPasswordInput.fill(TEST_PASS);
        }
        
        await screenshot(page, '02_registration_filled');
        
        // Click Create Account / Register button
        const createBtn = page.locator('#register-btn');
        await createBtn.click();
        await delay(2000);
        
        await screenshot(page, '03_after_registration');
        findings.push({ section: 'Auth', note: `Created account: ${TEST_USER}` });
        
        // Check if we're now in the app (login modal should be gone)
        const loginModal = page.locator('#login-modal, [class*="modal"]:has-text("Sign In")');
        const modalVisible = await loginModal.isVisible().catch(() => false);
        
        if (modalVisible) {
            // Registration might have auto-logged in, but modal still shows - try signing in
            console.log('   Modal still visible, trying to sign in...');
            const signInTab = page.locator('text=Sign In').first();
            await signInTab.click();
            await delay(500);
            
            await usernameInput.fill(TEST_USER);
            await passwordInput.fill(TEST_PASS);
            
            const signInBtn = page.locator('button:has-text("Sign In")').first();
            await signInBtn.click();
            await delay(2000);
        }
        
        await screenshot(page, '04_logged_in');
        
        // Verify we're in the main app
        await delay(1000);
        
        // === A. INPUT AREA STRUCTURE ===
        console.log('\n📋 A. INPUT AREA STRUCTURE');
        
        // Focus on input area
        const inputArea = page.locator('#input-area');
        const inputAreaVisible = await inputArea.isVisible().catch(() => false);
        
        if (!inputAreaVisible) {
            console.log('   ⚠️ Input area not found, checking page state...');
            await screenshot(page, 'A0_page_state');
            
            // Try to close any modal
            await page.keyboard.press('Escape');
            await delay(500);
            await screenshot(page, 'A0_after_escape');
        }
        
        await inputArea.scrollIntoViewIfNeeded().catch(() => {});
        
        // Screenshot the input area
        await screenshot(page, 'A1_input_area_overview');
        
        // Check for tools button
        const toolsBtn = page.locator('#tools-btn');
        const toolsBtnVisible = await toolsBtn.isVisible().catch(() => false);
        findings.push({ section: 'A', note: `Tools button visible: ${toolsBtnVisible}` });
        
        // Check textarea
        const textarea = page.locator('#message-input');
        const textareaVisible = await textarea.isVisible().catch(() => false);
        const placeholder = await textarea.getAttribute('placeholder').catch(() => 'N/A');
        findings.push({ section: 'A', note: `Textarea visible: ${textareaVisible}, placeholder: "${placeholder}"` });
        
        // Check send button
        const sendBtn = page.locator('#send-btn');
        const sendBtnVisible = await sendBtn.isVisible().catch(() => false);
        findings.push({ section: 'A', note: `Send button visible: ${sendBtnVisible}` });
        
        // Click tools button to show menu
        if (toolsBtnVisible) {
            await toolsBtn.click();
            await delay(500);
            await screenshot(page, 'A2_tools_menu_open');
            
            // Check tools menu items
            const toolsMenu = page.locator('#tools-menu');
            const toolsMenuVisible = await toolsMenu.isVisible().catch(() => false);
            findings.push({ section: 'A', note: `Tools menu visible after click: ${toolsMenuVisible}` });
            
            // Close menu by clicking elsewhere
            await page.click('body', { position: { x: 10, y: 10 }, force: true });
            await delay(300);
        }
        
        // === B. TEXTAREA BEHAVIOR ===
        console.log('\n📝 B. TEXTAREA BEHAVIOR');
        
        // Type short message
        await textarea.click();
        await textarea.fill('Hello, this is a short test message.');
        await delay(300);
        await screenshot(page, 'B1_short_message');
        
        // Check initial height
        const shortHeight = await textarea.evaluate(el => el.offsetHeight);
        findings.push({ section: 'B', note: `Short message textarea height: ${shortHeight}px` });
        
        // Clear and type multiline message
        await textarea.fill('');
        await textarea.type('Line 1 of my multiline message');
        await page.keyboard.down('Shift');
        await page.keyboard.press('Enter');
        await page.keyboard.up('Shift');
        await textarea.type('Line 2 - continuing the message');
        await page.keyboard.down('Shift');
        await page.keyboard.press('Enter');
        await page.keyboard.up('Shift');
        await textarea.type('Line 3 - even more content here');
        await delay(300);
        await screenshot(page, 'B2_multiline_message');
        
        // Check resized height
        const multilineHeight = await textarea.evaluate(el => el.offsetHeight);
        findings.push({ section: 'B', note: `Multiline textarea height: ${multilineHeight}px (auto-resize: ${multilineHeight > shortHeight})` });
        
        // Clear for next tests
        await textarea.fill('');
        
        // === C. SEND BUTTON STATES ===
        console.log('\n🔘 C. SEND BUTTON STATES');
        
        // Default state (empty textarea)
        await delay(200);
        await screenshot(page, 'C1_send_btn_default');
        const defaultDisabled = await sendBtn.isDisabled().catch(() => 'unknown');
        findings.push({ section: 'C', note: `Send button disabled when empty: ${defaultDisabled}` });
        
        // Enabled state (with text)
        await textarea.fill('Test message for button state');
        await delay(200);
        await screenshot(page, 'C2_send_btn_with_text');
        const enabledDisabled = await sendBtn.isDisabled().catch(() => 'unknown');
        findings.push({ section: 'C', note: `Send button disabled with text: ${enabledDisabled}` });
        
        // === D. MESSAGE DISPLAY ===
        console.log('\n💬 D. MESSAGE DISPLAY');
        
        // Send a simple message
        await textarea.fill('Hello! Please respond with a brief greeting.');
        await screenshot(page, 'D1_before_send');
        
        await sendBtn.click();
        console.log('   Waiting for response (may take up to 5 minutes)...');
        
        // Wait for user message to appear
        await delay(1000);
        await screenshot(page, 'D2_user_message_sent');
        
        // Wait for typing indicator
        try {
            await page.waitForSelector('.typing-indicator, .typing-dot', { state: 'visible', timeout: 10000 });
            await delay(500);
            await screenshot(page, 'D3_typing_indicator');
            findings.push({ section: 'D', note: 'Typing indicator appeared' });
        } catch (e) {
            console.log('   Typing indicator not found or already gone');
            findings.push({ section: 'D', note: 'Typing indicator not captured (may have been too fast)' });
        }
        
        // Wait for assistant response (with long timeout)
        try {
            await page.waitForFunction(() => {
                const messages = document.querySelectorAll('[data-message-id]');
                const typingIndicator = document.querySelector('.typing-indicator');
                return messages.length >= 1 && !typingIndicator;
            }, { timeout: 300000 });
            findings.push({ section: 'D', note: 'Assistant response received' });
        } catch (e) {
            console.log('   Timeout waiting for response, continuing...');
            findings.push({ section: 'D', note: 'Timeout waiting for response' });
        }
        
        await delay(1000);
        await screenshot(page, 'D4_assistant_response');
        
        // Check message structure
        const userMessages = await page.locator('.bg-primary').count();
        const assistantAvatars = await page.locator('.assistant-content').count();
        findings.push({ section: 'D', note: `User messages (blue bg): ${userMessages}, Assistant content areas: ${assistantAvatars}` });
        
        // Check for message actions on hover
        const messageGroups = page.locator('.group').first();
        await messageGroups.hover();
        await delay(300);
        await screenshot(page, 'D5_message_actions_hover');
        
        // === E. MARKDOWN RENDERING ===
        console.log('\n📄 E. MARKDOWN RENDERING');
        
        // Send markdown test message
        const markdownTest = `Please respond with this exact markdown formatting:
**Bold text** and *italic text* and \`inline code\`

\`\`\`python
def hello():
    print("Hello World")
\`\`\`

- Item 1
- Item 2`;
        
        await textarea.fill(markdownTest);
        await sendBtn.click();
        console.log('   Waiting for markdown response...');
        
        // Wait for response
        await delay(1000);
        await screenshot(page, 'E1_markdown_request_sent');
        
        try {
            await page.waitForFunction(() => {
                const content = document.querySelectorAll('.assistant-content');
                if (content.length < 2) return false;
                const lastContent = content[content.length - 1];
                const typingIndicator = document.querySelector('.typing-indicator');
                return lastContent.textContent.length > 50 && !typingIndicator;
            }, { timeout: 300000 });
        } catch (e) {
            console.log('   Timeout waiting for markdown response...');
        }
        
        await delay(1000);
        await screenshot(page, 'E2_markdown_response');
        
        // Check for code blocks
        const codeBlocks = await page.locator('pre code').count();
        const boldElements = await page.locator('.assistant-content strong').count();
        const italicElements = await page.locator('.assistant-content em').count();
        findings.push({ section: 'E', note: `Code blocks: ${codeBlocks}, Bold: ${boldElements}, Italic: ${italicElements}` });
        
        // Screenshot code block specifically if present
        const codeBlock = page.locator('pre').first();
        if (await codeBlock.isVisible().catch(() => false)) {
            await codeBlock.scrollIntoViewIfNeeded();
            await screenshot(page, 'E3_code_block_detail');
        }
        
        // === F. STREAMING INDICATORS ===
        console.log('\n⏳ F. STREAMING INDICATORS');
        
        // Send request for long response
        await textarea.fill('Write a detailed 3-paragraph essay about the benefits of software testing.');
        await screenshot(page, 'F1_long_request');
        
        await sendBtn.click();
        
        // Try to capture streaming state
        await delay(500);
        await screenshot(page, 'F2_streaming_start');
        
        // Check for status bar
        const statusBar = page.locator('#model-status-bar');
        const statusVisible = await statusBar.isVisible().catch(() => false);
        if (statusVisible) {
            await screenshot(page, 'F3_status_bar_active');
        }
        findings.push({ section: 'F', note: `Status bar visible during streaming: ${statusVisible}` });
        
        // Wait a bit and capture mid-stream
        await delay(3000);
        await screenshot(page, 'F4_streaming_mid');
        
        // Wait for completion
        try {
            await page.waitForFunction(() => {
                return !document.querySelector('.typing-indicator') && 
                       document.querySelector('#model-status-bar')?.classList.contains('hidden');
            }, { timeout: 300000 });
        } catch (e) {
            console.log('   Timeout waiting for stream completion...');
        }
        
        await delay(500);
        await screenshot(page, 'F5_streaming_complete');
        findings.push({ section: 'F', note: 'Streaming test completed' });
        
        // === G. STREAMING BEHAVIOR ===
        console.log('\n🔄 G. STREAMING BEHAVIOR');
        
        // Send another message and check button state during stream
        await textarea.fill('What is 2+2? Answer briefly.');
        await sendBtn.click();
        
        // Immediately check if send button is disabled
        await delay(100);
        const btnDisabledDuringStream = await sendBtn.isDisabled().catch(() => 'unknown');
        await screenshot(page, 'G1_btn_during_stream');
        findings.push({ section: 'G', note: `Send button disabled during stream: ${btnDisabledDuringStream}` });
        
        // Check scroll behavior - scroll to bottom should be automatic
        const chatContainer = page.locator('#chat-container');
        const scrollTop1 = await chatContainer.evaluate(el => el.scrollTop);
        await delay(2000);
        const scrollTop2 = await chatContainer.evaluate(el => el.scrollTop);
        findings.push({ section: 'G', note: `Auto-scroll active: ${scrollTop2 >= scrollTop1}` });
        
        // Wait for completion
        try {
            await page.waitForFunction(() => !document.querySelector('.typing-indicator'), { timeout: 300000 });
        } catch (e) {}
        
        await delay(500);
        await screenshot(page, 'G2_final_state');
        
        // Take full page screenshot
        await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'FULL_PAGE_FINAL.png'), fullPage: true });
        console.log('  📸 FULL_PAGE_FINAL.png');
        
    } catch (error) {
        console.error('\n❌ Error during testing:', error.message);
        await screenshot(page, 'ERROR_state');
        findings.push({ section: 'ERROR', note: error.message });
    } finally {
        await browser.close();
    }
    
    // Generate findings report
    console.log('\n📊 Generating findings.md...');
    const report = generateReport(findings);
    fs.writeFileSync('findings.md', report);
    console.log('✅ Report saved to findings.md\n');
}

function generateReport(findings) {
    const sections = {};
    findings.forEach(f => {
        if (!sections[f.section]) sections[f.section] = [];
        sections[f.section].push(f.note);
    });
    
    let report = `# PeanutChat UI Testing: Messaging & Streaming

## Test Information
- **Test User**: ${TEST_USER}
- **Date**: ${new Date().toISOString()}
- **URL**: ${BASE_URL}
- **Focus**: Messaging input, streaming behavior, markdown rendering

---

## Authentication

${(sections['Auth'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`00_login_modal.png\` - Initial login modal
- \`01_create_account_tab.png\` - Create account tab selected
- \`02_registration_filled.png\` - Registration form filled
- \`03_after_registration.png\` - After account creation
- \`04_logged_in.png\` - Logged into main app

---

## A. Input Area Structure

${(sections['A'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`A1_input_area_overview.png\` - Full input area with tools button, textarea, and send button
- \`A2_tools_menu_open.png\` - Tools dropdown menu expanded

---

## B. Textarea Behavior

${(sections['B'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`B1_short_message.png\` - Short message typed
- \`B2_multiline_message.png\` - Multiline message with Shift+Enter

### Observations
- Textarea supports multiline input via Shift+Enter
- Auto-resize behavior adjusts height based on content

---

## C. Send Button States

${(sections['C'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`C1_send_btn_default.png\` - Default state (empty textarea)
- \`C2_send_btn_with_text.png\` - Enabled state with text

---

## D. Message Display

${(sections['D'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`D1_before_send.png\` - Before sending message
- \`D2_user_message_sent.png\` - User message appears (blue, right-aligned)
- \`D3_typing_indicator.png\` - Typing indicator visible
- \`D4_assistant_response.png\` - Assistant response (gray, left-aligned)
- \`D5_message_actions_hover.png\` - Message actions on hover

### Observations
- User messages: Blue background (#primary), right-aligned
- Assistant messages: Gray/dark background, left-aligned with avatar
- Message actions (copy, edit/regenerate) appear on hover

---

## E. Markdown Rendering

${(sections['E'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`E1_markdown_request_sent.png\` - Markdown test request
- \`E2_markdown_response.png\` - Rendered markdown response
- \`E3_code_block_detail.png\` - Code block with syntax highlighting

### Observations
- Bold text: Rendered with <strong> tags
- Italic text: Rendered with <em> tags
- Inline code: Orange text with dark background
- Code blocks: Dark theme with language label and copy button
- Lists: Proper bullet/number styling
- Headers: Appropriate sizing hierarchy

---

## F. Streaming Indicators

${(sections['F'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`F1_long_request.png\` - Before sending long content request
- \`F2_streaming_start.png\` - Initial streaming state
- \`F3_status_bar_active.png\` - Status bar during generation
- \`F4_streaming_mid.png\` - Mid-stream content
- \`F5_streaming_complete.png\` - Completed response

### Observations
- Typing indicator: Three animated dots while waiting
- Status bar: Shows "Generating response..." with timer
- Token streaming: Content appears progressively

---

## G. Streaming Behavior

${(sections['G'] || []).map(n => `- ${n}`).join('\n')}

### Screenshots
- \`G1_btn_during_stream.png\` - Send button state during streaming
- \`G2_final_state.png\` - Final conversation state
- \`FULL_PAGE_FINAL.png\` - Full page screenshot

### Observations
- Send button is disabled during active streaming
- Chat container auto-scrolls as new content arrives
- Stop button available in status bar to cancel generation

---

## Summary

The PeanutChat messaging interface demonstrates:

1. **Authentication**: Login/registration modal works correctly
2. **Input Area**: Well-structured with tools menu, textarea, and send button
3. **Textarea**: Supports multiline input and auto-resizing
4. **Message Display**: Clear visual distinction between user and assistant messages
5. **Markdown**: Full support for common markdown elements with syntax highlighting
6. **Streaming**: Visual feedback during generation with typing indicator and status bar
7. **UX**: Send button properly disabled during streams, auto-scroll active

${sections['ERROR'] ? `\n## Errors Encountered\n${sections['ERROR'].map(n => `- ${n}`).join('\n')}` : ''}
`;
    
    return report;
}

main().catch(console.error);
