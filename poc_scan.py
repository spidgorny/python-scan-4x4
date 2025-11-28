#!/usr/bin/env python3
"""
Proof of Concept: Scan A4 Document from Scanner
Usage: python poc_scan.py

This POC requires a physical scanner connected via SANE.
For simulation mode, use: python simulate_scan.py
"""

import sys
from datetime import datetime
from pathlib import Path

try:
    import sane
    USE_SANE = True
except ImportError:
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
        print("SANE not available. Install with:")
        print("  macOS: brew install sane-backends && uv add python-sane")
        print("  Linux: sudo apt-get install sane libsane-dev && uv add python-sane")
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
        # Set source to Flatbed (not ADF/feeder)
        # This ensures we use the flatbed scanner, not the document feeder
        if 'source' in scanner.opt:
            try:
                # Get available sources
                available_sources = scanner.opt['source'].constraint
                print(f"  Available sources: {available_sources}")
                
                # Check if option is active (some scanners auto-select if only one source)
                if scanner.opt['source'].is_active():
                    # Try to set to Flatbed (prefer flatbed over ADF)
                    # Common names: 'Flatbed', 'FlatBed', 'Platen', 'Normal'
                    flatbed_names = ['Flatbed', 'FlatBed', 'Platen', 'Normal']
                    
                    source_set = False
                    for source_name in flatbed_names:
                        if source_name in available_sources:
                            try:
                                scanner.source = source_name
                                print(f"  Source: {scanner.source} ✓")
                                source_set = True
                                break
                            except AttributeError:
                                # Option might not be settable
                                pass
                    
                    if not source_set and available_sources:
                        # Just use the first available source
                        try:
                            scanner.source = available_sources[0]
                            print(f"  Source: {scanner.source} (auto-selected)")
                        except AttributeError:
                            print(f"  Source: {available_sources[0]} (read-only)")
                else:
                    # Option is inactive - scanner probably only has one source
                    if len(available_sources) == 1:
                        print(f"  Source: {available_sources[0]} (auto-selected)")
                    else:
                        print(f"  Source: Auto-detected (inactive option)")
                    
            except Exception as e:
                print(f"  Source: Could not configure ({e})")
        else:
            print("  Source: Not configurable (using default)")
        
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
        raise RuntimeError("WIA not available. Install with: uv add pywin32")
    
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
        print("\n✗ ERROR: No scanning library available!")
        print("\nInstall dependencies:")
        print("  Linux/macOS: brew install sane-backends && uv add python-sane")
        print("  Windows: uv add pywin32")
        print("\nOr use simulation mode:")
        print("  uv run simulate_scan.py")
        sys.exit(1)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"scan_{timestamp}.png"
    
    try:
        if USE_SANE:
            # List available scanners first
            devices = list_scanners()
            if not devices:
                print("\n✗ ERROR: No scanners detected!")
                print("\nTroubleshooting:")
                print("  1. Check scanner is powered on and connected")
                print("  2. Run: scanimage -L")
                print("  3. Check permissions (may need sudo)")
                print("\nOr use simulation mode:")
                print("  uv run simulate_scan.py")
                sys.exit(1)
            
            # Use first scanner by default
            print("\nUsing first scanner (index 0)")
            print("Press Ctrl+C to cancel, or Enter to continue...")
            input()
            
            try:
                scan_document_sane(output_path, device_index=0)
            except Exception as scan_error:
                print(f"\n✗ Scanner error: {scan_error}")
                print("\nPossible reasons:")
                print("  - No document on scanner bed")
                print("  - Scanner is in standby/power save mode")
                print("  - Scanner is being used by another application")
                print("  - Connection issue")
                print("\nTry simulation mode instead:")
                print("  uv run simulate_scan.py")
                sys.exit(1)
        
        elif USE_WIA:
            scan_document_wia(output_path)
        
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
