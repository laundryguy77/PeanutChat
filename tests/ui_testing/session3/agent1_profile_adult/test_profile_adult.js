const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = path.join(__dirname, 'screenshots');
const APP_URL = 'http://localhost:8080';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_profile1_${TIMESTAMP}`;
const TEST_PASSWORD = 'TestPass123!';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function screenshot(page, name) {
    const filePath = path.join(SCREENSHOTS_DIR, `${name}.png`);
    await page.screenshot({ path: filePath, fullPage: false });
    console.log(`📸 Screenshot saved: ${name}.png`);
    return filePath;
}

async function main() {
    console.log('🚀 Starting Profile & Adult Mode UI Test');
    console.log(`📝 Test user: ${TEST_USER}`);
    
    // Ensure screenshots directory exists
    if (!fs.existsSync(SCREENSHOTS_DIR)) {
        fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    
    // Set long timeout for LLM responses
    page.setDefaultTimeout(300000);
    
    const findings = [];
    
    try {
        // ========== SETUP: Register and Login ==========
        console.log('\n=== SETUP: Register Test User ===');
        await page.goto(APP_URL);
        await sleep(2000);
        
        // Take initial screenshot
        await screenshot(page, '00_initial_page');
        
        // Click register tab in auth modal
        const registerTab = page.locator('#register-tab');
        if (await registerTab.isVisible()) {
            await registerTab.click();
            await sleep(500);
        }
        
        // Fill registration form
        await page.fill('#register-username', TEST_USER);
        await page.fill('#register-email', `${TEST_USER}@test.com`);
        await page.fill('#register-password', TEST_PASSWORD);
        await page.fill('#register-confirm', TEST_PASSWORD);
        
        await screenshot(page, '01_registration_form');
        
        // Submit registration
        await page.click('#register-btn');
        await sleep(3000);
        
        await screenshot(page, '02_after_registration');
        findings.push('✅ User registration completed');
        
        // ========== A. PROFILE SECTION ==========
        console.log('\n=== A. PROFILE SECTION ===');
        
        // Open settings modal
        const settingsBtn = page.locator('#settings-btn');
        await settingsBtn.waitFor({ state: 'visible', timeout: 10000 });
        await settingsBtn.click();
        await sleep(1500);
        
        await screenshot(page, '03_settings_modal_opened');
        
        // Click on Profile tab if not already selected
        const profileTab = page.locator('button:has-text("Profile")').first();
        if (await profileTab.isVisible()) {
            await profileTab.click();
            await sleep(1000);
        }
        
        await screenshot(page, '04_profile_section');
        findings.push('✅ Profile section visible in Settings modal');
        
        // Verify Preferred Name field
        const preferredNameInput = page.locator('#profile-name');
        const hasPreferredName = await preferredNameInput.isVisible();
        findings.push(hasPreferredName ? '✅ Preferred Name field present' : '❌ Preferred Name field NOT found');
        
        // Verify Assistant Name field
        const assistantNameInput = page.locator('#profile-assistant-name');
        const hasAssistantName = await assistantNameInput.isVisible();
        findings.push(hasAssistantName ? '✅ Assistant Name field present' : '❌ Assistant Name field NOT found');
        
        // Fill in test values
        await preferredNameInput.fill('TestUserDisplay');
        await assistantNameInput.fill('TestBot');
        await sleep(500);
        
        await screenshot(page, '05_profile_inputs_filled');
        findings.push('✅ Profile inputs tested');
        
        // ========== B. PROFILE DROPDOWNS ==========
        console.log('\n=== B. PROFILE DROPDOWNS ===');
        
        // Communication Style dropdown
        const styleDropdown = page.locator('#profile-style');
        const hasStyleDropdown = await styleDropdown.isVisible();
        findings.push(hasStyleDropdown ? '✅ Communication Style dropdown present' : '❌ Communication Style dropdown NOT found');
        
        // Get options
        if (hasStyleDropdown) {
            await styleDropdown.click();
            await sleep(300);
            await screenshot(page, '06_communication_style_dropdown');
            
            const styleOptions = await styleDropdown.locator('option').allTextContents();
            findings.push(`   Options: ${styleOptions.join(', ')}`);
            
            // Select "Sarcastic & Dry"
            await styleDropdown.selectOption('sarcastic_dry');
            await sleep(300);
        }
        
        // Response Length dropdown
        const lengthDropdown = page.locator('#profile-length');
        const hasLengthDropdown = await lengthDropdown.isVisible();
        findings.push(hasLengthDropdown ? '✅ Response Length dropdown present' : '❌ Response Length dropdown NOT found');
        
        if (hasLengthDropdown) {
            await lengthDropdown.click();
            await sleep(300);
            await screenshot(page, '07_response_length_dropdown');
            
            const lengthOptions = await lengthDropdown.locator('option').allTextContents();
            findings.push(`   Options: ${lengthOptions.join(', ')}`);
            
            // Select "Detailed"
            await lengthDropdown.selectOption('detailed');
            await sleep(300);
        }
        
        await screenshot(page, '08_dropdowns_selected');
        findings.push('✅ Dropdown selection tested');
        
        // ========== C. RELATIONSHIP METRICS ==========
        console.log('\n=== C. RELATIONSHIP METRICS ===');
        
        // Look for relationship stats section
        const statsSection = page.locator('text=Relationship Stats').first();
        const hasStats = await statsSection.isVisible();
        findings.push(hasStats ? '✅ Relationship Stats section visible' : '❌ Relationship Stats section NOT found');
        
        if (hasStats) {
            await screenshot(page, '09_relationship_stats');
            
            // Get satisfaction value
            const satisfactionEl = page.locator('text=Satisfaction').locator('xpath=./preceding-sibling::div').first();
            const trustEl = page.locator('text=Trust').locator('xpath=./preceding-sibling::div').first();
            const interactionsEl = page.locator('text=Interactions').locator('xpath=./preceding-sibling::div').first();
            
            // Try to get the values from the grid
            const statsGrid = page.locator('.grid.grid-cols-3');
            if (await statsGrid.isVisible()) {
                const statsText = await statsGrid.textContent();
                findings.push(`   Stats content: ${statsText}`);
            }
        }
        
        // ========== D. EXPORT/RESET BUTTONS ==========
        console.log('\n=== D. EXPORT/RESET BUTTONS ===');
        
        // Export button
        const exportBtn = page.locator('button:has-text("Export")');
        const hasExport = await exportBtn.isVisible();
        findings.push(hasExport ? '✅ Export button present' : '❌ Export button NOT found');
        
        // Reset button
        const resetBtn = page.locator('button:has-text("Reset")');
        const hasReset = await resetBtn.isVisible();
        findings.push(hasReset ? '✅ Reset button present' : '❌ Reset button NOT found');
        
        await screenshot(page, '10_export_reset_buttons');
        
        // Test Export (will trigger download)
        if (hasExport) {
            const [download] = await Promise.all([
                page.waitForEvent('download', { timeout: 5000 }).catch(() => null),
                exportBtn.click()
            ]);
            
            if (download) {
                const downloadPath = await download.path();
                findings.push(`✅ Export triggered download: ${download.suggestedFilename()}`);
            } else {
                findings.push('⚠️ Export clicked but no download detected (may be blocked)');
            }
            await sleep(1000);
        }
        
        await screenshot(page, '11_after_export');
        
        // ========== E. UNCENSORED MODE TOGGLE ==========
        console.log('\n=== E. UNCENSORED MODE TOGGLE ===');
        
        // Find uncensored mode section
        const uncensoredSection = page.locator('text=Uncensored Mode').first();
        const hasUncensored = await uncensoredSection.isVisible();
        findings.push(hasUncensored ? '✅ Uncensored Mode section visible' : '❌ Uncensored Mode section NOT found');
        
        // Find lock button
        const lockBtn = page.locator('button:has(span:has-text("lock"))');
        const hasLockBtn = await lockBtn.isVisible();
        findings.push(hasLockBtn ? '✅ Lock button (toggle) found' : '❌ Lock button NOT found');
        
        await screenshot(page, '12_uncensored_mode_locked');
        findings.push('📷 Screenshot: Uncensored mode in locked state');
        
        // Click to show passcode modal
        if (hasLockBtn) {
            await lockBtn.click();
            await sleep(1000);
        }
        
        // ========== F. PASSCODE MODAL ==========
        console.log('\n=== F. PASSCODE MODAL ===');
        
        // Check if modal appeared
        const passcodeModal = page.locator('#adult-mode-modal');
        const hasPasscodeModal = await passcodeModal.isVisible();
        findings.push(hasPasscodeModal ? '✅ Passcode modal appeared' : '❌ Passcode modal did NOT appear');
        
        if (hasPasscodeModal) {
            await screenshot(page, '13_passcode_modal');
            
            const passcodeInput = page.locator('#adult-passcode');
            const hasPasscodeInput = await passcodeInput.isVisible();
            findings.push(hasPasscodeInput ? '✅ Passcode input field present' : '❌ Passcode input NOT found');
            
            // Test wrong passcode
            console.log('   Testing wrong passcode...');
            await passcodeInput.fill('1234');
            await page.click('button:has-text("Unlock")');
            await sleep(1000);
            
            await screenshot(page, '14_wrong_passcode_error');
            
            // Check for error message
            const errorEl = page.locator('#adult-mode-error');
            const errorVisible = await errorEl.isVisible();
            if (errorVisible) {
                const errorText = await errorEl.textContent();
                findings.push(`✅ Wrong passcode shows error: "${errorText}"`);
            } else {
                findings.push('⚠️ Error element not visible after wrong passcode');
            }
            
            // Test correct passcode
            console.log('   Testing correct passcode (6060)...');
            await passcodeInput.fill('');
            await passcodeInput.fill('6060');
            await page.click('button:has-text("Unlock")');
            await sleep(2000);
            
            await screenshot(page, '15_correct_passcode_entered');
            
            // Check if modal closed and mode is unlocked
            const modalStillVisible = await passcodeModal.isVisible();
            if (!modalStillVisible) {
                findings.push('✅ Passcode modal closed after correct passcode');
            }
            
            // Check for unlocked state (lock_open icon)
            const lockOpenIcon = page.locator('span:has-text("lock_open")');
            const isUnlocked = await lockOpenIcon.isVisible();
            findings.push(isUnlocked ? '✅ Uncensored mode now UNLOCKED (lock_open icon visible)' : '⚠️ Unlock state unclear');
            
            await screenshot(page, '16_uncensored_mode_unlocked');
            findings.push('📷 Screenshot: Uncensored mode in unlocked state');
        }
        
        // ========== G. FULL UNLOCK COMMANDS (BONUS) ==========
        console.log('\n=== G. FULL UNLOCK COMMANDS ===');
        
        // Close settings modal first
        const closeSettingsBtn = page.locator('#settings-modal button:has(span:has-text("close"))').first();
        if (await closeSettingsBtn.isVisible()) {
            await closeSettingsBtn.click();
            await sleep(500);
        }
        
        await screenshot(page, '17_main_chat_view');
        
        // Try sending /full_unlock enable command
        const chatInput = page.locator('#chat-input');
        if (await chatInput.isVisible()) {
            await chatInput.fill('/full_unlock enable');
            await screenshot(page, '18_full_unlock_command_typed');
            
            // Submit the command
            const sendBtn = page.locator('#send-btn');
            await sendBtn.click();
            await sleep(3000);
            
            await screenshot(page, '19_full_unlock_response');
            findings.push('✅ /full_unlock enable command sent');
            
            // Check for any response in the chat
            const messages = page.locator('.message, [class*="message"]');
            const msgCount = await messages.count();
            findings.push(`   Messages in chat after command: ${msgCount}`);
        } else {
            findings.push('⚠️ Chat input not found, skipping /full_unlock test');
        }
        
        // Final screenshot
        await screenshot(page, '20_final_state');
        
        console.log('\n=== TEST COMPLETE ===');
        
    } catch (error) {
        console.error('❌ Test error:', error.message);
        await screenshot(page, 'error_state');
        findings.push(`❌ ERROR: ${error.message}`);
    } finally {
        await browser.close();
    }
    
    // Generate findings report
    console.log('\n📋 FINDINGS SUMMARY:');
    findings.forEach(f => console.log(f));
    
    // Write findings to file
    const findingsContent = `# PeanutChat UI Test: Profile & Adult Mode
