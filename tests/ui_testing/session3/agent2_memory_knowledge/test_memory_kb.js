/**
 * PeanutChat UI Testing - Memory & Knowledge Base
 * Session 3 - Agent 2
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8080';
const SCREENSHOT_DIR = './screenshots';
const TEST_USER = `testuser_memory2_${Date.now()}`;

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name, fullPage = false) {
    const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: filepath, fullPage });
    console.log(`📸 Screenshot: ${name}`);
    return filepath;
}

async function main() {
    // Ensure directories exist
    if (!fs.existsSync(SCREENSHOT_DIR)) {
        fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    }

    // Create test KB file
    fs.writeFileSync('test_kb.txt', 'Test document content for PeanutChat knowledge base testing.\nThis file contains sample text that should be searchable.\nKey facts: The sky is blue. Water is wet. PeanutChat is awesome.');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
    const page = await context.newPage();
    
    // Set long timeout for slow operations
    page.setDefaultTimeout(300000);

    const findings = [];
    
    try {
        console.log('\n🥜 PeanutChat Memory & Knowledge Base UI Testing');
        console.log('================================================\n');

        // 1. Navigate to app and register
        console.log('📍 Step 1: Navigate and Register');
        await page.goto(BASE_URL);
        await sleep(2000);
        await takeScreenshot(page, '01_landing_page');

        // Click register tab (labeled "Create Account")
        await page.click('#register-tab');
        await sleep(500);
        await takeScreenshot(page, '02_create_account_tab');
        
        // Fill registration form using exact IDs
        await page.fill('#register-username', TEST_USER);
        await page.fill('#register-email', `${TEST_USER}@test.com`);
        await page.fill('#register-password', 'TestPassword123!');
        await page.fill('#register-confirm', 'TestPassword123!');
        await takeScreenshot(page, '02_registration_form');

        // Click register button
        await page.click('#register-btn');
        await sleep(3000);
        
        // Check if we're logged in by looking for the chat interface
        const chatInput = await page.$('#message-input');
        if (chatInput) {
            console.log(`✅ Registered and logged in as: ${TEST_USER}`);
            findings.push({ section: 'Setup', finding: `Successfully created test user: ${TEST_USER}` });
        } else {
            console.log('⚠️ May already be logged in or registration had issues');
        }

        await takeScreenshot(page, '03_after_login');

        // 2. Open Settings Panel
        console.log('\n📍 Step 2: Open Settings Panel');
        const settingsBtn = await page.$('#settings-btn');
        if (settingsBtn) {
            await settingsBtn.click();
            await sleep(1000);
            await takeScreenshot(page, '04_settings_panel_open');
            findings.push({ section: 'Settings', finding: 'Settings panel opens via gear icon button (#settings-btn)' });
        }

        // ========================================
        // SECTION A: MEMORY SECTION
        // ========================================
        console.log('\n📍 Section A: MEMORY SECTION');
        
        // Scroll to Memory section
        const memorySection = await page.$('text=Memory');
        if (memorySection) {
            await memorySection.scrollIntoViewIfNeeded();
            await sleep(500);
        }

        // Screenshot memory stats
        const memoryCount = await page.$('#memory-count');
        const memoryCategoriesEl = await page.$('#memory-categories');
        
        if (memoryCount) {
            const countText = await memoryCount.textContent();
            findings.push({ section: 'Memory', finding: `Memory count element (#memory-count): displays "${countText}"` });
        }
        if (memoryCategoriesEl) {
            const catText = await memoryCategoriesEl.textContent();
            findings.push({ section: 'Memory', finding: `Categories count element (#memory-categories): displays "${catText}"` });
        }

        await takeScreenshot(page, '05_memory_section_stats');

        // Check for memory stats structure
        const memoryStatsHtml = await page.evaluate(() => {
            const stats = document.querySelectorAll('#memory-count, #memory-categories');
            return Array.from(stats).map(el => ({
                id: el.id,
                text: el.textContent,
                classes: el.className
            }));
        });
        findings.push({ section: 'Memory Stats Structure', finding: JSON.stringify(memoryStatsHtml, null, 2) });

        // ========================================
        // SECTION B: MEMORY CARD STRUCTURE
        // ========================================
        console.log('\n📍 Section B: MEMORY CARD STRUCTURE');
        
        // Expand memory list to see cards
        const viewMemoriesDetails = await page.$('summary:has-text("View all memories")');
        if (viewMemoriesDetails) {
            await viewMemoriesDetails.click();
            await sleep(1000);
            await takeScreenshot(page, '06_memory_list_expanded');
            findings.push({ section: 'Memory', finding: 'Memory list is expandable via <details> with "View all memories" summary' });
        }

        // Check memory list content
        const memoryListContent = await page.evaluate(() => {
            const list = document.getElementById('memory-list');
            return list ? list.innerHTML : 'Memory list not found';
        });
        
        if (memoryListContent.includes('No memories yet')) {
            findings.push({ section: 'Memory Cards', finding: 'Empty state shows: "No memories yet. The AI will learn about you over time."' });
        }

        // Document expected card structure from source
        findings.push({ 
            section: 'Memory Card Structure (from source)', 
            finding: `Expected card components:
- Container: .flex.items-start.gap-2.p-2.bg-background-dark/50.rounded-lg.group
- Content: p.text-sm.text-gray-300.break-words (memory content)
- Metadata: p.text-xs.text-gray-500 (source + date)
- Source types: "You asked" (explicit) or "Learned" (inferred)
- Importance indicator: text-yellow-500 "Important" for importance >= 8
- Delete button: opacity-0 group-hover:opacity-100, trash icon`
        });

        // Category icons from source
        findings.push({
            section: 'Memory Category Icons',
            finding: `Category icons (material-symbols-outlined):
- personal: "person"
- preference: "favorite"
- topic: "topic"
- instruction: "rule"
- general: "memory"`
        });

        // ========================================
        // SECTION C: MEMORY OPERATIONS
        // ========================================
        console.log('\n📍 Section C: MEMORY OPERATIONS');
        
        // Find Clear all button
        const clearAllBtn = await page.$('button:has-text("Clear all memories")');
        if (clearAllBtn) {
            await clearAllBtn.scrollIntoViewIfNeeded();
            await takeScreenshot(page, '07_clear_all_memories_button');
            findings.push({ section: 'Memory Operations', finding: 'Clear all button exists with delete_forever icon and red text styling' });
            
            // Document the button structure
            const clearBtnHtml = await page.evaluate(() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Clear all memories'));
                return btn ? btn.outerHTML : 'Button HTML not captured';
            });
            findings.push({ section: 'Clear All Button HTML', finding: clearBtnHtml });
        }

        // Document confirmation dialogs from source
        findings.push({
            section: 'Memory Confirmation Dialogs',
            finding: `Confirmation dialogs (window.confirm):
- Delete single: "Delete this memory?"
- Clear all: "Clear ALL memories? This cannot be undone."`
        });

        // ========================================
        // SECTION D: KNOWLEDGE BASE SECTION
        // ========================================
        console.log('\n📍 Section D: KNOWLEDGE BASE SECTION');
        
        // Scroll to Knowledge Base section
        const kbSection = await page.$('text=Knowledge Base');
        if (kbSection) {
            await kbSection.scrollIntoViewIfNeeded();
            await sleep(500);
        }

        await takeScreenshot(page, '08_knowledge_base_section');

        // Screenshot KB upload area
        const kbUploadArea = await page.$('#kb-upload-area');
        if (kbUploadArea) {
            await kbUploadArea.scrollIntoViewIfNeeded();
            await takeScreenshot(page, '09_kb_upload_area');
            
            // Get upload area styling
            const uploadAreaStyles = await page.evaluate(() => {
                const area = document.getElementById('kb-upload-area');
                if (!area) return null;
                return {
                    classes: area.className,
                    innerHTML: area.innerHTML.trim(),
                    computedBorder: getComputedStyle(area).border,
                    computedBackground: getComputedStyle(area).background
                };
            });
            findings.push({ section: 'KB Upload Area', finding: JSON.stringify(uploadAreaStyles, null, 2) });
        }

        // Document drag-drop zone styling from source
        findings.push({
            section: 'KB Drag-Drop Styling',
            finding: `Drag-drop zone (#kb-upload-area):
- Default: border-2 border-dashed border-gray-700 rounded-xl p-6 text-center hover:border-primary/50
- On dragover: adds border-primary bg-primary/10
- On dragleave/drop: removes those classes
- Contains upload_file icon (text-4xl text-gray-500)
- Text: "Drop files here or click to upload"
- Subtext: "Max 150MB per file"`
        });

        // KB Stats
        const kbDocCount = await page.$('#kb-doc-count');
        const kbChunkCount = await page.$('#kb-chunk-count');
        if (kbDocCount && kbChunkCount) {
            const docCount = await kbDocCount.textContent();
            const chunkCount = await kbChunkCount.textContent();
            findings.push({ section: 'KB Stats', finding: `Document count: ${docCount}, Chunk count: ${chunkCount}` });
        }

        await takeScreenshot(page, '10_kb_stats');

        // ========================================
        // SECTION E: KB FILE UPLOAD
        // ========================================
        console.log('\n📍 Section E: KB FILE UPLOAD');
        
        // Upload test file
        const fileInput = await page.$('#kb-file-input');
        if (fileInput) {
            const testFilePath = path.resolve('test_kb.txt');
            await fileInput.setInputFiles(testFilePath);
            console.log('📤 Uploading test_kb.txt...');
            
            // Wait for upload to complete
            await sleep(5000);
            await takeScreenshot(page, '11_after_file_upload');
            
            // Check for uploaded document in list
            const kbDocuments = await page.$('#kb-documents');
            if (kbDocuments) {
                const docListHtml = await kbDocuments.innerHTML();
                if (docListHtml.includes('test_kb.txt')) {
                    findings.push({ section: 'KB Upload', finding: 'File upload successful - test_kb.txt appears in document list' });
                }
                await takeScreenshot(page, '12_kb_document_list');
            }
        }

        // Document file type icons from source
        findings.push({
            section: 'KB File Type Icons',
            finding: `File type icons (material-symbols-outlined):
- pdf: "picture_as_pdf"
- text: "description"
- code: "code"
- default: "description"`
        });

        // Document file type mappings from backend
        findings.push({
            section: 'KB File Type Mappings (Backend)',
            finding: `File extension to type:
- pdf: 'pdf'
- txt, md, markdown, csv, log, ini, cfg: 'text'
- py, js, ts, jsx, tsx, java, go, rs, c, cpp, h, rb, php, sh, html, css, json, xml, yaml, yml, toml: 'code'
- default: 'text'`
        });

        // ========================================
        // SECTION F: KB OPERATIONS
        // ========================================
        console.log('\n📍 Section F: KB OPERATIONS');
        
        // Check for upload progress element
        const uploadProgress = await page.$('#kb-upload-progress');
        if (uploadProgress) {
            const isHidden = await uploadProgress.evaluate(el => el.classList.contains('hidden'));
            findings.push({ section: 'KB Upload Progress', finding: `Progress element exists, hidden: ${isHidden}` });
        }

        // Document delete confirmation from source
        findings.push({
            section: 'KB Delete Confirmation',
            finding: 'Confirmation dialog: "Delete this document from the knowledge base?"'
        });

        // Check for delete button on uploaded document
        const deleteBtn = await page.$('.kb-delete-btn');
        if (deleteBtn) {
            await takeScreenshot(page, '13_kb_delete_button_visible');
            findings.push({ section: 'KB Operations', finding: 'Delete button appears on hover (.kb-delete-btn) with trash icon' });
        }

        // Hover over document to show delete button
        const docItem = await page.$('#kb-documents > div');
        if (docItem) {
            await docItem.hover();
            await sleep(500);
            await takeScreenshot(page, '14_kb_document_hover');
        }

        // ========================================
        // SECTION G: KB INTEGRATION
        // ========================================
        console.log('\n📍 Section G: KB INTEGRATION');
        
        // Close settings panel first
        const closeSettingsBtn = await page.$('#close-settings, [aria-label="Close settings"]');
        if (closeSettingsBtn) {
            await closeSettingsBtn.click();
            await sleep(500);
        } else {
            // Click outside settings to close
            await page.click('#chat-container', { position: { x: 10, y: 10 } });
            await sleep(500);
        }

        await takeScreenshot(page, '15_settings_closed');

        // Send a message referencing KB content
        const messageInput = await page.$('#message-input');
        if (messageInput) {
            const testQuery = 'What color is the sky according to the documents I uploaded?';
            await messageInput.fill(testQuery);
            await takeScreenshot(page, '16_message_with_kb_query');
            
            // Send the message
            const sendBtn = await page.$('#send-btn');
            if (sendBtn) {
                await sendBtn.click();
                console.log('📨 Sent KB query, waiting for response (up to 5 min)...');
                
                // Wait for response
                await sleep(10000); // Initial wait
                
                // Poll for response
                let responseReceived = false;
                for (let i = 0; i < 30; i++) { // Up to 5 minutes (30 * 10s)
                    const messages = await page.$$('.message-assistant, .chat-message.assistant');
                    if (messages.length > 0) {
                        responseReceived = true;
                        break;
                    }
                    await sleep(10000);
                }
                
                await takeScreenshot(page, '17_kb_query_response');
                
                if (responseReceived) {
                    findings.push({ section: 'KB Integration', finding: 'AI responded to query about uploaded document content' });
                } else {
                    findings.push({ section: 'KB Integration', finding: 'No response received within timeout (may need longer)' });
                }
            }
        }

        // Check for KB usage indicator in response
        const responseHtml = await page.evaluate(() => {
            const msgs = document.querySelectorAll('.message-assistant, .chat-message');
            return Array.from(msgs).map(m => m.outerHTML).join('\n');
        });
        
        if (responseHtml.includes('knowledge') || responseHtml.includes('document')) {
            findings.push({ section: 'KB Integration', finding: 'Response may reference knowledge base content' });
        }

        await takeScreenshot(page, '18_final_state', true);

        // ========================================
        // DOCUMENT API ENDPOINTS
        // ========================================
        findings.push({
            section: 'Memory API Endpoints',
            finding: `
- GET /api/memory - List all memories with stats
- POST /api/memory - Add memory (content, category, importance)
- DELETE /api/memory/{memory_id} - Delete specific memory
- DELETE /api/memory - Clear all memories
- GET /api/memory/stats - Get memory statistics`
        });

        findings.push({
            section: 'Knowledge Base API Endpoints',
            finding: `
- POST /api/knowledge/upload - Upload document (multipart form)
- POST /api/knowledge/search - Search KB (query, top_k, threshold)
- GET /api/knowledge/documents - List all documents
- DELETE /api/knowledge/documents/{document_id} - Delete document
- GET /api/knowledge/stats - Get KB statistics`
        });

        console.log('\n✅ Testing complete!');

    } catch (error) {
        console.error('❌ Test error:', error);
        await takeScreenshot(page, 'error_state');
        findings.push({ section: 'Error', finding: error.message });
    } finally {
        await browser.close();
    }

    // Generate findings.md
    let markdown = `# PeanutChat Memory & Knowledge Base - UI Testing Findings

**Test User:** ${TEST_USER}
**Test Date:** ${new Date().toISOString()}
**App URL:** ${BASE_URL}

---

`;

    // Group findings by section
    const sections = {};
    for (const f of findings) {
        if (!sections[f.section]) sections[f.section] = [];
        sections[f.section].push(f.finding);
    }

    for (const [section, items] of Object.entries(sections)) {
        markdown += `## ${section}\n\n`;
        for (const item of items) {
            if (item.includes('\n')) {
                markdown += `\`\`\`\n${item}\n\`\`\`\n\n`;
            } else {
                markdown += `- ${item}\n`;
            }
        }
        markdown += '\n';
    }

    // Add screenshots section
    markdown += `## Screenshots Captured\n\n`;
    const screenshots = fs.readdirSync(SCREENSHOT_DIR).filter(f => f.endsWith('.png'));
    for (const ss of screenshots) {
        markdown += `- \`${ss}\`\n`;
    }

    fs.writeFileSync('findings.md', markdown);
    console.log('\n📄 Findings written to findings.md');
}

main().catch(console.error);
