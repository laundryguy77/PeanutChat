const { chromium } = require('@playwright/test');

async function debug() {
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    page.setDefaultTimeout(30000);
    
    console.log('1. Going to PeanutChat...');
    await page.goto('http://localhost:8080', { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 3000)); // Just wait a few seconds
    
    await page.screenshot({ path: './screenshots/debug_01_initial.png' });
    console.log('📸 Initial page screenshot saved');
    
    // Check what's on the page
    console.log('\n2. Checking page state...');
    const authModal = await page.$('#auth-modal');
    const authModalHidden = authModal ? await authModal.getAttribute('class') : 'not found';
    console.log(`Auth modal class: ${authModalHidden}`);
    
    const userMenuBtn = await page.$('#user-menu-btn');
    console.log(`User menu button: ${userMenuBtn ? 'found' : 'not found'}`);
    
    // Try to find registration elements
    const registerUsername = await page.$('#register-username');
    console.log(`Register username field visible: ${registerUsername ? 'found' : 'not found'}`);
    
    // Check if already logged in
    const messageInput = await page.$('#message-input');
    console.log(`Message input: ${messageInput ? 'found' : 'not found'}`);
    
    // Check for login form
    const loginForm = await page.$('#login-username');
    console.log(`Login username field: ${loginForm ? 'found' : 'not found'}`);
    
    // Check tabs in auth modal
    const authTabs = await page.$$('#auth-modal button');
    console.log(`Auth modal buttons count: ${authTabs.length}`);
    
    // Try clicking user menu to show auth modal
    if (userMenuBtn) {
        console.log('\n3. Clicking user menu button...');
        await userMenuBtn.click();
        await new Promise(r => setTimeout(r, 1000));
        await page.screenshot({ path: './screenshots/debug_02_after_menu_click.png' });
        console.log('📸 After menu click screenshot saved');
    }
    
    // Check auth modal state again
    const authModalAfter = await page.$('#auth-modal');
    const authModalClassAfter = authModalAfter ? await authModalAfter.getAttribute('class') : 'not found';
    console.log(`Auth modal class after click: ${authModalClassAfter}`);
    
    // Look for register tab
    const registerTab = await page.$('button:has-text("Register")');
    console.log(`Register tab: ${registerTab ? 'found' : 'not found'}`);
    
    if (registerTab) {
        console.log('\n4. Clicking Register tab...');
        await registerTab.click();
        await new Promise(r => setTimeout(r, 500));
        await page.screenshot({ path: './screenshots/debug_03_register_tab.png' });
        
        const regUsernameNow = await page.$('#register-username');
        console.log(`Register username visible after tab click: ${regUsernameNow ? 'yes' : 'no'}`);
    }
    
    await browser.close();
    console.log('\nDebug complete');
}

debug().catch(console.error);
