# Installation Guide

## Quick Start

### 1. Install uv (Python package manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your shell or run:
```bash
source $HOME/.local/bin/env
```

### 2. Install System Dependencies (macOS)

#### For Simulation Mode Only (No scanner needed)
No additional dependencies required! Just skip to step 3.

#### For Real Scanner Support
```bash
# Install SANE backends
brew install sane-backends

# Verify scanner is detected
scanimage -L
```

### 3. Install Python Dependencies
```bash
cd python-scan-4x4

# Basic installation (Pillow only)
uv sync

# OR: Full installation with scanner support
export CFLAGS="$(sane-config --cflags)"
export LDFLAGS="$(sane-config --ldflags)"
uv add python-sane
```

## Usage

### Test the Installation
```bash
# Test with simulation mode
uv run scan_and_split.py
# Press 's' + Enter when prompted

# Test scanner detection (if SANE installed)
uv run poc_scan.py
```

### Linux Installation

```bash
# 1. Install SANE
sudo apt-get update
sudo apt-get install sane sane-utils libsane-dev python3-dev

# 2. Add user to scanner group
sudo usermod -a -G scanner $USER
# Log out and back in for group changes to take effect

# 3. Verify scanner
scanimage -L

# 4. Clone and install
cd python-scan-4x4
uv sync
uv add python-sane

# 5. Test
uv run scan_and_split.py
```

## Troubleshooting

### "uv: command not found"
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
source $HOME/.local/bin/env
```

### "python-sane build failed"
This means SANE headers aren't found. Fix:

```bash
# macOS
brew install sane-backends
export CFLAGS="$(sane-config --cflags)"
export LDFLAGS="$(sane-config --ldflags)"
uv add python-sane

# Linux
sudo apt-get install libsane-dev python3-dev
uv add python-sane
```

### "No scanners detected"
1. Check scanner is powered on and connected
2. Verify with system: `scanimage -L`
3. Check permissions (Linux): `groups` should show "scanner"
4. Try running with sudo: `sudo scanimage -L`

### Scanner found but scan fails
Common causes:
- No document on scanner bed
- Scanner in standby/sleep mode (press a button on scanner to wake)
- Scanner being used by another application
- Network scanner offline (check IP address)

**Solution**: Use simulation mode by pressing 's' when prompted.

## Verification

Run the test suite:
```bash
# Test scan (simulation)
echo "s" | uv run poc_scan.py

# Test split
uv run poc_split.py scan_*.png

# Test complete workflow
echo "s" | uv run scan_and_split.py

# Check output
ls -lh output/
```

You should see 4 split images in the `output/` directory.

## What's Installed

After installation, you'll have:
- ✅ `uv` - Modern Python package manager
- ✅ `pillow` - Image processing library
- ✅ `python-sane` - Scanner interface (optional)
- ✅ Three POC scripts:
  - `poc_scan.py` - Scanner test
  - `poc_split.py` - Image splitter
  - `scan_and_split.py` - Complete workflow

## Next Steps

After successful installation:
1. Review the split images in `output/` directory
2. Test with real scanner hardware (if available)
3. See `README.md` for detailed usage examples
4. Check `docs/` for architecture and design docs

## Support

See troubleshooting guides:
- [Python-SANE Installation](PYTHON_SANE_INSTALL.md)
- [POC Guide](POC_GUIDE.md)
- [Project Plan](PROJECT_PLAN.md)
