const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_int3_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

// Ensure screenshots directory exists
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

async function waitForNetworkIdle(page, timeout = 5000) {
    try {
        await page.waitForLoadState('networkidle', { timeout });
    } catch (e) {
        // Continue if timeout
    }
}

async function runTests() {
    log('='.repeat(60));
    log('PEANUTCHAT INTEGRATION TEST - AGENT 3');
    log(`Test User: ${TEST_USER}`);
    log('='.repeat(60));

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();
    page.setDefaultTimeout(300000);

    try {
        // ==================== SECTION A: COMPLETE USER JOURNEY ====================
        log('\n' + '='.repeat(60));
        log('SECTION A: COMPLETE USER JOURNEY');
        log('='.repeat(60));

        // A1. Register new user
        log('\n--- A1: REGISTER NEW USER ---');
        await page.goto(BASE_URL);
        await waitForNetworkIdle(page);
        await screenshot(page, 'A1a_initial_page');

        // Look for register link/button
        const registerLink = await page.$('text=Register') || await page.$('text=Sign up') || await page.$('a[href*="register"]');
        if (registerLink) {
            await registerLink.click();
            await waitForNetworkIdle(page);
            await screenshot(page, 'A1b_register_form');
        }

        // Fill registration form
        const usernameField = await page.$('input[name="username"]') || await page.$('input[id="username"]') || await page.$('input[placeholder*="sername"]');
        const passwordField = await page.$('input[name="password"]') || await page.$('input[id="password"]') || await page.$('input[type="password"]');
        const confirmPasswordField = await page.$('input[name="confirm_password"]') || await page.$('input[name="confirmPassword"]') || await page.$('input[id="confirm"]');

        if (usernameField) {
            await usernameField.fill(TEST_USER);
            log(`Filled username: ${TEST_USER}`);
        }
        if (passwordField) {
            await passwordField.fill(TEST_PASS);
            log('Filled password');
        }
        if (confirmPasswordField) {
            await confirmPasswordField.fill(TEST_PASS);
            log('Filled confirm password');
        }

        await screenshot(page, 'A1c_register_filled');

        // Submit registration
        const registerBtn = await page.$('button[type="submit"]') || await page.$('button:has-text("Register")') || await page.$('button:has-text("Sign up")');
        if (registerBtn) {
            await registerBtn.click();
            await waitForNetworkIdle(page, 10000);
            await page.waitForTimeout(2000);
        }
        await screenshot(page, 'A1d_after_register');
        log('✅ Registration attempted');

        // A2. Login
        log('\n--- A2: LOGIN ---');
        // Check if we need to go to login page
        const currentUrl = page.url();
        log(`Current URL after register: ${currentUrl}`);

        if (!currentUrl.includes('chat') && !currentUrl.includes('conversation')) {
            // Try to login
            const loginLink = await page.$('text=Login') || await page.$('text=Sign in') || await page.$('a[href*="login"]');
            if (loginLink) {
                await loginLink.click();
                await waitForNetworkIdle(page);
            }
        }

        await screenshot(page, 'A2a_login_page');

        // Fill login form
        const loginUsername = await page.$('input[name="username"]') || await page.$('input[id="username"]');
        const loginPassword = await page.$('input[name="password"]') || await page.$('input[type="password"]');

        if (loginUsername && loginPassword) {
            await loginUsername.fill(TEST_USER);
            await loginPassword.fill(TEST_PASS);
            await screenshot(page, 'A2b_login_filled');

            const loginBtn = await page.$('button[type="submit"]') || await page.$('button:has-text("Login")') || await page.$('button:has-text("Sign in")');
            if (loginBtn) {
                await loginBtn.click();
                await waitForNetworkIdle(page, 10000);
                await page.waitForTimeout(2000);
            }
        }
        await screenshot(page, 'A2c_after_login');
        log(`✅ Login completed - URL: ${page.url()}`);

        // A3. Create new conversation
        log('\n--- A3: CREATE NEW CONVERSATION ---');
        await screenshot(page, 'A3a_main_interface');

        // Look for new conversation button
        const newConvoBtn = await page.$('button:has-text("New")') || 
                           await page.$('button:has-text("New Chat")') ||
                           await page.$('button:has-text("New Conversation")') ||
                           await page.$('[data-testid="new-conversation"]') ||
                           await page.$('.new-conversation') ||
                           await page.$('button.new-chat');

        if (newConvoBtn) {
            await newConvoBtn.click();
            await waitForNetworkIdle(page);
            await page.waitForTimeout(1000);
            log('✅ Clicked new conversation button');
        } else {
            log('⚠️ New conversation button not found - may already be in new chat state');
        }
        await screenshot(page, 'A3b_new_conversation');

        // A4. Send first message and wait for response
        log('\n--- A4: SEND FIRST MESSAGE ---');
        const messageInput = await page.$('textarea') || 
                            await page.$('input[type="text"][placeholder*="message"]') ||
                            await page.$('input[placeholder*="Type"]') ||
                            await page.$('.message-input') ||
                            await page.$('[data-testid="message-input"]');

        if (messageInput) {
            await messageInput.fill('Hello! This is my first message for integration testing. Can you introduce yourself briefly?');
            await screenshot(page, 'A4a_message_typed');

            // Send the message
            const sendBtn = await page.$('button:has-text("Send")') || 
                           await page.$('button[type="submit"]') ||
                           await page.$('.send-button') ||
                           await page.$('[data-testid="send-button"]');

            if (sendBtn) {
                await sendBtn.click();
            } else {
                await messageInput.press('Enter');
            }

            log('Message sent, waiting for AI response...');
            await screenshot(page, 'A4b_message_sent');

            // Wait for response
            await page.waitForTimeout(15000); // Wait for AI to respond
            await screenshot(page, 'A4c_response_received');
            log('✅ First message exchange completed');
        } else {
            log('❌ Message input not found');
        }

        // A5. Open Settings
        log('\n--- A5: OPEN SETTINGS ---');
        const settingsBtn = await page.$('button:has-text("Settings")') ||
                           await page.$('button[aria-label="Settings"]') ||
                           await page.$('.settings-button') ||
                           await page.$('[data-testid="settings"]') ||
                           await page.$('button:has-text("⚙")') ||
                           await page.$('button:has(.gear-icon)') ||
                           await page.$('a[href*="settings"]');

        let settingsOpened = false;
        if (settingsBtn) {
            await settingsBtn.click();
            await waitForNetworkIdle(page);
            await page.waitForTimeout(1000);
            settingsOpened = true;
            log('✅ Settings opened');
        } else {
            // Try clicking a user menu first
            const userMenu = await page.$('.user-menu') || await page.$('[data-testid="user-menu"]') || await page.$('.profile-icon');
            if (userMenu) {
                await userMenu.click();
                await page.waitForTimeout(500);
                const settingsOption = await page.$('text=Settings');
                if (settingsOption) {
                    await settingsOption.click();
                    await waitForNetworkIdle(page);
                    settingsOpened = true;
                    log('✅ Settings opened via user menu');
                }
            }
        }
        await screenshot(page, 'A5_settings_opened');

        // A6. Change theme
        log('\n--- A6: CHANGE THEME ---');
        let themeChanged = false;
        
        // Look for theme toggle/selector
        const themeToggle = await page.$('button:has-text("Dark")') ||
                           await page.$('button:has-text("Light")') ||
                           await page.$('select[name="theme"]') ||
                           await page.$('[data-testid="theme-toggle"]') ||
                           await page.$('.theme-toggle') ||
                           await page.$('input[type="checkbox"][id*="theme"]');

        if (themeToggle) {
            const tagName = await themeToggle.evaluate(el => el.tagName.toLowerCase());
            if (tagName === 'select') {
                await themeToggle.selectOption('dark');
            } else {
                await themeToggle.click();
            }
            await page.waitForTimeout(500);
            themeChanged = true;
            log('✅ Theme changed');
        } else {
            // Look for theme section
            const themeSection = await page.$('text=Theme') || await page.$('text=Appearance');
            if (themeSection) {
                log('Found theme section text');
            }
        }
        await screenshot(page, 'A6_theme_changed');

        // A7. Configure profile
        log('\n--- A7: CONFIGURE PROFILE ---');
        // Look for profile tab or settings
        const profileTab = await page.$('text=Profile') || 
                          await page.$('button:has-text("Profile")') ||
                          await page.$('[data-tab="profile"]');

        if (profileTab) {
            await profileTab.click();
            await page.waitForTimeout(500);
            log('✅ Profile tab opened');
        }

        // Try to find and modify profile settings
        const displayNameInput = await page.$('input[name="displayName"]') || await page.$('input[name="display_name"]');
        if (displayNameInput) {
            await displayNameInput.fill(`Test User Int3`);
            log('✅ Display name updated');
        }

        await screenshot(page, 'A7_profile_configured');

        // A8. Close settings
        log('\n--- A8: CLOSE SETTINGS ---');
        const closeBtn = await page.$('button:has-text("Close")') ||
                        await page.$('button:has-text("Done")') ||
                        await page.$('button:has-text("Save")') ||
                        await page.$('.close-button') ||
                        await page.$('button[aria-label="Close"]') ||
                        await page.$('.modal-close');

        if (closeBtn) {
            await closeBtn.click();
            await page.waitForTimeout(500);
            log('✅ Settings closed');
        } else {
            // Try pressing Escape
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
        }
        await screenshot(page, 'A8_settings_closed');

        // A9. Continue chatting
        log('\n--- A9: CONTINUE CHATTING ---');
        const messageInput2 = await page.$('textarea') || await page.$('input[type="text"][placeholder*="message"]');
        if (messageInput2) {
            await messageInput2.fill('Thanks! Now tell me about your capabilities in one sentence.');
            
            const sendBtn2 = await page.$('button:has-text("Send")') || await page.$('button[type="submit"]');
            if (sendBtn2) {
                await sendBtn2.click();
            } else {
                await messageInput2.press('Enter');
            }
            
            log('Second message sent, waiting for response...');
            await page.waitForTimeout(15000);
            log('✅ Continued chatting');
        }
        await screenshot(page, 'A9_continued_chat');

        // A10. Logout
        log('\n--- A10: LOGOUT ---');
        const logoutBtn = await page.$('button:has-text("Logout")') ||
                         await page.$('button:has-text("Sign out")') ||
                         await page.$('a[href*="logout"]') ||
                         await page.$('[data-testid="logout"]');

        if (logoutBtn) {
            await logoutBtn.click();
            await waitForNetworkIdle(page);
            await page.waitForTimeout(1000);
            log('✅ Logged out');
        } else {
            // Try user menu
            const userMenu = await page.$('.user-menu') || await page.$('[data-testid="user-menu"]');
            if (userMenu) {
                await userMenu.click();
                await page.waitForTimeout(500);
                const logoutOption = await page.$('text=Logout') || await page.$('text=Sign out');
                if (logoutOption) {
                    await logoutOption.click();
                    await waitForNetworkIdle(page);
                    log('✅ Logged out via user menu');
                }
            }
        }
        await screenshot(page, 'A10_logged_out');

        // A11. Login again
        log('\n--- A11: LOGIN AGAIN ---');
        await page.waitForTimeout(1000);
        
        // Go to login if needed
        if (!page.url().includes('login')) {
            await page.goto(BASE_URL);
            await waitForNetworkIdle(page);
        }

        const loginUsername2 = await page.$('input[name="username"]') || await page.$('input[id="username"]');
        const loginPassword2 = await page.$('input[name="password"]') || await page.$('input[type="password"]');

        if (loginUsername2 && loginPassword2) {
            await loginUsername2.fill(TEST_USER);
            await loginPassword2.fill(TEST_PASS);
            
            const loginBtn2 = await page.$('button[type="submit"]') || await page.$('button:has-text("Login")');
            if (loginBtn2) {
                await loginBtn2.click();
                await waitForNetworkIdle(page, 10000);
                await page.waitForTimeout(2000);
            }
            log('✅ Logged in again');
        }
        await screenshot(page, 'A11_logged_in_again');

        // ==================== SECTION B: SETTINGS PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION B: SETTINGS PERSISTENCE');
        log('='.repeat(60));

        log('\n--- B: VERIFY THEME PERSISTENCE ---');
        // Check if dark theme persisted (look for body class or CSS)
        const bodyClasses = await page.evaluate(() => document.body.className);
        const htmlClasses = await page.evaluate(() => document.documentElement.className);
        log(`Body classes after re-login: ${bodyClasses}`);
        log(`HTML classes after re-login: ${htmlClasses}`);

        // Check computed background color
        const bgColor = await page.evaluate(() => {
            return window.getComputedStyle(document.body).backgroundColor;
        });
        log(`Background color: ${bgColor}`);
        await screenshot(page, 'B_theme_persistence_check');

        // ==================== SECTION C: CONVERSATION PERSISTENCE ====================
        log('\n' + '='.repeat(60));
        log('SECTION C: CONVERSATION PERSISTENCE');
        log('='.repeat(60));

        log('\n--- C: VERIFY CONVERSATION HISTORY ---');
        // Look for conversation list/sidebar
        const conversationList = await page.$$('.conversation-item') || 
                                await page.$$('[data-testid="conversation"]') ||
                                await page.$$('.chat-history-item');

        const convoCount = conversationList ? conversationList.length : 0;
        log(`Found ${convoCount} conversations in list`);

        // Check if previous conversation content is visible
        const messageArea = await page.$('.message-area') || await page.$('.chat-messages') || await page.$('[data-testid="messages"]');
        if (messageArea) {
            const messageCount = await page.$$eval('.message, [data-testid="message"]', msgs => msgs.length).catch(() => 0);
            log(`Found ${messageCount} messages displayed`);
        }
        await screenshot(page, 'C_conversation_persistence');

        // ==================== SECTION D: PROFILE EFFECTS ====================
        log('\n' + '='.repeat(60));
        log('SECTION D: PROFILE EFFECTS');
        log('='.repeat(60));

        log('\n--- D: CHANGE COMMUNICATION STYLE ---');
        // Open settings again
        const settingsBtn2 = await page.$('button:has-text("Settings")') ||
                            await page.$('[data-testid="settings"]') ||
                            await page.$('.settings-button');

        if (settingsBtn2) {
            await settingsBtn2.click();
            await waitForNetworkIdle(page);
            await page.waitForTimeout(1000);
        }
        await screenshot(page, 'D1_settings_for_profile');

        // Look for communication style setting
        const styleSelect = await page.$('select[name="communication_style"]') ||
                           await page.$('select[name="style"]') ||
                           await page.$('[data-testid="style-select"]');

        if (styleSelect) {
            // Get available options
            const options = await styleSelect.$$eval('option', opts => opts.map(o => o.value));
            log(`Available styles: ${options.join(', ')}`);
            
            // Try changing to a different style
            if (options.includes('formal')) {
                await styleSelect.selectOption('formal');
                log('Changed to formal style');
            } else if (options.length > 1) {
                await styleSelect.selectOption(options[1]);
                log(`Changed to: ${options[1]}`);
            }
        }
        await screenshot(page, 'D2_style_changed');

        // Close settings and test response
        const closeBtn2 = await page.$('button:has-text("Close")') || await page.$('button:has-text("Save")');
        if (closeBtn2) {
            await closeBtn2.click();
            await page.waitForTimeout(500);
        } else {
            await page.keyboard.press('Escape');
        }

        // Send a message to test style
        const msgInput3 = await page.$('textarea') || await page.$('input[type="text"][placeholder*="message"]');
        if (msgInput3) {
            await msgInput3.fill('Hi there! How are you doing today?');
            const sendBtn3 = await page.$('button:has-text("Send")') || await page.$('button[type="submit"]');
            if (sendBtn3) {
                await sendBtn3.click();
            } else {
                await msgInput3.press('Enter');
            }
            await page.waitForTimeout(15000);
        }
        await screenshot(page, 'D3_response_with_new_style');

        // ==================== SECTION E: MODEL SWITCH MID-CONVERSATION ====================
        log('\n' + '='.repeat(60));
        log('SECTION E: MODEL SWITCH MID-CONVERSATION');
        log('='.repeat(60));

        log('\n--- E: START NEW CONVERSATION FOR MODEL TEST ---');
        const newConvoBtn2 = await page.$('button:has-text("New")') || 
                            await page.$('button:has-text("New Chat")');
        if (newConvoBtn2) {
            await newConvoBtn2.click();
            await page.waitForTimeout(1000);
        }
        await screenshot(page, 'E1_new_conversation');

        // Send initial message
        const msgInput4 = await page.$('textarea');
        if (msgInput4) {
            await msgInput4.fill('Tell me a short joke about programming.');
            const sendBtn4 = await page.$('button:has-text("Send")') || await page.$('button[type="submit"]');
            if (sendBtn4) {
                await sendBtn4.click();
            } else {
                await msgInput4.press('Enter');
            }
            await page.waitForTimeout(10000);
        }
        await screenshot(page, 'E2_first_model_response');

        // Look for model selector
        log('\n--- E: SWITCH MODEL ---');
        const modelSelector = await page.$('select[name="model"]') ||
                             await page.$('[data-testid="model-selector"]') ||
                             await page.$('.model-select') ||
                             await page.$('button:has-text("Model")');

        if (modelSelector) {
            const tagName = await modelSelector.evaluate(el => el.tagName.toLowerCase());
            if (tagName === 'select') {
                const modelOptions = await modelSelector.$$eval('option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
                log(`Available models: ${JSON.stringify(modelOptions)}`);
                
                // Select a different model if available
                if (modelOptions.length > 1) {
                    await modelSelector.selectOption(modelOptions[1].value);
                    log(`Switched to model: ${modelOptions[1].text}`);
                }
            } else {
                await modelSelector.click();
                await page.waitForTimeout(500);
                // Look for dropdown option
                const modelOption = await page.$('.model-option:nth-child(2)') || await page.$('[data-model]:nth-child(2)');
                if (modelOption) {
                    await modelOption.click();
                    log('Switched model via dropdown');
                }
            }
        } else {
            log('⚠️ Model selector not found in UI');
        }
        await screenshot(page, 'E3_model_switched');

        // Continue conversation with new model
        const msgInput5 = await page.$('textarea');
        if (msgInput5) {
            await msgInput5.fill('Now tell me another joke, but about AI this time.');
            const sendBtn5 = await page.$('button:has-text("Send")') || await page.$('button[type="submit"]');
            if (sendBtn5) {
                await sendBtn5.click();
            } else {
                await msgInput5.press('Enter');
            }
            await page.waitForTimeout(10000);
        }
        await screenshot(page, 'E4_second_model_response');

        // ==================== SECTION F: MULTI-FEATURE FLOW ====================
        log('\n' + '='.repeat(60));
        log('SECTION F: MULTI-FEATURE FLOW (THINKING MODE)');
        log('='.repeat(60));

        log('\n--- F: ENABLE THINKING MODE ---');
        // Look for thinking mode toggle
        const thinkingToggle = await page.$('input[type="checkbox"][name*="thinking"]') ||
                              await page.$('[data-testid="thinking-toggle"]') ||
                              await page.$('button:has-text("Thinking")') ||
                              await page.$('label:has-text("Thinking") input[type="checkbox"]');

        if (thinkingToggle) {
            await thinkingToggle.click();
            log('✅ Thinking mode toggled');
        } else {
            // Check settings for thinking mode
            const settingsBtn3 = await page.$('button:has-text("Settings")');
            if (settingsBtn3) {
                await settingsBtn3.click();
                await page.waitForTimeout(1000);
                
                const thinkingOption = await page.$('input[name*="thinking"]') || 
                                       await page.$('[data-testid="thinking-mode"]');
                if (thinkingOption) {
                    await thinkingOption.click();
                    log('✅ Thinking mode enabled in settings');
                }
                
                const closeBtn3 = await page.$('button:has-text("Close")') || await page.$('button:has-text("Save")');
                if (closeBtn3) await closeBtn3.click();
                else await page.keyboard.press('Escape');
            }
        }
        await screenshot(page, 'F1_thinking_mode_enabled');

        // Send complex question
        log('\n--- F: SEND COMPLEX QUESTION ---');
        const msgInput6 = await page.$('textarea');
        if (msgInput6) {
            await msgInput6.fill('Explain the philosophical implications of artificial consciousness and whether machines can truly be said to "think" in the Cartesian sense. Consider both materialist and dualist perspectives.');
            const sendBtn6 = await page.$('button:has-text("Send")') || await page.$('button[type="submit"]');
            if (sendBtn6) {
                await sendBtn6.click();
            } else {
                await msgInput6.press('Enter');
            }
            
            // Screenshot while potentially thinking
            await page.waitForTimeout(3000);
            await screenshot(page, 'F2_during_thinking');
            
            // Wait for full response
            await page.waitForTimeout(20000);
        }
        await screenshot(page, 'F3_after_thinking_response');

        // ==================== FINAL SUMMARY ====================
        log('\n' + '='.repeat(60));
        log('TEST EXECUTION COMPLETE');
        log('='.repeat(60));
        log(`Total screenshots taken: ${screenshotCount}`);
        log(`Test user: ${TEST_USER}`);
        log(`Final URL: ${page.url()}`);

    } catch (error) {
        log(`❌ ERROR: ${error.message}`);
        await screenshot(page, 'ERROR_state');
        throw error;
    } finally {
        await browser.close();
    }

    return findings;
}

// Run and save findings
runTests().then(findings => {
    const report = findings.join('\n');
    fs.writeFileSync('test_output.log', report);
    console.log('\n✅ Test complete. Output saved to test_output.log');
}).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
});
