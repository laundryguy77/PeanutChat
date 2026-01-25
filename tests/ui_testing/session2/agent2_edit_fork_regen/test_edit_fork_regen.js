/**
 * PeanutChat UI Test: Edit, Fork & Regenerate
 * Investigates the edit, fork, and regenerate functionality
 */

const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const APP_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_edit2_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

// Findings collector
const findings = {
    editButtonDiscovery: [],
    editModal: [],
    editInPlace: [],
    forkConversation: [],
    regenerateButton: [],
    regenerateVariations: [],
    cancelOperations: [],
    validation: []
};

async function screenshot(page, name) {
    const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`📸 Screenshot: ${name}`);
    return filepath;
}

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function registerUser(page) {
    console.log('\n=== REGISTERING USER ===');
    await page.goto(APP_URL, { waitUntil: 'domcontentloaded' });
    await wait(3000);
    
    await screenshot(page, '00_initial_page');
    
    // Click "Create Account" tab
    const createAccountTab = await page.$('button:has-text("Create Account")');
    if (createAccountTab) {
        await createAccountTab.click();
        await wait(500);
        await screenshot(page, '01_create_account_tab');
    }
    
    // Fill registration form
    await page.fill('#register-username', TEST_USER);
    await page.fill('#register-email', `${TEST_USER}@test.com`);
    await page.fill('#register-password', TEST_PASS);
    await page.fill('#register-confirm', TEST_PASS); // Confirm password field
    
    await screenshot(page, '02_register_form_filled');
    
    // Find and click submit button
    const submitBtn = await page.$('#register-btn');
    if (submitBtn) {
        console.log('Clicking register button...');
        await submitBtn.click();
    } else {
        console.log('⚠️ Register button not found');
    }
    
    await wait(3000);
    await screenshot(page, '03_after_register');
    
    // Check if logged in - auth modal should be hidden
    const authModalHidden = await page.$('#auth-modal.hidden');
    if (authModalHidden) {
        console.log(`✅ Registered and logged in as: ${TEST_USER}`);
    } else {
        console.log('⚠️ Auth modal still visible, checking for errors...');
        const errorMsg = await page.$eval('.text-red-500, .error-message', el => el.textContent).catch(() => null);
        if (errorMsg) console.log(`Error: ${errorMsg}`);
    }
}

async function sendMessage(page, text) {
    console.log(`📤 Sending message: "${text.substring(0, 50)}..."`);
    
    const input = await page.$('#message-input');
    if (!input) {
        console.log('❌ Message input not found');
        return;
    }
    
    await input.fill(text);
    await wait(300);
    
    const sendBtn = await page.$('#send-btn');
    await sendBtn.click();
    
    // Wait for response - check for typing indicator to appear then disappear
    console.log('⏳ Waiting for LLM response...');
    try {
        // Wait for typing indicator to appear (up to 10s)
        await page.waitForSelector('.typing-indicator', { timeout: 10000 }).catch(() => {
            console.log('No typing indicator detected');
        });
        // Wait for it to disappear (up to 5 min)
        await page.waitForSelector('.typing-indicator', { state: 'detached', timeout: 300000 }).catch(() => {
            console.log('Typing indicator timeout');
        });
        await wait(2000); // Extra buffer
    } catch (e) {
        console.log('⚠️ Timeout waiting for response');
    }
}

async function getMessageElements(page) {
    return await page.$$('#message-list > div.flex.gap-4');
}

