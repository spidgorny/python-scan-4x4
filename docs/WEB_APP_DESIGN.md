# Web Application Design

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │◄───────►│  Web Server  │◄───────►│   Scanner   │
│  (Frontend) │  HTTP   │   (Flask)    │  SANE   │  Hardware   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Image     │
                        │  Processor   │
                        │  (Pillow)    │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  File System │
                        │   (Output)   │
                        └──────────────┘
```

## Technology Stack

### Backend Framework: Flask
**Rationale**: 
- Simple, lightweight
- Perfect for POC and MVP
- Easy to add async workers (Celery/RQ)
- Great template engine (Jinja2)

**Alternative**: FastAPI (if need async/websockets)

### Task Queue: None initially, then Flask-RQ or Celery
**Rationale**:
- Scanning takes 5-30 seconds
- Can't block HTTP request
- Need background job processing

### File Storage
- Local filesystem initially
- Structure: `output/<session_id>/<timestamp>/[1-4].png`

## API Design

### Endpoints

#### `GET /`
Home page with scan interface

**Response**: HTML page
```html
<!DOCTYPE html>
<html>
<head>
    <title>A4 Scanner - 2x2 Split</title>
</head>
<body>
    <h1>A4 Document Scanner</h1>
    <button id="scan-btn">Scan Document</button>
    <div id="status"></div>
    <div id="results"></div>
</body>
</html>
```

#### `POST /api/scan`
Trigger a scan operation

**Request**: 
```json
{
  "scanner_index": 0,
  "resolution": 300,
  "mode": "Color"
}
```

**Response**: 
```json
{
  "job_id": "abc123",
  "status": "queued",
  "message": "Scan started"
}
```

#### `GET /api/status/<job_id>`
Check scan job status

**Response**: 
```json
{
  "job_id": "abc123",
  "status": "completed",  // or "scanning", "processing", "failed"
  "progress": 100,
  "message": "Scan complete",
  "images": [
    "/api/images/abc123/1",
    "/api/images/abc123/2",
    "/api/images/abc123/3",
    "/api/images/abc123/4"
  ]
}
```

#### `GET /api/images/<job_id>/<index>`
Download a split image

**Response**: PNG image file

#### `GET /api/scanners`
List available scanners

**Response**:
```json
{
  "scanners": [
    {
      "index": 0,
      "name": "Epson GT-8400",
      "device": "epson2:libusb:001:005",
      "type": "flatbed scanner"
    }
  ]
}
```

## Frontend Design

### Simple HTML/CSS/JS Version

#### Main Interface
```
┌────────────────────────────────────────┐
│  A4 Document Scanner - 2x2 Split       │
├────────────────────────────────────────┤
│                                        │
│  Scanner: [Epson GT-8400        ▼]    │
│  Resolution: [300 DPI           ▼]    │
│  Mode: [Color                   ▼]    │
│                                        │
│         [  Scan Document  ]            │
│                                        │
│  Status: Ready                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                        │
├────────────────────────────────────────┤
│  Split Images:                         │
│                                        │
│  ┌────────┐  ┌────────┐               │
│  │ Top    │  │ Top    │               │
│  │ Left   │  │ Right  │               │
│  │   1    │  │   2    │               │
│  └────────┘  └────────┘               │
│    [Download]  [Download]             │
│                                        │
│  ┌────────┐  ┌────────┐               │
│  │Bottom  │  │Bottom  │               │
│  │ Left   │  │ Right  │               │
│  │   3    │  │   4    │               │
│  └────────┘  └────────┘               │
│    [Download]  [Download]             │
│                                        │
│              [Download All]            │
└────────────────────────────────────────┘
```

#### JavaScript Logic
```javascript
// Handle scan button click
async function startScan() {
    const scanBtn = document.getElementById('scan-btn');
    scanBtn.disabled = true;
    updateStatus('Starting scan...');
    
    // Start scan
    const response = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            scanner_index: 0,
            resolution: 300,
            mode: 'Color'
        })
    });
    
    const data = await response.json();
    const jobId = data.job_id;
    
    // Poll for status
    pollStatus(jobId);
}

async function pollStatus(jobId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/status/${jobId}`);
        const data = await response.json();
        
        updateStatus(data.message);
        updateProgress(data.progress);
        
        if (data.status === 'completed') {
            clearInterval(interval);
            displayImages(data.images);
            document.getElementById('scan-btn').disabled = false;
        } else if (data.status === 'failed') {
            clearInterval(interval);
            showError(data.message);
            document.getElementById('scan-btn').disabled = false;
        }
    }, 1000);  // Poll every second
}
```

## Backend Implementation

### Flask App Structure

```python
# app.py
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['OUTPUT_DIR'] = Path('output')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# In-memory job storage (use Redis for production)
jobs = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scanners', methods=['GET'])
def list_scanners():
    from scanner_module import get_available_scanners
    scanners = get_available_scanners()
    return jsonify({'scanners': scanners})

@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.json
    job_id = str(uuid.uuid4())
    
    # Create job
    jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'message': 'Scan queued'
    }
    
    # Start background task
    from tasks import scan_and_split_task
    scan_and_split_task.delay(job_id, data)
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Scan started'
    })

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])

@app.route('/api/images/<job_id>/<int:index>', methods=['GET'])
def get_image(job_id, index):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    if 'images' not in jobs[job_id]:
        return jsonify({'error': 'No images available'}), 404
    
    if index < 1 or index > 4:
        return jsonify({'error': 'Invalid index'}), 400
    
    image_path = jobs[job_id]['images'][index - 1]
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Background Task Worker

```python
# tasks.py
from scanner_module import scan_document
from image_processor import split_image_2x2
from pathlib import Path

def scan_and_split_task(job_id, config):
    """Background task for scanning and splitting."""
    from app import jobs, app
    
    try:
        # Update status
        jobs[job_id]['status'] = 'scanning'
        jobs[job_id]['progress'] = 10
        jobs[job_id]['message'] = 'Scanning document...'
        
        # Scan
        output_dir = Path(app.config['OUTPUT_DIR']) / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        scanned_file = scan_document(
            output_path=output_dir / 'scanned.png',
            scanner_index=config.get('scanner_index', 0),
            resolution=config.get('resolution', 300)
        )
        
        # Update status
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 50
        jobs[job_id]['message'] = 'Splitting image...'
        
        # Split
        split_files = split_image_2x2(
            scanned_file,
            output_dir=output_dir
        )
        
        # Update status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['message'] = 'Scan complete'
        jobs[job_id]['images'] = [str(f) for f in split_files]
        
        # Clean up original scan
        scanned_file.unlink()
        
    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['message'] = str(e)
```

## Deployment

### Development
```bash
# Install dependencies
uv add flask pillow python-sane

# Run development server
uv run python app.py
```

### Production (with Gunicorn)
```bash
# Install production server
uv add gunicorn

# Run
uv run gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sane sane-utils libsane-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Install dependencies
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## Security Considerations

1. **File Upload Limits**: Set MAX_CONTENT_LENGTH
2. **Path Traversal**: Validate job_id and file paths
3. **Rate Limiting**: Prevent scanner abuse
4. **Authentication**: Add if needed (Flask-Login)
5. **HTTPS**: Use reverse proxy (nginx) with SSL

## Next Steps

1. Implement POC scripts (scan + split)
2. Create Flask app with basic routes
3. Build HTML/JS frontend
4. Add background task processing
5. Test with real scanner
6. Add error handling and logging
7. Deploy and iterate