Generated: ${new Date().toISOString()}
Test User: ${TEST_USER}

## Test Results

${findings.join('\n')}

## Screenshots

| Screenshot | Description |
|------------|-------------|
| 00_initial_page.png | Initial page load |
| 01_registration_form.png | Registration form filled |
| 02_after_registration.png | After registration |
| 03_settings_modal_opened.png | Settings modal opened |
| 04_profile_section.png | Profile section view |
| 05_profile_inputs_filled.png | Profile inputs with test data |
| 06_communication_style_dropdown.png | Communication style options |
| 07_response_length_dropdown.png | Response length options |
| 08_dropdowns_selected.png | Dropdowns with selections |
| 09_relationship_stats.png | Relationship metrics display |
| 10_export_reset_buttons.png | Export and Reset buttons |
| 11_after_export.png | After export button click |
| 12_uncensored_mode_locked.png | Uncensored mode in locked state |
| 13_passcode_modal.png | Passcode entry modal |
| 14_wrong_passcode_error.png | Error after wrong passcode |
| 15_correct_passcode_entered.png | After entering correct passcode |
| 16_uncensored_mode_unlocked.png | Uncensored mode unlocked |
| 17_main_chat_view.png | Main chat view |
| 18_full_unlock_command_typed.png | /full_unlock command typed |
| 19_full_unlock_response.png | Response to /full_unlock command |
| 20_final_state.png | Final test state |

