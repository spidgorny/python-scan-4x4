# A4 Scanner to 2x2 Grid Web App - Project Plan

## Overview
A web application that scans A4 documents from a connected scanner and automatically splits them into a 2x2 grid of images (4 separate images total).

## Project Goals
1. Scan A4 documents from hardware scanner
2. Split scanned document into 2x2 grid (4 equal parts)
3. Provide web interface for scanning and viewing results
4. Save/download individual split images

## Technology Stack

### Backend
- **Python 3.10+** - Core language
- **uv** - Modern Python package manager (fast, reliable, pip/poetry compatible)
- **Flask/FastAPI** - Web framework (TBD based on requirements)
- **python-sane** or **python-escpos** - Scanner interface library
- **Pillow (PIL)** - Image processing for splitting

### Frontend
- **HTML5/CSS3/JavaScript** - Basic web interface
- **HTMX** (optional) - Dynamic updates without heavy JavaScript
- Alternative: **React/Vue** if more interactivity needed

## Project Structure
```
python-scan-4x4/
├── docs/                    # Documentation
│   ├── PROJECT_PLAN.md
│   ├── POC_GUIDE.md
│   └── API_DESIGN.md
├── src/
│   ├── scanner/            # Scanner interface module
│   ├── image_processor/    # Image splitting logic
│   ├── web/                # Web app (routes, templates)
│   └── main.py             # Entry point
├── tests/                  # Unit and integration tests
├── static/                 # CSS, JS, images
├── templates/              # HTML templates
├── output/                 # Scanned and split images
├── pyproject.toml          # uv/Python dependencies
└── README.md
```

## Development Phases

### Phase 1: Proof of Concept (POC) ✓ Current Phase
**Goal**: Create a simple CLI script that scans a document from the scanner

**Tasks**:
1. Set up uv package manager
2. Install scanner library (python-sane for Linux/macOS, WIA for Windows)
3. Create `poc_scan.py` script that:
   - Detects available scanners
   - Scans a single A4 document
   - Saves to file
4. Test with actual scanner hardware

**Deliverable**: Working `poc_scan.py` script

### Phase 2: Image Processing POC
**Goal**: Split scanned image into 2x2 grid

**Tasks**:
1. Create `poc_split.py` script using Pillow
2. Load scanned image
3. Calculate dimensions for 2x2 split
4. Crop and save 4 separate images
5. Handle different image resolutions

**Deliverable**: Working `poc_split.py` script

### Phase 3: Combined POC
**Goal**: End-to-end scanning and splitting

**Tasks**:
1. Combine scanning + splitting into single workflow
2. Add error handling
3. Add basic CLI arguments (output path, scanner selection)
4. Validate with multiple scans

**Deliverable**: `scan_and_split.py` CLI tool

### Phase 4: Web Application MVP
**Goal**: Basic web interface

**Tasks**:
1. Set up Flask/FastAPI application
2. Create simple web UI with:
   - "Scan" button
   - Progress indicator
   - Display 4 split images
   - Download buttons
3. API endpoints:
   - `POST /scan` - Trigger scan
   - `GET /status` - Check scan status
   - `GET /images/<id>` - Retrieve split images
4. Background task handling for scanning

**Deliverable**: Working web app

### Phase 5: Enhancement & Production Ready
**Goal**: Polish and deployment readiness

**Tasks**:
1. Add scanner configuration UI
2. Image history/gallery
3. Batch scanning
4. Image quality settings
5. Error handling & logging
6. Docker containerization
7. Documentation

## Technical Considerations

### Scanner Interface
- **Linux/macOS**: SANE (Scanner Access Now Easy) via `python-sane`
- **Windows**: WIA (Windows Image Acquisition) via `pywin32` or `wia-scan`
- **Cross-platform**: Consider `scanimage` CLI wrapper as fallback

### Image Processing
- **Pillow**: Standard library for image manipulation
- **Resolution handling**: A4 = 210mm × 297mm, typical scan DPI: 150-600
- **Split calculation**: 
  - Width split: image_width / 2
  - Height split: image_height / 2
  - 4 regions: top-left, top-right, bottom-left, bottom-right

### Performance
- Scanning is I/O bound (hardware dependent)
- Image processing is CPU bound but fast for single A4
- Use background tasks for web app (Celery or asyncio)

### Error Handling
- No scanner detected
- Scanner busy/in use
- Paper jam or feed errors
- Invalid image format
- Disk space issues

## Dependencies (Initial)

```toml
[project]
name = "python-scan-4x4"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pillow>=10.0.0",
    "python-sane>=2.9.1",  # Linux/macOS
    # "pywin32>=306",       # Windows alternative
]

[project.optional-dependencies]
web = [
    "flask>=3.0.0",
    # or "fastapi>=0.104.0",
    # "uvicorn>=0.24.0",
]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
]
```

## Success Criteria

### POC Phase
- [x] Script successfully detects scanner
- [x] Script scans A4 document
- [x] Image saved in standard format (PNG/JPEG)

### Full Application
- [ ] Web UI accessible via browser
- [ ] Scan triggered from web interface
- [ ] Image automatically split into 4 parts
- [ ] All 4 images downloadable
- [ ] Error messages displayed clearly
- [ ] Works with at least one common scanner model

## Timeline Estimate
- **Phase 1 (POC)**: 1-2 days
- **Phase 2 (Split POC)**: 1 day
- **Phase 3 (Combined)**: 1-2 days
- **Phase 4 (Web MVP)**: 3-5 days
- **Phase 5 (Polish)**: 3-7 days

**Total**: ~2-3 weeks for MVP

## Next Steps
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Initialize project: `uv init`
3. Create POC scanning script (see POC_GUIDE.md)
4. Test with hardware scanner
