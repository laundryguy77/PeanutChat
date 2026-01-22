// Settings Manager - Handles settings modal and persistence
export class SettingsManager {
    constructor(app) {
        this.app = app;
        this.modal = document.getElementById('settings-modal');
        this.settings = {};
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Close button
        document.getElementById('close-settings').addEventListener('click', () => {
            this.hideModal();
        });

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });

        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.hideModal();
            }
        });

        // Save button
        document.getElementById('save-settings').addEventListener('click', () => {
            this.saveSettings();
        });

        // Theme buttons
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const theme = btn.dataset.theme;
                this.setTheme(theme);
            });
        });

        // Range input value displays
        this.setupRangeInput('temperature', 'temp-value');
        this.setupRangeInput('top-p', 'topp-value');
        this.setupRangeInput('top-k', 'topk-value');
        this.setupRangeInput('num-ctx', 'ctx-value');
        this.setupRangeInput('repeat-penalty', 'repeat-value');

        // Compaction settings
        this.setupRangeInput('compaction-buffer', 'buffer-value', '%');
        this.setupRangeInput('compaction-threshold', 'threshold-value', '%');
        this.setupRangeInput('compaction-protected', 'protected-value');

        // Compaction enable toggle
        const compactionEnabled = document.getElementById('compaction-enabled');
        const compactionSettings = document.getElementById('compaction-settings');
        if (compactionEnabled && compactionSettings) {
            compactionEnabled.addEventListener('change', () => {
                compactionSettings.style.opacity = compactionEnabled.checked ? '1' : '0.5';
                compactionSettings.style.pointerEvents = compactionEnabled.checked ? 'auto' : 'none';
            });
        }
    }

    setTheme(theme) {
        this.currentTheme = theme;
        this.applyTheme(theme);
        localStorage.setItem('theme', theme);
        this.updateThemeButtons();
    }

    applyTheme(theme) {
        // Set data-theme attribute for CSS variable switching
        if (theme === 'dark') {
            document.documentElement.removeAttribute('data-theme');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }

        // Toggle dark class for Tailwind
        if (theme === 'light') {
            document.documentElement.classList.remove('dark');
        } else {
            document.documentElement.classList.add('dark');
        }

        // Apply theme colors to key elements using CSS variables
        const body = document.body;
        const sidebar = document.getElementById('sidebar');
        const main = document.querySelector('main');
        const header = document.querySelector('header');
        const inputArea = document.getElementById('input-area');
        const chatContainer = document.getElementById('chat-container');
        const menuButton = document.getElementById('sidebar-toggle');

        // Apply background colors from CSS variables
        body.style.backgroundColor = 'var(--bg-primary)';
        body.style.color = 'var(--text-primary)';

        if (sidebar) sidebar.style.backgroundColor = 'var(--bg-sidebar)';
        if (main) main.style.backgroundColor = 'var(--bg-primary)';
        if (header) header.style.backgroundColor = 'var(--bg-primary)';
        if (inputArea) inputArea.style.backgroundColor = 'var(--bg-primary)';
        if (chatContainer) chatContainer.style.backgroundColor = 'var(--bg-primary)';
        if (menuButton) menuButton.style.backgroundColor = 'var(--bg-sidebar)';
    }

    updateThemeButtons() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            const isActive = btn.dataset.theme === this.currentTheme;
            if (isActive) {
                btn.classList.remove('border-gray-700');
                btn.classList.add('border-primary', 'bg-primary/10');
            } else {
                btn.classList.add('border-gray-700');
                btn.classList.remove('border-primary', 'bg-primary/10');
            }
        });
    }

    setupRangeInput(inputId, displayId, suffix = '') {
        const input = document.getElementById(inputId);
        const display = document.getElementById(displayId);

        if (!input || !display) return;  // Skip if elements don't exist

        input.addEventListener('input', () => {
            display.textContent = input.value + suffix;
        });
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            this.settings = await response.json();
            this.updateUI();
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    updateUI() {
        // Persona
        const personaInput = document.getElementById('persona-input');
        if (personaInput) {
            personaInput.value = this.settings.persona || '';
        }

        // Model parameters
        this.setRangeValue('temperature', 'temp-value', this.settings.temperature || 0.7);
        this.setRangeValue('top-p', 'topp-value', this.settings.top_p || 0.9);
        this.setRangeValue('top-k', 'topk-value', this.settings.top_k || 40);
        this.setRangeValue('num-ctx', 'ctx-value', this.settings.num_ctx || 4096);
        this.setRangeValue('repeat-penalty', 'repeat-value', this.settings.repeat_penalty || 1.1);

        // Compaction settings
        const compactionEnabled = document.getElementById('compaction-enabled');
        const compactionSettings = document.getElementById('compaction-settings');
        if (compactionEnabled) {
            compactionEnabled.checked = this.settings.compaction_enabled !== false;
            if (compactionSettings) {
                compactionSettings.style.opacity = compactionEnabled.checked ? '1' : '0.5';
                compactionSettings.style.pointerEvents = compactionEnabled.checked ? 'auto' : 'none';
            }
        }
        this.setRangeValue('compaction-buffer', 'buffer-value', this.settings.compaction_buffer_percent || 15, '%');
        this.setRangeValue('compaction-threshold', 'threshold-value', this.settings.compaction_threshold_percent || 70, '%');
        this.setRangeValue('compaction-protected', 'protected-value', this.settings.compaction_protected_messages || 6);
    }

    setRangeValue(inputId, displayId, value, suffix = '') {
        const input = document.getElementById(inputId);
        const display = document.getElementById(displayId);
        if (!input || !display) return;
        input.value = value;
        display.textContent = value + suffix;
    }

    async saveSettings() {
        const personaEl = document.getElementById('persona-input');
        const compactionEnabledEl = document.getElementById('compaction-enabled');
        const newSettings = {
            persona: personaEl ? personaEl.value || null : null,
            temperature: parseFloat(document.getElementById('temperature').value),
            top_p: parseFloat(document.getElementById('top-p').value),
            top_k: parseInt(document.getElementById('top-k').value),
            num_ctx: parseInt(document.getElementById('num-ctx').value),
            repeat_penalty: parseFloat(document.getElementById('repeat-penalty').value),
            // Compaction settings
            compaction_enabled: compactionEnabledEl ? compactionEnabledEl.checked : true,
            compaction_buffer_percent: parseInt(document.getElementById('compaction-buffer')?.value || 15),
            compaction_threshold_percent: parseInt(document.getElementById('compaction-threshold')?.value || 70),
            compaction_protected_messages: parseInt(document.getElementById('compaction-protected')?.value || 6)
        };

        try {
            // Save profile first if available
            if (typeof profileManager !== 'undefined') {
                await profileManager.saveProfile();
            }

            const response = await fetch('/api/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newSettings)
            });

            if (response.ok) {
                this.settings = await response.json();
                this.hideModal();
                console.log('Settings saved:', this.settings);
            } else {
                throw new Error('Failed to save settings');
            }
        } catch (error) {
            console.error('Failed to save settings:', error);
            alert('Failed to save settings. Please try again.');
        }
    }

    showModal() {
        this.loadSettings().then(() => {
            this.updateThemeButtons();
            this.modal.classList.remove('hidden');

            // Initialize knowledge base manager
            knowledgeManager.init();

            // Initialize MCP manager
            mcpManager.init();

            // Initialize memory manager
            memoryManager.init();

            // Initialize profile manager
            if (typeof profileManager !== 'undefined') {
                profileManager.init();
            }
        });
    }

    hideModal() {
        this.modal.classList.add('hidden');
    }
}