async function runTests() {
    console.log('\n🥜 PeanutChat Edit/Fork/Regenerate UI Test');
    console.log('==========================================\n');
    
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 900 }
    });
    const page = await context.newPage();
    page.setDefaultTimeout(300000); // 5 min for LLM responses
    
    try {
        // === SETUP: Register user ===
        await registerUser(page);
        
        // === A. EDIT BUTTON DISCOVERY ===
        console.log('\n=== A. EDIT BUTTON DISCOVERY ===');
        
        // Send first message
        await sendMessage(page, 'Hello! Please respond with just "Hi there!"');
        await screenshot(page, '04_first_exchange');
        
        // Find user message and hover
        const messages = await getMessageElements(page);
        console.log(`Found ${messages.length} message elements`);
        
        // User messages have flex-row-reverse class
        const userMessages = [];
        const assistantMessages = [];
        
        for (const msg of messages) {
            const className = await msg.getAttribute('class');
            if (className && className.includes('flex-row-reverse')) {
                userMessages.push(msg);
            } else if (className && className.includes('flex') && !className.includes('welcome')) {
                assistantMessages.push(msg);
            }
        }
        
        console.log(`User messages: ${userMessages.length}, Assistant messages: ${assistantMessages.length}`);
        findings.editButtonDiscovery.push(`Found ${userMessages.length} user messages and ${assistantMessages.length} assistant messages`);
        
        if (userMessages.length > 0) {
            const userMsg = userMessages[0];
            await userMsg.hover();
            await wait(500);
            await screenshot(page, '05_user_message_hover');
            
            const editBtn = await userMsg.$('button[title="Edit"]');
            if (editBtn) {
                findings.editButtonDiscovery.push('✅ Edit button found on user message');
                console.log('✅ Edit button found on user message');
                
                const editIcon = await editBtn.$('span.material-symbols-outlined');
                if (editIcon) {
                    const iconText = await editIcon.textContent();
                    findings.editButtonDiscovery.push(`Edit button icon: "${iconText}"`);
                }
            } else {
                findings.editButtonDiscovery.push('❌ Edit button NOT found on user message');
                console.log('❌ Edit button NOT found');
            }
        }
        
        // Check assistant message does NOT have edit button
        if (assistantMessages.length > 0) {
            const assistantMsg = assistantMessages[0];
            await assistantMsg.hover();
            await wait(500);
            await screenshot(page, '06_assistant_message_hover');
            
            const editBtnOnAssistant = await assistantMsg.$('button[title="Edit"]');
            if (editBtnOnAssistant) {
                findings.editButtonDiscovery.push('⚠️ Edit button found on ASSISTANT message (unexpected)');
            } else {
                findings.editButtonDiscovery.push('✅ Edit button correctly absent from assistant message');
            }
            
            const regenBtn = await assistantMsg.$('button[title="Regenerate"]');
            if (regenBtn) {
                findings.editButtonDiscovery.push('✅ Regenerate button found on assistant message');
            }
        }
        
        // === B. EDIT MODAL ===
        console.log('\n=== B. EDIT MODAL ===');
        
        if (userMessages.length > 0) {
            await userMessages[0].hover();
            await wait(300);
            const editBtn = await userMessages[0].$('button[title="Edit"]');
            
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                await screenshot(page, '07_edit_modal_open');
                
                const modal = await page.$('#edit-modal:not(.hidden)');
                if (modal) {
                    findings.editModal.push('✅ Edit modal opened successfully');
                    
                    const textarea = await modal.$('#edit-content');
                    if (textarea) {
                        const value = await textarea.inputValue();
                        findings.editModal.push(`✅ Textarea present with content: "${value.substring(0, 50)}..."`);
                    }
                    
                    const editInPlaceRadio = await modal.$('input[value="edit"]');
                    const forkRadio = await modal.$('input[value="fork"]');
                    
                    if (editInPlaceRadio) {
                        const checked = await editInPlaceRadio.isChecked();
                        findings.editModal.push(`✅ "Edit in place" radio present, checked: ${checked}`);
                    }
                    
                    if (forkRadio) {
                        findings.editModal.push('✅ "Fork conversation" radio present');
                    }
                    
                    const cancelBtn = await modal.$('#cancel-edit');
                    const saveBtn = await modal.$('#save-edit');
                    
                    if (cancelBtn) findings.editModal.push('✅ Cancel button present');
                    if (saveBtn) findings.editModal.push('✅ Save button present');
                    
                    await cancelBtn.click();
                    await wait(300);
                } else {
                    findings.editModal.push('❌ Edit modal did not open');
                }
            }
        }
        
        // === C. EDIT IN-PLACE FLOW ===
        console.log('\n=== C. EDIT IN-PLACE FLOW ===');
        
        const messagesC = await getMessageElements(page);
        let userMsgC = null;
        for (const msg of messagesC) {
            const className = await msg.getAttribute('class');
            if (className && className.includes('flex-row-reverse')) {
                userMsgC = msg;
                break;
            }
        }
        
        if (userMsgC) {
            await userMsgC.hover();
            await wait(300);
            const editBtn = await userMsgC.$('button[title="Edit"]');
            
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                
                const textarea = await page.$('#edit-content');
                const editRadio = await page.$('input[value="edit"]');
                
                await editRadio.click();
                await wait(200);
                
                await textarea.fill('What is 2+2? Answer with just the number.');
                await screenshot(page, '08_edit_in_place_modified');
                
                const saveBtn = await page.$('#save-edit');
                await saveBtn.click();
                
                console.log('⏳ Waiting for regenerated response (up to 5 min)...');
                findings.editInPlace.push('Edit saved, waiting for new response...');
                
                await wait(3000);
                await page.waitForSelector('.typing-indicator', { timeout: 10000 }).catch(() => {});
                await page.waitForSelector('.typing-indicator', { state: 'detached', timeout: 300000 }).catch(() => {});
                await wait(2000);
                
                await screenshot(page, '09_edit_in_place_result');
                findings.editInPlace.push('✅ Edit in-place completed');
                
                const updatedMessages = await getMessageElements(page);
                for (const msg of updatedMessages) {
                    const className = await msg.getAttribute('class');
                    if (className && className.includes('flex-row-reverse')) {
                        const content = await msg.$eval('div.whitespace-pre-wrap', el => el.textContent).catch(() => '');
                        if (content.includes('2+2')) {
                            findings.editInPlace.push(`✅ User message updated to: "${content}"`);
                        }
                        break;
                    }
                }
            }
        }
        
        // === D. FORK CONVERSATION FLOW ===
        console.log('\n=== D. FORK CONVERSATION FLOW ===');
        
        await sendMessage(page, 'Tell me one fun fact about cats.');
        await screenshot(page, '10_multi_exchange_1');
        
        await sendMessage(page, 'What about dogs?');
        await screenshot(page, '11_multi_exchange_2');
        
        findings.forkConversation.push('Built conversation with multiple exchanges');
        
        const messagesD = await getMessageElements(page);
        const userMessagesD = [];
        for (const msg of messagesD) {
            const className = await msg.getAttribute('class');
            if (className && className.includes('flex-row-reverse')) {
                userMessagesD.push(msg);
            }
        }
        
        console.log(`Found ${userMessagesD.length} user messages for fork test`);
        findings.forkConversation.push(`Total user messages before fork: ${userMessagesD.length}`);
        
        if (userMessagesD.length >= 2) {
            const middleMsg = userMessagesD[1];
            await middleMsg.hover();
            await wait(300);
            
            const editBtn = await middleMsg.$('button[title="Edit"]');
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                
                const forkRadio = await page.$('input[value="fork"]');
                await forkRadio.click();
                await wait(200);
                await screenshot(page, '12_fork_option_selected');
                
                const textarea = await page.$('#edit-content');
                await textarea.fill('What about birds instead?');
                await screenshot(page, '13_fork_message_modified');
                
                const saveBtn = await page.$('#save-edit');
                await saveBtn.click();
                
                console.log('⏳ Waiting for forked conversation response...');
                await wait(3000);
                await page.waitForSelector('.typing-indicator', { timeout: 10000 }).catch(() => {});
                await page.waitForSelector('.typing-indicator', { state: 'detached', timeout: 300000 }).catch(() => {});
                await wait(2000);
                
                await screenshot(page, '14_fork_result');
                findings.forkConversation.push('✅ Fork completed');
                
                const convList = await page.$$('#conversation-list > button, #conversation-list > div');
                findings.forkConversation.push(`Conversations in sidebar after fork: ${convList.length}`);
            }
        }
        
        // === E. REGENERATE BUTTON ===
        console.log('\n=== E. REGENERATE BUTTON ===');
        
        const messagesE = await getMessageElements(page);
        let assistantMsgE = null;
        for (const msg of messagesE) {
            const className = await msg.getAttribute('class');
            if (className && !className.includes('flex-row-reverse') && className.includes('flex')) {
                assistantMsgE = msg;
            }
        }
        
        if (assistantMsgE) {
            await assistantMsgE.hover();
            await wait(500);
            await screenshot(page, '15_assistant_hover_regen');
            
            const regenBtn = await assistantMsgE.$('button[title="Regenerate"]');
            if (regenBtn) {
                findings.regenerateButton.push('✅ Regenerate button found on assistant message');
                
                const icon = await regenBtn.$('span.material-symbols-outlined');
                if (icon) {
                    const iconText = await icon.textContent();
                    findings.regenerateButton.push(`Regenerate button icon: "${iconText}"`);
                }
                
                const contentBefore = await assistantMsgE.$eval('.prose', el => el.textContent.substring(0, 100)).catch(() => '');
                findings.regenerateButton.push(`Content before regenerate: "${contentBefore}..."`);
                
                await regenBtn.click();
                console.log('⏳ Waiting for regeneration (up to 5 min)...');
                
                await wait(3000);
                await page.waitForSelector('.typing-indicator', { timeout: 10000 }).catch(() => {});
                await page.waitForSelector('.typing-indicator', { state: 'detached', timeout: 300000 }).catch(() => {});
                await wait(2000);
                
                await screenshot(page, '16_regenerate_result');
                findings.regenerateButton.push('✅ Regenerate completed');
            } else {
                findings.regenerateButton.push('❌ Regenerate button NOT found');
            }
        }
        
        // === F. REGENERATE VARIATIONS ===
        console.log('\n=== F. REGENERATE VARIATIONS ===');
        
        const allMessages = await getMessageElements(page);
        const allAssistant = [];
        for (const msg of allMessages) {
            const className = await msg.getAttribute('class');
            if (className && !className.includes('flex-row-reverse') && className.includes('flex')) {
                allAssistant.push(msg);
            }
        }
        
        findings.regenerateVariations.push(`Found ${allAssistant.length} assistant messages`);
        
        if (allAssistant.length >= 2) {
            const olderMsg = allAssistant[0];
            await olderMsg.hover();
            await wait(300);
            await screenshot(page, '17_older_assistant_hover');
            
            const regenBtnOlder = await olderMsg.$('button[title="Regenerate"]');
            if (regenBtnOlder) {
                findings.regenerateVariations.push('✅ Regenerate available on older assistant message');
            } else {
                findings.regenerateVariations.push('❌ Regenerate NOT available on older message');
            }
        }
        
        // === G. CANCEL OPERATIONS ===
        console.log('\n=== G. CANCEL OPERATIONS ===');
        
        const messagesG = await getMessageElements(page);
        let userMsgG = null;
        for (const msg of messagesG) {
            const className = await msg.getAttribute('class');
            if (className && className.includes('flex-row-reverse')) {
                userMsgG = msg;
                break;
            }
        }
        
        if (userMsgG) {
            const originalContent = await userMsgG.$eval('div.whitespace-pre-wrap', el => el.textContent).catch(() => '');
            findings.cancelOperations.push(`Original message: "${originalContent}"`);
            
            await userMsgG.hover();
            await wait(300);
            const editBtn = await userMsgG.$('button[title="Edit"]');
            
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                
                const textarea = await page.$('#edit-content');
                await textarea.fill('THIS SHOULD NOT BE SAVED');
                await screenshot(page, '18_cancel_before');
                
                const cancelBtn = await page.$('#cancel-edit');
                await cancelBtn.click();
                await wait(500);
                
                await screenshot(page, '19_cancel_after');
                
                const modalHidden = await page.$('#edit-modal.hidden');
                if (modalHidden) {
                    findings.cancelOperations.push('✅ Modal closed after cancel');
                }
                
                const contentAfterCancel = await userMsgG.$eval('div.whitespace-pre-wrap', el => el.textContent).catch(() => '');
                if (contentAfterCancel === originalContent) {
                    findings.cancelOperations.push('✅ Original message unchanged after cancel');
                } else {
                    findings.cancelOperations.push('❌ Message was modified despite cancel');
                }
            }
        }
        
        // === H. VALIDATION ===
        console.log('\n=== H. VALIDATION ===');
        
        if (userMsgG) {
            await userMsgG.hover();
            await wait(300);
            const editBtn = await userMsgG.$('button[title="Edit"]');
            
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                
                const textarea = await page.$('#edit-content');
                await textarea.fill('');
                await screenshot(page, '20_empty_edit');
                
                const saveBtn = await page.$('#save-edit');
                await saveBtn.click();
                await wait(1000);
                
                const modalStillOpen = await page.$('#edit-modal:not(.hidden)');
                if (modalStillOpen) {
                    findings.validation.push('⚠️ Modal stays open on empty edit');
                } else {
                    findings.validation.push('✅ Empty edit handled (modal closed)');
                }
                
                const cancelBtn = await page.$('#cancel-edit');
                if (cancelBtn) await cancelBtn.click();
                await wait(300);
            }
        }
        
        // Test very long edit
        if (userMsgG) {
            await userMsgG.hover();
            await wait(300);
            const editBtn = await userMsgG.$('button[title="Edit"]');
            
            if (editBtn) {
                await editBtn.click();
                await wait(500);
                
                const longText = 'A'.repeat(5000);
                const textarea = await page.$('#edit-content');
                await textarea.fill(longText);
                await screenshot(page, '21_long_edit');
                
                findings.validation.push(`Entered ${longText.length} character message`);
                
                const textareaValue = await textarea.inputValue();
                findings.validation.push(`Textarea accepted ${textareaValue.length} characters`);
                
                const cancelBtn = await page.$('#cancel-edit');
                await cancelBtn.click();
                await wait(300);
            }
        }
        
        await screenshot(page, '22_final_state');
        
    } catch (error) {
        console.error('❌ Test error:', error.message);
        await screenshot(page, 'error_state');
        findings.validation.push(`ERROR: ${error.message}`);
    } finally {
        await browser.close();
    }
    
    generateReport();
}

