const { chromium } = require('playwright');

async function inspect() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    page.setDefaultTimeout(30000);

    try {
        console.log('Navigating to PeanutChat...');
        await page.goto('http://localhost:8080');
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        
        console.log('\n=== PAGE STRUCTURE ===');
        console.log('URL:', page.url());
        console.log('Title:', await page.title());
        
        // Get all forms
        const forms = await page.$$eval('form', forms => forms.map(f => ({
            id: f.id,
            action: f.action,
            method: f.method
        })));
        console.log('\nForms:', JSON.stringify(forms, null, 2));
        
        // Get all inputs
        const inputs = await page.$$eval('input', inputs => inputs.map(i => ({
            type: i.type,
            name: i.name,
            id: i.id,
            placeholder: i.placeholder
        })));
        console.log('\nInputs:', JSON.stringify(inputs, null, 2));
        
        // Get all buttons
        const buttons = await page.$$eval('button', buttons => buttons.map(b => ({
            text: b.textContent.trim(),
            type: b.type,
            class: b.className
        })));
        console.log('\nButtons:', JSON.stringify(buttons, null, 2));
        
        // Get all links
        const links = await page.$$eval('a', links => links.map(a => ({
            text: a.textContent.trim().substring(0, 50),
            href: a.href
        })));
        console.log('\nLinks:', JSON.stringify(links, null, 2));
        
        // Take screenshot
        await page.screenshot({ path: './screenshots/00_inspect_initial.png', fullPage: true });
        console.log('\n📸 Screenshot saved: 00_inspect_initial.png');
        
        // Get the full HTML structure (truncated)
        const bodyHTML = await page.$eval('body', el => el.innerHTML.substring(0, 5000));
        console.log('\nBody HTML (first 5000 chars):\n', bodyHTML);
        
    } catch (e) {
        console.error('Error:', e.message);
    } finally {
        await browser.close();
    }
}

inspect();
