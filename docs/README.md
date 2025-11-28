# Documentation Index

Welcome to the **python-scan-4x4** documentation!

## Overview
This project is a web application that scans A4 documents from a hardware scanner and automatically splits them into a 2×2 grid (4 separate images).

## Documentation Files

### 1. [PROJECT_PLAN.md](PROJECT_PLAN.md)
Complete project plan including:
- Project overview and goals
- Technology stack decisions
- Project structure
- Development phases (5 phases)
- Timeline estimates
- Success criteria

**Start here** for the big picture.

### 2. [POC_GUIDE.md](POC_GUIDE.md)
Proof of concept guide for the scanner script:
- Installation instructions for uv (modern Python package manager)
- System dependencies (SANE for Linux/macOS, WIA for Windows)
- Complete `poc_scan.py` script
- Setup and usage instructions
- Troubleshooting common scanner issues

**Use this** to get the scanner working.

### 3. [IMAGE_SPLITTING_GUIDE.md](IMAGE_SPLITTING_GUIDE.md)
Guide for splitting scanned images into 2×2 grid:
- Algorithm explanation
- Complete `poc_split.py` script
- Advanced features (overlap, margins, quality control)
- Testing checklist
- Performance notes

**Use this** to implement image splitting.

### 4. [WEB_APP_DESIGN.md](WEB_APP_DESIGN.md)
Web application architecture and design:
- System architecture diagram
- API endpoint specifications
- Frontend design mockup
- Backend implementation (Flask)
- Background task processing
- Deployment options (development, production, Docker)
- Security considerations

**Use this** to build the web interface.

## Quick Start

### Phase 1: Scanner POC (Current)
```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Initialize project
cd python-scan-4x4
uv init

# 3. Add dependencies
uv add pillow python-sane

# 4. Create and run POC script
# (See POC_GUIDE.md for complete script)
uv run poc_scan.py
```

### Phase 2: Image Splitting
```bash
# Run splitting script
uv run poc_split.py scan_20251128_172859.png
```

### Phase 3: Combined Workflow
```bash
# Scan and split in one command
uv run scan_and_split.py
```

### Phase 4: Web Application
```bash
# Add web dependencies
uv add flask

# Run web server
uv run python app.py
```

## Project Status

- [x] Project planning complete
- [x] Documentation created
- [ ] Scanner POC implemented
- [ ] Image splitting POC implemented
- [ ] Combined workflow
- [ ] Web application MVP
- [ ] Production deployment

## Technology Stack

- **Python 3.10+**: Core language
- **uv**: Modern Python package manager
- **SANE/WIA**: Scanner interface
- **Pillow**: Image processing
- **Flask**: Web framework (planned)

## Repository Structure

```
python-scan-4x4/
├── docs/                       # ← You are here
│   ├── README.md              # This file
│   ├── PROJECT_PLAN.md        # Overall project plan
│   ├── POC_GUIDE.md           # Scanner POC guide
│   ├── IMAGE_SPLITTING_GUIDE.md  # Splitting guide
│   └── WEB_APP_DESIGN.md      # Web app architecture
├── src/                       # Source code (TBD)
├── tests/                     # Tests (TBD)
├── output/                    # Scanned images (TBD)
├── pyproject.toml            # Dependencies (TBD)
└── README.md                 # Main README (TBD)
```

## Support

### Common Issues
See [POC_GUIDE.md](POC_GUIDE.md#troubleshooting) for scanner troubleshooting.

### References
- [SANE Project](http://www.sane-project.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Contributing

This is currently in POC/planning phase. Focus on:
1. Getting scanner POC working
2. Testing image splitting
3. Building MVP web interface

## License

TBD
