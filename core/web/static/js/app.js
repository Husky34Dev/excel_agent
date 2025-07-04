/**
 * Excel Chatbot Web Interface - JavaScript Principal
 * Maneja la interacción del usuario, uploads, y comunicación con la API
 */

class ExcelChatbotApp {
    constructor() {
        this.currentClient = null;
        this.currentFile = null;
        this.isProcessing = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadInitialData();
    }
    
    initializeElements() {
        // Selectores
        this.clientSelect = document.getElementById('clientSelect');
        this.fileSelect = document.getElementById('fileSelect');
        this.fileInput = document.getElementById('fileInput');
        this.dragArea = document.getElementById('dragArea');
        
        // Información
        this.clientInfo = document.getElementById('clientInfo');
        this.clientBanner = document.getElementById('clientBanner');
        this.clientDescription = document.getElementById('clientDescription');
        this.questionsList = document.getElementById('questionsList');
        this.filesList = document.getElementById('filesList');
        
        // Chat
        this.chatMessages = document.getElementById('chatMessages');
        this.queryForm = document.getElementById('queryForm');
        this.queryInput = document.getElementById('queryInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearChat = document.getElementById('clearChat');
        
        // Upload
        this.uploadProgress = document.getElementById('uploadProgress');
        this.progressBar = document.getElementById('progressBar');
        this.uploadStatus = document.getElementById('uploadStatus');
    }
    
    bindEvents() {
        // Cliente selector
        this.clientSelect.addEventListener('change', (e) => this.onClientChange(e));
        
        // Archivo selector
        this.fileSelect.addEventListener('change', (e) => this.onFileChange(e));
        
        // Drag & Drop
        this.dragArea.addEventListener('click', () => this.fileInput.click());
        this.dragArea.addEventListener('dragover', (e) => this.onDragOver(e));
        this.dragArea.addEventListener('dragleave', (e) => this.onDragLeave(e));
        this.dragArea.addEventListener('drop', (e) => this.onDrop(e));
        
        // File input
        this.fileInput.addEventListener('change', (e) => this.onFileSelected(e));
        
        // Chat form
        this.queryForm.addEventListener('submit', (e) => this.onSubmitQuery(e));
        
        // Clear chat
        this.clearChat.addEventListener('click', () => this.onClearChat());
        
        // Enter key en input
        this.queryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.onSubmitQuery(e);
            }
        });
    }
    
    async loadInitialData() {
        try {
            const response = await fetch('/api/clients');
            const data = await response.json();
            
            if (data.success) {
                console.log('Clientes cargados:', data.clients);
            }
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
        }
    }
    
    async onClientChange(event) {
        const clientId = event.target.value;
        
        if (!clientId) {
            this.currentClient = null;
            this.hideClientInfo();
            this.clearFilesList();
            this.disableChat();
            return;
        }
        
        this.currentClient = clientId;
        this.showClientInfo(event.target.selectedOptions[0]);
        await this.loadClientFiles(clientId);
        this.enableFileSelection();
    }
    
    showClientInfo(option) {
        const name = option.dataset.name;
        const description = option.dataset.description;
        const banner = option.dataset.banner;
        
        this.clientBanner.textContent = banner || name;
        this.clientDescription.textContent = description;
        
        // Mostrar preguntas de ejemplo (desde el HTML template)
        const exampleQuestions = this.getExampleQuestions(this.currentClient);
        this.renderExampleQuestions(exampleQuestions);
        
        this.clientInfo.classList.remove('hidden');
    }
    
    hideClientInfo() {
        this.clientInfo.classList.add('hidden');
    }
    
    getExampleQuestions(clientId) {
        // Estas se cargan desde el template, pero podríamos hacerlo via API
        const clientData = window.clientsData && window.clientsData[clientId];
        return clientData ? clientData.example_questions : [];
    }
    
    renderExampleQuestions(questions) {
        this.questionsList.innerHTML = '';
        
        questions.forEach(question => {
            const button = document.createElement('button');
            button.className = 'text-left text-xs text-blue-600 hover:text-blue-800 hover:underline block w-full';
            button.textContent = question;
            button.addEventListener('click', () => {
                this.queryInput.value = question;
                this.queryInput.focus();
            });
            this.questionsList.appendChild(button);
        });
    }
    
    async loadClientFiles(clientId) {
        try {
            const response = await fetch(`/api/clients/${clientId}/files`);
            const data = await response.json();
            
            if (data.success) {
                this.renderFilesList(data.files);
                this.populateFileSelect(data.files);
            }
        } catch (error) {
            console.error('Error cargando archivos:', error);
            this.showError('Error cargando archivos del cliente');
        }
    }
    
    renderFilesList(files) {
        this.filesList.innerHTML = '';
        
        if (files.length === 0) {
            this.filesList.innerHTML = '<p class="text-gray-500 text-sm">No hay archivos. Sube un Excel para comenzar.</p>';
            return;
        }
        
        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer';
            fileItem.innerHTML = `
                <div class="flex items-center space-x-2">
                    <i class="fas fa-file-excel text-green-600"></i>
                    <span class="text-sm font-medium">${file.name}</span>
                </div>
                <div class="text-xs text-gray-500">
                    ${this.formatFileSize(file.size)}
                </div>
            `;
            
            fileItem.addEventListener('click', () => {
                this.selectFile(file);
            });
            
            this.filesList.appendChild(fileItem);
        });
    }
    
    populateFileSelect(files) {
        this.fileSelect.innerHTML = '<option value="">Seleccionar archivo...</option>';
        
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.path;
            option.textContent = file.name;
            this.fileSelect.appendChild(option);
        });
        
        this.fileSelect.disabled = false;
    }
    
    selectFile(file) {
        this.currentFile = file.path;
        this.fileSelect.value = file.path;
        this.enableChat();
        this.addSystemMessage(`Archivo seleccionado: ${file.name}`);
    }
    
    onFileChange(event) {
        const filePath = event.target.value;
        if (filePath) {
            this.currentFile = filePath;
            this.enableChat();
            const fileName = filePath.split('/').pop();
            this.addSystemMessage(`Archivo seleccionado: ${fileName}`);
        } else {
            this.currentFile = null;
            this.disableChat();
        }
    }
    
    enableFileSelection() {
        this.dragArea.classList.remove('opacity-50');
        this.dragArea.style.pointerEvents = 'auto';
    }
    
    enableChat() {
        this.queryInput.disabled = false;
        this.sendButton.disabled = false;
        this.queryInput.placeholder = 'Escribe tu pregunta sobre los datos...';
    }
    
    disableChat() {
        this.queryInput.disabled = true;
        this.sendButton.disabled = true;
        this.queryInput.placeholder = 'Selecciona un archivo para hacer consultas...';
    }
    
    clearFilesList() {
        this.filesList.innerHTML = '<p class="text-gray-500 text-sm">Selecciona un cliente para ver archivos</p>';
        this.fileSelect.innerHTML = '<option value="">Seleccionar archivo...</option>';
        this.fileSelect.disabled = true;
    }
    
    // === DRAG & DROP ===
    
    onDragOver(event) {
        event.preventDefault();
        this.dragArea.classList.add('drag-over');
    }
    
    onDragLeave(event) {
        event.preventDefault();
        this.dragArea.classList.remove('drag-over');
    }
    
    onDrop(event) {
        event.preventDefault();
        this.dragArea.classList.remove('drag-over');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.handleFileUpload(files[0]);
        }
    }
    
    onFileSelected(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFileUpload(file);
        }
    }
    
    async handleFileUpload(file) {
        if (!this.currentClient) {
            this.showError('Selecciona un cliente antes de subir archivos');
            return;
        }
        
        if (!file.name.match(/\.(xlsx|xls)$/i)) {
            this.showError('Solo se permiten archivos Excel (.xlsx, .xls)');
            return;
        }
        
        if (file.size > 50 * 1024 * 1024) { // 50MB
            this.showError('El archivo es demasiado grande (máx. 50MB)');
            return;
        }
        
        await this.uploadFile(file);
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('client_id', this.currentClient);
        
        this.showUploadProgress(0, 'Preparando upload...');
        
        try {
            const response = await fetch('/upload/file', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.hideUploadProgress();
                this.showSuccess(`Archivo "${file.name}" subido exitosamente`);
                await this.loadClientFiles(this.currentClient); // Recargar lista
            } else {
                this.hideUploadProgress();
                this.showError(result.detail || 'Error subiendo archivo');
            }
        } catch (error) {
            this.hideUploadProgress();
            this.showError('Error de conexión al subir archivo');
            console.error('Upload error:', error);
        }
    }
    
    showUploadProgress(percent, status) {
        this.uploadProgress.classList.remove('hidden');
        this.progressBar.style.width = `${percent}%`;
        this.uploadStatus.textContent = status;
    }
    
    hideUploadProgress() {
        this.uploadProgress.classList.add('hidden');
        this.progressBar.style.width = '0%';
    }
    
    // === CHAT ===
    
    async onSubmitQuery(event) {
        event.preventDefault();
        
        if (this.isProcessing) return;
        
        const question = this.queryInput.value.trim();
        if (!question) return;
        
        if (!this.currentClient || !this.currentFile) {
            this.showError('Selecciona un cliente y archivo antes de hacer consultas');
            return;
        }
        
        this.isProcessing = true;
        this.addUserMessage(question);
        this.queryInput.value = '';
        this.showTyping();
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    client_id: this.currentClient,
                    file_path: this.currentFile
                })
            });
            
            const result = await response.json();
            this.hideTyping();
            
            if (result.success) {
                this.addBotMessage(result.result, result.execution_time);
            } else {
                this.addErrorMessage(result.error || 'Error procesando consulta');
            }
            
        } catch (error) {
            this.hideTyping();
            this.addErrorMessage('Error de conexión al procesar consulta');
            console.error('Query error:', error);
        } finally {
            this.isProcessing = false;
        }
    }
    
    addUserMessage(message) {
        const messageDiv = this.createMessageElement('user', message);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(result, executionTime) {
        const messageDiv = this.createMessageElement('bot', result, executionTime);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSystemMessage(message) {
        const messageDiv = this.createMessageElement('system', message);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(error) {
        const messageDiv = this.createMessageElement('error', error);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createMessageElement(type, content, executionTime = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        
        let iconClass, bgClass, textClass;
        
        switch (type) {
            case 'user':
                iconClass = 'fas fa-user';
                bgClass = 'bg-blue-500';
                textClass = 'text-white';
                messageDiv.className += ' flex justify-end';
                break;
            case 'bot':
                iconClass = 'fas fa-robot';
                bgClass = 'bg-white border';
                textClass = 'text-gray-800';
                messageDiv.className += ' flex justify-start';
                break;
            case 'system':
                iconClass = 'fas fa-info-circle';
                bgClass = 'bg-gray-100';
                textClass = 'text-gray-600';
                messageDiv.className += ' flex justify-center';
                break;
            case 'error':
                iconClass = 'fas fa-exclamation-triangle';
                bgClass = 'bg-red-100 border-red-200';
                textClass = 'text-red-700';
                messageDiv.className += ' flex justify-center';
                break;
        }
        
        const timeInfo = executionTime ? ` (${executionTime.toFixed(2)}s)` : '';
        
        messageDiv.innerHTML = `
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${bgClass} ${textClass}">
                <div class="flex items-start space-x-2">
                    <i class="${iconClass} mt-1"></i>
                    <div class="flex-1">
                        <div class="whitespace-pre-wrap">${this.formatMessage(content)}</div>
                        ${timeInfo ? `<div class="text-xs opacity-75 mt-1">${timeInfo}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
        
        return messageDiv;
    }
    
    formatMessage(content) {
        if (typeof content === 'string') {
            return content;
        } else if (typeof content === 'object') {
            return JSON.stringify(content, null, 2);
        } else {
            return String(content);
        }
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'chat-message flex justify-start';
        typingDiv.innerHTML = `
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-100">
                <div class="flex items-center space-x-2">
                    <i class="fas fa-robot"></i>
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
                    </div>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    onClearChat() {
        this.chatMessages.innerHTML = `
            <div class="text-center text-gray-500">
                <i class="fas fa-robot text-4xl mb-4"></i>
                <p>Chat limpiado. ¿En qué puedo ayudarte?</p>
            </div>
        `;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    // === UTILITIES ===
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        // Simple notification - could be enhanced with a proper notification system
        const className = type === 'error' ? 'bg-red-500' : 'bg-green-500';
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 ${className} text-white rounded-lg shadow-lg z-50`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ExcelChatbotApp();
});
