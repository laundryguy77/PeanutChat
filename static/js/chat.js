// Chat Manager - Handles message display and streaming
export class ChatManager {
    constructor(app) {
        this.app = app;
        this.messageList = document.getElementById('message-list');
        this.chatContainer = document.getElementById('chat-container');
        this.isStreaming = false;
        this.currentAssistantMessage = null;
        this.editingMessageId = null;
        this.currentStreamContent = '';
        this.currentThinkingContent = '';
        this.thinkingContainer = null;
        this.initializeMarkdown();
    }

    initializeMarkdown() {
        if (typeof marked !== 'undefined') {
            const renderer = new marked.Renderer();

            // Custom table renderer to wrap in scrollable div
            renderer.table = function(header, body) {
                return `<div class="overflow-x-auto my-4 rounded-lg border border-gray-700">
                    <table class="min-w-full text-sm text-left">${header}${body}</table>
                </div>`;
            };

            // Custom code renderer for inline code
            renderer.codespan = function(code) {
                return `<code class="px-1.5 py-0.5 bg-surface-dark text-orange-400 rounded text-sm font-mono">${code}</code>`;
            };

            marked.setOptions({
                renderer: renderer,
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {}
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }

    renderMarkdown(content) {
        if (!content || typeof marked === 'undefined') return content || '';

        try {
            let html = marked.parse(content);

            // Style code blocks with GitHub-dark theme
            html = html.replace(/<pre><code class="language-(\w+)">/g, (match, lang) => {
                return `<div class="rounded-xl overflow-hidden border border-gray-700 bg-[#0d1117] shadow-xl my-4">
                    <div class="flex items-center justify-between px-4 py-2.5 bg-[#161b22] border-b border-gray-700">
                        <span class="text-xs text-gray-400 font-mono">${lang}</span>
                        <button onclick="navigator.clipboard.writeText(this.closest('.rounded-xl').querySelector('code').textContent).then(()=>{this.innerHTML='<span class=\\'material-symbols-outlined text-sm\\'>check</span> Copied';setTimeout(()=>{this.innerHTML='<span class=\\'material-symbols-outlined text-sm\\'>content_copy</span> Copy'},1500)})" class="text-gray-400 hover:text-white transition-colors flex items-center gap-1 text-xs">
                            <span class="material-symbols-outlined text-sm">content_copy</span> Copy
                        </button>
                    </div>
                    <pre class="p-4 overflow-x-auto"><code class="language-${lang} text-sm font-mono leading-relaxed">`;
            });

            html = html.replace(/<pre><code>/g, `<div class="rounded-xl overflow-hidden border border-gray-700 bg-[#0d1117] shadow-xl my-4">
                <div class="flex items-center justify-between px-4 py-2.5 bg-[#161b22] border-b border-gray-700">
                    <span class="text-xs text-gray-400 font-mono">code</span>
                    <button onclick="navigator.clipboard.writeText(this.closest('.rounded-xl').querySelector('code').textContent).then(()=>{this.innerHTML='<span class=\\'material-symbols-outlined text-sm\\'>check</span> Copied';setTimeout(()=>{this.innerHTML='<span class=\\'material-symbols-outlined text-sm\\'>content_copy</span> Copy'},1500)})" class="text-gray-400 hover:text-white transition-colors flex items-center gap-1 text-xs">
                        <span class="material-symbols-outlined text-sm">content_copy</span> Copy
                    </button>
                </div>
                <pre class="p-4 overflow-x-auto"><code class="text-sm font-mono leading-relaxed">`);

            html = html.replace(/<\/code><\/pre>/g, '</code></pre></div>');

            // Style tables
            html = html.replace(/<thead>/g, '<thead class="bg-surface-darker text-gray-400 font-bold uppercase text-xs tracking-wider">');
            html = html.replace(/<th>/g, '<th class="px-4 py-3 border-b border-gray-700">');
            html = html.replace(/<td>/g, '<td class="px-4 py-3 text-gray-300">');
            html = html.replace(/<tr>/g, '<tr class="hover:bg-white/5 transition-colors border-b border-gray-700/50">');

            // Style blockquotes as info callouts
            html = html.replace(/<blockquote>/g, '<div class="flex gap-4 p-4 rounded-xl bg-primary/10 border border-primary/20 text-gray-200 my-4"><span class="material-symbols-outlined text-primary flex-shrink-0">info</span><div>');
            html = html.replace(/<\/blockquote>/g, '</div></div>');

            // Style links
            html = html.replace(/<a /g, '<a class="text-primary hover:underline" ');

            return html;
        } catch (e) {
            console.error('Markdown parse error:', e);
            return content;
        }
    }

    createMessageElement(role, content, images = [], messageId = null, files = []) {
        const isUser = role === 'user';
        const message = document.createElement('div');
        message.className = `flex gap-4 md:gap-6 animate-fadeIn group ${isUser ? 'flex-row-reverse' : ''}`;
        if (messageId) message.dataset.messageId = messageId;

        // Avatar
        const avatar = document.createElement('div');
        if (isUser) {
            avatar.className = 'size-8 md:size-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1 shadow-md';
            avatar.innerHTML = '<span class="material-symbols-outlined text-white text-lg">person</span>';
        } else {
            avatar.className = 'size-8 md:size-10 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 flex items-center justify-center flex-shrink-0 mt-1 shadow-md';
            avatar.innerHTML = '<span class="material-symbols-outlined text-primary text-xl">smart_toy</span>';
        }

        // Bubble container
        const bubbleContainer = document.createElement('div');
        bubbleContainer.className = `max-w-[85%] space-y-2 ${isUser ? '' : 'flex-1 min-w-0'}`;

        // Assistant header
        if (!isUser) {
            const header = document.createElement('div');
            header.className = 'flex items-center gap-2 mb-1';
            header.innerHTML = `
                <span class="font-bold text-gray-200 text-sm">PeanutChat</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gray-800 text-gray-400 border border-gray-700">AI</span>
            `;
            bubbleContainer.appendChild(header);
        }

        // Message bubble
        const bubble = document.createElement('div');
        if (isUser) {
            bubble.className = 'rounded-2xl rounded-tr-sm bg-primary p-4 text-white shadow-lg shadow-blue-900/10';
        } else {
            bubble.className = 'space-y-4';
        }

        // Render files if any
        if (files && files.length > 0) {
            const fileList = document.createElement('div');
            fileList.className = 'flex flex-wrap gap-2 mb-3';
            const icons = { pdf: 'picture_as_pdf', zip: 'folder_zip', text: 'description', code: 'code' };
            files.forEach(f => {
                const fileEl = document.createElement('div');
                fileEl.className = 'flex items-center gap-2 px-3 py-2 bg-surface-dark/50 border border-gray-700 rounded-lg text-sm';
                fileEl.innerHTML = `
                    <span class="material-symbols-outlined text-primary text-lg">${icons[f.type] || icons.text}</span>
                    <span class="text-gray-300">${f.name}</span>
                `;
                fileList.appendChild(fileEl);
            });
            bubble.appendChild(fileList);
        }

        // Render images if any
        if (images && images.length > 0) {
            const imageGrid = document.createElement('div');
            imageGrid.className = 'flex flex-wrap gap-2 mb-3';
            images.forEach(img => {
                const imgEl = document.createElement('img');
                imgEl.src = img.startsWith('data:') ? img : `data:image/jpeg;base64,${img}`;
                imgEl.className = 'max-w-[200px] max-h-[200px] rounded-lg object-cover';
                imageGrid.appendChild(imgEl);
            });
            bubble.appendChild(imageGrid);
        }

        // Content
        const contentEl = document.createElement('div');
        if (isUser) {
            contentEl.className = 'leading-relaxed whitespace-pre-wrap';
            contentEl.textContent = content;
        } else {
            contentEl.className = 'prose prose-invert prose-sm max-w-none text-gray-300 leading-relaxed';
            contentEl.innerHTML = this.renderMarkdown(content);
        }
        bubble.appendChild(contentEl);
        bubbleContainer.appendChild(bubble);

        // Timestamp
        const timestamp = document.createElement('div');
        timestamp.className = `text-xs text-gray-500 font-medium mt-1 ${isUser ? 'text-right pr-1' : 'pl-1'}`;
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        bubbleContainer.appendChild(timestamp);

        // Action buttons
        const actions = document.createElement('div');
        actions.className = `flex gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity ${isUser ? 'justify-end' : 'justify-start'}`;

        // Store content for closure
        const messageContent = content;
        const msgId = messageId;
        const chatManager = this;

        console.log('Creating action buttons for message:', { role, msgId, contentPreview: messageContent?.substring(0, 30) });

        if (isUser) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
            copyBtn.title = 'Copy';
            copyBtn.innerHTML = '<span class="material-symbols-outlined text-sm">content_copy</span>';
            copyBtn.onclick = (e) => {
                console.log('User copy button clicked!');
                e.preventDefault();
                e.stopPropagation();
                chatManager.copyToClipboard(messageContent, copyBtn);
            };
            actions.appendChild(copyBtn);

            if (msgId) {
                const editBtn = document.createElement('button');
                editBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
                editBtn.title = 'Edit';
                editBtn.innerHTML = '<span class="material-symbols-outlined text-sm">edit</span>';
                editBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    chatManager.showEditModal(msgId, messageContent);
                };
                actions.appendChild(editBtn);
            }
        } else {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
            copyBtn.title = 'Copy';
            copyBtn.innerHTML = '<span class="material-symbols-outlined text-sm">content_copy</span>';
            copyBtn.onclick = (e) => {
                console.log('Assistant copy button clicked!');
                e.preventDefault();
                e.stopPropagation();
                chatManager.copyToClipboard(messageContent, copyBtn);
            };
            actions.appendChild(copyBtn);

            if (msgId) {
                const regenBtn = document.createElement('button');
                regenBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
                regenBtn.title = 'Regenerate';
                regenBtn.innerHTML = '<span class="material-symbols-outlined text-sm">refresh</span>';
                regenBtn.onclick = (e) => {
                    console.log('Regenerate button clicked!', msgId);
                    e.preventDefault();
                    e.stopPropagation();
                    chatManager.regenerateResponse(msgId);
                };
                actions.appendChild(regenBtn);
            }
        }
        bubbleContainer.appendChild(actions);

        message.appendChild(avatar);
        message.appendChild(bubbleContainer);

        return message;
    }

    createActionButton(icon, title, onClick) {
        const btn = document.createElement('button');
        btn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
        btn.title = title;
        btn.innerHTML = `<span class="material-symbols-outlined text-sm">${icon}</span>`;
        btn.addEventListener('click', onClick);
        return btn;
    }

    renderConversation(conv) {
        this.clearMessages();

        if (!conv.messages || conv.messages.length === 0) {
            this.showWelcome();
            return;
        }

        conv.messages.forEach(msg => {
            const msgEl = this.createMessageElement(msg.role, msg.content, msg.images || [], msg.id, msg.files);
            this.messageList.appendChild(msgEl);
        });

        this.scrollToBottom();
    }

    showWelcome() {
        const welcome = document.createElement('div');
        welcome.className = 'welcome-message text-center py-16 space-y-4 animate-fadeIn';
        welcome.innerHTML = `
            <div class="size-16 rounded-2xl bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center mx-auto shadow-lg shadow-primary/30">
                <span class="material-symbols-outlined text-3xl text-white">smart_toy</span>
            </div>
            <h2 class="font-display font-bold text-2xl text-white">Welcome to PeanutChat</h2>
            <p class="text-gray-400 max-w-md mx-auto">Chat with a local AI that can search the web and help with any task.</p>
            <p class="text-gray-500 text-sm">Choose a model from the dropdown to get started.</p>
        `;
        this.messageList.appendChild(welcome);
    }

    clearMessages() {
        while (this.messageList.firstChild) {
            this.messageList.removeChild(this.messageList.firstChild);
        }
        this.showWelcome();
    }

    addMessage(role, content, images = [], messageId = null, files = []) {
        const welcome = this.messageList.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        const message = this.createMessageElement(role, content, images, messageId, files);
        this.messageList.appendChild(message);
        this.scrollToBottom();
        return message;
    }

    startAssistantMessage() {
        const welcome = this.messageList.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        this.currentStreamContent = '';
        this.currentThinkingContent = '';
        this.thinkingContainer = null;

        const message = document.createElement('div');
        message.className = 'flex gap-4 md:gap-6 animate-fadeIn group';

        // Avatar
        const avatar = document.createElement('div');
        avatar.className = 'size-8 md:size-10 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 flex items-center justify-center flex-shrink-0 mt-1 shadow-md';
        avatar.innerHTML = '<span class="material-symbols-outlined text-primary text-xl">smart_toy</span>';

        // Bubble container
        const bubbleContainer = document.createElement('div');
        bubbleContainer.className = 'flex-1 min-w-0 space-y-2';

        // Header
        const header = document.createElement('div');
        header.className = 'flex items-center gap-2 mb-1';
        header.innerHTML = `
            <span class="font-bold text-gray-200 text-sm">PeanutChat</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gray-800 text-gray-400 border border-gray-700">AI</span>
        `;
        bubbleContainer.appendChild(header);

        // Content area
        const content = document.createElement('div');
        content.className = 'prose prose-invert prose-sm max-w-none text-gray-300 leading-relaxed assistant-content';

        // Typing indicator
        content.innerHTML = `
            <div class="flex items-center gap-1.5 text-gray-500 typing-indicator">
                <div class="size-2 bg-gray-500 rounded-full typing-dot"></div>
                <div class="size-2 bg-gray-500 rounded-full typing-dot"></div>
                <div class="size-2 bg-gray-500 rounded-full typing-dot"></div>
            </div>
        `;

        bubbleContainer.appendChild(content);
        message.appendChild(avatar);
        message.appendChild(bubbleContainer);

        this.currentAssistantMessage = {
            element: message,
            content: '',
            contentEl: content,
            bubbleContainer: bubbleContainer
        };

        this.messageList.appendChild(message);
        this.scrollToBottom();

        return message;
    }

    appendToAssistantMessage(text) {
        if (!this.currentAssistantMessage) return;

        const typing = this.currentAssistantMessage.contentEl.querySelector('.typing-indicator');
        if (typing) typing.remove();

        this.currentStreamContent += text;
        this.currentAssistantMessage.contentEl.innerHTML = this.renderMarkdown(this.currentStreamContent);
        this.scrollToBottom();
    }

    appendThinkingContent(text) {
        if (!this.currentAssistantMessage) return;

        const typing = this.currentAssistantMessage.contentEl.querySelector('.typing-indicator');
        if (typing) typing.remove();

        if (!this.thinkingContainer) {
            this.thinkingContainer = document.createElement('div');
            this.thinkingContainer.className = 'mb-4 p-4 rounded-xl bg-primary/10 border border-primary/20';
            this.thinkingContainer.innerHTML = `
                <div class="flex items-center gap-2 mb-2 text-primary text-sm font-medium">
                    <span class="material-symbols-outlined text-lg animate-spin">psychology</span>
                    <span>Thinking...</span>
                </div>
                <div class="thinking-content text-gray-400 text-sm max-h-48 overflow-y-auto whitespace-pre-wrap"></div>
            `;
            this.currentAssistantMessage.contentEl.appendChild(this.thinkingContainer);
        }

        this.currentThinkingContent += text;
        this.thinkingContainer.querySelector('.thinking-content').textContent = this.currentThinkingContent;
        this.scrollToBottom();
    }

    finishThinking() {
        if (!this.thinkingContainer) return;

        this.thinkingContainer.innerHTML = `
            <details class="group">
                <summary class="flex items-center gap-2 cursor-pointer text-primary text-sm font-medium list-none">
                    <span class="material-symbols-outlined text-lg">psychology</span>
                    <span>Thought process</span>
                    <span class="material-symbols-outlined text-gray-500 group-open:rotate-180 transition-transform">expand_more</span>
                </summary>
                <div class="mt-2 text-gray-400 text-sm max-h-48 overflow-y-auto whitespace-pre-wrap">${this.currentThinkingContent}</div>
            </details>
        `;
    }

    addToolIndicator(toolName, status = 'processing') {
        if (!this.currentAssistantMessage) return null;

        const indicator = document.createElement('div');
        indicator.className = 'flex items-center gap-2 p-3 rounded-lg bg-surface-dark border border-gray-700 my-3 text-sm';

        if (status === 'processing') {
            indicator.innerHTML = `
                <span class="material-symbols-outlined text-primary animate-spin">sync</span>
                <span class="text-gray-300">Using <strong class="text-white">${toolName}</strong>...</span>
            `;
        }

        this.currentAssistantMessage.contentEl.appendChild(indicator);
        this.scrollToBottom();
        return indicator;
    }

    updateToolIndicator(indicator, status, message) {
        if (!indicator) return;

        if (status === 'complete') {
            indicator.innerHTML = `
                <span class="material-symbols-outlined text-green-500">check_circle</span>
                <span class="text-gray-300">${message}</span>
            `;
        } else if (status === 'error') {
            indicator.innerHTML = `
                <span class="material-symbols-outlined text-red-500">error</span>
                <span class="text-gray-300">${message}</span>
            `;
        }
    }

    addGeneratedImage(imageUrl) {
        if (!this.currentAssistantMessage) return;

        const container = document.createElement('div');
        container.className = 'my-4 rounded-xl overflow-hidden border border-gray-700';

        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'Generated image';
        img.className = 'w-full cursor-pointer hover:opacity-90 transition-opacity';
        img.addEventListener('click', () => window.open(imageUrl, '_blank'));

        const downloadBar = document.createElement('div');
        downloadBar.className = 'flex items-center justify-between p-3 bg-surface-dark border-t border-gray-700';
        downloadBar.innerHTML = `
            <span class="text-sm text-gray-400">Generated Image</span>
            <a href="${imageUrl}" download class="text-primary hover:text-white text-sm font-medium transition-colors flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">download</span> Download
            </a>
        `;

        container.appendChild(img);
        container.appendChild(downloadBar);
        this.currentAssistantMessage.contentEl.appendChild(container);
        this.scrollToBottom();
    }

    addAssistantActions(messageId) {
        if (!this.currentAssistantMessage) return;

        const actions = document.createElement('div');
        actions.className = 'flex gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity';

        // Store for closure
        const streamContent = this.currentStreamContent;
        const msgId = messageId;
        const chatManager = this;

        const copyBtn = document.createElement('button');
        copyBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
        copyBtn.title = 'Copy';
        copyBtn.innerHTML = '<span class="material-symbols-outlined text-sm">content_copy</span>';
        copyBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            chatManager.copyToClipboard(streamContent, copyBtn);
        };

        const regenBtn = document.createElement('button');
        regenBtn.className = 'p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all';
        regenBtn.title = 'Regenerate';
        regenBtn.innerHTML = '<span class="material-symbols-outlined text-sm">refresh</span>';
        regenBtn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            chatManager.regenerateResponse(msgId);
        };

