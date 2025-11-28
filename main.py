#!/usr/bin/env python3
"""
A4 Document Scanner with 2x2 Split

Main application using the scanner driver architecture.
"""

import sys
from pathlib import Path
from datetime import datetime

from scanners import ScannerManager, ScanSettings, ColorMode
from poc_split import split_image_2x2


def main():
    """Main application entry point"""
    print("=" * 60)
    print("A4 Document Scanner - 2x2 Split")
    print("=" * 60)
    print()
    
    # Initialize scanner manager
    manager = ScannerManager()
    
    # Show available scanners
    manager.print_available_scanners()
    
    # Get preferred scanner
    scanner = manager.get_preferred_scanner()
    
    if scanner is None:
        print("✗ No scanners available!")
        print("\nOptions:")
        print("  1. Check scanner is powered on and connected")
        print("  2. Install scanner drivers:")
        print("     - macOS/Linux: brew install sane-backends && uv add python-sane")
        print("     - Windows: uv add pywin32")
        print("  3. Use simulation mode: uv run simulate_scan.py")
        sys.exit(1)
    
    if scanner.driver == "simulation":
        print("⚠️  Using simulation mode (no physical scanner found)")
        print()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    scan_output = output_dir / f"scan_{timestamp}.png"
    split_output_dir = output_dir
    
    # Configure scan settings
    settings = ScanSettings(
        resolution=300,
        color_mode=ColorMode.COLOR,
        format="PNG"
    )
    
    print("=" * 60)
    print("STEP 1: Scanning")
    print("=" * 60)
    print()
    print(f"Scanner: {scanner.name}")
    print(f"Driver: {scanner.driver}")
    print(f"Resolution: {settings.resolution} DPI")
    print(f"Color mode: {settings.color_mode.value}")
    print()
    
    if scanner.driver != "simulation":
        print("Make sure document is on scanner bed...")
        print()
    
    try:
        # Scan
        scanned_file = manager.scan(
            scanner_info=scanner,
            output_path=scan_output,
            settings=settings
        )
        
        print()
        print(f"✓ Scan complete: {scanned_file}")
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Scan failed: {e}")
        print("\nTry:")
        print("  - Check scanner is ready (powered on, not in standby)")
        print("  - Use simulation mode: uv run simulate_scan.py")
        sys.exit(1)
    
    # Split into 2x2
    print()
    print("=" * 60)
    print("STEP 2: Splitting into 2x2 Grid")
    print("=" * 60)
    print()
    
    try:
        split_files = split_image_2x2(str(scanned_file), str(split_output_dir))
        
        print()
        print("=" * 60)
        print("✓ Complete!")
        print("=" * 60)
        print()
        print(f"Scan: {scanned_file}")
        print(f"Split images: {split_output_dir}/")
        for split_file in split_files:
            print(f"  - {split_file.name}")
        
    except Exception as e:
        print(f"✗ Split failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
