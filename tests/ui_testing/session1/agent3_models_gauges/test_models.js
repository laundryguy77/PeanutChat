const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = './screenshots';
const BASE_URL = 'http://localhost:8080';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_models3_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

// Ensure screenshots dir exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function screenshot(page, name) {
    const filePath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filePath, fullPage: false });
    console.log(`📸 Screenshot: ${filePath}`);
    return filePath;
}

async function main() {
    console.log('Starting PeanutChat Models & Gauges Test');
    console.log(`Test user: ${TEST_USER}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    
    const findings = [];
    
    try {
        // A. Navigate to app
        console.log('\n=== A. INITIAL LOAD ===');
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000); // Allow JS to initialize
        await screenshot(page, '01_initial_load');
        findings.push('## A. Initial Load\n- Screenshot: 01_initial_load.png');
        
        // Check if auth modal appears
        const authModal = await page.$('#auth-modal:not(.hidden)');
        
        if (authModal) {
            console.log('Auth modal detected, registering...');
            await screenshot(page, '02_auth_modal');
            findings.push('- Auth modal visible: 02_auth_modal.png');
            
            // Click "Create Account" tab
            await page.click('#register-tab');
            await page.waitForTimeout(500);
            await screenshot(page, '03_register_tab');
            
            // Fill registration form
            await page.fill('#register-username', TEST_USER);
            await page.fill('#register-email', `${TEST_USER}@test.com`);
            await page.fill('#register-password', TEST_PASS);
            await page.fill('#register-confirm', TEST_PASS);
            await screenshot(page, '04_register_form_filled');
            findings.push('- Register form filled: 04_register_form_filled.png');
            
            // Submit registration
            await page.click('#register-btn');
            await page.waitForTimeout(3000);
            await screenshot(page, '05_after_register');
            findings.push('- Registered user: ' + TEST_USER);
        }
        
        // Wait for main interface to load
        await page.waitForSelector('#model-select', { timeout: 10000 });
        await page.waitForTimeout(1000);
        
        // B. MODEL SELECTOR LOCATION
        console.log('\n=== B. MODEL SELECTOR ===');
        await screenshot(page, '06_main_interface');
        findings.push('\n## B. Model Selector\n- Screenshot: 06_main_interface.png');
        
        // Get model selector info
        const modelSelect = await page.$('#model-select');
        const modelSelectBox = await modelSelect.boundingBox();
        console.log(`Model selector location: x=${modelSelectBox.x}, y=${modelSelectBox.y}, w=${modelSelectBox.width}, h=${modelSelectBox.height}`);
        findings.push(`- Model selector location: x=${Math.round(modelSelectBox.x)}, y=${Math.round(modelSelectBox.y)}`);
        
        // Get current selected value
        const currentModel = await page.$eval('#model-select', el => el.value);
        console.log(`Current model: ${currentModel}`);
        findings.push(`- Current model: ${currentModel}`);
        
        // C. DROPDOWN CONTENTS
        console.log('\n=== C. DROPDOWN CONTENTS ===');
        
        // Get all model options
        const models = await page.$$eval('#model-select option', options => 
            options.map(o => ({ value: o.value, text: o.textContent.trim() }))
        );
        console.log('Available models:', models);
        findings.push('\n## C. Dropdown Contents');
        findings.push('### Available Models:');
        models.forEach(m => {
            if (m.value) findings.push(`- ${m.text} (${m.value})`);
        });
        
        // Click to open dropdown (for visual)
        await page.click('#model-select');
        await page.waitForTimeout(500);
        await screenshot(page, '06_dropdown_open');
        findings.push('- Dropdown screenshot: 06_dropdown_open.png');
        
        // Press Escape to close
        await page.keyboard.press('Escape');
        
        // D. MODEL SWITCHING
        console.log('\n=== D. MODEL SWITCHING ===');
        findings.push('\n## D. Model Switching');
        
        // Try to select a different model if more than one
        const modelValues = models.filter(m => m.value && m.value !== currentModel);
        if (modelValues.length > 0) {
            const newModel = modelValues[0].value;
            console.log(`Switching to: ${newModel}`);
            await page.selectOption('#model-select', newModel);
            await page.waitForTimeout(1500); // Wait for capability update
            await screenshot(page, '07_model_switched');
            findings.push(`- Switched to: ${newModel}`);
            findings.push('- Screenshot: 07_model_switched.png');
        } else {
            findings.push('- Only one model available, cannot test switching');
        }
        
        // E. CAPABILITY INDICATORS
        console.log('\n=== E. CAPABILITY INDICATORS ===');
        findings.push('\n## E. Capability Indicators');
        
        // Check current capability states
        const capTools = await page.$eval('#cap-tools', el => !el.classList.contains('hidden'));
        const capVision = await page.$eval('#cap-vision', el => !el.classList.contains('hidden'));
        const capThinking = await page.$eval('#cap-thinking', el => !el.classList.contains('hidden'));
        
        console.log(`Tools: ${capTools}, Vision: ${capVision}, Thinking: ${capThinking}`);
        findings.push(`- Tools capability icon visible: ${capTools}`);
        findings.push(`- Vision capability icon visible: ${capVision}`);
        findings.push(`- Thinking capability icon visible: ${capThinking}`);
        
        await screenshot(page, '08_capability_icons');
        findings.push('- Screenshot: 08_capability_icons.png');
        
        // Test different models for capabilities
        const capabilityTests = [];
        for (const model of models.slice(0, 5)) { // Test up to 5 models
            if (!model.value) continue;
            await page.selectOption('#model-select', model.value);
            await page.waitForTimeout(1000);
            
            const tools = await page.$eval('#cap-tools', el => !el.classList.contains('hidden'));
            const vision = await page.$eval('#cap-vision', el => !el.classList.contains('hidden'));
            const thinking = await page.$eval('#cap-thinking', el => !el.classList.contains('hidden'));
            
            capabilityTests.push({
                model: model.value,
                tools,
                vision,
                thinking
            });
        }
        
        findings.push('\n### Capability Matrix:');
        findings.push('| Model | Tools | Vision | Thinking |');
        findings.push('|-------|-------|--------|----------|');
        capabilityTests.forEach(t => {
            findings.push(`| ${t.model} | ${t.tools ? '✅' : '❌'} | ${t.vision ? '✅' : '❌'} | ${t.thinking ? '✅' : '❌'} |`);
        });
        
        // Select a model with tools for the message test
        const toolsModel = capabilityTests.find(t => t.tools);
        if (toolsModel) {
            await page.selectOption('#model-select', toolsModel.model);
            await page.waitForTimeout(500);
        }
        
        // F. CONTEXT GAUGE
        console.log('\n=== F. CONTEXT GAUGE ===');
        findings.push('\n## F. Context Gauge');
        
        // Check initial context gauge
        const contextGaugeWidth = await page.$eval('#context-gauge', el => el.style.width);
        const contextLabel = await page.$eval('#context-label', el => el.textContent);
        console.log(`Initial context: ${contextGaugeWidth}, label: ${contextLabel}`);
        findings.push(`- Initial context gauge: ${contextGaugeWidth} (${contextLabel})`);
        
        await screenshot(page, '09_context_gauge_initial');
        findings.push('- Screenshot: 09_context_gauge_initial.png');
        
        // Send a test message and wait for response
        console.log('Sending test message...');
        const textarea = await page.$('#message-input');
        await textarea.fill('Hello! What model are you?');
        await screenshot(page, '10_message_typed');
        
        // Submit the message
        await page.click('#send-btn');
        
        // Wait for response (up to 5 minutes)
        console.log('Waiting for response (up to 5 minutes)...');
        try {
            await page.waitForSelector('.assistant-content', { timeout: 300000 });
            await page.waitForTimeout(2000); // Wait for streaming to complete
            
            // Check context gauge after response
            const contextGaugeWidthAfter = await page.$eval('#context-gauge', el => el.style.width);
            const contextLabelAfter = await page.$eval('#context-label', el => el.textContent);
            console.log(`After response context: ${contextGaugeWidthAfter}, label: ${contextLabelAfter}`);
            findings.push(`- After response context gauge: ${contextGaugeWidthAfter} (${contextLabelAfter})`);
            
            await screenshot(page, '11_after_response');
            findings.push('- Screenshot: 11_after_response.png');
        } catch (e) {
            console.log('Response timeout or error:', e.message);
            findings.push(`- Response error: ${e.message}`);
            await screenshot(page, '11_response_error');
        }
        
        // G. VRAM GAUGE
        console.log('\n=== G. VRAM GAUGE ===');
        findings.push('\n## G. VRAM Gauge');
        
        const vramContainerHidden = await page.$eval('#vram-gauge-container', el => el.classList.contains('hidden'));
        console.log(`VRAM container hidden: ${vramContainerHidden}`);
        findings.push(`- VRAM gauge container hidden: ${vramContainerHidden}`);
        
        if (!vramContainerHidden) {
            const vramGaugeWidth = await page.$eval('#vram-gauge', el => el.style.width);
            const vramLabel = await page.$eval('#vram-label', el => el.textContent);
            console.log(`VRAM: ${vramGaugeWidth}, label: ${vramLabel}`);
            findings.push(`- VRAM gauge: ${vramGaugeWidth} (${vramLabel})`);
        } else {
            findings.push('- VRAM gauge is hidden (no NVIDIA GPU detected or not exposed)');
        }
        
        await screenshot(page, '12_vram_gauge');
        findings.push('- Screenshot: 12_vram_gauge.png');
        
        // Final screenshot
        await screenshot(page, '13_final_state');
        findings.push('\n## Final State\n- Screenshot: 13_final_state.png');
        
    } catch (error) {
        console.error('Test error:', error);
        findings.push(`\n## ERROR\n${error.message}`);
        await screenshot(page, 'error_state');
    } finally {
        await browser.close();
    }
    
    // Write findings
    const findingsContent = `# PeanutChat Models & Capability Gauges - UI Test Findings

**Test Date:** ${new Date().toISOString()}
**Test User:** ${TEST_USER}
**Base URL:** ${BASE_URL}

${findings.join('\n')}

---
*Generated by automated UI test*
`;
    
    fs.writeFileSync('findings.md', findingsContent);
    console.log('\n✅ Findings written to findings.md');
}

main().catch(console.error);
