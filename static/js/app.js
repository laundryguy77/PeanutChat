// Main Application Controller
import { ChatManager } from './chat.js';
import { SettingsManager } from './settings.js';

class App {
    constructor() {
        this.currentConversationId = null;
        this.chatManager = new ChatManager(this);
        this.settingsManager = new SettingsManager(this);
        this.currentModel = null;
        this.pendingImages = [];
        this.pendingFiles = [];
        this.modelCapabilities = null;
        this.thinkEnabled = false;
        this.maxFileSize = 25 * 1024 * 1024; // 25 MB
        this.isMobileView = null;
        this.sidebarCollapsed = false;
        // Search state
        this.allConversations = [];
        this.searchQuery = '';
        // Auth state
        this.isAuthenticated = false;
        this.appInitStarted = false;
        // Session ID for adult content gating
        // CRITICAL: New sessions start locked. User must run /full_unlock enable each session.
        this.sessionId = this.generateSessionId();
    }

    /**
     * Generate a unique session ID for this browser session.
     * Session ID resets on browser refresh/tab close (critical child safety requirement).
     */
    generateSessionId() {
        // Check if we already have a session ID for this tab
        let sessionId = sessionStorage.getItem('peanutchat_session_id');
        if (!sessionId) {
            // Generate a new UUID-like session ID (with fallback for non-secure contexts)
            const uuid = (typeof crypto.randomUUID === 'function')
                ? crypto.randomUUID()
                : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
                    const r = Math.random() * 16 | 0;
                    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });
            sessionId = 'sess_' + uuid;
            sessionStorage.setItem('peanutchat_session_id', sessionId);
        }
        return sessionId;
    }

    /**
     * Get headers with session ID for API requests.
     * All requests should include this to enable session-scoped adult content.
     */
    getSessionHeaders() {
        return {
            'X-Session-ID': this.sessionId
        };
    }

    async init() {
        // Setup auth event listeners first (needed before login)
        this.setupAuthEventListeners();

        // Setup auth state change handler
        authManager.setOnAuthChange((user) => this.handleAuthChange(user));

        // Check if user is already authenticated
        const authResult = await authManager.init();

        if (!authResult.authenticated) {
            // If this is a new session (new tab), clear stored conversation
            // so user starts fresh after login
            if (authResult.isNewSession) {
                sessionStorage.removeItem('currentConversationId');
            }
            // Show auth modal and wait for login
            this.showAuthModal();
            return;
        }

        // User is authenticated, continue with normal init
        await this.initializeApp();
    }

    setupAuthEventListeners() {
        // Auth modal tabs
        document.getElementById('login-tab')?.addEventListener('click', () => {
            this.switchAuthTab('login');
        });
        document.getElementById('register-tab')?.addEventListener('click', () => {
            this.switchAuthTab('register');
        });

        // Login/Register buttons
        document.getElementById('login-btn')?.addEventListener('click', () => {
            this.handleLogin();
        });
        document.getElementById('register-btn')?.addEventListener('click', () => {
            this.handleRegister();
        });
        document.getElementById('close-auth')?.addEventListener('click', () => {
            if (this.isAuthenticated) {
                this.hideAuthModal();
            }
        });

        // Enter key for login/register forms
        document.getElementById('login-password')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });
        document.getElementById('register-confirm')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.handleRegister();
        });

        // Logout button
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.handleLogout();
        });
    }

    async initializeApp() {
        if (this.appInitStarted) return;  // Prevent double initialization
        this.appInitStarted = true;

        this.isAuthenticated = true;
        this.setupEventListeners();  // Attach UI handlers first
        this.updateUserDisplay();

        await this.loadModelCapabilities();
        await this.settingsManager.loadSettings();
        await this.loadModels();
        await this.loadConversations();
        await this.updateUsageGauges();

        // Initialize profile to get assistant name
        if (typeof profileManager !== 'undefined') {
            await profileManager.init();
            this.updateAssistantName(profileManager.getAssistantName());
        }

        // Clear any stored conversation ID on page load/refresh
        // This ensures each refresh/new tab starts a fresh conversation
        console.log('[Init] Clearing stored conversation ID - new session started');
        sessionStorage.removeItem('currentConversationId');
        this.currentConversationId = null;

        // Handle sidebar based on viewport
        this.handleViewportResize();
        window.addEventListener('resize', () => this.handleViewportResize());

        // Dynamic viewport height for mobile (handles keyboard, browser chrome)
        this.updateViewportHeight();
        window.addEventListener('resize', () => this.updateViewportHeight());
        // Use visualViewport API if available (better for mobile keyboard)
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => this.updateViewportHeight());
        }

        console.log('App initialized');
    }

    handleAuthChange(user) {
        if (user) {
            this.isAuthenticated = true;
            this.hideAuthModal();
            this.updateUserDisplay();

            // If app wasn't initialized yet, do it now
            if (!this.currentModel) {
                this.initializeApp();
            }
        } else {
            this.isAuthenticated = false;
            this.updateUserDisplay();
            // Clear local state
            this.currentConversationId = null;
            this.allConversations = [];
            sessionStorage.removeItem('currentConversationId');
            // Show login modal
            this.showAuthModal();
        }
    }

    updateUserDisplay() {
        const userInfo = document.getElementById('user-info');
        const userDisplayName = document.getElementById('user-display-name');

        if (authManager.isAuthenticated()) {
            const user = authManager.getUser();
            userInfo.classList.remove('hidden');
            userDisplayName.textContent = user.username;
        } else {
            userInfo.classList.add('hidden');
            userDisplayName.textContent = 'User';
        }
    }

    showAuthModal() {
        const modal = document.getElementById('auth-modal');
        modal.classList.remove('hidden');
        // Reset to login form
        this.switchAuthTab('login');
    }

    hideAuthModal() {
        const modal = document.getElementById('auth-modal');
        modal.classList.add('hidden');
        // Clear any errors
        document.getElementById('auth-error').classList.add('hidden');
        document.getElementById('register-error').classList.add('hidden');
    }

    switchAuthTab(tab) {
        const loginTab = document.getElementById('login-tab');
        const registerTab = document.getElementById('register-tab');
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const modalTitle = document.getElementById('auth-modal-title');

        if (tab === 'login') {
            loginTab.classList.add('text-primary', 'border-primary');
            loginTab.classList.remove('text-gray-400', 'border-transparent');
            registerTab.classList.remove('text-primary', 'border-primary');
            registerTab.classList.add('text-gray-400', 'border-transparent');
            loginForm.classList.remove('hidden');
            registerForm.classList.add('hidden');
            modalTitle.textContent = 'Sign In';
        } else {
            registerTab.classList.add('text-primary', 'border-primary');
            registerTab.classList.remove('text-gray-400', 'border-transparent');
            loginTab.classList.remove('text-primary', 'border-primary');
            loginTab.classList.add('text-gray-400', 'border-transparent');
            registerForm.classList.remove('hidden');
            loginForm.classList.add('hidden');
            modalTitle.textContent = 'Create Account';
        }

        // Clear errors when switching tabs
        document.getElementById('auth-error').classList.add('hidden');
        document.getElementById('register-error').classList.add('hidden');
    }

    async handleLogin() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('auth-error');

        if (!username || !password) {
            errorDiv.textContent = 'Please enter username and password';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            await authManager.login(username, password);
            // Clear inputs
            document.getElementById('login-username').value = '';
            document.getElementById('login-password').value = '';
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('hidden');
        }
    }

    async handleRegister() {
        const username = document.getElementById('register-username').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('register-confirm').value;
        const errorDiv = document.getElementById('register-error');

        if (!username || !password) {
            errorDiv.textContent = 'Please enter username and password';
            errorDiv.classList.remove('hidden');
            return;
        }

        if (username.length < 3) {
            errorDiv.textContent = 'Username must be at least 3 characters';
            errorDiv.classList.remove('hidden');
            return;
        }

        // Password validation to match backend requirements
        if (password.length < 12) {
            errorDiv.textContent = 'Password must be at least 12 characters';
            errorDiv.classList.remove('hidden');
            return;
        }
        if (!/[A-Z]/.test(password)) {
            errorDiv.textContent = 'Password must contain at least one uppercase letter';
            errorDiv.classList.remove('hidden');
            return;
        }
        if (!/[a-z]/.test(password)) {
            errorDiv.textContent = 'Password must contain at least one lowercase letter';
            errorDiv.classList.remove('hidden');
            return;
        }
        if (!/\d/.test(password)) {
            errorDiv.textContent = 'Password must contain at least one digit';
            errorDiv.classList.remove('hidden');
            return;
        }
        if (!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;'`~]/.test(password)) {
            errorDiv.textContent = 'Password must contain at least one special character';
            errorDiv.classList.remove('hidden');
            return;
        }

        if (password !== confirm) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            await authManager.register(username, password, email || null);
            // Clear inputs
            document.getElementById('register-username').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-confirm').value = '';
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('hidden');
        }
    }

    async handleLogout() {
        await authManager.logout();
        // Clear chat and reload
        this.chatManager.clearMessages();
        document.getElementById('conversation-list').innerHTML = '';
        document.getElementById('current-chat-title').textContent = 'New Chat';
    }

    showError(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded shadow-lg z-50';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    updateViewportHeight() {
        // Use visualViewport if available (accounts for keyboard on mobile)
        const vh = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        document.documentElement.style.setProperty('--app-height', `${vh}px`);
    }

    handleViewportResize() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        const menuButton = document.getElementById('sidebar-toggle');
        const wasMobile = this.isMobileView;
        const isMobile = window.innerWidth < 768; // md breakpoint

        // First run - initialize sidebar state
        if (wasMobile === null) {
            this.isMobileView = isMobile;
            this.sidebarCollapsed = false;

            if (isMobile) {
                sidebar.classList.add('-translate-x-full');
                this.showMenuButton();
            } else {
                sidebar.classList.remove('-translate-x-full');
                this.hideMenuButton();
            }
            return;
        }

        if (wasMobile === isMobile) return;
        this.isMobileView = isMobile;

        if (isMobile) {
            // Switching to mobile - hide sidebar, show menu button
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
            this.showMenuButton();
        } else {
            // Switching to desktop - show sidebar unless user collapsed it
            if (!this.sidebarCollapsed) {
                sidebar.classList.remove('-translate-x-full');
                this.hideMenuButton();
            }
            overlay.classList.add('hidden');
        }
    }

    showMenuButton() {
        const btn = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        if (btn) {
            btn.classList.remove('hidden');
            btn.classList.add('flex');
        }
        // On desktop, collapse sidebar to hamburger button width (64px)
        if (sidebar && !this.isMobileView) {
            sidebar.style.width = '64px';
            sidebar.style.minWidth = '64px';
            sidebar.style.overflow = 'hidden';
        }
        // Expand content area when sidebar is collapsed
        this.expandContentArea();
    }

    hideMenuButton() {
        const btn = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        if (btn) {
            btn.classList.add('hidden');
            btn.classList.remove('flex');
        }
        // Restore sidebar width on desktop
        if (sidebar && !this.isMobileView) {
            sidebar.style.width = '';
            sidebar.style.minWidth = '';
            sidebar.style.overflow = '';
        }
        // Restore normal content width when sidebar is visible
        this.restoreContentArea();
    }

    expandContentArea() {
        const main = document.querySelector('main');
        const messageList = document.getElementById('message-list');
        const inputContainer = document.getElementById('input-container');
        // Add right padding to balance the 64px collapsed sidebar
        if (main && !this.isMobileView) {
            main.style.paddingRight = '64px';
        }
        // Remove max-width constraint or expand it
        if (messageList) {
            messageList.classList.remove('max-w-4xl');
            messageList.classList.add('max-w-6xl');
        }
        if (inputContainer) {
            inputContainer.classList.remove('max-w-4xl');
            inputContainer.classList.add('max-w-6xl');
        }
    }

    restoreContentArea() {
        const main = document.querySelector('main');
        const messageList = document.getElementById('message-list');
        const inputContainer = document.getElementById('input-container');
        // Remove right padding
        if (main) {
            main.style.paddingRight = '';
        }
        // Restore normal max-width
        if (messageList) {
            messageList.classList.add('max-w-4xl');
            messageList.classList.remove('max-w-6xl');
        }
        if (inputContainer) {
            inputContainer.classList.add('max-w-4xl');
            inputContainer.classList.remove('max-w-6xl');
        }
    }

    async loadModelCapabilities() {
        try {
            const response = await fetch('/api/models/capabilities', {
                credentials: 'include'
            });
            this.modelCapabilities = await response.json();
        } catch (error) {
            console.error('Failed to load model capabilities:', error);
            this.modelCapabilities = { supports_tools: false, tools: [] };
        }
    }

    async loadModels() {
        console.log('[loadModels] Starting model load...');
        const select = document.getElementById('model-select');
        try {
            const response = await fetch('/api/models', {
                credentials: 'include'
            });
            const data = await response.json();
            console.log('[loadModels] Got', data.models?.length, 'models, adult_mode:', data.adult_mode);

            // Filter out embedding models that cannot chat
            const chatModels = (data.models || []).filter(model => {
                const name = model.name.toLowerCase();
                return !name.includes('embed');
            });

            select.innerHTML = '';
            this.modelsData = {}; // Store model data for capability lookup

            if (chatModels.length > 0) {
                let selectedModel = null;
                chatModels.forEach(model => {
                    // Store model data for later use
                    this.modelsData[model.name] = model;

                    const option = document.createElement('option');
                    option.value = model.name;

                    // Build display name with capability indicators
                    let displayName = model.name;
                    const caps = [];
                    if (model.supports_tools) caps.push('tools');
                    if (model.supports_vision) caps.push('vision');
                    if (model.supports_thinking) caps.push('think');
                    if (caps.length > 0) {
                        displayName += ` (${caps.join(', ')})`;
                    }
                    option.textContent = displayName;

                    if (model.name === data.current) {
                        option.selected = true;
                        this.currentModel = model.name;
                        selectedModel = model;
                    }
                    select.appendChild(option);
                });

                // If no model matched data.current, use the first model as default
                if (!selectedModel && chatModels.length > 0) {
                    select.selectedIndex = 0;
                    this.currentModel = chatModels[0].name;
                    selectedModel = chatModels[0];
                }

                // Always update capability indicators for the selected/default model
                if (selectedModel) {
                    this.updateCapabilityIndicators(selectedModel);
                }
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No models available';
                select.appendChild(option);
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            select.innerHTML = '<option value="">Failed to load</option>';
            this.showError('Failed to load models. Check Ollama connection.');
        }
    }

    updateCapabilityIndicators(model) {
        // Update header capability icons
        const toolsIcon = document.getElementById('cap-tools');
        const visionIcon = document.getElementById('cap-vision');
        const thinkingIcon = document.getElementById('cap-thinking');

        if (toolsIcon) {
            toolsIcon.classList.toggle('hidden', !model?.supports_tools);
        }
        if (visionIcon) {
            visionIcon.classList.toggle('hidden', !model?.supports_vision);
        }
        if (thinkingIcon) {
            thinkingIcon.classList.toggle('hidden', !model?.supports_thinking);
        }

        // Update thinking toggle visibility based on model capability
        const thinkingMenuItem = document.getElementById('menu-thinking');
        if (thinkingMenuItem) {
            thinkingMenuItem.classList.toggle('hidden', !model?.supports_thinking);
        }

        // Show no-tools warning if model doesn't support tools
        const noToolsWarning = document.getElementById('no-tools-warning');
        if (noToolsWarning) {
            noToolsWarning.classList.toggle('hidden', model?.supports_tools !== false);
        }
    }

    // Gauge update methods
    async updateUsageGauges() {
        try {
            const response = await fetch('/api/models/usage', { credentials: 'include' });
            if (!response.ok) return;

            const data = await response.json();

            // Update VRAM gauge
            if (data.vram?.available) {
                this.updateGauge('vram', data.vram.percent);
                document.getElementById('vram-gauge-container')?.classList.remove('hidden');
            }
        } catch (error) {
            // Silent fail - gauges are optional
        }
    }

    updateGauge(type, percent) {
        const gauge = document.getElementById(`${type}-gauge`);
        const label = document.getElementById(`${type}-label`);

        if (!gauge || !label) return;

        gauge.style.width = `${percent}%`;
        label.textContent = `${Math.round(percent)}%`;

        // Color coding based on usage
        gauge.classList.remove('bg-primary', 'bg-yellow-500', 'bg-red-500', 'bg-green-500');

        if (type === 'vram') {
            if (percent > 90) gauge.classList.add('bg-red-500');
            else if (percent > 75) gauge.classList.add('bg-yellow-500');
            else gauge.classList.add('bg-green-500');
        } else {
            if (percent > 90) gauge.classList.add('bg-red-500');
            else if (percent > 75) gauge.classList.add('bg-yellow-500');
            else gauge.classList.add('bg-primary');
        }
    }

    updateContextUsage(currentTokens, maxTokens) {
        const percent = maxTokens > 0 ? (currentTokens / maxTokens) * 100 : 0;
        this.updateGauge('context', Math.min(percent, 100));
    }

    async updateModelCapabilities(modelName) {
        try {
            const response = await fetch(`/api/models/capabilities/${encodeURIComponent(modelName)}`, {
                credentials: 'include'
            });
            if (!response.ok) return;

            const caps = await response.json();
            this.currentModelContextWindow = caps.context_window || 4096;

            // Update context slider max if settings panel exists
            const ctxSlider = document.getElementById('settings-context');
            if (ctxSlider && caps.context_window) {
                ctxSlider.max = caps.context_window;
                if (parseInt(ctxSlider.value) > caps.context_window) {
                    ctxSlider.value = caps.context_window;
                    const ctxValue = document.getElementById('context-value');
                    if (ctxValue) ctxValue.textContent = caps.context_window;
                }
            }
        } catch (error) {
            console.warn('Failed to get model capabilities:', error);
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations', {
                credentials: 'include'
            });
            const data = await response.json();
            this.allConversations = data.conversations || [];
            this.filterAndRenderConversations();
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    }

    filterAndRenderConversations() {
        const query = this.searchQuery.toLowerCase().trim();
        let filtered = this.allConversations;

        if (query) {
            filtered = this.allConversations.filter(conv =>
                conv.title.toLowerCase().includes(query)
            );
        }

        this.renderConversationList(filtered);
    }

    groupConversationsByDate(conversations) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);

        const groups = {
            today: [],
            yesterday: [],
            week: [],
            older: []
        };

        conversations.forEach(conv => {
            const convDate = new Date(conv.updated_at);
            if (convDate >= today) {
                groups.today.push(conv);
            } else if (convDate >= yesterday) {
                groups.yesterday.push(conv);
            } else if (convDate >= weekAgo) {
                groups.week.push(conv);
            } else {
                groups.older.push(conv);
            }
        });

        return groups;
    }

    renderConversationList(conversations) {
        const list = document.getElementById('conversation-list');
        list.innerHTML = '';

        if (conversations.length === 0) {
            list.innerHTML = `
                <div class="text-center text-gray-500 py-8 text-sm">
                    No conversations yet
                </div>
            `;
            return;
        }

        const groups = this.groupConversationsByDate(conversations);

        const renderGroup = (title, convs) => {
            if (convs.length === 0) return;

            const groupEl = document.createElement('div');
            groupEl.className = 'space-y-1 mb-4';
            groupEl.innerHTML = `
                <div class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">${title}</div>
            `;

            convs.forEach(conv => {
                const isActive = conv.id === this.currentConversationId;
                const item = document.createElement('button');
                item.className = `w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors truncate group relative ${
                    isActive
                        ? 'bg-surface-dark/80 border border-gray-700/50 text-white font-medium shadow-sm'
                        : 'text-gray-400 hover:bg-surface-dark/50 hover:text-gray-200'
                }`;
                item.dataset.id = conv.id;

                if (isActive) {
                    item.innerHTML = `
                        <span class="block truncate pr-12">${conv.title || 'New Chat'}</span>
                        <div class="absolute inset-y-0 left-0 w-1 bg-primary rounded-l-lg"></div>
                        <div class="absolute right-2 top-1/2 -translate-y-1/2 hidden group-hover:flex gap-1">
                            <span class="conv-action p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white" data-action="rename" title="Rename">
                                <span class="material-symbols-outlined text-sm">edit</span>
                            </span>
                            <span class="conv-action p-1 hover:bg-white/10 rounded text-gray-400 hover:text-red-400" data-action="delete" title="Delete">
                                <span class="material-symbols-outlined text-sm">delete</span>
                            </span>
                        </div>
                    `;
                } else {
                    item.innerHTML = `
                        <span class="block truncate pr-12">${conv.title || 'New Chat'}</span>
                        <div class="absolute right-2 top-1/2 -translate-y-1/2 hidden group-hover:flex gap-1">
                            <span class="conv-action p-1 hover:bg-white/10 rounded text-gray-400 hover:text-white" data-action="rename" title="Rename">
                                <span class="material-symbols-outlined text-sm">edit</span>
                            </span>
                            <span class="conv-action p-1 hover:bg-white/10 rounded text-gray-400 hover:text-red-400" data-action="delete" title="Delete">
                                <span class="material-symbols-outlined text-sm">delete</span>
                            </span>
                        </div>
                    `;
                }

                // Main click to load conversation
                item.addEventListener('click', (e) => {
                    if (e.target.closest('.conv-action')) return;
                    this.loadConversation(conv.id);
                    if (this.isMobileView) {
                        this.closeSidebar();
                    }
                });

                // Action buttons
                item.querySelectorAll('.conv-action').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const action = btn.dataset.action;
                        if (action === 'rename') {
                            this.showRenameModal(conv.id, conv.title);
                        } else if (action === 'delete') {
                            this.deleteConversation(conv.id);
                        }
                    });
                });

                groupEl.appendChild(item);
            });

            list.appendChild(groupEl);
        };

        renderGroup('Today', groups.today);
        renderGroup('Yesterday', groups.yesterday);
        renderGroup('Previous 7 Days', groups.week);
        renderGroup('Older', groups.older);
    }

    async loadConversation(convId) {
        try {
            const response = await fetch(`/api/chat/conversations/${convId}`, {
                credentials: 'include'
            });
            if (!response.ok) throw new Error('Conversation not found');

            const conv = await response.json();
            this.setCurrentConversation(convId);

            // Update chat title in header
            document.getElementById('current-chat-title').textContent = conv.title || 'New Chat';

            // Update sidebar active state
            await this.loadConversations();

            // Render messages
            this.chatManager.renderConversation(conv);
        } catch (error) {
            console.error('Failed to load conversation:', error);
            sessionStorage.removeItem('currentConversationId');
        }
    }

    setCurrentConversation(convId) {
        this.currentConversationId = convId;
        if (convId) {
            sessionStorage.setItem('currentConversationId', convId);
        } else {
            sessionStorage.removeItem('currentConversationId');
        }
    }

    async createNewConversation() {
        this.setCurrentConversation(null);
        document.getElementById('current-chat-title').textContent = 'New Chat';
        this.chatManager.clearMessages();
        await this.loadConversations();
    }

    async deleteConversation(convId) {
        if (!confirm('Delete this conversation?')) return;

        try {
            await fetch(`/api/chat/conversations/${convId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            if (convId === this.currentConversationId) {
                this.setCurrentConversation(null);
                document.getElementById('current-chat-title').textContent = 'New Chat';
                this.chatManager.clearMessages();
            }
            await this.loadConversations();
        } catch (error) {
            console.error('Failed to delete conversation:', error);
        }
    }

    showRenameModal(convId, currentTitle) {
        const modal = document.getElementById('rename-modal');
        const input = document.getElementById('rename-input');
        input.value = currentTitle || '';
        input.dataset.convId = convId;
        modal.classList.remove('hidden');
        input.focus();
    }

    async saveRename() {
        const input = document.getElementById('rename-input');
        const convId = input.dataset.convId;
        const newTitle = input.value.trim();

        if (!newTitle) return;

        try {
            await fetch(`/api/chat/conversations/${convId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ title: newTitle })
            });
            document.getElementById('rename-modal').classList.add('hidden');
            if (convId === this.currentConversationId) {
                document.getElementById('current-chat-title').textContent = newTitle;
            }
            await this.loadConversations();
        } catch (error) {
            console.error('Failed to rename conversation:', error);
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        const isHidden = sidebar.classList.contains('-translate-x-full');

        if (isHidden) {
            // Show sidebar
            sidebar.classList.remove('-translate-x-full');
            if (this.isMobileView) {
                overlay.classList.remove('hidden');
            } else {
                this.sidebarCollapsed = false;
            }
            this.hideMenuButton();
        } else {
            // Hide sidebar
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
            if (!this.isMobileView) {
                this.sidebarCollapsed = true;
            }
            this.showMenuButton();
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');

        // Track collapsed state and show menu button
        if (!this.isMobileView) {
            this.sidebarCollapsed = true;
        }
        this.showMenuButton();
    }

    setupEventListeners() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');

        // Sidebar toggle (mobile)
        document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Sidebar close button (mobile)
        document.getElementById('sidebar-close-btn')?.addEventListener('click', () => {
            this.closeSidebar();
        });

        // Sidebar collapse (desktop) - uses same toggle logic
        document.getElementById('sidebar-collapse-btn')?.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Overlay click closes sidebar
        overlay?.addEventListener('click', () => {
            this.closeSidebar();
        });

        // New chat button
        document.getElementById('new-chat-btn')?.addEventListener('click', () => {
            this.createNewConversation();
            if (this.isMobileView) {
                this.closeSidebar();
            }
        });

        // Conversation search
        const searchInput = document.getElementById('conversation-search');
        const clearSearchBtn = document.getElementById('clear-search');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                clearSearchBtn.classList.toggle('hidden', !this.searchQuery);
                this.filterAndRenderConversations();
            });

            clearSearchBtn.addEventListener('click', () => {
                searchInput.value = '';
                this.searchQuery = '';
                clearSearchBtn.classList.add('hidden');
                this.filterAndRenderConversations();
            });

            // Clear search on Escape key
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    searchInput.value = '';
                    this.searchQuery = '';
                    clearSearchBtn.classList.add('hidden');
                    this.filterAndRenderConversations();
                    searchInput.blur();
                }
            });
        }

        // Model selection
        document.getElementById('model-select')?.addEventListener('change', async (e) => {
            const model = e.target.value;
            if (model) {
                await this.selectModel(model);
            }
        });

        // Settings button
        document.getElementById('settings-btn')?.addEventListener('click', () => {
            this.settingsManager.showModal();
        });

        // Tools menu toggle
        const toolsBtn = document.getElementById('tools-btn');
        const toolsMenu = document.getElementById('tools-menu');

        toolsBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toolsMenu?.classList.toggle('hidden');
        });

        // Close tools menu when clicking outside
        document.addEventListener('click', (e) => {
            if (toolsMenu && !toolsMenu.classList.contains('hidden') && !e.target.closest('#tools-menu-container')) {
                toolsMenu.classList.add('hidden');
            }
        });

        // File upload
        document.getElementById('file-upload')?.addEventListener('change', (e) => {
            this.handleDroppedFiles(Array.from(e.target.files));
            e.target.value = '';
        });

        // Menu: Attach files
        document.getElementById('menu-attach-files')?.addEventListener('click', () => {
            toolsMenu?.classList.add('hidden');
            document.getElementById('file-upload')?.click();
        });

        // Menu: Thinking toggle
        const thinkingCheckbox = document.getElementById('thinking-checkbox');
        const modeIndicator = document.getElementById('mode-indicator');

        document.getElementById('menu-thinking')?.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox' && thinkingCheckbox) {
                thinkingCheckbox.checked = !thinkingCheckbox.checked;
            }
            this.thinkEnabled = thinkingCheckbox?.checked ?? false;
            modeIndicator?.classList.toggle('hidden', !this.thinkEnabled);
        });

        thinkingCheckbox?.addEventListener('change', () => {
            this.thinkEnabled = thinkingCheckbox.checked;
            modeIndicator?.classList.toggle('hidden', !this.thinkEnabled);
        });

        // Drag and drop
        const inputArea = document.getElementById('input-area');
        let dragCounter = 0;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        document.body.addEventListener('dragenter', () => {
            dragCounter++;
            inputArea?.classList.add('ring-2', 'ring-primary');
        });

        document.body.addEventListener('dragleave', () => {
            dragCounter--;
            if (dragCounter === 0) {
                inputArea?.classList.remove('ring-2', 'ring-primary');
            }
        });

        document.body.addEventListener('drop', (e) => {
            dragCounter = 0;
            inputArea?.classList.remove('ring-2', 'ring-primary');
            const files = Array.from(e.dataTransfer.files);
            this.handleDroppedFiles(files);
        });

        // Message input
        const messageInput = document.getElementById('message-input');
        messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        messageInput?.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 192) + 'px';
        });

        // Send button
        document.getElementById('send-btn')?.addEventListener('click', () => {
            this.sendMessage();
        });

        // Rename modal
        document.getElementById('close-rename')?.addEventListener('click', () => {
            document.getElementById('rename-modal')?.classList.add('hidden');
        });
        document.getElementById('cancel-rename')?.addEventListener('click', () => {
            document.getElementById('rename-modal')?.classList.add('hidden');
        });
        document.getElementById('save-rename')?.addEventListener('click', () => {
            this.saveRename();
        });
        document.getElementById('rename-input')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.saveRename();
            }
        });

        // Edit modal
        document.getElementById('close-edit')?.addEventListener('click', () => {
            document.getElementById('edit-modal')?.classList.add('hidden');
        });
        document.getElementById('cancel-edit')?.addEventListener('click', () => {
            document.getElementById('edit-modal')?.classList.add('hidden');
        });
        document.getElementById('save-edit')?.addEventListener('click', () => {
            this.chatManager.saveEdit();
        });

        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const renameModal = document.getElementById('rename-modal');
                const editModal = document.getElementById('edit-modal');
                if (renameModal && !renameModal.classList.contains('hidden')) {
                    renameModal.classList.add('hidden');
                }
                if (editModal && !editModal.classList.contains('hidden')) {
                    editModal.classList.add('hidden');
                }
            }
        });

    }

    /**
     * Update all locations that display the assistant name
     * @param {string} name - The new assistant name
     */
    updateAssistantName(name) {
        const displayName = name || 'PeanutChat';
        console.log('[AssistantName] Updating assistant name to:', displayName);

        // Update sidebar header
        const sidebarHeader = document.querySelector('#sidebar h2.font-display');
        if (sidebarHeader) {
            sidebarHeader.textContent = displayName;
        }

        // Update welcome message if visible
        const welcomeTitle = document.querySelector('.welcome-message h2');
        if (welcomeTitle) {
            welcomeTitle.textContent = `Welcome to ${displayName}`;
        }

        // Update input placeholder
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.placeholder = `Message ${displayName}...`;
        }

        // Update all existing assistant message headers
        const assistantNameEls = document.querySelectorAll('.assistant-header .assistant-name');
        assistantNameEls.forEach(el => {
            el.textContent = displayName;
        });

        // Store for use by chat manager
        this.assistantName = displayName;
    }

    /**
     * Get the current assistant name
     */
    getAssistantName() {
        // Try to get from profileManager first, fall back to cached value or default
        if (typeof profileManager !== 'undefined' && profileManager.getAssistantName) {
            const name = profileManager.getAssistantName();
            console.log('[AssistantName] getAssistantName() from profile:', name);
            return name;
        }
        console.log('[AssistantName] getAssistantName() fallback:', this.assistantName || 'PeanutChat');
        return this.assistantName || 'PeanutChat';
    }

    async selectModel(model) {
        try {
            await fetch('/api/models/select', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ model })
            });
            this.currentModel = model;

            // Update capability indicators for new model
            const modelData = this.modelsData?.[model];
            if (modelData) {
                this.updateCapabilityIndicators(modelData);
            }

            // Reload full capabilities from server
            await this.loadModelCapabilities();

            // Fetch comprehensive capabilities for context window
            await this.updateModelCapabilities(model);
        } catch (error) {
            console.error('Failed to select model:', error);
        }
    }

    handleDroppedFiles(files) {
        const imageFiles = [];
        const otherFiles = [];

        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                imageFiles.push(file);
            } else {
                otherFiles.push(file);
            }
        });

        if (imageFiles.length > 0) {
            this.handleImageUpload(imageFiles);
        }
        if (otherFiles.length > 0) {
            this.handleFileUpload(otherFiles);
        }
    }

    handleImageUpload(files) {
        Array.from(files).forEach(file => {
            // Skip if file with same name already exists
            if (this.pendingImages.some(img => img.name === file.name)) {
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const base64 = e.target.result.split(',')[1];
                this.pendingImages.push({
                    base64,
                    dataUrl: e.target.result,
                    name: file.name
                });
                this.updateImagePreviews();
            };
            reader.readAsDataURL(file);
        });
    }

    updateImagePreviews() {
        const container = document.getElementById('image-previews');
        container.innerHTML = '';

        this.pendingImages.forEach((img, index) => {
            const preview = document.createElement('div');
            preview.className = 'relative size-14 rounded-lg overflow-hidden bg-surface-dark border border-gray-700';
            preview.innerHTML = `
                <img src="${img.dataUrl}" alt="${img.name}" class="w-full h-full object-cover">
                <button class="absolute top-0.5 right-0.5 size-5 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white text-xs transition-colors">
                    <span class="material-symbols-outlined text-sm">close</span>
                </button>
            `;
            preview.querySelector('button').addEventListener('click', () => {
                this.pendingImages.splice(index, 1);
                this.updateImagePreviews();
            });
            container.appendChild(preview);
        });
    }

    handleFileUpload(files) {
        Array.from(files).forEach(file => {
            // Skip if file with same name already exists
            if (this.pendingFiles.some(f => f.name === file.name)) {
                return;
            }

            if (file.size > this.maxFileSize) {
                alert(`File "${file.name}" exceeds the 25 MB limit`);
                return;
            }

            const fileType = this.getFileType(file.name);
            const isText = this.isTextFile(file.name);

            const reader = new FileReader();
            reader.onload = (e) => {
                let content;
                if (isText) {
                    content = e.target.result;
                } else {
                    content = e.target.result.split(',')[1];
                }

                this.pendingFiles.push({
                    name: file.name,
                    type: fileType,
                    content: content,
                    size: file.size,
                    isBase64: !isText
                });
                this.updateFilePreviews();
            };

            if (isText) {
                reader.readAsText(file);
            } else {
                reader.readAsDataURL(file);
            }
        });
    }

    getFileType(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const typeMap = {
            'pdf': 'pdf', 'zip': 'zip', 'txt': 'text', 'md': 'text',
            'json': 'code', 'xml': 'code', 'csv': 'text', 'py': 'code',
            'js': 'code', 'ts': 'code', 'jsx': 'code', 'tsx': 'code',
            'html': 'code', 'css': 'code', 'java': 'code', 'c': 'code',
            'cpp': 'code', 'h': 'code', 'go': 'code', 'rs': 'code',
            'rb': 'code', 'php': 'code', 'sh': 'code', 'yaml': 'code',
            'yml': 'code', 'toml': 'code', 'ini': 'text', 'cfg': 'text', 'log': 'text'
        };
        return typeMap[ext] || 'text';
    }

    isTextFile(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const binaryExtensions = ['pdf', 'zip'];
        return !binaryExtensions.includes(ext);
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    updateFilePreviews() {
        const container = document.getElementById('file-previews');
        container.innerHTML = '';

        const icons = {
            pdf: 'picture_as_pdf',
            zip: 'folder_zip',
            text: 'description',
            code: 'code'
        };

        this.pendingFiles.forEach((file, index) => {
            const preview = document.createElement('div');
            preview.className = 'flex items-center gap-2 px-3 py-2 bg-surface-dark border border-gray-700 rounded-lg text-sm';
            preview.innerHTML = `
                <span class="material-symbols-outlined text-primary text-lg">${icons[file.type] || icons.text}</span>
                <span class="text-gray-300 truncate max-w-[120px]" title="${file.name}">${file.name}</span>
                <span class="text-gray-500 text-xs">${this.formatFileSize(file.size)}</span>
                <button class="text-gray-400 hover:text-red-400 transition-colors ml-1">
                    <span class="material-symbols-outlined text-sm">close</span>
                </button>
            `;
            preview.querySelector('button').addEventListener('click', () => {
                this.pendingFiles.splice(index, 1);
                this.updateFilePreviews();
            });
            container.appendChild(preview);
        });
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();

        if (!message && this.pendingImages.length === 0 && this.pendingFiles.length === 0) return;

        const images = this.pendingImages.map(img => img.base64);
        const imageDataUrls = this.pendingImages.map(img => img.dataUrl);
        const files = this.pendingFiles.map(f => ({
            name: f.name,
            type: f.type,
            content: f.content,
            is_base64: f.isBase64
        }));
        const think = this.thinkEnabled;

        input.value = '';
        input.style.height = 'auto';
        this.pendingImages = [];
        this.pendingFiles = [];
        this.updateImagePreviews();
        this.updateFilePreviews();

        await this.chatManager.sendMessage(message, images, imageDataUrls, think, files);
        await this.loadConversations();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    // Expose chatManager globally for modal onclick handlers
    window.chatManager = window.app.chatManager;
    window.app.init();
});
