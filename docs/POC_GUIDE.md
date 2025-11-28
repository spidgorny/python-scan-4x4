# Proof of Concept - Scanner Script Guide

## Objective
Create a simple Python script that scans an A4 document from a connected scanner when executed.

## Prerequisites

### 1. Install uv (Modern Python Package Manager)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. System Dependencies

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install sane sane-utils libsane-dev
sudo apt-get install python3-dev  # For building python-sane
```

#### macOS
```bash
brew install sane-backends
```

#### Windows
- No SANE required; will use WIA (Windows Image Acquisition)
- Ensure scanner drivers are installed

### 3. Verify Scanner Connection
```bash
# Linux/macOS - List available scanners
scanimage -L

# Should output something like:
# device `epson2:libusb:001:005' is a Epson GT-8400 flatbed scanner
```

## POC Script Implementation

### Script: `poc_scan.py`

```python
#!/usr/bin/env python3
"""
Proof of Concept: Scan A4 Document from Scanner
Usage: python poc_scan.py
"""

import sys
from datetime import datetime
from pathlib import Path

try:
    import sane
    USE_SANE = True
except ImportError:
    print("Warning: python-sane not available")
    USE_SANE = False

# Alternative for Windows
try:
    import win32com.client
    USE_WIA = True
except ImportError:
    USE_WIA = False


def list_scanners():
    """List all available scanners."""
    if not USE_SANE:
        print("SANE not available. Install with: uv pip install python-sane")
        return []
    
    sane.init()
    devices = sane.get_devices()
    
    if not devices:
        print("No scanners detected!")
        print("Troubleshooting:")
        print("  1. Check scanner is powered on and connected")
        print("  2. Run: scanimage -L")
        print("  3. Check permissions (may need sudo)")
        return []
    
    print(f"Found {len(devices)} scanner(s):")
    for i, dev in enumerate(devices):
        print(f"  [{i}] {dev[0]} - {dev[1]} ({dev[2]})")
    
    return devices