        actions.appendChild(copyBtn);
        actions.appendChild(regenBtn);
        this.currentAssistantMessage.bubbleContainer.appendChild(actions);
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    copyToClipboard(text, button) {
        console.log('copyToClipboard called with:', { text: text?.substring(0, 50), button });
        if (!text) {
            console.error('Copy failed: No text to copy');
            return;
        }
        navigator.clipboard.writeText(text).then(() => {
            if (button) {
                const icon = button.querySelector('.material-symbols-outlined');
                if (icon) {
                    const original = icon.textContent;
                    icon.textContent = 'check';
                    button.classList.add('text-green-500');
                    setTimeout(() => {
                        icon.textContent = original;
                        button.classList.remove('text-green-500');
                    }, 1500);
                }
            }
            console.log('Copied to clipboard:', text.substring(0, 50) + '...');
        }).catch(err => {
            console.error('Copy failed:', err);
            // Fallback for older browsers or HTTP contexts
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                console.log('Copied via fallback');
            } catch (e) {
                console.error('Fallback copy failed:', e);
            }
            document.body.removeChild(textarea);
        });
    }

    async regenerateResponse(messageId) {
        console.log('regenerateResponse called with messageId:', messageId);
        if (this.isStreaming) {
            console.log('Blocked: already streaming');
            return;
        }

        const convId = this.app.currentConversationId;
        console.log('Conversation ID:', convId);
        if (!convId) {
            console.log('Blocked: no conversation ID');
            return;
        }

        try {
            console.log('Fetching regenerate endpoint...');
            const response = await fetch(`/api/chat/conversations/${convId}/regenerate/${messageId}`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to regenerate');

            this.startAssistantMessage();
            this.isStreaming = true;
            document.getElementById('send-btn').disabled = true;

            await this.handleSSEStream(response);
            await this.app.loadConversation(convId);
        } catch (error) {
            console.error('Regenerate error:', error);
        } finally {
            this.isStreaming = false;
            this.currentAssistantMessage = null;
            document.getElementById('send-btn').disabled = false;
        }
    }

    showEditModal(messageId, content) {
        this.editingMessageId = messageId;
        const modal = document.getElementById('edit-modal');
        const textarea = document.getElementById('edit-content');
        textarea.value = content;
        modal.classList.remove('hidden');
        textarea.focus();
    }

    async saveEdit() {
        const modal = document.getElementById('edit-modal');
        const textarea = document.getElementById('edit-content');
        const newContent = textarea.value.trim();
        const editType = document.querySelector('input[name="edit-type"]:checked').value;

        if (!newContent || !this.editingMessageId) {
            modal.classList.add('hidden');
            return;
        }

        const convId = this.app.currentConversationId;
        if (!convId) {
            modal.classList.add('hidden');
            return;
        }

        try {
            if (editType === 'fork') {
                const response = await fetch(`/api/chat/conversations/${convId}/messages/${this.editingMessageId}/fork`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: newContent })
                });
                const data = await response.json();
                if (data.id) {
                    await this.app.loadConversation(data.id);
                    await this.app.loadConversations();
                }
            } else {
                await fetch(`/api/chat/conversations/${convId}/messages/${this.editingMessageId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: newContent })
                });
                await this.app.loadConversation(convId);
            }
        } catch (error) {
            console.error('Failed to edit message:', error);
        }

        modal.classList.add('hidden');
        this.editingMessageId = null;
    }

    async sendMessage(text, images = [], imageDataUrls = [], think = false, files = []) {
        if (this.isStreaming) return;

        this.addMessage('user', text, imageDataUrls, null, files);
        this.startAssistantMessage();
        this.isStreaming = true;

        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = true;

        try {
            const headers = { 'Content-Type': 'application/json' };
            if (this.app.currentConversationId) {
                headers['X-Conversation-ID'] = this.app.currentConversationId;
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    message: text,
                    images: images.length > 0 ? images : undefined,
                    think: think || undefined,
                    files: files.length > 0 ? files : undefined
                })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            await this.handleSSEStream(response);
        } catch (error) {
            console.error('Chat error:', error);
            this.appendToAssistantMessage(`Error: ${error.message}`);
        } finally {
            this.isStreaming = false;
            this.currentAssistantMessage = null;
            sendBtn.disabled = false;
        }
    }

    async handleSSEStream(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let toolIndicator = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event:')) continue;
                if (line.startsWith('data:')) {
                    const dataStr = line.slice(5).trim();
                    if (!dataStr) continue;
                    try {
                        const data = JSON.parse(dataStr);
                        toolIndicator = await this.handleSSEEvent(data, toolIndicator);
                    } catch (e) {
                        console.error('Failed to parse SSE data:', dataStr, e);
                    }
                }
            }
        }
    }

    async handleSSEEvent(data, toolIndicator) {
        // Conversation ID
        if (data.id !== undefined && data.id && !data.role) {
            this.app.setCurrentConversation(data.id);
        }

        // Thinking tokens
        if (data.thinking !== undefined) {
            this.appendThinkingContent(data.thinking);
        }

        // Thinking done
        if (data.thinking_done) {
            this.finishThinking();
        }

        // Content tokens
        if (data.content !== undefined) {
            this.appendToAssistantMessage(data.content);
        }

        // Tool call
        if (data.name && data.arguments !== undefined) {
            toolIndicator = this.addToolIndicator(data.name, 'processing');
        }

        // Tool result
        if (data.result !== undefined && toolIndicator) {
            const status = data.result.success ? 'complete' : 'error';
            let message = data.result.success ? 'Complete' : data.result.error;

            if (data.name === 'web_search') {
                message = data.result.success ? `Found ${data.result.num_results} results` : data.result.error;
            } else if (data.name === 'generate_image') {
                message = data.result.success ? 'Image generated' : data.result.error;
                if (data.result.success && data.result.image_url) {
                    this.addGeneratedImage(data.result.image_url);
                }
            }
            this.updateToolIndicator(toolIndicator, status, message);
        }

        // Message ID for actions
        if (data.role === 'assistant' && data.id) {
            if (this.currentAssistantMessage) {
                this.currentAssistantMessage.element.dataset.messageId = data.id;
                this.addAssistantActions(data.id);
            }
        }

        // Done
        if (data.finish_reason !== undefined) {
            console.log('Stream complete:', data.finish_reason);
        }

        // Error
        if (data.message !== undefined && data.content === undefined) {
            this.appendToAssistantMessage(`\n\nError: ${data.message}`);
        }

        return toolIndicator;
    }

    async clearHistory() {
        await this.app.createNewConversation();
    }
}