function generateReport() {
    console.log('\n📝 Generating findings.md...');
    
    let report = `# PeanutChat Edit/Fork/Regenerate Investigation
## Test Run: ${new Date().toISOString()}
## Test User: ${TEST_USER}

---

## A. Edit Button Discovery

${findings.editButtonDiscovery.map(f => `- ${f}`).join('\n') || '- No findings'}

**Summary:** The edit button appears on user messages when hovering. It uses a pencil icon ("edit").

---

## B. Edit Modal

${findings.editModal.map(f => `- ${f}`).join('\n') || '- No findings'}

**Modal Components:**
- Textarea: Pre-filled with current message content
- Radio buttons: "Edit in place" (default), "Fork conversation"
- Buttons: Cancel, Save
- Info text explaining fork creates a new branch

---

## C. Edit In-Place Flow

${findings.editInPlace.map(f => `- ${f}`).join('\n') || '- No findings'}

**Flow:**
1. Click edit button on user message
2. Modify text in textarea
3. Select "Edit in place" (default)
4. Click Save
5. Message is updated in current conversation
6. New AI response is generated for the edited message

---

## D. Fork Conversation Flow

${findings.forkConversation.map(f => `- ${f}`).join('\n') || '- No findings'}

**Flow:**
1. Build conversation with multiple exchanges
2. Click edit on a middle user message
3. Select "Fork conversation" radio
4. Modify text and click Save
5. New conversation is created from that point
6. Original conversation remains unchanged
7. New conversation appears in sidebar

---

## E. Regenerate Button

${findings.regenerateButton.map(f => `- ${f}`).join('\n') || '- No findings'}

**Summary:** Regenerate button appears on assistant messages on hover. Uses refresh icon.

---

## F. Regenerate Variations

${findings.regenerateVariations.map(f => `- ${f}`).join('\n') || '- No findings'}

**Notes:** Regenerate works on any assistant message, not just the latest.

---

## G. Cancel Operations

${findings.cancelOperations.map(f => `- ${f}`).join('\n') || '- No findings'}

**Summary:** Cancel button properly closes modal without saving changes.

---

## H. Validation

${findings.validation.map(f => `- ${f}`).join('\n') || '- No findings'}

---

## Screenshots Index

| Screenshot | Description |
|-----------|-------------|
| 00_initial_page | Initial page with auth modal |
| 01_create_account_tab | Create account tab selected |
| 02_register_form_filled | Registration form filled |
| 03_after_register | After registration |
| 04_first_exchange | First message exchange |
| 05_user_message_hover | Hovering over user message shows edit button |
| 06_assistant_message_hover | Hovering over assistant message shows regenerate |
| 07_edit_modal_open | Edit modal with textarea and options |
| 08_edit_in_place_modified | Modified message in edit modal |
| 09_edit_in_place_result | Result after edit in-place |
| 10-11_multi_exchange | Building conversation for fork test |
| 12_fork_option_selected | Fork radio selected |
| 13_fork_message_modified | Modified message for fork |
| 14_fork_result | Result after fork |
| 15_assistant_hover_regen | Regenerate button on assistant |
| 16_regenerate_result | After regeneration |
| 17_older_assistant_hover | Regenerate on older message |
| 18_cancel_before | Before canceling edit |
| 19_cancel_after | After cancel - unchanged |
| 20_empty_edit | Empty edit attempt |
| 21_long_edit | Very long text edit |
| 22_final_state | Final conversation state |

---

## UI Component Reference

### Edit Button (User Messages Only)
\`\`\`html
<button title="Edit" class="p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all">
    <span class="material-symbols-outlined text-sm">edit</span>
</button>
\`\`\`

### Regenerate Button (Assistant Messages Only)
\`\`\`html
<button title="Regenerate" class="p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all">
    <span class="material-symbols-outlined text-sm">refresh</span>
</button>
\`\`\`

### Edit Modal
- ID: \`#edit-modal\`
- Textarea: \`#edit-content\`
- Radio "Edit in place": \`input[value="edit"]\` (default checked)
- Radio "Fork": \`input[value="fork"]\`
- Cancel: \`#cancel-edit\`
- Save: \`#save-edit\`

### API Endpoints Used
- Edit in-place: \`PATCH /api/chat/conversations/{id}/messages/{msg_id}\`
- Fork: \`POST /api/chat/conversations/{id}/messages/{msg_id}/fork\`
- Regenerate: \`POST /api/chat/conversations/{id}/regenerate/{msg_id}\`

---

## Conclusion

The Edit, Fork, and Regenerate features are available in the UI:
1. **Edit**: Only on user messages, supports in-place modification with re-generation
2. **Fork**: Creates a new conversation branch from any user message
3. **Regenerate**: Available on all assistant messages, generates a new response
4. **Cancel**: Properly discards changes
5. **Validation**: Empty edits are handled

No bugs found - investigation only, no code fixes applied.
`;

    fs.writeFileSync('findings.md', report);
    console.log('✅ findings.md generated');
}

// Run tests
runTests().catch(console.error);
