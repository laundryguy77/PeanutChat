const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TIMESTAMP = Date.now();
const TEST_USER = `testuser_attach_${TIMESTAMP}`;
const TEST_PASS = 'TestPass123!';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function screenshot(page, name) {
    const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage: false });
    console.log(`📸 Screenshot: ${name}`);
    return filepath;
}

// Helper to close tools menu if open
async function closeToolsMenu(page) {
    const menu = await page.$('#tools-menu:not(.hidden)');
    if (menu) {
        await page.click('body', { position: { x: 640, y: 300 } }); // Click away
        await sleep(300);
    }
}

async function main() {
    console.log('🚀 Starting PeanutChat UI Test - Attachments & Thinking Mode');
    console.log(`Test user: ${TEST_USER}\n`);

    if (!fs.existsSync(SCREENSHOT_DIR)) {
        fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    }

    const browser = await chromium.launch({
        executablePath: '/home/tech/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome',
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 900 }  // Taller viewport to see full menu
    });
    
    const page = await context.newPage();
    page.setDefaultTimeout(30000);

    const findings = [];
    
    try {
        // Navigate to app
        console.log('📍 Navigating to PeanutChat...');
        await page.goto(BASE_URL);
        await sleep(2000);
        await screenshot(page, '00_login_page');

        // Create account
        console.log('👤 Creating test account...');
        const createTab = await page.$('button:has-text("Create Account")');
        if (createTab) {
            await createTab.click();
            await sleep(500);
            await page.fill('#register-username', TEST_USER);
            await page.fill('#register-password', TEST_PASS);
            await page.fill('#register-confirm', TEST_PASS);
            await page.click('#register-btn');
            await sleep(2000);
        }

        await page.waitForSelector('#message-input', { timeout: 10000 });
        await sleep(1000);
        await screenshot(page, '01_main_ui');
        console.log('✅ Logged in!\n');

        // ============================================
        // A. TOOLS MENU
        // ============================================
        console.log('🔧 A. TOOLS MENU INVESTIGATION');
        
        const toolsBtn = await page.$('#tools-btn');
        await screenshot(page, 'A1_tools_button');
        
        if (toolsBtn) {
            findings.push({ section: 'A', element: '#tools-btn', found: true, notes: 'Plus button in input area' });

            await toolsBtn.click();
            await sleep(500);
            
            // Take screenshot of full page to see menu position
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'A2_tools_menu_open.png'), fullPage: true });
            console.log('📸 Screenshot: A2_tools_menu_open');
            
            // Check for both menu items
            const addFilesBtn = await page.$('#menu-attach-files');
            const thinkingBtn = await page.$('#menu-thinking');
            const checkbox = await page.$('#thinking-checkbox');
            
            findings.push({
                section: 'A',
                element: 'Menu Items',
                found: !!addFilesBtn && !!thinkingBtn,
                notes: `Add files: ${!!addFilesBtn}, Thinking: ${!!thinkingBtn}, Checkbox: ${!!checkbox}`
            });

            await closeToolsMenu(page);
        }

        // ============================================
        // B. FILE INPUTS
        // ============================================
        console.log('\n📂 B. FILE INPUTS INVESTIGATION');
        
        const imageUpload = await page.$('#image-upload');
        const fileUpload = await page.$('#file-upload');
        
        if (imageUpload) {
            const accept = await imageUpload.getAttribute('accept');
            findings.push({ section: 'B', element: '#image-upload', found: true, notes: `accept="${accept}"` });
        }
        
        if (fileUpload) {
            const accept = await fileUpload.getAttribute('accept');
            findings.push({ section: 'B', element: '#file-upload', found: true, notes: `accept="${accept?.substring(0,80)}..."` });
        }

        // ============================================
        // C. IMAGE UPLOAD  
        // ============================================
        console.log('\n🖼️ C. IMAGE UPLOAD INVESTIGATION');
        
        const testImagePath = path.resolve('./test_image.png');
        if (fs.existsSync(testImagePath) && imageUpload) {
            await closeToolsMenu(page);
            
            await imageUpload.setInputFiles(testImagePath);
            await sleep(1000);
            await screenshot(page, 'C1_image_preview');
            
            const previewContainer = await page.$('#image-previews');
            const html = previewContainer ? await previewContainer.innerHTML() : '';
            findings.push({ section: 'C', element: 'Image Preview', found: html.length > 10, notes: `HTML length: ${html.length}` });

            // Find and click remove button
            const removeBtn = await page.$('#image-previews button');
            if (removeBtn) {
                findings.push({ section: 'C', element: 'Remove Button', found: true, notes: 'Remove button present' });
                await removeBtn.click();
                await sleep(300);
                await screenshot(page, 'C2_after_remove');
            }
        }

        // ============================================
        // D. FILE UPLOAD
        // ============================================
        console.log('\n📄 D. FILE UPLOAD INVESTIGATION');
        
        const testDocPath = path.resolve('./test_doc.txt');
        if (fs.existsSync(testDocPath) && fileUpload) {
            await closeToolsMenu(page);
            
            await fileUpload.setInputFiles(testDocPath);
            await sleep(1000);
            await screenshot(page, 'D1_file_badge');
            
            const previewContainer = await page.$('#file-previews');
            const text = previewContainer ? await previewContainer.textContent() : '';
            findings.push({ section: 'D', element: 'File Badge', found: text.includes('test_doc'), notes: `Text: "${text.trim()}"` });

            // Clear
            const removeBtn = await page.$('#file-previews button');
            if (removeBtn) {
                await removeBtn.click();
                await sleep(300);
            }
        }

        // ============================================
        // E. MULTIPLE ATTACHMENTS
        // ============================================
        console.log('\n📎 E. MULTIPLE ATTACHMENTS INVESTIGATION');
        
        fs.writeFileSync('./test_doc2.txt', 'Second file');
        fs.writeFileSync('./test_doc3.txt', 'Third file');
        
        if (fileUpload) {
            await closeToolsMenu(page);
            
            await fileUpload.setInputFiles([testDocPath, './test_doc2.txt', './test_doc3.txt']);
            await sleep(1000);
            await screenshot(page, 'E1_multiple_files');
            
            const badges = await page.$$('#file-previews > div');
            findings.push({ section: 'E', element: 'Multiple Files', found: badges.length >= 3, notes: `Count: ${badges.length}` });

            // Remove one
            const btns = await page.$$('#file-previews button');
            if (btns.length > 0) {
                await btns[0].click();
                await sleep(300);
                const remaining = await page.$$('#file-previews > div');
                await screenshot(page, 'E2_after_remove');
                findings.push({ section: 'E', element: 'Individual Remove', found: remaining.length < badges.length, notes: `After: ${remaining.length}` });
            }

            // Clear all
            let allBtns = await page.$$('#file-previews button');
            for (const btn of allBtns) { await btn.click(); await sleep(100); }
        }

        // ============================================
        // G. THINKING MODE TOGGLE
        // ============================================
        console.log('\n🧠 G. THINKING MODE TOGGLE INVESTIGATION');
        
        await page.click('#tools-btn');
        await sleep(500);
        
        // Scroll menu if needed to see thinking option
        const menu = await page.$('#tools-menu');
        if (menu) {
            await menu.evaluate(el => el.scrollTop = el.scrollHeight);
        }
        await screenshot(page, 'G1_thinking_in_menu');
        
        const thinkingCheckbox = await page.$('#thinking-checkbox');
        if (thinkingCheckbox) {
            const initial = await thinkingCheckbox.isChecked();
            findings.push({ section: 'G', element: 'Checkbox', found: true, notes: `Initial: ${initial ? 'ON' : 'OFF'}` });

            // Toggle via menu button
            await page.click('#menu-thinking');
            await sleep(500);
            
            const after = await thinkingCheckbox.isChecked();
            await screenshot(page, 'G2_thinking_toggled');
            findings.push({ section: 'G', element: 'Toggle', found: after !== initial, notes: `After: ${after ? 'ON' : 'OFF'}` });
        } else {
            findings.push({ section: 'G', element: 'Checkbox', found: false, notes: 'Not found in DOM' });
        }
        
        await closeToolsMenu(page);
        
        // Check mode indicator
        const indicator = await page.$('#mode-indicator');
        if (indicator) {
            const hidden = await indicator.evaluate(el => el.classList.contains('hidden'));
            await screenshot(page, 'G3_mode_indicator');
            findings.push({ section: 'G', element: 'Mode Indicator', found: true, notes: `Visible: ${!hidden}` });
        }

        // ============================================
        // F. SEND WITH ATTACHMENTS
        // ============================================
        console.log('\n📤 F. SEND WITH ATTACHMENTS INVESTIGATION');
        
        // Disable thinking first
        await page.click('#tools-btn');
        await sleep(300);
        const chk = await page.$('#thinking-checkbox');
        if (chk && await chk.isChecked()) {
            await page.click('#menu-thinking');
            await sleep(200);
        }
        await closeToolsMenu(page);
        
        // Attach and send
        await fileUpload.setInputFiles(testDocPath);
        await sleep(500);
        await page.fill('#message-input', 'What is in this file?');
        await screenshot(page, 'F1_ready_to_send');
        
        await page.click('#send-btn');
        console.log('   Waiting for response (up to 5 min)...');
        
        page.setDefaultTimeout(300000);
        try {
            await page.waitForFunction(() => {
                const bar = document.querySelector('#model-status-bar');
                return !bar || bar.classList.contains('hidden');
            }, { timeout: 300000 });
            await sleep(2000);
            await screenshot(page, 'F2_response');
            findings.push({ section: 'F', element: 'Response', found: true, notes: 'Response received' });
        } catch (e) {
            await screenshot(page, 'F2_timeout');
            findings.push({ section: 'F', element: 'Response', found: false, notes: e.message });
        }

        // ============================================
        // H. THINKING IN ACTION
        // ============================================
        console.log('\n💭 H. THINKING IN ACTION INVESTIGATION');
        
        // Enable thinking
        await page.click('#tools-btn');
        await sleep(300);
        const chkH = await page.$('#thinking-checkbox');
        if (chkH && !(await chkH.isChecked())) {
            await page.click('#menu-thinking');
            await sleep(200);
        }
        await closeToolsMenu(page);
        
        await page.fill('#message-input', 'Explain quantum entanglement briefly');
        await page.click('#send-btn');
        
        console.log('   Capturing thinking...');
        let thinkingCaptured = false;
        page.setDefaultTimeout(3000);
        
        for (let i = 0; i < 120 && !thinkingCaptured; i++) {
            await sleep(250);
            
            const statusText = await page.$eval('#status-text', el => el?.textContent || '').catch(() => '');
            const thinkingEl = await page.$('details .thinking-content');
            
            if (statusText.includes('Thinking') || thinkingEl) {
                await screenshot(page, `H1_thinking_${i}`);
                thinkingCaptured = true;
                findings.push({ section: 'H', element: 'Thinking', found: true, notes: `At ${i}: "${statusText}"` });
            }
        }
        
        if (!thinkingCaptured) {
            findings.push({ section: 'H', element: 'Thinking', found: false, notes: 'Not captured' });
        }
        
        // Wait for completion
        console.log('   Waiting...');
        page.setDefaultTimeout(300000);
        await page.waitForFunction(() => {
            const bar = document.querySelector('#model-status-bar');
            return !bar || bar.classList.contains('hidden');
        }, { timeout: 300000 }).catch(() => {});
        await sleep(2000);
        await screenshot(page, 'H2_complete');
        
        // Check context section
        const ctx = await page.$('details.context-section');
        findings.push({ section: 'H', element: 'Context Section', found: !!ctx, notes: `Found: ${!!ctx}` });

        // ============================================
        // I. THINKING COLLAPSE
        // ============================================
        console.log('\n📂 I. THINKING COLLAPSE INVESTIGATION');
        
        if (ctx) {
            const open1 = await ctx.getAttribute('open');
            await screenshot(page, 'I1_initial');
            findings.push({ section: 'I', element: 'Initial', found: true, notes: `Open: ${open1 !== null}` });
            
            const sum = await ctx.$('summary');
            if (sum) {
                await sum.click();
                await sleep(300);
                const open2 = await ctx.getAttribute('open');
                await screenshot(page, 'I2_toggled');
                findings.push({ section: 'I', element: 'Toggle', found: true, notes: `After: ${open2 !== null}` });
            }
        }

        // ============================================
        // J. WITHOUT THINKING
        // ============================================
        console.log('\n❌ J. WITHOUT THINKING INVESTIGATION');
        
        await page.click('#tools-btn');
        await sleep(300);
        const chkJ = await page.$('#thinking-checkbox');
        if (chkJ && await chkJ.isChecked()) {
            await page.click('#menu-thinking');
            await sleep(200);
        }
        await closeToolsMenu(page);
        
        const ind = await page.$('#mode-indicator');
        const hidden = ind ? await ind.evaluate(el => el.classList.contains('hidden')) : true;
        await screenshot(page, 'J1_disabled');
        findings.push({ section: 'J', element: 'Indicator', found: hidden, notes: `Hidden: ${hidden}` });
        
        await page.fill('#message-input', 'What is 2+2?');
        await page.click('#send-btn');
        
        console.log('   Simple response...');
        await page.waitForFunction(() => {
            const bar = document.querySelector('#model-status-bar');
            return !bar || bar.classList.contains('hidden');
        }, { timeout: 300000 }).catch(() => {});
        await sleep(2000);
        await screenshot(page, 'J2_response');

        // ============================================
        // K. CONTEXT SECTIONS
        // ============================================
        console.log('\n📊 K. CONTEXT SECTIONS INVESTIGATION');
        
        const allCtx = await page.$$('details.context-section');
        await screenshot(page, 'K1_overview');
        findings.push({ section: 'K', element: 'Count', found: allCtx.length > 0, notes: `Total: ${allCtx.length}` });
        
        if (allCtx.length > 0) {
            await allCtx[0].scrollIntoViewIfNeeded();
            const s = await allCtx[0].$('summary');
            if (s) await s.click();
            await sleep(300);
            await screenshot(page, 'K2_expanded');
            
            const html = await allCtx[0].innerHTML();
            findings.push({
                section: 'K',
                element: 'Contents',
                found: true,
                notes: `Reasoning: ${html.includes('psychology')}, Memories: ${html.includes('memory')}, Tools: ${html.includes('build')}`
            });
        }

        await screenshot(page, 'ZZ_final');

    } catch (error) {
        console.error('❌ Error:', error.message);
        await screenshot(page, 'ERROR_state');
        findings.push({ section: 'ERROR', element: 'Error', found: false, notes: error.message });
    } finally {
        // Generate findings.md
        console.log('\n📝 Generating findings.md...');
        
        let md = `# PeanutChat UI Investigation - Attachments & Thinking Mode

**User:** ${TEST_USER}  
**Date:** ${new Date().toISOString()}

---

## Findings

`;
        const sections = {};
        for (const f of findings) {
            if (!sections[f.section]) sections[f.section] = [];
            sections[f.section].push(f);
        }

        const sectionNames = {
            'A': 'A. TOOLS MENU',
            'B': 'B. FILE INPUTS', 
            'C': 'C. IMAGE UPLOAD',
            'D': 'D. FILE UPLOAD',
            'E': 'E. MULTIPLE ATTACHMENTS',
            'F': 'F. SEND WITH ATTACHMENTS',
            'G': 'G. THINKING MODE TOGGLE',
            'H': 'H. THINKING IN ACTION',
            'I': 'I. THINKING COLLAPSE',
            'J': 'J. WITHOUT THINKING',
            'K': 'K. CONTEXT SECTIONS',
            'ERROR': 'ERRORS'
        };

        for (const [key, items] of Object.entries(sections)) {
            md += `### ${sectionNames[key] || key}\n\n`;
            for (const item of items) {
                md += `- **${item.element}**: ${item.found ? '✅' : '❌'} - ${item.notes}\n`;
            }
            md += '\n';
        }

        md += `---

## Screenshots

`;
        const screenshots = fs.readdirSync(SCREENSHOT_DIR).filter(f => f.endsWith('.png')).sort();
        for (const ss of screenshots) {
            md += `- \`${ss}\`\n`;
        }

        md += `
---

## Code Reference

### index.html - Tools Menu (lines 336-365)
\`\`\`html
<div id="tools-menu" class="hidden absolute bottom-full ...">
  <button id="menu-attach-files">Add files</button>
  <button id="menu-thinking">
    Thinking mode
    <input type="checkbox" id="thinking-checkbox">
  </button>
</div>
\`\`\`

### index.html - File Inputs (lines 366-367)
\`\`\`html
<input type="file" id="image-upload" accept="image/*" multiple hidden>
<input type="file" id="file-upload" accept="image/*,.pdf,.zip,..." multiple hidden>
\`\`\`

### index.html - Preview Containers (lines 326-329)
\`\`\`html
<div id="file-previews" class="flex gap-2 mb-2 flex-wrap"></div>
<div id="image-previews" class="flex gap-2 mb-2 flex-wrap"></div>
\`\`\`

### index.html - Mode Indicator (lines 392-395)
\`\`\`html
<div id="mode-indicator" class="hidden ...">
  <span>psychology</span>
  <span>Thinking mode enabled</span>
</div>
\`\`\`

### chat.js - Thinking Methods
- \`appendThinkingContent(text)\`: Streams thinking tokens into details element
- \`finishThinking()\`: Stops spinner, collapses details
- \`createContextSection(metadata)\`: Creates reasoning/memories/tools section

### Thinking Display Structure
\`\`\`html
<details open class="p-4 rounded-xl bg-primary/10">
  <summary>
    <span class="animate-spin">psychology</span>
    Thinking...
  </summary>
  <div class="thinking-content">...</div>
</details>
\`\`\`

### Context Section Structure
\`\`\`html
<details class="context-section mt-3">
  <summary>Context (reasoning, N memories, M tools)</summary>
  <div class="mt-2 space-y-3">
    <!-- Model Reasoning -->
    <div class="p-3 rounded-lg bg-primary/10">...</div>
    <!-- Memories Used -->
    <div class="p-3 rounded-lg bg-purple-500/10">...</div>
    <!-- Tools Available -->
    <div class="p-3 rounded-lg bg-green-500/10">...</div>
  </div>
</details>
\`\`\`
`;

        fs.writeFileSync('findings.md', md);
        console.log('✅ findings.md generated');

        await browser.close();
        console.log('\n🎉 Test complete!');
    }
}

main().catch(console.error);