def scan_document_sane(output_path="scanned_document.png", device_index=0):
    """
    Scan a document using SANE (Linux/macOS).
    
    Args:
        output_path: Where to save the scanned image
        device_index: Index of scanner to use (from list_scanners)
    """
    sane.init()
    devices = sane.get_devices()
    
    if not devices:
        raise RuntimeError("No scanner found")
    
    if device_index >= len(devices):
        raise ValueError(f"Invalid device index {device_index}")
    
    device_name = devices[device_index][0]
    print(f"\nOpening scanner: {device_name}")
    
    scanner = sane.open(device_name)
    
    # Configure scanner for A4 document
    # A4 size: 210mm x 297mm
    print("Configuring scanner...")
    
    try:
        # Set mode to color (or 'Gray' for grayscale, 'Lineart' for B&W)
        scanner.mode = 'Color'
        
        # Set resolution (DPI) - higher = better quality but larger file
        scanner.resolution = 300  # 300 DPI is good balance
        
        # Set scan area to A4 (if supported)
        # Note: Not all scanners support these options
        # scanner.tl_x = 0    # Top-left X
        # scanner.tl_y = 0    # Top-left Y
        # scanner.br_x = 210  # Bottom-right X (210mm for A4 width)
        # scanner.br_y = 297  # Bottom-right Y (297mm for A4 height)
        
        print(f"  Mode: {scanner.mode}")
        print(f"  Resolution: {scanner.resolution} DPI")
        
    except AttributeError as e:
        print(f"  Warning: Could not set some options: {e}")
    
    # Start scanning
    print("\nScanning... Please wait.")
    print("(Ensure document is placed on scanner bed)")
    
    scanner.start()
    image = scanner.snap()
    
    # Save image
    output_file = Path(output_path)
    image.save(output_file)
    
    scanner.close()
    sane.exit()
    
    print(f"\n✓ Scan complete!")
    print(f"  Saved to: {output_file.absolute()}")
    print(f"  Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"  Dimensions: {image.size[0]} x {image.size[1]} pixels")
    
    return output_file


def scan_document_wia(output_path="scanned_document.png"):
    """
    Scan a document using WIA (Windows).
    
    Args:
        output_path: Where to save the scanned image
    """
    if not USE_WIA:
        raise RuntimeError("WIA not available. Install with: uv pip install pywin32")
    
    print("Using Windows Image Acquisition (WIA)...")
    
    # Create WIA device manager
    device_manager = win32com.client.Dispatch("WIA.DeviceManager")
    
    # Get first available scanner
    if device_manager.DeviceInfos.Count == 0:
        raise RuntimeError("No scanner found")
    
    device_info = device_manager.DeviceInfos[1]
    print(f"Using scanner: {device_info.Properties('Name').Value}")
    
    # Connect to scanner
    device = device_info.Connect()
    
    # Scan
    print("\nScanning... Please wait.")
    item = device.Items[1]
    
    # Configure (optional)
    # item.Properties("6146").Value = 4  # Color mode
    # item.Properties("6147").Value = 300  # Resolution
    
    image = item.Transfer("{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}")  # PNG format
    
    # Save
    output_file = Path(output_path)
    image.SaveFile(str(output_file.absolute()))
    
    print(f"\n✓ Scan complete!")
    print(f"  Saved to: {output_file.absolute()}")
    
    return output_file


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Document Scanner - Proof of Concept")
    print("=" * 60)
    
    # Check which scanning method is available
    if not USE_SANE and not USE_WIA:
        print("\nERROR: No scanning library available!")
        print("\nInstall dependencies:")
        print("  Linux/macOS: uv pip install python-sane")
        print("  Windows: uv pip install pywin32")
        sys.exit(1)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"scan_{timestamp}.png"
    
    try:
        if USE_SANE:
            # List available scanners first
            devices = list_scanners()
            if not devices:
                sys.exit(1)
            
            # Use first scanner by default
            print("\nUsing first scanner (index 0)")
            print("Press Ctrl+C to cancel, or Enter to continue...")
            input()
            
            scan_document_sane(output_path, device_index=0)
        
        elif USE_WIA:
            scan_document_wia(output_path)
        
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Error during scan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Setup and Usage

### 1. Initialize Project
```bash
cd python-scan-4x4

# Initialize with uv
uv init

# Add dependencies
uv add pillow
uv add python-sane  # Linux/macOS
# OR
uv add pywin32      # Windows
```

### 2. Create POC Script
```bash
# Copy the poc_scan.py script above into the project root
```

### 3. Run the POC
```bash
# Run with uv
uv run poc_scan.py

# Or activate venv and run
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
python poc_scan.py
```

### 4. Expected Output
```
============================================================
A4 Document Scanner - Proof of Concept
============================================================
Found 1 scanner(s):
  [0] epson2:libusb:001:005 - Epson GT-8400 (flatbed scanner)

Using first scanner (index 0)
Press Ctrl+C to cancel, or Enter to continue...

Opening scanner: epson2:libusb:001:005
Configuring scanner...
  Mode: Color
  Resolution: 300 DPI

Scanning... Please wait.
(Ensure document is placed on scanner bed)

✓ Scan complete!
  Saved to: /path/to/scan_20251128_172859.png
  Size: 24.56 MB
  Dimensions: 2480 x 3508 pixels
```

## Troubleshooting

### "No scanners detected"
1. Check scanner is powered on and connected via USB
2. Check scanner appears in system:
   - Linux: `lsusb` should show scanner
   - macOS: System Preferences → Printers & Scanners
   - Windows: Device Manager → Imaging Devices
3. Test with system tool: `scanimage -L`
4. Check permissions: May need to run with `sudo`

### "Permission denied"
```bash
# Linux: Add user to scanner group
sudo usermod -a -G scanner $USER
# Log out and back in
```

### "Module 'sane' not found"
```bash
# Install system dependencies first
sudo apt-get install libsane-dev python3-dev

# Then install Python package
uv pip install python-sane
```

### Scanner locks up
```bash
# Reset scanner connection
sudo scanimage -L
# Or restart SANE daemon
sudo systemctl restart saned
```

## Next Steps
Once POC is working:
1. Create `poc_split.py` to split scanned image into 2x2 grid
2. Combine both into single workflow
3. Add error handling and configuration options
4. Build web interface

## Reference Links
- [SANE Documentation](http://www.sane-project.org/)
- [python-sane PyPI](https://pypi.org/project/python-sane/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [uv Documentation](https://github.com/astral-sh/uv)

## Scanner Source Selection (Flatbed vs ADF)

### Feature: Automatic Flatbed Selection

The POC scripts automatically select the **Flatbed** (glass platen) source when scanning, rather than the ADF (Automatic Document Feeder). This is important for scanners with multiple scanning sources.

#### Why Flatbed?

Flatbed scanning is preferred for the 2x2 split use case because:
- ✅ Better for single documents, photos, and books
- ✅ Higher quality scans (no paper feed mechanism)
- ✅ Suitable for A4 documents that will be split
- ✅ No risk of paper jams or misfeeds

#### How It Works

The POC automatically:
1. Checks if scanner has a `source` option
2. Lists available sources (e.g., `['Flatbed', 'ADF', 'ADF Duplex']`)
3. Attempts to set source to one of:
   - `Flatbed`
   - `FlatBed` (some manufacturers)
   - `Platen`
   - `Normal`
4. Falls back to first available source if Flatbed not found
5. Handles inactive/auto-selected sources gracefully

#### Example Output

```
Configuring scanner...
  Available sources: ['Flatbed', 'ADF']
  Source: Flatbed ✓
  Mode: Color
  Resolution: 300 DPI
```

Or with auto-selection:

```
Configuring scanner...
  Available sources: ['Flatbed']
  Source: Flatbed (auto-selected)
  Mode: Color
  Resolution: 300 DPI
```

#### Testing Scanner Sources

Use the test script to see your scanner's available sources:

```bash
uv run python test_source_selection.py
```

This will show:
- Available sources
- Which source will be selected
- Whether option is active or auto-selected
- Other scanner capabilities (ADF mode, duplex, etc.)

#### Scanner Types

**Single-source scanners** (Flatbed only):
- Option is inactive (auto-selected)
- POC reports: "Flatbed (auto-selected)"
- No configuration needed

**Multi-source scanners** (Flatbed + ADF):
- Option is active and settable
- POC will explicitly set to Flatbed
- Prevents accidental ADF usage

**ADF-only scanners** (rare):
- Will use ADF as only source
- May require manual feed for each scan

#### Future Enhancements

For production use, consider adding:
- Command-line option to choose source: `--source flatbed|adf`
- Batch scanning support for ADF
- Auto-detect paper in feeder vs flatbed
- Duplex scanning for two-sided documents

#### Troubleshooting

**"Source: Not configurable"**
- Scanner doesn't have source selection
- Will use default source (usually Flatbed)

**"Source: Could not configure"**
- Option exists but failed to set
- Check scanner permissions
- Scanner may not support SANE source selection

**Using ADF instead of Flatbed**
- Check available sources with test script
- Verify Flatbed is in the list
- May need scanner firmware update

