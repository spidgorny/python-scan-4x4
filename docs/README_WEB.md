# A4 Scanner Web Interface

A modern web-based interface for scanning A4 documents and automatically extracting 2x2 photos.

## ✨ Features

- 🖱️ **One-Click Scanning** - Single button to scan documents
- 🎯 **Smart Photo Detection** - Automatic edge detection and straightening
- 📊 **Three-Panel Layout** - Sidebar, main view, and photo panel
- ⚡ **Real-Time Updates** - Auto-refresh and status polling
- 📁 **Scan History** - Browse and view all previous scans
- 🎨 **Modern UI** - Clean, responsive design

## 🚀 Quick Start

```bash
# Start the web server
./start_web.sh

# Or using uv directly
uv run python app.py
```

Then open your browser to: **http://localhost:8080**

## 📸 How It Works

1. **Click "Scan Document"**
   - Scanner starts automatically
   - Status indicator shows progress

2. **Wait for Processing**
   - Document scanned at 300 DPI
   - Smart split detects photo edges
   - Photos extracted and straightened

3. **View Results**
   - Full scan displayed in center
   - 4 extracted photos on right
   - Scan added to history

## 🎨 Interface Layout

```
┌──────────────┬────────────────────┬──────────────┐
│   Sidebar    │   Main Content     │ Photos Panel │
│              │                    │              │
│ ┌──────────┐ │ ┌────────────────┐ │ ┌──────────┐ │
│ │   SCAN   │ │ │                │ │ │ Photo 1  │ │
│ │  BUTTON  │ │ │   Scanned      │ │ └──────────┘ │
│ └──────────┘ │ │   Document     │ │ ┌──────────┐ │
│              │ │                │ │ │ Photo 2  │ │
│ Recent Scans:│ │   (Full Size)  │ │ └──────────┘ │
│ • Scan 1 ✓   │ │                │ │ ┌──────────┐ │
│ • Scan 2     │ │                │ │ │ Photo 3  │ │
│ • Scan 3     │ └────────────────┘ │ └──────────┘ │
│              │                    │ ┌──────────┐ │
│              │                    │ │ Photo 4  │ │
│              │                    │ └──────────┘ │
└──────────────┴────────────────────┴──────────────┘
```

## 🔧 API Endpoints

- `GET /` - Main web interface
- `GET /api/scans` - List all scans with photos
- `POST /api/scan` - Trigger new scan
- `GET /api/scan/status` - Check scan progress
- `GET /scans/<filename>` - Serve scanned image
- `GET /photos/<filename>` - Serve extracted photo

## 📁 File Structure

```
python-scan-4x4/
├── app.py                      # Flask web application
├── start_web.sh                # Startup script
├── templates/
│   └── index.html             # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend JavaScript
├── output/
│   └── scans/                 # Scanned documents
└── photos/                    # Extracted photos
```

## 🛠️ Technology Stack

**Backend:**
- Flask 3.1.2 - Web framework
- Python 3.13 - Runtime
- Threading - Background scan processing

**Frontend:**
- Vanilla JavaScript - No dependencies
- CSS Grid - Modern layout
- Fetch API - AJAX requests

**Integration:**
- Scanner drivers (SANE/eSCL/Windows)
- Smart split with OpenCV
- Edge detection and rotation correction

## 🌐 Network Access

Access from other devices on your network:

1. Find your IP:
   ```bash
   ifconfig | grep "inet "
   ```

2. Open from any device:
   ```
   http://<your-ip>:8080
   ```

## ⚙️ Configuration

### Change Port

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Scan Settings

Edit `app.py` in `perform_scan()`:
```python
settings = ScanSettings(
    resolution=300,              # DPI
    color_mode=ColorMode.COLOR,  # or GRAY
    format="PNG"                 # or JPEG
)
```

## 📖 Documentation

- [Web Interface Guide](WEB_INTERFACE.md) - Complete documentation
- [Smart Split Algorithm](SMART_SPLIT.md) - Edge detection details
- [Main README](../README.md) - Project overview

## 🎯 Workflow

```
User Action → Backend Processing → Frontend Update
───────────────────────────────────────────────────

1. Click "Scan" →

2. POST /api/scan →

3. Background thread:
   - Initialize scanner
   - Scan document (300 DPI)
   - Save to output/scans/
   - Run smart split
   - Extract 4 photos
   - Save to photos/ →

4. Frontend polls status:
   - GET /api/scan/status
   - When done → GET /api/scans
   - Update UI with new scan
   - Display photos

All automatic! ✨
```

## 🧪 Testing

Create test scan and view in browser:

```bash
# Generate test scan
uv run python create_test_scan.py output/scans/test.png

# Split into photos
uv run python smart_split.py output/scans/test.png

# Refresh browser to see results
```

## 🐛 Troubleshooting

### Port in Use

```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use different port
# Edit app.py and change port number
```

### Scanner Not Found

```bash
# Test scanner
uv run python poc_scan.py

# Or use simulation
uv run python simulate_scan.py
```

### Photos Not Appearing

```bash
# Check directories exist
ls output/scans/
ls photos/

# Test smart split manually
uv run python smart_split.py output/scans/scan.png --debug

# View debug image
open photos/scan_debug.png
```

## 🎨 UI Features

- **Responsive Design** - Adapts to screen size
- **Smooth Animations** - Fade in/out transitions
- **Loading States** - Spinners and disabled buttons
- **Active Highlighting** - Selected scan highlighted
- **Auto-scroll** - Keeps latest scan visible
- **Custom Scrollbars** - Styled for consistency

## 🔒 Security Note

**Development server only!**

For production:
- Use proper WSGI server (gunicorn)
- Add authentication
- Use HTTPS
- Restrict network access

## 🚧 Future Enhancements

- [ ] Click photos to enlarge
- [ ] Download individual photos
- [ ] Batch scanning mode
- [ ] Scan settings in UI
- [ ] Photo editing tools
- [ ] Export to PDF
- [ ] Mobile app version
- [ ] Dark mode
- [ ] Keyboard shortcuts

## 📄 License

Part of python-scan-4x4 project.

---

**Ready to scan!** Open http://localhost:8080 and start scanning documents! 📄 → 📷📷📷📷
