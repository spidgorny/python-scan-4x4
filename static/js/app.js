// App State
let currentScan = null;
let scans = [];

// DOM Elements
const scanBtn = document.getElementById('scanBtn');
const splitBtn = document.getElementById('splitBtn');
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
        scansList.innerHTML = '<p class="text-gray-400 text-sm">No scans yet</p>';
        return;
    }
    
    scansList.innerHTML = scans.map(scan => `
        <div class="p-3 rounded-lg cursor-pointer transition duration-150 ${currentScan?.filename === scan.filename ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 hover:bg-gray-100 border border-transparent'}"
             onclick="selectScanByFilename('${scan.filename}')">
            <div class="font-medium text-sm text-gray-800 truncate">${scan.filename}</div>
            <div class="text-xs text-gray-500 mt-1">${formatTime(scan.timestamp)}</div>
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
    
    // Show split button
    splitBtn.classList.remove('hidden');
}

// Display scan
function displayScan(scan) {
    scanInfo.textContent = scan.filename;
    scanView.innerHTML = `<div class="flex justify-center items-center h-full"><img src="${scan.path}" alt="Scanned document" class="max-w-full max-h-full object-contain shadow-lg"></div>`;
}

// Display photos
function displayPhotos(scan) {
    photosGrid.innerHTML = '';
    
    for (let i = 0; i < 4; i++) {
        const slot = document.createElement('div');
        slot.className = 'aspect-square rounded-lg overflow-hidden';
        
        if (i < scan.photos.length) {
            slot.innerHTML = `<img src="${scan.photos[i]}" alt="Photo ${i + 1}" class="w-full h-full object-cover">`;
        } else {
            slot.innerHTML = `<div class="w-full h-full bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center"><span class="text-3xl font-light text-gray-400">${i + 1}</span></div>`;
        }
        
        photosGrid.appendChild(slot);
    }
    
    photoCount.textContent = `${scan.photos.length}/4`;
}

// Trigger split
splitBtn.addEventListener('click', async () => {
    if (!currentScan || splitBtn.disabled) {
        return;
    }
    
    try {
        splitBtn.disabled = true;
        splitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> <span>Splitting...</span>';
        
        const response = await fetch('/api/split', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: currentScan.filename })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Split error: ' + data.error);
        } else {
            // Reload scans to update photos
            await loadScans();
            const updatedScan = scans.find(s => s.filename === currentScan.filename);
            if (updatedScan) {
                selectScan(updatedScan);
            }
        }
    } catch (error) {
        console.error('Error splitting photos:', error);
        alert('Failed to split photos: ' + error.message);
    } finally {
        splitBtn.disabled = false;
        splitBtn.innerHTML = '<span>✂️</span> <span>Split Photos</span>';
    }
});

// Trigger scan
scanBtn.addEventListener('click', async () => {
    console.log('Scan button clicked');
    if (scanBtn.disabled) {
        console.log('Button is disabled, ignoring click');
        return;
    }
    
    try {
        scanBtn.disabled = true;
        scanStatus.classList.remove('hidden');
        console.log('Sending scan request to /api/scan');
        
        const response = await fetch('/api/scan', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.error) {
            alert(data.error);
            scanBtn.disabled = false;
            scanStatus.classList.add('hidden');
        } else {
            console.log('Scan started successfully');
        }
    } catch (error) {
        console.error('Error starting scan:', error);
        alert('Failed to start scan: ' + error.message);
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
