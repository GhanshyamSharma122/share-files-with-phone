/**
 * Wi-Fi Share - Main JavaScript Application
 */

// ========== GLOBAL STATE ==========
let selectedFiles = [];
let currentFilter = 'all';

// ========== TOAST NOTIFICATIONS ==========
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

// ========== DRAG & DROP ==========
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

['dragenter', 'dragover'].forEach(event => {
    dropZone.addEventListener(event, () => dropZone.classList.add('drag-over'));
});

['dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, () => dropZone.classList.remove('drag-over'));
});

dropZone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', e => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    for (let file of files) {
        if (!selectedFiles.find(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    }
    renderSelectedFiles();
}

function renderSelectedFiles() {
    const container = document.getElementById('selectedFiles');
    if (selectedFiles.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = selectedFiles.map((file, i) => `
        <div class="selected-file">
            <span class="name">${file.name}</span>
            <span class="size">${formatSize(file.size)}</span>
            <span class="remove" onclick="removeFile(${i})">&times;</span>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderSelectedFiles();
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

// ========== UPLOAD ==========
function uploadFiles() {
    if (selectedFiles.length === 0) {
        showToast('Please select files to upload', 'warning');
        return;
    }
    
    const formData = new FormData();
    for (let file of selectedFiles) {
        formData.append('files', file);
    }
    
    const xhr = new XMLHttpRequest();
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressSpeed = document.getElementById('progressSpeed');
    const progressEta = document.getElementById('progressEta');
    const uploadBtn = document.getElementById('uploadBtn');
    
    const startTime = Date.now();
    
    progressContainer.classList.add('active');
    uploadBtn.disabled = true;
    
    xhr.upload.onprogress = e => {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressFill.style.width = percent + '%';
            progressPercent.textContent = percent.toFixed(1) + '%';
            
            const elapsed = (Date.now() - startTime) / 1000;
            const speed = e.loaded / elapsed;
            const remaining = (e.total - e.loaded) / speed;
            
            progressSpeed.textContent = formatSize(speed) + '/s';
            progressEta.textContent = remaining.toFixed(0) + 's left';
        }
    };
    
    xhr.onload = () => {
        uploadBtn.disabled = false;
        if (xhr.status === 200) {
            showToast(`Successfully uploaded ${selectedFiles.length} file(s)`, 'success');
            selectedFiles = [];
            renderSelectedFiles();
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Upload failed. Please try again.', 'error');
            progressContainer.classList.remove('active');
        }
    };
    
    xhr.onerror = () => {
        uploadBtn.disabled = false;
        showToast('Network error. Please check your connection.', 'error');
        progressContainer.classList.remove('active');
    };
    
    xhr.open('POST', '/upload');
    xhr.send(formData);
}

// ========== SEARCH & FILTER ==========
function filterFiles() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const items = document.querySelectorAll('.file-item');
    
    items.forEach(item => {
        const name = item.dataset.name.toLowerCase();
        const category = item.dataset.category;
        const matchesSearch = name.includes(query);
        const matchesFilter = currentFilter === 'all' || category === currentFilter;
        
        item.style.display = (matchesSearch && matchesFilter) ? 'flex' : 'none';
    });
}

function setFilter(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterFiles();
}

function sortFiles() {
    const sortValue = document.getElementById('sortSelect').value;
    const fileList = document.getElementById('fileList');
    const items = Array.from(fileList.querySelectorAll('.file-item'));
    
    items.sort((a, b) => {
        switch(sortValue) {
            case 'name-asc': return a.dataset.name.localeCompare(b.dataset.name);
            case 'name-desc': return b.dataset.name.localeCompare(a.dataset.name);
            case 'size-asc': return parseInt(a.dataset.size) - parseInt(b.dataset.size);
            case 'size-desc': return parseInt(b.dataset.size) - parseInt(a.dataset.size);
            case 'date-asc': return parseFloat(a.dataset.mtime) - parseFloat(b.dataset.mtime);
            case 'date-desc': return parseFloat(b.dataset.mtime) - parseFloat(a.dataset.mtime);
            default: return 0;
        }
    });
    
    items.forEach(item => fileList.appendChild(item));
}

// ========== FILE ACTIONS ==========
function copyLink(filename) {
    const url = window.location.origin + '/download/' + encodeURIComponent(filename);
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!', 'success');
        }).catch(() => fallbackCopy(url));
    } else {
        fallbackCopy(url);
    }
}

function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    try {
        document.execCommand('copy');
        showToast('Link copied to clipboard!', 'success');
    } catch (e) {
        showToast('Failed to copy link', 'error');
    }
    document.body.removeChild(ta);
}

function deleteFile(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;
    
    fetch('/delete/' + encodeURIComponent(filename), { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast('File deleted successfully', 'success');
                setTimeout(() => location.reload(), 500);
            } else {
                showToast(data.error || 'Failed to delete file', 'error');
            }
        })
        .catch(() => showToast('Network error', 'error'));
}

// ========== PREVIEW ==========
function previewFile(filename, category) {
    const modal = document.getElementById('previewModal');
    const title = document.getElementById('previewTitle');
    const body = document.getElementById('previewBody');
    
    title.textContent = filename;
    const url = '/stream/' + encodeURIComponent(filename);
    
    let content = '';
    switch(category) {
        case 'image':
            content = `<img src="${url}" alt="${filename}">`;
            break;
        case 'video':
            content = `<video src="${url}" controls autoplay></video>`;
            break;
        case 'audio':
            content = `<audio src="${url}" controls autoplay style="width: 400px;"></audio>`;
            break;
        case 'document':
            if (filename.toLowerCase().endsWith('.pdf')) {
                content = `<iframe src="${url}"></iframe>`;
            }
            break;
        default:
            content = '<p>Preview not available</p>';
    }
    
    body.innerHTML = content;
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('previewModal');
    modal.classList.remove('active');
    document.getElementById('previewBody').innerHTML = '';
}

// Close modal on escape key
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});

// Close modal on outside click
document.getElementById('previewModal').addEventListener('click', e => {
    if (e.target.id === 'previewModal') closeModal();
});

// ========== CLIPBOARD PASTE ==========
document.addEventListener('paste', async e => {
    const items = e.clipboardData?.items;
    if (!items) return;
    
    for (let item of items) {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            if (file) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const newFile = new File([file], `clipboard-${timestamp}.png`, { type: file.type });
                handleFiles([newFile]);
                showToast('Image pasted from clipboard!', 'info');
            }
        }
    }
});
