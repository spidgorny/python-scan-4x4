# Python Scan 4x4 - A4 Scanner to 2x2 Grid

A web application that scans A4 documents from a connected scanner and automatically splits them into a 2×2 grid (4 separate images).

## Project Status

✅ **Phase 1 Complete: Proof of Concept**
- Scanner POC script implemented
- Image splitting POC script implemented  
- Combined workflow script working
- Simulation mode for testing without hardware

## Quick Start

### Prerequisites

1. **Install uv** (modern Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install system dependencies** (for real scanner support):
```bash
# macOS
brew install sane-backends

# Linux (Debian/Ubuntu)
sudo apt-get install sane sane-utils libsane-dev python3-dev
```

### Installation

```bash
# Clone/navigate to project directory
cd python-scan-4x4

# Dependencies are already installed via uv
# (Pillow is included in pyproject.toml)
```

### Usage

#### 1. Scan Only (POC)
```bash
# Run scanner POC
uv run poc_scan.py

# Creates: scan_YYYYMMDD_HHMMSS.png
```

#### 2. Split Only (POC)
```bash
# Split an existing scanned image
uv run poc_split.py scan_20241128_183755.png

# Output: 4 images in output/ directory
```

#### 3. Complete Workflow (Scan + Split)
```bash
# Scan and split in one command
uv run scan_and_split.py

# Optional: specify output directory
uv run scan_and_split.py my_output/
```

## Features

### Current (Phase 1 - POC)
- ✅ Scan A4 documents at 300 DPI
- ✅ Split scanned images into 2×2 grid (4 equal parts)
- ✅ Simulation mode (works without scanner hardware)
- ✅ Cross-platform support (macOS, Linux, Windows planned)
- ✅ PNG output format with DPI metadata

### Upcoming (Phase 2-5)
- 🔲 Web interface (Flask-based)
- 🔲 Real-time scanning progress
- 🔲 Image preview and download
- 🔲 Scanner configuration UI
- 🔲 Batch scanning
- 🔲 Multiple format support (JPEG, TIFF)

## Output

### Scanned Image
- **Format**: PNG
- **Resolution**: 2480 × 3508 pixels (A4 @ 300 DPI)
- **Size**: ~100-500 KB (simulated), ~5-25 MB (real scan)

### Split Images
Each quadrant is split into equal parts:
- **Quadrant 1**: Top-left (1240 × 1754 pixels)
- **Quadrant 2**: Top-right (1240 × 1754 pixels)
- **Quadrant 3**: Bottom-left (1240 × 1754 pixels)
- **Quadrant 4**: Bottom-right (1240 × 1754 pixels)

## Project Structure

```
python-scan-4x4/
├── docs/                    # Documentation
│   ├── README.md           # Documentation index
│   ├── PROJECT_PLAN.md     # Project plan
│   ├── POC_GUIDE.md        # Scanner POC guide
│   ├── IMAGE_SPLITTING_GUIDE.md
│   └── WEB_APP_DESIGN.md
├── poc_scan.py             # Scanner POC script ✅
├── poc_split.py            # Image splitting POC script ✅
├── scan_and_split.py       # Combined workflow ✅
├── output/                 # Split images output
├── pyproject.toml          # Python dependencies
└── README.md               # This file
```

## Technology Stack

- **Python 3.13+**: Core language
- **uv**: Modern package manager (fast, reliable)
- **Pillow**: Image processing
- **SANE**: Scanner interface (Linux/macOS)
- **WIA**: Scanner interface (Windows, planned)

## Simulation Mode

The POC scripts include simulation mode that works without scanner hardware:
- Generates realistic A4 document (2480×3508 @ 300 DPI)
- Includes quadrant markers for visual verification
- Perfect for testing the splitting logic
- Useful for development without physical scanner

## Real Scanner Support

### macOS
```bash
# Install SANE
brew install sane-backends

# Add python-sane (requires SANE installed first)
uv add python-sane

# Verify scanner is detected
scanimage -L
```

### Linux
```bash
# Install SANE
sudo apt-get install sane sane-utils libsane-dev python3-dev

# Add python-sane
uv add python-sane

# Add user to scanner group
sudo usermod -a -G scanner $USER
```

### Windows
Support planned using Windows Image Acquisition (WIA).

## Examples

### Example 1: Quick Test
```bash
# Generate simulated scan and split it
uv run scan_and_split.py

# View output
ls -lh output/
```

### Example 2: Process Existing Image
```bash
# Split any existing A4 image
uv run poc_split.py my_document.png custom_output/
```

### Example 3: Real Scanner
```bash
# With SANE installed and scanner connected
uv run poc_scan.py
# Follow prompts to scan from hardware

# Then split the scan
uv run poc_split.py scan_*.png
```

## Troubleshooting

### "No scanners detected"
1. Check scanner is powered on and connected
2. Verify with system: `scanimage -L` (macOS/Linux)
3. Check permissions (may need `sudo` or scanner group)

### "python-sane not available"
This is normal on macOS without SANE installed. The script will use simulation mode. To enable real scanning:
```bash
brew install sane-backends
uv add python-sane
```

### Split images not showing quadrants correctly
The simulation includes visual markers. Real scans will split based on exact pixel dimensions.

## Documentation

See the `docs/` folder for detailed documentation:
- **PROJECT_PLAN.md**: Complete project roadmap
- **POC_GUIDE.md**: Detailed scanner POC implementation
- **IMAGE_SPLITTING_GUIDE.md**: Image processing details
- **WEB_APP_DESIGN.md**: Future web application design

## Next Steps

1. ✅ Phase 1: POC Complete
2. 🔄 Phase 2: Test with real scanner hardware
3. 📋 Phase 3: Build Flask web application
4. 📋 Phase 4: Add web UI and background tasks
5. 📋 Phase 5: Production deployment

## Contributing

This project is currently in POC phase. Focus areas:
- Testing with different scanner models
- Improving image quality handling
- Adding error handling for edge cases

## License

TBD

## Author

Created as a proof of concept for A4 document scanning and splitting workflow.
