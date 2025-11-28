#!/usr/bin/env python3
"""
Proof of Concept: Scan A4 Document from Scanner
Usage: python poc_scan.py

Uses eSCL driver for reliable scanning.
"""

import sys
from datetime import datetime
from pathlib import Path

from scanners import ScannerManager, ScanSettings, ColorMode


def main():
    """Main entry point"""
    print("=" * 60)
    print("A4 Document Scanner - Proof of Concept")
    print("=" * 60)
    print()
    
    # Initialize scanner manager
    manager = ScannerManager()
    
    # List all scanners
    all_scanners = manager.list_all_scanners()
    
    if not all_scanners:
        print("✗ No scanners detected!")
        print("\nTroubleshooting:")
        print("  1. Check scanner is powered on and connected")
        print("  2. Check network connection (for network scanners)")
        print("  3. Install drivers:")
        print("     - macOS/Linux: brew install sane-backends")
        print("     - Windows: Install scanner manufacturer drivers")
        sys.exit(1)
    
    # Filter out simulation scanner for POC
    real_scanners = [s for s in all_scanners if s.driver != "simulation"]
    
    if not real_scanners:
        print("✗ No physical scanners detected!")
        print("  Only simulation scanner available.")
        print("\nUse 'uv run python simulate_scan.py' for testing.")
        sys.exit(1)
    
    # Display available scanners
    print(f"Found {len(real_scanners)} scanner(s):")
    for i, scanner in enumerate(real_scanners):
        print(f"  [{i}] {scanner.name}")
        print(f"      Driver: {scanner.driver}")
        print(f"      ID: {scanner.id}")
        if scanner.connection:
            print(f"      Connection: {scanner.connection}")
        print()
    
    # Select first real scanner (prefer eSCL)
    selected_scanner = None
    
    # Try to find eSCL scanner first
    for scanner in real_scanners:
        if scanner.driver.lower() == "escl":
            selected_scanner = scanner
            print(f"Using scanner: {scanner.name} (eSCL driver)")
            break
    
    # Fallback to first available
    if selected_scanner is None:
        selected_scanner = real_scanners[0]
        print(f"Using scanner: {selected_scanner.name} ({selected_scanner.driver} driver)")
    
    print()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"scan_{timestamp}.png"
    
    # Configure scan settings
    settings = ScanSettings(
        resolution=300,
        color_mode=ColorMode.COLOR,
        format="PNG"
    )
    
    print("Scan settings:")
    print(f"  Resolution: {settings.resolution} DPI")
    print(f"  Color mode: {settings.color_mode.value}")
    print(f"  Output: {output_path}")
    print()
    
    print("Starting scan...")
    print("(Make sure document is on scanner bed)")
    print()
    
    try:
        # Perform scan
        scanned_file = manager.scan(
            scanner_info=selected_scanner,
            output_path=output_path,
            settings=settings
        )
        
        # Get file info
        file_size_mb = scanned_file.stat().st_size / 1024 / 1024
        
        print()
        print("✓ Scan complete!")
        print(f"  Saved to: {scanned_file.absolute()}")
        print(f"  Size: {file_size_mb:.2f} MB")
        print()
        print("Next steps:")
        print(f"  Split image: uv run poc_split.py {scanned_file}")
        print(f"  View: open {scanned_file}")
        
        return scanned_file
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Scan failed: {e}")
        print("\nTroubleshooting:")
        print("  - Check scanner is ready (not in standby mode)")
        print("  - Try pressing a button on the scanner to wake it up")
        print("  - Wait 15-20 seconds and try again")
        print("  - Check scanner is visible in System Settings")
        sys.exit(1)


if __name__ == "__main__":
    main()
