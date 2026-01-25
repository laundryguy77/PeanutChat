/**
 * PeanutChat Admin Portal
 *
 * Single-page admin interface for user management, feature flags,
 * and system monitoring.
 */

class AdminPortal {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentUser = null;

        this.init();
    }

    init() {
        // Setup login form
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });

        // Setup navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.loadSection(section);
            });
        });

        // Check if already logged in
        this.checkAuth();
    }

    // =========================================================================
    // Authentication
    // =========================================================================

    async checkAuth() {
        try {
            const response = await fetch('/api/auth/me', {
                credentials: 'include'
            });

            if (response.ok) {
                const user = await response.json();
                // Verify admin status
                const adminCheck = await fetch('/api/admin/dashboard', {
                    credentials: 'include'
                });

                if (adminCheck.ok) {
                    this.currentUser = user;
                    this.showAdminPanel();
                } else {
                    this.showLoginError('Admin access required');
                }
            }
        } catch (error) {
            console.log('Not authenticated');
        }
    }

    async login() {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                this.showLoginError(error.detail || 'Login failed');
                return;
            }

            const user = await response.json();

            // Verify admin status
            const adminCheck = await fetch('/api/admin/dashboard', {
                credentials: 'include'
            });

            if (!adminCheck.ok) {
                this.showLoginError('Admin access required');
                return;
            }

            this.currentUser = user;
            this.showAdminPanel();

        } catch (error) {
            this.showLoginError('Connection error');
        }
    }

    logout() {
        fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        }).finally(() => {
            this.currentUser = null;
            document.getElementById('admin-panel').classList.add('hidden');
            document.getElementById('login-screen').classList.remove('hidden');
        });
    }

    showLoginError(message) {
        const errorEl = document.getElementById('login-error');
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }

    showAdminPanel() {
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('admin-panel').classList.remove('hidden');
        document.getElementById('admin-username').textContent = this.currentUser?.username || '';
        this.loadSection('dashboard');
    }

    // =========================================================================
    // Navigation
    // =========================================================================

    async loadSection(section) {
        this.currentSection = section;

        // Update nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.section === section);
        });

        const container = document.getElementById('content-area');

        switch (section) {
            case 'dashboard':
                await this.renderDashboard(container);
                break;
            case 'users':
                await this.renderUsers(container);
                break;
            case 'features':
                await this.renderFeatures(container);
                break;
            case 'audit':
                await this.renderAuditLog(container);
                break;
        }
    }

    // =========================================================================
    // Dashboard
    // =========================================================================

    async renderDashboard(container) {
        container.innerHTML = '<p class="text-gray-400">Loading dashboard...</p>';

        try {
            const stats = await this.fetchJson('/api/admin/dashboard');

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Dashboard</h2>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div class="card p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Total Users</p>
                        <p class="text-3xl font-bold">${stats.users.total}</p>
                        <p class="text-sm text-gray-500">${stats.users.admins} admins</p>
                    </div>
                    <div class="card p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Active Users</p>
                        <p class="text-3xl font-bold">${stats.users.active}</p>
                    </div>
                    <div class="card p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Conversations</p>
                        <p class="text-3xl font-bold">${stats.content.conversations}</p>
                    </div>
                    <div class="card p-4 rounded-lg">
                        <p class="text-gray-400 text-sm">Memories</p>
                        <p class="text-3xl font-bold">${stats.content.memories}</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div class="card p-4 rounded-lg">
                        <h3 class="font-semibold mb-4">Feature Flags</h3>
                        <p class="text-gray-400">
                            ${stats.features.enabled} of ${stats.features.total} features enabled
                        </p>
                    </div>
                    <div class="card p-4 rounded-lg">
                        <h3 class="font-semibold mb-4">Recent Activity</h3>
                        <p class="text-gray-400">
                            ${stats.activity.recent_admin_actions} admin actions in last 24h
                        </p>
                    </div>
                </div>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading dashboard: ${error.message}</p>`;
        }
    }

    // =========================================================================
    // Users
    // =========================================================================

    async renderUsers(container) {
        container.innerHTML = '<p class="text-gray-400">Loading users...</p>';

        try {
            const data = await this.fetchJson('/api/admin/users?include_inactive=true');

            container.innerHTML = `
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Users</h2>
                    <button onclick="admin.showCreateUserModal()" class="btn-primary px-4 py-2 rounded">
                        Create User
                    </button>
                </div>

                <div class="card rounded-lg overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-gray-700">
                            <tr>
                                <th class="px-4 py-3 text-left">Username</th>
                                <th class="px-4 py-3 text-left">Status</th>
                                <th class="px-4 py-3 text-left">Role</th>
                                <th class="px-4 py-3 text-left">Created</th>
                                <th class="px-4 py-3 text-left">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.users.map(user => this.userRow(user)).join('')}
                        </tbody>
                    </table>
                </div>

                <p class="mt-4 text-gray-400">
                    Showing ${data.users.length} of ${data.total} users
                </p>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading users: ${error.message}</p>`;
        }
    }

    userRow(user) {
        const statusClass = user.is_active ? 'text-green-400' : 'text-red-400';
        const statusText = user.is_active ? 'Active' : 'Inactive';
        const roleText = user.is_admin ? 'Admin' : 'User';
        const created = new Date(user.created_at).toLocaleDateString();

        return `
            <tr class="border-t border-gray-700">
                <td class="px-4 py-3">${this.escapeHtml(user.username)}</td>
                <td class="px-4 py-3 ${statusClass}">${statusText}</td>
                <td class="px-4 py-3">${roleText}</td>
                <td class="px-4 py-3 text-gray-400">${created}</td>
                <td class="px-4 py-3">
                    <button onclick="admin.editUser(${user.id})"
                            class="text-blue-400 hover:text-blue-300 mr-2">
                        Edit
                    </button>
                    <button onclick="admin.showUserFeatures(${user.id})"
                            class="text-green-400 hover:text-green-300 mr-2">
                        Features
                    </button>
                    <button onclick="admin.confirmDeleteUser(${user.id}, '${this.escapeHtml(user.username)}')"
                            class="text-red-400 hover:text-red-300">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    }

    showCreateUserModal() {
        this.showModal(`
            <h3 class="text-lg font-semibold mb-4">Create User</h3>
            <form id="create-user-form" class="space-y-4">
                <div>
                    <label class="block text-sm mb-2">Username</label>
                    <input type="text" id="new-username" required minlength="3"
                           class="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600">
                </div>
                <div>
                    <label class="block text-sm mb-2">Password</label>
                    <input type="password" id="new-password" required minlength="8"
                           class="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600">
                </div>
                <div class="flex items-center">
                    <input type="checkbox" id="new-is-admin" class="mr-2">
                    <label for="new-is-admin">Admin privileges</label>
                </div>
                <div class="flex justify-end space-x-2">
                    <button type="button" onclick="admin.hideModal()"
                            class="px-4 py-2 bg-gray-600 rounded">Cancel</button>
                    <button type="submit" class="btn-primary px-4 py-2 rounded">Create</button>
                </div>
            </form>
        `);

        document.getElementById('create-user-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.createUser();
        });
    }

    async createUser() {
        const username = document.getElementById('new-username').value;
        const password = document.getElementById('new-password').value;
        const isAdmin = document.getElementById('new-is-admin').checked;

        try {
            await this.fetchJson('/api/admin/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, is_admin: isAdmin })
            });

            this.hideModal();
            this.showToast('User created successfully');
            this.loadSection('users');
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    async editUser(userId) {
        try {
            const user = await this.fetchJson(`/api/admin/users/${userId}`);

            this.showModal(`
                <h3 class="text-lg font-semibold mb-4">Edit User: ${this.escapeHtml(user.username)}</h3>
                <form id="edit-user-form" class="space-y-4">
                    <div class="flex items-center justify-between">
                        <label>Admin</label>
                        <label class="toggle-switch">
                            <input type="checkbox" id="edit-is-admin" ${user.is_admin ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="flex items-center justify-between">
                        <label>Active</label>
                        <label class="toggle-switch">
                            <input type="checkbox" id="edit-is-active" ${user.is_active ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="flex items-center justify-between">
                        <label>Voice Enabled</label>
                        <label class="toggle-switch">
                            <input type="checkbox" id="edit-voice-enabled" ${user.voice_enabled ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div>
                        <label class="block text-sm mb-2">Mode Restriction</label>
                        <select id="edit-mode-restriction" class="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600">
                            <option value="" ${!user.mode_restriction ? 'selected' : ''}>None</option>
                            <option value="normal_only" ${user.mode_restriction === 'normal_only' ? 'selected' : ''}>Normal Only</option>
                            <option value="no_full_unlock" ${user.mode_restriction === 'no_full_unlock' ? 'selected' : ''}>No Full Unlock</option>
                        </select>
                    </div>
                    <hr class="border-gray-600">
                    <div>
                        <label class="block text-sm mb-2">Reset Password</label>
                        <input type="password" id="edit-new-password" placeholder="Leave blank to keep current"
                               class="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600">
                    </div>
                    <div class="flex justify-end space-x-2">
                        <button type="button" onclick="admin.hideModal()"
                                class="px-4 py-2 bg-gray-600 rounded">Cancel</button>
                        <button type="submit" class="btn-primary px-4 py-2 rounded">Save</button>
                    </div>
                </form>
            `);

            document.getElementById('edit-user-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.saveUser(userId);
            });
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    async saveUser(userId) {
        const updates = {
            is_admin: document.getElementById('edit-is-admin').checked,
            is_active: document.getElementById('edit-is-active').checked,
            voice_enabled: document.getElementById('edit-voice-enabled').checked,
            mode_restriction: document.getElementById('edit-mode-restriction').value || null
        };

        const newPassword = document.getElementById('edit-new-password').value;

        try {
            await this.fetchJson(`/api/admin/users/${userId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (newPassword) {
                await this.fetchJson(`/api/admin/users/${userId}/reset-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_password: newPassword })
                });
            }

            this.hideModal();
            this.showToast('User updated successfully');
            this.loadSection('users');
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    confirmDeleteUser(userId, username) {
        this.showModal(`
            <h3 class="text-lg font-semibold mb-4">Delete User</h3>
            <p class="mb-4">Are you sure you want to delete <strong>${this.escapeHtml(username)}</strong>?</p>
            <p class="text-red-400 mb-4">This will permanently delete all their data.</p>
            <div class="flex justify-end space-x-2">
                <button onclick="admin.hideModal()" class="px-4 py-2 bg-gray-600 rounded">Cancel</button>
                <button onclick="admin.deleteUser(${userId})" class="btn-danger px-4 py-2 rounded">Delete</button>
            </div>
        `);
    }

    async deleteUser(userId) {
        try {
            await this.fetchJson(`/api/admin/users/${userId}`, {
                method: 'DELETE'
            });

            this.hideModal();
            this.showToast('User deleted successfully');
            this.loadSection('users');
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    async showUserFeatures(userId) {
        try {
            const data = await this.fetchJson(`/api/admin/users/${userId}/features`);
            const features = await this.fetchJson('/api/admin/features');

            let html = `
                <h3 class="text-lg font-semibold mb-4">User Features</h3>
                <p class="text-gray-400 mb-4">Override global defaults for this user</p>
                <div class="space-y-3 max-h-96 overflow-y-auto">
            `;

            for (const feature of features) {
                const hasOverride = feature.key in data.overrides;
                const isEnabled = data.features[feature.key];
                const overrideValue = data.overrides[feature.key];

                html += `
                    <div class="flex items-center justify-between py-2 border-b border-gray-700">
                        <div>
                            <span class="font-medium">${feature.display_name}</span>
                            ${hasOverride ? '<span class="ml-2 text-xs bg-blue-600 px-2 py-1 rounded">Override</span>' : ''}
                        </div>
                        <select onchange="admin.setUserFeature(${userId}, '${feature.key}', this.value)"
                                class="px-3 py-1 bg-gray-700 rounded">
                            <option value="default" ${!hasOverride ? 'selected' : ''}>
                                Default (${feature.default_enabled ? 'On' : 'Off'})
                            </option>
                            <option value="true" ${hasOverride && overrideValue ? 'selected' : ''}>On</option>
                            <option value="false" ${hasOverride && !overrideValue ? 'selected' : ''}>Off</option>
                        </select>
                    </div>
                `;
            }

            html += `
                </div>
                <div class="mt-4 flex justify-end">
                    <button onclick="admin.hideModal()" class="px-4 py-2 bg-gray-600 rounded">Close</button>
                </div>
            `;

            this.showModal(html);
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    async setUserFeature(userId, featureKey, value) {
        try {
            const enabled = value === 'default' ? null : value === 'true';

            await this.fetchJson(`/api/admin/users/${userId}/features/${featureKey}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled })
            });

            this.showToast('Feature updated');
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        }
    }

    // =========================================================================
    // Features
    // =========================================================================

    async renderFeatures(container) {
        container.innerHTML = '<p class="text-gray-400">Loading features...</p>';

        try {
            const features = await this.fetchJson('/api/admin/features');

            // Group by category
            const grouped = {};
            for (const feature of features) {
                const cat = feature.category || 'general';
                if (!grouped[cat]) grouped[cat] = [];
                grouped[cat].push(feature);
            }

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Feature Flags</h2>
                <p class="text-gray-400 mb-6">
                    Toggle features globally. Individual users can be overridden in the Users section.
                </p>

                ${Object.entries(grouped).map(([category, features]) => `
                    <div class="card rounded-lg p-6 mb-4">
                        <h3 class="text-lg font-semibold mb-4 capitalize">${category}</h3>
                        <div class="space-y-4">
                            ${features.map(f => this.featureToggle(f)).join('')}
                        </div>
                    </div>
                `).join('')}
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading features: ${error.message}</p>`;
        }
    }

    featureToggle(feature) {
        return `
            <div class="flex items-center justify-between">
                <div>
                    <span class="font-medium">${feature.display_name}</span>
                    <p class="text-gray-400 text-sm">${feature.description || ''}</p>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" ${feature.default_enabled ? 'checked' : ''}
                           onchange="admin.toggleFeature('${feature.key}', this.checked)">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        `;
    }

    async toggleFeature(key, enabled) {
        try {
            await this.fetchJson(`/api/admin/features/${key}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ default_enabled: enabled })
            });
            this.showToast(`Feature "${key}" ${enabled ? 'enabled' : 'disabled'}`);
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
            this.loadSection('features'); // Refresh to restore state
        }
    }

    // =========================================================================
    // Audit Log
    // =========================================================================

    async renderAuditLog(container) {
        container.innerHTML = '<p class="text-gray-400">Loading audit log...</p>';

        try {
            const data = await this.fetchJson('/api/admin/audit-log');

            container.innerHTML = `
                <h2 class="text-2xl font-bold mb-6">Audit Log</h2>

                <div class="card rounded-lg overflow-hidden">
                    <table class="w-full">
                        <thead class="bg-gray-700">
                            <tr>
                                <th class="px-4 py-3 text-left">Time</th>
                                <th class="px-4 py-3 text-left">Admin</th>
                                <th class="px-4 py-3 text-left">Action</th>
                                <th class="px-4 py-3 text-left">Target</th>
                                <th class="px-4 py-3 text-left">Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.entries.map(entry => this.auditRow(entry)).join('')}
                        </tbody>
                    </table>
                </div>

                <p class="mt-4 text-gray-400">
                    Showing ${data.entries.length} of ${data.total} entries
                </p>
            `;
        } catch (error) {
            container.innerHTML = `<p class="text-red-400">Error loading audit log: ${error.message}</p>`;
        }
    }

    auditRow(entry) {
        const time = new Date(entry.created_at).toLocaleString();
        const details = entry.details ? JSON.stringify(entry.details) : '-';

        return `
            <tr class="border-t border-gray-700">
                <td class="px-4 py-3 text-sm">${time}</td>
                <td class="px-4 py-3">${this.escapeHtml(entry.admin_username)}</td>
                <td class="px-4 py-3">
                    <span class="bg-gray-600 px-2 py-1 rounded text-xs">${entry.action}</span>
                </td>
                <td class="px-4 py-3">${entry.target_type}: ${entry.target_id || '-'}</td>
                <td class="px-4 py-3 text-sm text-gray-400 truncate max-w-xs"
                    title="${this.escapeHtml(details)}">${this.escapeHtml(details)}</td>
            </tr>
        `;
    }

    // =========================================================================
    // Modal
    // =========================================================================

    showModal(content) {
        document.getElementById('modal-content').innerHTML = content;
        document.getElementById('modal-container').classList.remove('hidden');
        document.getElementById('modal-container').classList.add('flex');
    }

    hideModal() {
        document.getElementById('modal-container').classList.add('hidden');
        document.getElementById('modal-container').classList.remove('flex');
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    async fetchJson(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            credentials: 'include'
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || response.statusText);
        }

        return response.json();
    }

    escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"']/g, char => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[char]);
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `px-6 py-3 rounded-lg text-white ${
            type === 'error' ? 'bg-red-600' : 'bg-green-600'
        }`;
        toast.textContent = message;
        document.getElementById('toast-container').appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize admin portal
const admin = new AdminPortal();
