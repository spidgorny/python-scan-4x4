// App State
let currentScan = null;
let scans = [];

// DOM Elements
const scanBtn = document.getElementById('scanBtn');
const scanStatus = document.getElementById('scanStatus');
const scansList = document.getElementById('scansList');
const scanView = document.getElementById('scanView');
const scanInfo = document.getElementById('scanInfo');
const photosGrid = document.getElementById('photosGrid');
const photoCount = document.getElementById('photoCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadScans();
    setInterval(checkScanStatus, 2000);
});

// Load all scans
async function loadScans() {
    try {
        const response = await fetch('/api/scans');
        scans = await response.json();
        renderScansList();
        
        // Auto-select latest scan if none selected
        if (!currentScan && scans.length > 0) {
            selectScan(scans[0]);
        }
    } catch (error) {
        console.error('Error loading scans:', error);
    }
}

// Render scans list
function renderScansList() {
    if (scans.length === 0) {
        scansList.innerHTML = '<p class="empty-message">No scans yet</p>';
        return;
    }
    
    scansList.innerHTML = scans.map(scan => `
        <div class="scan-item ${currentScan?.filename === scan.filename ? 'active' : ''}"
             onclick="selectScanByFilename('${scan.filename}')">
            <div class="scan-item-name">${scan.filename}</div>
            <div class="scan-item-time">${formatTime(scan.timestamp)}</div>
        </div>
    `).join('');
}

// Select scan
function selectScanByFilename(filename) {
    const scan = scans.find(s => s.filename === filename);
    if (scan) {
        selectScan(scan);
    }
}

function selectScan(scan) {
    currentScan = scan;
    renderScansList();
    displayScan(scan);
    displayPhotos(scan);
}

// Display scan
function displayScan(scan) {
    scanInfo.textContent = scan.filename;
    scanView.innerHTML = `<img src="${scan.path}" alt="Scanned document">`;
}

// Display photos
function displayPhotos(scan) {
    const photoSlots = photosGrid.querySelectorAll('.photo-slot');
    
    photoSlots.forEach((slot, index) => {
        if (index < scan.photos.length) {
            slot.innerHTML = `<img src="${scan.photos[index]}" alt="Photo ${index + 1}">`;
        } else {
            slot.innerHTML = `
                <div class="photo-placeholder">
                    <span>${index + 1}</span>
                </div>
            `;
        }
    });
    
    photoCount.textContent = `${scan.photos.length}/4`;
}

// Trigger scan
scanBtn.addEventListener('click', async () => {
    if (scanBtn.disabled) return;
    
    try {
        scanBtn.disabled = true;
        scanStatus.classList.remove('hidden');
        
        const response = await fetch('/api/scan', { method: 'POST' });
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            scanBtn.disabled = false;
            scanStatus.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error starting scan:', error);
        alert('Failed to start scan');
        scanBtn.disabled = false;
        scanStatus.classList.add('hidden');
    }
});

// Check scan status
async function checkScanStatus() {
    try {
        const response = await fetch('/api/scan/status');
        const data = await response.json();
        
        if (data.in_progress) {
            scanBtn.disabled = true;
            scanStatus.classList.remove('hidden');
        } else {
            scanBtn.disabled = false;
            scanStatus.classList.add('hidden');
            
            // Reload scans when scan completes
            const oldCount = scans.length;
            await loadScans();
            
            // Select newest scan if new scan appeared
            if (scans.length > oldCount && scans.length > 0) {
                selectScan(scans[0]);
            }
        }
    } catch (error) {
        console.error('Error checking scan status:', error);
    }
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    }
    
    // Less than 24 hours
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}h ago`;
    }
    
    // Format as date
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Auto-refresh scans list every 5 seconds
setInterval(() => {
    loadScans();
}, 5000);
