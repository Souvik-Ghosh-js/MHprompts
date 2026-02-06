// Global Socket.IO instance
let socket = null;

// Initialize Socket.IO connection
function initSocketIO() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        showRealtimeIndicator();
        showToast('Connected to real-time server', 'success');
    });
    
    socket.on('prompt_updated', function(data) {
        console.log('Prompt updated:', data);
        
        let message = '';
        switch(data.action) {
            case 'insert':
                message = `${data.type} prompt created`;
                break;
            case 'update':
                message = `${data.type} prompt updated`;
                break;
            case 'delete':
                message = `${data.type} prompt deleted`;
                break;
            default:
                message = `${data.type} prompt ${data.action}`;
        }
        
        showToast(message, 'success');
        
        // Refresh the appropriate page
        const currentPath = window.location.pathname;
        if ((currentPath.includes('/l1-prompts') || currentPath === '/') && data.type === 'L1') {
            if (typeof loadL1Prompts === 'function') loadL1Prompts();
        } else if (currentPath.includes('/l2-prompts') && data.type === 'L2') {
            if (typeof loadL2Prompts === 'function') loadL2Prompts();
        }
        
        if (currentPath.includes('/statistics') || currentPath === '/') {
            if (typeof refreshStatistics === 'function') refreshStatistics();
            if (typeof loadClientData === 'function') loadClientData();
            if (typeof loadL2Summary === 'function') loadL2Summary();
        }
    });
    
    socket.on('connected', function(data) {
        console.log('Server connection established:', data.message);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        document.getElementById('realtime-indicator').style.display = 'none';
        showToast('Disconnected from server', 'error');
    });
}

// Toast notification system
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) {
        createToastElement();
    }
    
    toast.textContent = message;
    toast.className = 'toast ' + type;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function createToastElement() {
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
}

// Real-time indicator
function showRealtimeIndicator() {
    let indicator = document.getElementById('realtime-indicator');
    if (!indicator) return;
    
    indicator.style.display = 'inline-flex';
    indicator.style.background = '#28a745';
    
    setTimeout(() => {
        indicator.style.background = '#667eea';
    }, 2000);
}

// Confirmation modal
let pendingAction = null;

function showConfirmModal(title, message, action) {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    pendingAction = action;
    document.getElementById('confirmModal').classList.add('active');
}

function closeConfirmModal() {
    document.getElementById('confirmModal').classList.remove('active');
    pendingAction = null;
}

function executeConfirmedAction() {
    if (pendingAction && typeof pendingAction === 'function') {
        pendingAction();
    }
    closeConfirmModal();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSocketIO();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save form
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                activeForm.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeModal();
            closeConfirmModal();
        }
    });
    
    // Add modal close on outside click
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('promptModal');
        if (modal && modal.classList.contains('active') && e.target === modal) {
            closeModal();
        }
        
        const confirmModal = document.getElementById('confirmModal');
        if (confirmModal && confirmModal.classList.contains('active') && e.target === confirmModal) {
            closeConfirmModal();
        }
    });
});

// Common utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (response.ok) {
            showToast(`System Status: ${data.status} | Database: ${data.database}`, 'success');
        } else {
            showToast(`Health Check Failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast('Health check error: ' + error.message, 'error');
    }
}

// These functions are overridden by page-specific scripts
function openModal(type) {
    console.log('openModal should be overridden by page script');
}

function closeModal() {
    console.log('closeModal should be overridden by page script');
}

function editPrompt(type, id) {
    console.log('editPrompt should be overridden by page script');
}

function deletePrompt(type, id) {
    console.log('deletePrompt should be overridden by page script');
}

function loadL1Prompts() {
    console.log('loadL1Prompts should be overridden by page script');
}

function loadL2Prompts() {
    console.log('loadL2Prompts should be overridden by page script');
}

function refreshStatistics() {
    console.log('refreshStatistics should be overridden by page script');
}