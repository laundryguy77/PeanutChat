const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = './screenshots';
const APP_URL = 'http://localhost:8080';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name) {
    const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`Screenshot: ${name}.png`);
    return filepath;
}

async function main() {
    // Ensure screenshot directory exists
    if (!fs.existsSync(SCREENSHOT_DIR)) {
        fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    }

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1400, height: 900 }
    });
    const page = await context.newPage();
    page.setDefaultTimeout(300000);

    const timestamp = Date.now();
    const testUser = `testuser_params3_${timestamp}`;
    
    console.log('=== PeanutChat Parameters & Compaction UI Test ===\n');
    console.log(`Test user: ${testUser}\n`);

    // Navigate to app
    await page.goto(APP_URL);
    await sleep(2000);
    await takeScreenshot(page, '01_initial_load');

    // Create account
    console.log('\n--- Creating test account ---');
    const authModal = await page.$('#auth-modal');
    if (authModal) {
        const isVisible = await authModal.evaluate(el => !el.classList.contains('hidden'));
        if (isVisible) {
            // Click Create Account tab (id=register-tab)
            const registerTab = await page.$('#register-tab');
            if (registerTab) {
                await registerTab.click();
                await sleep(500);
            }
            
            // Fill registration form
            await page.fill('#register-username', testUser);
            await page.fill('#register-password', 'TestPass123!@#');  // Complex password
            await page.fill('#register-confirm', 'TestPass123!@#');
            
            await takeScreenshot(page, '02_register_form');
            
            // Submit registration
            const registerBtn = await page.$('#register-btn');
            if (registerBtn) {
                await registerBtn.click();
                await sleep(2000);
            }
        }
    }
    
    await takeScreenshot(page, '03_after_login');

    // === A. MODEL PARAMETERS SECTION ===
    console.log('\n=== A. MODEL PARAMETERS SECTION ===');
    
    // Open settings modal
    const settingsBtn = await page.$('#settings-btn');
    if (settingsBtn) {
        await settingsBtn.click();
        await sleep(1000);
    }
    
    await takeScreenshot(page, '04_settings_modal_open');

    // Scroll to Model Parameters section
    const paramSection = await page.$('h3:has-text("Model Parameters")');
    if (paramSection) {
        await paramSection.scrollIntoViewIfNeeded();
        await sleep(500);
    }
    
    await takeScreenshot(page, '05_model_parameters_section');

    // === B. PARAMETER SLIDERS ===
    console.log('\n=== B. PARAMETER SLIDERS ===');
    
    const sliderConfigs = [
        { id: 'temperature', valueId: 'temp-value', name: 'Temperature', min: 0, max: 2, step: 0.1, default: 0.7 },
        { id: 'top-p', valueId: 'topp-value', name: 'Top_P', min: 0, max: 1, step: 0.05, default: 0.9 },
        { id: 'top-k', valueId: 'topk-value', name: 'Top_K', min: 1, max: 100, step: 1, default: 40 },
        { id: 'num-ctx', valueId: 'ctx-value', name: 'Context_Length', min: 1024, max: 32768, step: 1024, default: 4096 },
        { id: 'repeat-penalty', valueId: 'repeat-value', name: 'Repeat_Penalty', min: 1, max: 2, step: 0.1, default: 1.1 }
    ];

    const sliderResults = [];

    for (const config of sliderConfigs) {
        console.log(`\nTesting slider: ${config.name}`);
        
        const slider = await page.$(`#${config.id}`);
        const valueDisplay = await page.$(`#${config.valueId}`);
        
        if (slider) {
            // Scroll slider into view
            await slider.scrollIntoViewIfNeeded();
            await sleep(300);
            
            // Get current value
            const currentValue = await slider.evaluate(el => el.value);
            const displayValue = valueDisplay ? await valueDisplay.textContent() : 'N/A';
            
            console.log(`  Current value: ${currentValue} (display: ${displayValue})`);
            console.log(`  Range: ${config.min} - ${config.max}, Step: ${config.step}`);
            
            await takeScreenshot(page, `06_slider_${config.name}_default`);
            
            sliderResults.push({
                name: config.name,
                id: config.id,
                min: config.min,
                max: config.max,
                step: config.step,
                default: config.default,
                currentValue: currentValue,
                displayValue: displayValue
            });
        }
    }

    // === C. SLIDER INTERACTION ===
    console.log('\n=== C. SLIDER INTERACTION ===');
    
    // Test Temperature slider interaction
    const tempSlider = await page.$('#temperature');
    if (tempSlider) {
        console.log('\nTesting Temperature slider drag...');
        
        // Set to minimum (0)
        await tempSlider.evaluate(el => {
            el.value = 0;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
        
        let tempValue = await page.$eval('#temp-value', el => el.textContent);
        console.log(`  At minimum: ${tempValue}`);
        await takeScreenshot(page, '07_temperature_min');
        
        // Set to maximum (2)
        await tempSlider.evaluate(el => {
            el.value = 2;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
        
        tempValue = await page.$eval('#temp-value', el => el.textContent);
        console.log(`  At maximum: ${tempValue}`);
        await takeScreenshot(page, '08_temperature_max');
        
        // Set to middle (1)
        await tempSlider.evaluate(el => {
            el.value = 1;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
        
        tempValue = await page.$eval('#temp-value', el => el.textContent);
        console.log(`  At middle: ${tempValue}`);
        await takeScreenshot(page, '09_temperature_middle');
    }

    // Test Context Length slider
    const ctxSlider = await page.$('#num-ctx');
    if (ctxSlider) {
        console.log('\nTesting Context Length slider...');
        await ctxSlider.scrollIntoViewIfNeeded();
        
        // Set to minimum
        await ctxSlider.evaluate(el => {
            el.value = 1024;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
        
        let ctxValue = await page.$eval('#ctx-value', el => el.textContent);
        console.log(`  At minimum: ${ctxValue}`);
        await takeScreenshot(page, '10_context_length_min');
        
        // Set to maximum
        await ctxSlider.evaluate(el => {
            el.value = 32768;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
        
        ctxValue = await page.$eval('#ctx-value', el => el.textContent);
        console.log(`  At maximum: ${ctxValue}`);
        await takeScreenshot(page, '11_context_length_max');
        
        // Reset to default
        await ctxSlider.evaluate(el => {
            el.value = 4096;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(300);
    }

    // === D. COMPACTION SETTINGS ===
    console.log('\n=== D. COMPACTION SETTINGS ===');
    
    // Scroll to compaction section
    const compactionSection = await page.$('h3:has-text("Context Compaction")');
    if (compactionSection) {
        await compactionSection.scrollIntoViewIfNeeded();
        await sleep(500);
    }
    
    await takeScreenshot(page, '12_compaction_section');
    
    // Check compaction toggle
    const compactionToggle = await page.$('#compaction-enabled');
    const compactionSettings = await page.$('#compaction-settings');
    
    if (compactionToggle) {
        // Check current state
        const isEnabled = await compactionToggle.evaluate(el => el.checked);
        console.log(`  Compaction toggle enabled: ${isEnabled}`);
        
        // Screenshot enabled state
        await takeScreenshot(page, '13_compaction_enabled');
        
        // Disable compaction by clicking the label (checkbox is sr-only/hidden)
        if (isEnabled) {
            // Click the parent label that wraps the toggle
            await compactionToggle.evaluate(el => {
                el.click();
            });
            await sleep(500);
            
            const nowDisabled = await compactionToggle.evaluate(el => el.checked);
            console.log(`  After toggle, enabled: ${nowDisabled}`);
            await takeScreenshot(page, '14_compaction_disabled');
            
            // Re-enable for further testing
            await compactionToggle.evaluate(el => {
                el.click();
            });
            await sleep(500);
        }
    }

    // === E. COMPACTION SLIDERS ===
    console.log('\n=== E. COMPACTION SLIDERS ===');
    
    const compactionSliders = [
        { id: 'compaction-buffer', valueId: 'buffer-value', name: 'Summary_Buffer', min: 5, max: 30, step: 5, default: 15 },
        { id: 'compaction-threshold', valueId: 'threshold-value', name: 'Compaction_Threshold', min: 50, max: 90, step: 5, default: 70 },
        { id: 'compaction-protected', valueId: 'protected-value', name: 'Protected_Messages', min: 4, max: 12, step: 1, default: 6 }
    ];

    const compactionResults = [];

    for (const config of compactionSliders) {
        console.log(`\nTesting compaction slider: ${config.name}`);
        
        const slider = await page.$(`#${config.id}`);
        const valueDisplay = await page.$(`#${config.valueId}`);
        
        if (slider) {
            await slider.scrollIntoViewIfNeeded();
            await sleep(300);
            
            const currentValue = await slider.evaluate(el => el.value);
            const displayValue = valueDisplay ? await valueDisplay.textContent() : 'N/A';
            
            console.log(`  Current value: ${currentValue} (display: ${displayValue})`);
            console.log(`  Range: ${config.min} - ${config.max}, Step: ${config.step}`);
            
            await takeScreenshot(page, `15_compaction_${config.name}_default`);
            
            // Test slider at different values
            // Set to min
            await slider.evaluate((el, min) => {
                el.value = min;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }, config.min);
            await sleep(300);
            
            let newValue = valueDisplay ? await valueDisplay.textContent() : 'N/A';
            console.log(`  At minimum: ${newValue}`);
            await takeScreenshot(page, `16_compaction_${config.name}_min`);
            
            // Set to max
            await slider.evaluate((el, max) => {
                el.value = max;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }, config.max);
            await sleep(300);
            
            newValue = valueDisplay ? await valueDisplay.textContent() : 'N/A';
            console.log(`  At maximum: ${newValue}`);
            await takeScreenshot(page, `17_compaction_${config.name}_max`);
            
            // Reset to default
            await slider.evaluate((el, def) => {
                el.value = def;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }, config.default);
            await sleep(300);
            
            compactionResults.push({
                name: config.name,
                id: config.id,
                min: config.min,
                max: config.max,
                step: config.step,
                default: config.default,
                currentValue: currentValue,
                displayValue: displayValue
            });
        }
    }

    // Close settings modal first
    const closeBtn = await page.$('#close-settings');
    if (closeBtn) {
        await closeBtn.click();
        await sleep(500);
    }

    // === F. CONTEXT GAUGE BEHAVIOR ===
    console.log('\n=== F. CONTEXT GAUGE BEHAVIOR ===');
    
    // Check context gauge
    const contextGauge = await page.$('#context-gauge');
    if (contextGauge) {
        const gaugeWidth = await contextGauge.evaluate(el => el.style.width);
        console.log(`  Initial gauge width: ${gaugeWidth}`);
    }
    
    await takeScreenshot(page, '18_context_gauge_initial');
    
    // Send messages and monitor gauge
    const messageInput = await page.$('#message-input');
    const sendBtn = await page.$('#send-btn');
    
    if (messageInput && sendBtn) {
        console.log('\n  Sending test messages to observe gauge...');
        
        const testMessages = [
            'Hello! This is test message 1.',
            'Tell me a short joke.',
            'What is 2+2?'
        ];
        
        for (let i = 0; i < testMessages.length; i++) {
            console.log(`  Sending message ${i + 1}: "${testMessages[i]}"`);
            
            await messageInput.fill(testMessages[i]);
            await sendBtn.click();
            
            // Wait for response (with timeout)
            console.log('  Waiting for response...');
            try {
                await page.waitForSelector('.message-content', { timeout: 60000, state: 'attached' });
                // Wait a bit more for response to complete
                await sleep(5000);
            } catch (e) {
                console.log('  Response timeout - continuing...');
            }
            
            // Check gauge after each message
            if (contextGauge) {
                const gaugeWidth = await contextGauge.evaluate(el => el.style.width);
                console.log(`  Gauge width after message ${i + 1}: ${gaugeWidth}`);
            }
            
            await takeScreenshot(page, `19_gauge_after_msg_${i + 1}`);
        }
    }
    
    await takeScreenshot(page, '20_gauge_after_all_messages');

    // === G. SAVE PERSISTENCE ===
    console.log('\n=== G. SAVE PERSISTENCE ===');
    
    // Re-open settings
    if (settingsBtn) {
        await settingsBtn.click();
        await sleep(1000);
    }
    
    // Change some values
    console.log('\n  Setting custom values...');
    
    const newTemp = 1.5;
    const newTopK = 75;
    const newBuffer = 25;
    
    // Set temperature
    if (tempSlider) {
        await tempSlider.scrollIntoViewIfNeeded();
        await tempSlider.evaluate(el => {
            el.value = 1.5;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(200);
        console.log(`  Set temperature to 1.5`);
    }
    
    // Set top-k
    const topKSlider = await page.$('#top-k');
    if (topKSlider) {
        await topKSlider.scrollIntoViewIfNeeded();
        await topKSlider.evaluate(el => {
            el.value = 75;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(200);
        console.log(`  Set top-k to 75`);
    }
    
    // Set compaction buffer
    const bufferSlider = await page.$('#compaction-buffer');
    if (bufferSlider) {
        await bufferSlider.scrollIntoViewIfNeeded();
        await bufferSlider.evaluate(el => {
            el.value = 25;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
        await sleep(200);
        console.log(`  Set compaction buffer to 25%`);
    }
    
    await takeScreenshot(page, '21_custom_values_set');
    
    // Save settings
    const saveBtn = await page.$('#save-settings');
    if (saveBtn) {
        await saveBtn.scrollIntoViewIfNeeded();
        await saveBtn.click();
        await sleep(2000);
        console.log('  Settings saved');
    }
    
    await takeScreenshot(page, '22_after_save');
    
    // Refresh page
    console.log('\n  Refreshing page...');
    await page.reload();
    await sleep(3000);
    
    await takeScreenshot(page, '23_after_refresh');
    
    // Re-open settings and verify persistence
    const settingsBtnAfter = await page.$('#settings-btn');
    if (settingsBtnAfter) {
        await settingsBtnAfter.click();
        await sleep(1000);
    }
    
    // Check values
    console.log('\n  Verifying persisted values...');
    
    const tempSliderAfter = await page.$('#temperature');
    if (tempSliderAfter) {
        const tempValue = await tempSliderAfter.evaluate(el => el.value);
        const tempDisplay = await page.$eval('#temp-value', el => el.textContent);
        console.log(`  Temperature: ${tempValue} (display: ${tempDisplay}) - Expected: 1.5`);
    }
    
    const topKSliderAfter = await page.$('#top-k');
    if (topKSliderAfter) {
        const topKValue = await topKSliderAfter.evaluate(el => el.value);
        const topKDisplay = await page.$eval('#topk-value', el => el.textContent);
        console.log(`  Top K: ${topKValue} (display: ${topKDisplay}) - Expected: 75`);
    }
    
    const bufferSliderAfter = await page.$('#compaction-buffer');
    if (bufferSliderAfter) {
        await bufferSliderAfter.scrollIntoViewIfNeeded();
        const bufferValue = await bufferSliderAfter.evaluate(el => el.value);
        const bufferDisplay = await page.$eval('#buffer-value', el => el.textContent);
        console.log(`  Compaction Buffer: ${bufferValue} (display: ${bufferDisplay}) - Expected: 25%`);
    }
    
    await takeScreenshot(page, '24_verify_persistence');
    
    // Close browser
    await browser.close();
    
    console.log('\n=== Test Complete ===');
    console.log(`\nScreenshots saved to: ${SCREENSHOT_DIR}`);
    
    // Output summary for findings.md
    console.log('\n\n=== FINDINGS SUMMARY ===');
    console.log('\nModel Parameters:');
    sliderResults.forEach(s => {
        console.log(`  ${s.name}: range ${s.min}-${s.max}, step ${s.step}, default ${s.default}`);
    });
    console.log('\nCompaction Settings:');
    compactionResults.forEach(s => {
        console.log(`  ${s.name}: range ${s.min}-${s.max}, step ${s.step}, default ${s.default}`);
    });
}

main().catch(console.error);
