# Web Interface Documentation

## Overview

The A4 Scanner web interface provides a user-friendly browser-based UI for scanning documents and viewing extracted photos.

## Architecture

### Three-Panel Layout

```
┌────────────┬──────────────────┬────────────┐
│  Sidebar   │  Main Content    │   Photos   │
│            │                  │   Panel    │
│  - Scan    │  Full Scanned    │            │
│    Button  │  Document        │   Photo 1  │
│            │                  │            │
│  - Scans   │                  │   Photo 2  │
│    List    │                  │            │
│            │                  │   Photo 3  │
│            │                  │            │
│            │                  │   Photo 4  │
└────────────┴──────────────────┴────────────┘
```

### Components

#### 1. Sidebar (Left Panel)
- **Scan Button** - Triggers new scan
- **Scans List** - Shows all previous scans
  - Click to view
  - Shows filename and timestamp
  - Active scan highlighted

#### 2. Main Content (Center)
- **Full Scanned Document** - Shows complete A4 scan
- **Zoom/Pan** - View full resolution
- **Scan Info** - Filename and metadata

#### 3. Photos Panel (Right)
- **4 Photo Slots** - Shows extracted photos
- **Photo Counter** - "X/4 photos"
- **Thumbnails** - Click to enlarge (future)

## Technology Stack

### Backend
- **Flask 3.1.2** - Web framework
- **Python 3.13** - Runtime
- **Threading** - Background scan processing

### Frontend
- **Vanilla JavaScript** - No frameworks
- **CSS Grid** - Responsive layout
- **Fetch API** - REST communication

### File Structure

```
python-scan-4x4/
├── app.py                      # Flask application
├── start_web.sh                # Startup script
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend logic
├── output/
│   └── scans/                 # Scanned documents
└── photos/                    # Extracted photos
```

## API Endpoints

### GET `/`
Main application page

**Response:** HTML page

### GET `/api/scans`
List all scanned documents

**Response:**
```json
[
  {
    "filename": "scan_20241128_190000.png",
    "path": "/scans/scan_20241128_190000.png",
    "timestamp": 1764358432.816,
    "photos": [
      "/photos/scan_20241128_190000_photo1.png",
      "/photos/scan_20241128_190000_photo2.png",
      "/photos/scan_20241128_190000_photo3.png",
      "/photos/scan_20241128_190000_photo4.png"
    ]
  }
]
```

### POST `/api/scan`
Trigger new scan

**Response:**
```json
{
  "status": "started"
}
```

**Errors:**
```json
{
  "error": "Scan already in progress"
}
```

### GET `/api/scan/status`
Check scan progress

**Response:**
```json
{
  "in_progress": false
}
```

### GET `/scans/<filename>`
Serve scanned image

**Response:** PNG image

### GET `/photos/<filename>`
Serve extracted photo

**Response:** PNG image

## Usage

### Starting the Server

```bash
# Method 1: Using startup script
./start_web.sh

# Method 2: Direct command
uv run python app.py

# Method 3: With custom port
FLASK_RUN_PORT=9000 uv run python app.py
```

### Accessing the Interface

Open browser to:
```
http://localhost:8080
```

Or from other devices on network:
```
http://<your-ip>:8080
```

### Scanning Workflow

1. **Click "Scan Document"**
   - Scanner starts automatically
   - Button disabled during scan
   - Status indicator shows progress

2. **Wait for Scan**
   - Scanner acquires image
   - Smart split processes photos
   - Photos extracted automatically

3. **View Results**
   - Scan appears in sidebar
   - Full scan shown in center
   - Photos appear in right panel

4. **Browse History**
   - Click any scan in sidebar
   - View previous scans
   - See all extracted photos

## Features

### Real-Time Updates

- **Auto-refresh** - Scans list updates every 5 seconds
- **Status polling** - Checks scan progress every 2 seconds
- **Instant feedback** - New scans appear immediately

### Responsive Design

- **Three-column layout** - Optimized for desktop
- **Scrollable panels** - Independent scroll areas
- **Adaptive sizing** - Content scales to fit

### Visual Feedback

- **Active states** - Selected scan highlighted
- **Loading states** - Spinner during scan
- **Disabled states** - Button disabled when busy
- **Animations** - Smooth transitions

## Configuration

### Port Settings

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Directory Paths

Edit `app.py`:
```python
SCANS_DIR = Path("output/scans")
PHOTOS_DIR = Path("photos")
```

### Scanner Settings

Edit `app.py` in `perform_scan()`:
```python
settings = ScanSettings(
    resolution=300,    # DPI
    color_mode=ColorMode.COLOR,
    format="PNG"
)
```

## Development

### Debug Mode

The app runs in debug mode by default:
- Auto-reload on code changes
- Detailed error pages
- Debug console

### Adding Features

**Example: Add scan delete**

1. Add endpoint:
```python
@app.route('/api/scan/<filename>', methods=['DELETE'])
def delete_scan(filename):
    scan_path = SCANS_DIR / filename
    scan_path.unlink()
    return jsonify({'status': 'deleted'})
```

2. Add frontend:
```javascript
async function deleteScan(filename) {
    await fetch(`/api/scan/${filename}`, { method: 'DELETE' });
    loadScans();
}
```

3. Add UI button:
```html
<button onclick="deleteScan('scan.png')">🗑️</button>
```

## Deployment

### Production Setup

**NOT recommended for public internet!**

For production use:

1. **Use WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

2. **Add authentication:**
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
```

3. **Use HTTPS:**
```bash
gunicorn --certfile=cert.pem --keyfile=key.pem app:app
```

### Local Network Access

To access from other devices:

1. Find your IP:
```bash
ifconfig | grep "inet "
```

2. Allow firewall:
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python)
```

3. Access from device:
```
http://192.168.1.223:8080
```

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process
lsof -ti:8080

# Kill process
kill -9 $(lsof -ti:8080)

# Or use different port
# Edit app.py and change port number
```

### Scanner Not Found

**Error:** No scanner available

**Solutions:**
1. Check scanner is connected
2. Test with command line: `uv run python poc_scan.py`
3. Use simulation mode: `uv run python simulate_scan.py`

### Photos Not Appearing

**Cause:** Smart split failed

**Solutions:**
1. Check `photos/` directory exists
2. View debug image: `photos/*_debug.png`
3. Try manual split: `uv run python smart_split.py scan.png`

### Slow Performance

**Causes:**
- Large image files
- Slow scanner
- CPU-intensive processing

**Solutions:**
1. Reduce resolution in settings
2. Use faster scanner driver
3. Disable debug mode

## Browser Compatibility

**Tested:**
- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Safari 17+
- ✅ Edge 120+

**Required features:**
- Fetch API
- CSS Grid
- ES6 JavaScript

## Future Enhancements

- [ ] Click photos to enlarge
- [ ] Download individual photos
- [ ] Batch scanning
- [ ] Scan settings UI
- [ ] Photo rotation/cropping
- [ ] Export as PDF
- [ ] Share via email
- [ ] Mobile responsive layout
- [ ] Dark mode
- [ ] Keyboard shortcuts

## License

Part of python-scan-4x4 project.
