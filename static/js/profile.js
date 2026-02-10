// Profile Manager - Handles user profile UI and operations
class ProfileManager {
    constructor() {
        this.profile = null;
        this.initialized = false;
        this.isDirty = false;  // Track unsaved changes
        this.saveTimeout = null;  // Debounce timer for auto-save
    }

    async init(forceReload = false) {
        // Check if user is authenticated
        if (typeof authManager !== 'undefined' && !authManager.isAuthenticated()) {
            this.renderNotAuthenticated();
            return;
        }

        // Force reload if requested (e.g., when opening settings modal)
        if (forceReload) {
            console.log('[Profile] Force reloading profile from server');
            await this.loadProfile();
            return;
        }

        // Only load profile once per session
        if (this.initialized && this.profile) {
            // Just re-render with cached data
            console.log('[Profile] Using cached profile');
            this.render();
            return;
        }

        console.log('[Profile] Loading profile from server (first init)');
        await this.loadProfile();
        this.initialized = true;
        console.log('[Profile] Profile loaded and cached');
    }

    async loadProfile() {
        try {
            const response = await fetch('/api/profile', {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                // Initialize with empty profile structure if none exists
                this.profile = data.profile || {
                    identity: {},
                    relationship_metrics: {},
                    communication: {}
                };
                this.render();
            } else if (response.status === 401) {
                // Not authenticated
                this.renderNotAuthenticated();
            } else {
                console.warn('Profile fetch failed:', response.status);
                // Even if profile fetch fails, show UI with defaults
                this.profile = {
                    identity: {},
                    relationship_metrics: {},
                    communication: {}
                };
                this.render();
            }
        } catch (error) {
            console.error('Failed to load profile:', error);
            // Show UI with defaults on error
            this.profile = {
                identity: {},
                relationship_metrics: {},
                communication: {}
            };
            this.render();
        }
    }

    renderNotAuthenticated() {
        const container = document.getElementById('profile-section');
        if (!container) return;

        container.innerHTML = `
            <div class="text-center py-4">
                <span class="material-symbols-outlined text-3xl text-gray-500 mb-2">login</span>
                <p class="text-sm text-gray-400">Please log in to access your profile</p>
            </div>
        `;
    }

    render() {
        const container = document.getElementById('profile-section');
        if (!container || !this.profile) return;

        const identity = this.profile.identity || {};
        const metrics = this.profile.relationship_metrics || {};
        const comm = this.profile.communication || {};

        container.innerHTML = `
            <div class="space-y-4">
                <!-- Basic Info -->
                <div class="space-y-3">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Preferred Name</label>
                        <input type="text" id="profile-name"
                               class="w-full bg-background-dark border border-gray-700 rounded-lg p-2 text-white text-sm"
                               value="${identity.preferred_name || ''}"
                               placeholder="What should I call you?">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Assistant Name</label>
                        <input type="text" id="profile-assistant-name"
                               class="w-full bg-background-dark border border-gray-700 rounded-lg p-2 text-white text-sm"
                               value="${this.profile.persona_preferences?.assistant_name || ''}"
                               placeholder="Name your AI assistant (default: PeanutChat)">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Communication Style</label>
                        <select id="profile-style"
                                class="w-full bg-background-dark border border-gray-700 rounded-lg p-2 text-white text-sm">
                            <option value="candid_direct" ${comm.conversation_style === 'candid_direct' ? 'selected' : ''}>Candid & Direct</option>
                            <option value="quirky_imaginative" ${comm.conversation_style === 'quirky_imaginative' ? 'selected' : ''}>Quirky & Imaginative</option>
                            <option value="nerdy_exploratory" ${comm.conversation_style === 'nerdy_exploratory' ? 'selected' : ''}>Nerdy & Exploratory</option>
                            <option value="sarcastic_dry" ${comm.conversation_style === 'sarcastic_dry' ? 'selected' : ''}>Sarcastic & Dry</option>
                            <option value="empathetic_supportive" ${comm.conversation_style === 'empathetic_supportive' ? 'selected' : ''}>Empathetic & Supportive</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">Response Length</label>
                        <select id="profile-length"
                                class="w-full bg-background-dark border border-gray-700 rounded-lg p-2 text-white text-sm">
                            <option value="brief" ${comm.response_length === 'brief' ? 'selected' : ''}>Brief</option>
                            <option value="adaptive" ${comm.response_length === 'adaptive' ? 'selected' : ''}>Adaptive</option>
                            <option value="detailed" ${comm.response_length === 'detailed' ? 'selected' : ''}>Detailed</option>
                        </select>
                    </div>
                </div>

                <!-- Relationship Stats -->
                <div class="bg-background-dark rounded-xl p-4">
                    <h4 class="text-sm font-medium text-gray-300 mb-3">Relationship Stats</h4>
                    <div class="grid grid-cols-3 gap-3 text-center">
                        <div>
                            <div class="text-xl font-bold text-primary">${metrics.satisfaction_level || 50}</div>
                            <div class="text-xs text-gray-500">Satisfaction</div>
                        </div>
                        <div>
                            <div class="text-xl font-bold text-green-400">${metrics.trust_level || 50}</div>
                            <div class="text-xs text-gray-500">Trust</div>
                        </div>
                        <div>
                            <div class="text-xl font-bold text-blue-400">${metrics.interaction_count || 0}</div>
                            <div class="text-xs text-gray-500">Interactions</div>
                        </div>
                    </div>
                    <div class="mt-3 text-center">
                        <span class="text-xs px-2 py-1 rounded-full ${this.getStageColor(metrics.relationship_stage)}">
                            ${this.capitalizeStage(metrics.relationship_stage || 'new')}
                        </span>
                    </div>
                </div>

                <!-- Save Button -->
                <div id="profile-save-container" class="hidden">
                    <button id="profile-save-btn" onclick="profileManager.saveProfileWithFeedback()"
                            class="w-full flex items-center justify-center gap-2 py-2.5 bg-primary hover:bg-primary-hover rounded-lg text-sm text-white font-medium transition-colors">
                        <span class="material-symbols-outlined text-sm">save</span>
                        Save Changes
                    </button>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-2">
                    <button onclick="profileManager.exportProfile()"
                            class="flex-1 flex items-center justify-center gap-2 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm text-gray-300 transition-colors">
                        <span class="material-symbols-outlined text-sm">download</span>
                        Export
                    </button>
                    <button onclick="profileManager.showResetConfirm()"
                            class="flex-1 flex items-center justify-center gap-2 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm text-red-400 transition-colors">
                        <span class="material-symbols-outlined text-sm">restart_alt</span>
                        Reset
                    </button>
                </div>
            </div>
        `;

        // Set up event listeners after rendering
        this.setupFormEventListeners();
    }

    /**
     * Set up event listeners on profile form inputs for change detection and auto-save
     */
    setupFormEventListeners() {
        const inputs = [
            { id: 'profile-name', event: 'input' },
            { id: 'profile-assistant-name', event: 'input' },
            { id: 'profile-style', event: 'change' },
            { id: 'profile-length', event: 'change' }
        ];

        inputs.forEach(({ id, event }) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener(event, () => this.markDirty());
            }
        });
    }

    /**
     * Mark the form as having unsaved changes
     */
    markDirty() {
        this.isDirty = true;
        const saveContainer = document.getElementById('profile-save-container');
        if (saveContainer) {
            saveContainer.classList.remove('hidden');
        }

        // Debounce auto-save: save after 2 seconds of no changes
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }
        this.saveTimeout = setTimeout(() => {
            this.saveProfileWithFeedback();
        }, 2000);
    }

    /**
     * Mark the form as saved (no unsaved changes)
     */
    markClean() {
        this.isDirty = false;
        const saveContainer = document.getElementById('profile-save-container');
        if (saveContainer) {
            saveContainer.classList.add('hidden');
        }

        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
            this.saveTimeout = null;
        }
    }

    /**
     * Save profile with user feedback (toast notification)
     */
    async saveProfileWithFeedback() {
        // Cancel any pending auto-save
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
            this.saveTimeout = null;
        }

        const saveBtn = document.getElementById('profile-save-btn');
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = `
                <span class="material-symbols-outlined text-sm animate-spin">sync</span>
                Saving...
            `;
        }

        try {
            await this.saveProfile();
            this.markClean();
            this.showToast('Profile saved successfully', 'success');
        } catch (error) {
            console.error('[Profile] Save failed:', error);
            this.showToast('Failed to save profile', 'error');
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = `
                    <span class="material-symbols-outlined text-sm">save</span>
                    Save Changes
                `;
            }
        }
    }

    getStageColor(stage) {
        const colors = {
            'new': 'bg-gray-500/20 text-gray-400',
            'familiar': 'bg-blue-500/20 text-blue-400',
            'established': 'bg-green-500/20 text-green-400',
            'deep': 'bg-purple-500/20 text-purple-400'
        };
        return colors[stage] || colors.new;
    }

    capitalizeStage(stage) {
        return stage.charAt(0).toUpperCase() + stage.slice(1);
    }

    // Profile Operations

    async saveProfile() {
        const name = document.getElementById('profile-name')?.value;
        const assistantName = document.getElementById('profile-assistant-name')?.value;
        const style = document.getElementById('profile-style')?.value;
        const length = document.getElementById('profile-length')?.value;

        const updates = [];

        // Build updates and cache values locally for all fields
        if (name !== undefined) {
            updates.push({ path: 'identity.preferred_name', value: name || null, operation: 'set' });
            // Update in-memory cache
            if (!this.profile.identity) {
                this.profile.identity = {};
            }
            this.profile.identity.preferred_name = name || null;
            console.log('[Profile] Caching preferred_name:', name || '(empty)');
        }

        if (assistantName !== undefined) {
            updates.push({ path: 'persona_preferences.assistant_name', value: assistantName || null, operation: 'set' });
            // Update in-memory cache
            if (!this.profile.persona_preferences) {
                this.profile.persona_preferences = {};
            }
            this.profile.persona_preferences.assistant_name = assistantName || null;
            console.log('[Profile] Caching assistant_name:', assistantName || '(default)');
        }

        if (style) {
            updates.push({ path: 'communication.conversation_style', value: style, operation: 'set' });
            // Update in-memory cache
            if (!this.profile.communication) {
                this.profile.communication = {};
            }
            this.profile.communication.conversation_style = style;
            console.log('[Profile] Caching conversation_style:', style);
        }

        if (length) {
            updates.push({ path: 'communication.response_length', value: length, operation: 'set' });
            // Update in-memory cache
            if (!this.profile.communication) {
                this.profile.communication = {};
            }
            this.profile.communication.response_length = length;
            console.log('[Profile] Caching response_length:', length);
        }

        if (updates.length === 0) return;

        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                updates,
                reason: 'User updated profile via settings'
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Save failed with status ${response.status}`);
        }

        console.log('[Profile] Profile saved successfully to server');

        // Notify app to update headers with new assistant name
        if (window.app) {
            window.app.updateAssistantName(this.getAssistantName());
        }
    }

    /**
     * Get the assistant name, defaulting to 'PeanutChat' if not set
     */
    getAssistantName() {
        const name = this.profile?.persona_preferences?.assistant_name;
        console.log('[Profile] getAssistantName() persona_preferences.assistant_name:', name, '-> returning:', name || 'PeanutChat');
        return name || 'PeanutChat';
    }

    /**
     * Show a toast notification
     */
    showToast(message, type = 'info') {
        const colorMap = {
            'info': 'bg-blue-600',
            'success': 'bg-green-600',
            'warning': 'bg-yellow-600',
            'error': 'bg-red-600'
        };
        const bgColor = colorMap[type] || colorMap.info;

        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-[100] animate-fadeIn`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    async exportProfile() {
        try {
            const response = await fetch('/api/profile/export?format=json&tier=exportable', {
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                const blob = new Blob([result.data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'peanutchat_profile.json';
                a.click();
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Failed to export profile:', error);
            alert('Failed to export profile');
        }
    }

    showResetConfirm() {
        if (confirm('Are you sure you want to reset your profile? This will clear all preferences and relationship history. Your identity information will be preserved.')) {
            this.resetProfile();
        }
    }

    async resetProfile() {
        try {
            const response = await fetch('/api/profile', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    sections: ['all'],
                    preserve_identity: true,
                    user_confirmed: true,
                    confirmation_phrase: 'reset profile'
                })
            });

            if (response.ok) {
                await this.loadProfile();
                alert('Profile reset successfully');
            }
        } catch (error) {
            console.error('Failed to reset profile:', error);
            alert('Failed to reset profile');
        }
    }
}

// Global instance
const profileManager = new ProfileManager();
