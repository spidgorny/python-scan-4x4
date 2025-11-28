# Python-SANE Installation Guide

## Issue
When running `uv add python-sane` on macOS, the build fails with:
```
fatal error: 'sane/sane.h' file not found
```

## Root Cause
The `python-sane` package needs to compile C extensions that link against the SANE library. Even though SANE is installed via Homebrew, the build process doesn't automatically find the include paths.

## Solution

### 1. Install SANE backends first
```bash
brew install sane-backends
```

### 2. Set compiler flags
```bash
export CFLAGS="-I/opt/homebrew/Cellar/sane-backends/1.4.0_1/include"
export LDFLAGS="-L/opt/homebrew/Cellar/sane-backends/1.4.0_1/lib"
```

**Note**: Adjust the version number (`1.4.0_1`) to match your installed version. Check with:
```bash
ls /opt/homebrew/Cellar/sane-backends/
```

### 3. Install python-sane
```bash
uv add python-sane
```

## Alternative: Use sane-config
For a version-independent solution:
```bash
export CFLAGS="$(sane-config --cflags)"
export LDFLAGS="$(sane-config --ldflags)"
uv add python-sane
```

## Verification

Test that python-sane is working:
```bash
uv run python -c "import sane; sane.init(); print('✓ SANE initialized'); devices = sane.get_devices(); print(f'Scanners: {len(devices)}'); sane.exit()"
```

## Scanner Detection

The POC scripts now support:
- ✅ **Real scanner hardware** (via SANE)
- ✅ **Simulation mode** (when no scanner available)
- ✅ **Graceful fallback** on scanner errors

### Scanner Found
If a scanner is detected, you'll see:
```
Found 1 scanner(s):
  [0] epson2:net:192.168.1.208 - Epson (PID)

Press Enter to start scanning (or Ctrl+C to cancel)...
(Or type 's' + Enter to use simulation mode)
```

### No Scanner
If no scanner is found, it automatically falls back to simulation mode.

### Scanner Errors
Common scanner errors and their fixes:
- **"Error during device I/O"**: No document on scanner bed, or scanner in standby
- **Timeout**: Scanner may be offline or unpowered
- **Permission denied**: Add user to scanner group (Linux only)

## Platform Notes

### macOS
- SANE installed via Homebrew
- Headers in `/opt/homebrew/Cellar/sane-backends/*/include/`
- Libraries in `/opt/homebrew/Cellar/sane-backends/*/lib/`

### Linux
```bash
# Install SANE
sudo apt-get install sane sane-utils libsane-dev python3-dev

# Add user to scanner group
sudo usermod -a -G scanner $USER

# Install python-sane
uv add python-sane
```

### Windows
Not yet implemented. Will use WIA (Windows Image Acquisition) in future version.

## References
- [SANE Project](http://www.sane-project.org/)
- [python-sane on PyPI](https://pypi.org/project/python-sane/)
- [Homebrew SANE backends](https://formulae.brew.sh/formula/sane-backends)
