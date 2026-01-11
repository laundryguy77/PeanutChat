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
    }

    async init() {
        await this.loadModels();
        await this.settingsManager.loadSettings();
        await this.loadModelCapabilities();
        await this.loadConversations();
        this.setupEventListeners();

        // Restore last conversation from localStorage
        const savedConvId = localStorage.getItem('currentConversationId');
        if (savedConvId) {
            await this.loadConversation(savedConvId);
        }

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
            const response = await fetch('/api/models/capabilities');
            this.modelCapabilities = await response.json();
        } catch (error) {
            console.error('Failed to load model capabilities:', error);
            this.modelCapabilities = { supports_tools: false, tools: [] };
        }
    }

    async loadModels() {
        const select = document.getElementById('model-select');
        try {
            const response = await fetch('/api/models');
            const data = await response.json();

            select.innerHTML = '';

            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    if (model.name === data.current) {
                        option.selected = true;
                        this.currentModel = model.name;
                    }
                    select.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No models available';
                select.appendChild(option);
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            select.innerHTML = '<option value="">Failed to load</option>';
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            const data = await response.json();
            this.renderConversationList(data.conversations || []);
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
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
            const response = await fetch(`/api/chat/conversations/${convId}`);
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
            localStorage.removeItem('currentConversationId');
        }
    }

    setCurrentConversation(convId) {
        this.currentConversationId = convId;
        if (convId) {
            localStorage.setItem('currentConversationId', convId);
        } else {
            localStorage.removeItem('currentConversationId');
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
            await fetch(`/api/chat/conversations/${convId}`, { method: 'DELETE' });
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
        document.getElementById('sidebar-toggle').addEventListener('click', () => {
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
        overlay.addEventListener('click', () => {
            this.closeSidebar();
        });

        // New chat button
        document.getElementById('new-chat-btn').addEventListener('click', () => {
            this.createNewConversation();
            if (this.isMobileView) {
                this.closeSidebar();
            }
        });

        // Model selection
        document.getElementById('model-select').addEventListener('change', async (e) => {
            const model = e.target.value;
            if (model) {
                await this.selectModel(model);
            }
        });

        // Settings button
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.settingsManager.showModal();
        });

        // Tools menu toggle
        const toolsBtn = document.getElementById('tools-btn');
        const toolsMenu = document.getElementById('tools-menu');

        toolsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toolsMenu.classList.toggle('hidden');
        });

        // Close tools menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!toolsMenu.classList.contains('hidden') && !e.target.closest('#tools-menu-container')) {
                toolsMenu.classList.add('hidden');
            }
        });

        // File upload
        document.getElementById('file-upload').addEventListener('change', (e) => {
            this.handleDroppedFiles(Array.from(e.target.files));
            e.target.value = '';
        });

        // Menu: Attach files
        document.getElementById('menu-attach-files').addEventListener('click', () => {
            toolsMenu.classList.add('hidden');
            document.getElementById('file-upload').click();
        });

        // Menu: Thinking toggle
        const thinkingCheckbox = document.getElementById('thinking-checkbox');
        const modeIndicator = document.getElementById('mode-indicator');

        document.getElementById('menu-thinking').addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox') {
                thinkingCheckbox.checked = !thinkingCheckbox.checked;
            }
            this.thinkEnabled = thinkingCheckbox.checked;
            modeIndicator.classList.toggle('hidden', !this.thinkEnabled);
        });

        thinkingCheckbox.addEventListener('change', () => {
            this.thinkEnabled = thinkingCheckbox.checked;
            modeIndicator.classList.toggle('hidden', !this.thinkEnabled);
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
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 192) + 'px';
        });

        // Send button
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        // Rename modal
        document.getElementById('close-rename').addEventListener('click', () => {
            document.getElementById('rename-modal').classList.add('hidden');
        });
        document.getElementById('cancel-rename').addEventListener('click', () => {
            document.getElementById('rename-modal').classList.add('hidden');
        });
        document.getElementById('save-rename').addEventListener('click', () => {
            this.saveRename();
        });
        document.getElementById('rename-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.saveRename();
            }
        });

        // Edit modal
        document.getElementById('close-edit').addEventListener('click', () => {
            document.getElementById('edit-modal').classList.add('hidden');
        });
        document.getElementById('cancel-edit').addEventListener('click', () => {
            document.getElementById('edit-modal').classList.add('hidden');
        });
        document.getElementById('save-edit').addEventListener('click', () => {
            this.chatManager.saveEdit();
        });
    }

    async selectModel(model) {
        try {
            await fetch('/api/models/select', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model })
            });
            this.currentModel = model;
            console.log('Model selected:', model);
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
    window.app.init();
});