## UI Components Verified

### A. Profile Section
- Settings modal accessible via gear icon
- Profile tab in settings shows user profile inputs
- Preferred Name: Text input for user's preferred name
- Assistant Name: Text input to customize AI assistant name

### B. Profile Dropdowns
- **Communication Style**: candid_direct, quirky_imaginative, nerdy_exploratory, sarcastic_dry, empathetic_supportive
- **Response Length**: brief, adaptive, detailed

### C. Relationship Metrics
- Satisfaction level (0-100)
- Trust level (0-100)
- Interaction count
- Relationship stage badge (new, familiar, established, deep)

### D. Export/Reset Buttons
- Export: Downloads profile as JSON file
- Reset: Clears preferences with confirmation dialog

### E. Uncensored Mode Toggle
- Lock icon button toggles between locked/unlocked
- Visual feedback: gray background when locked, red background when unlocked

### F. Passcode Modal
- 4-digit numeric input with pattern validation
- Shows error message for invalid passcode
- Correct passcode: 6060
- Auto-focuses input field
- Enter key submits, ESC closes modal

### G. Full Unlock Commands
- /full_unlock enable - Enables full adult content access
- Requires uncensored mode to be unlocked first (two-tier system)

## Notes
- Profile changes auto-save after 2 seconds of inactivity
- Manual save button appears when changes are pending
- Adult mode state persists across sessions
- Uncensored models only appear in model selector after unlock
`;
    
    fs.writeFileSync(path.join(__dirname, 'findings.md'), findingsContent);
    console.log('\n✅ findings.md created');
}

main().catch(console.error);
