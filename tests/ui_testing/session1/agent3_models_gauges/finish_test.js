const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = './screenshots';
const BASE_URL = 'http://localhost:8080';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_models3_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

async function screenshot(page, name) {
    const filePath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filePath, fullPage: false });
    console.log(`📸 Screenshot: ${filePath}`);
    return filePath;
}

async function main() {
    console.log('Finishing PeanutChat Models & Gauges Test');
    console.log(`Test user: ${TEST_USER}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    
    const findings = [];
    
    try {
        // Navigate and register
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000);
        
        // Handle auth modal
        const authModal = await page.$('#auth-modal:not(.hidden)');
        if (authModal) {
            console.log('Registering...');
            await page.click('#register-tab');
            await page.waitForTimeout(500);
            await page.fill('#register-username', TEST_USER);
            await page.fill('#register-email', `${TEST_USER}@test.com`);
            await page.fill('#register-password', TEST_PASS);
            await page.fill('#register-confirm', TEST_PASS);
            await page.click('#register-btn');
            await page.waitForTimeout(3000);
        }
        
        // Wait for model selector to be populated
        await page.waitForSelector('#model-select', { timeout: 10000 });
        await page.waitForTimeout(2000);
        
        // Get models list
        const models = await page.$$eval('#model-select option', options => 
            options.map(o => ({ value: o.value, text: o.textContent.trim() }))
        );
        console.log('Models:', models.map(m => m.text));
        findings.push('\n## Model Inventory');
        models.forEach(m => {
            if (m.value) findings.push(`- ${m.text}`);
        });
        
        // Test each model's capabilities
        findings.push('\n## Capability Matrix');
        findings.push('| Model | Tools | Vision | Thinking |');
        findings.push('|-------|-------|--------|----------|');
        
        for (const model of models) {
            if (!model.value) continue;
            await page.selectOption('#model-select', model.value);
            await page.waitForTimeout(1500);
            
            const tools = await page.$eval('#cap-tools', el => !el.classList.contains('hidden'));
            const vision = await page.$eval('#cap-vision', el => !el.classList.contains('hidden'));
            const thinking = await page.$eval('#cap-thinking', el => !el.classList.contains('hidden'));
            
            const shortName = model.value.split('/').pop().split(':')[0];
            findings.push(`| ${shortName} | ${tools ? '✅' : '❌'} | ${vision ? '✅' : '❌'} | ${thinking ? '✅' : '❌'} |`);
            
            console.log(`${model.value}: tools=${tools}, vision=${vision}, thinking=${thinking}`);
        }
        
        // Screenshot all model capabilities - iterate and screenshot each
        for (const model of models.slice(0, 3)) {
            if (!model.value) continue;
            await page.selectOption('#model-select', model.value);
            await page.waitForTimeout(1000);
            const shortName = model.value.replace(/[/:]/g, '_');
            await screenshot(page, `cap_${shortName}`);
        }
        
        // Select a fast model for message test
        await page.selectOption('#model-select', 'qwen2.5-coder:3b');
        await page.waitForTimeout(500);
        
        // Initial gauge states
        const contextBefore = await page.$eval('#context-label', el => el.textContent);
        const vramHidden = await page.$eval('#vram-gauge-container', el => el.classList.contains('hidden'));
        let vramBefore = null;
        if (!vramHidden) {
            vramBefore = await page.$eval('#vram-label', el => el.textContent);
        }
        
        findings.push('\n## Gauge States (Before Message)');
        findings.push(`- Context gauge: ${contextBefore}`);
        findings.push(`- VRAM gauge visible: ${!vramHidden}`);
        if (vramBefore) findings.push(`- VRAM: ${vramBefore}`);
        
        await screenshot(page, '20_gauges_before');
        
        // Send message
        console.log('Sending test message...');
        await page.fill('#message-input', 'Hello! Please respond briefly.');
        await screenshot(page, '21_message_ready');
        
        await page.click('#send-btn');
        console.log('Message sent, waiting for response...');
        
        // Wait for assistant response
        try {
            await page.waitForSelector('.assistant-content', { timeout: 180000 });
            console.log('Response detected, waiting for completion...');
            await page.waitForTimeout(5000); // Let streaming finish
            
            // Get response text
            const responseText = await page.$eval('.assistant-content', el => el.textContent.substring(0, 200));
            console.log('Response preview:', responseText);
            
            await screenshot(page, '22_response_received');
            
            // Check gauges after response
            const contextAfter = await page.$eval('#context-label', el => el.textContent);
            let vramAfter = null;
            const vramStillHidden = await page.$eval('#vram-gauge-container', el => el.classList.contains('hidden'));
            if (!vramStillHidden) {
                vramAfter = await page.$eval('#vram-label', el => el.textContent);
            }
            
            findings.push('\n## Gauge States (After Message)');
            findings.push(`- Context gauge: ${contextAfter}`);
            findings.push(`- VRAM gauge visible: ${!vramStillHidden}`);
            if (vramAfter) findings.push(`- VRAM: ${vramAfter}`);
            findings.push(`- Response preview: "${responseText.substring(0, 100)}..."`);
            
            await screenshot(page, '23_gauges_after');
            
        } catch (e) {
            console.log('Response timeout:', e.message);
            findings.push('\n## Message Response');
            findings.push(`- ERROR: ${e.message}`);
            await screenshot(page, '22_response_timeout');
        }
        
        // Final header screenshot
        await screenshot(page, '24_final_header');
        
    } catch (error) {
        console.error('Test error:', error);
        findings.push(`\n## ERROR\n${error.message}`);
        await screenshot(page, 'error_final');
    } finally {
        await browser.close();
    }
    
    // Append to findings
    const appendContent = `

---

# Additional Findings (Completion Run)

**Run Date:** ${new Date().toISOString()}

${findings.join('\n')}
`;
    
    fs.appendFileSync('findings.md', appendContent);
    console.log('\n✅ Additional findings appended to findings.md');
}

main().catch(console.error);
