#!/usr/bin/env python3
"""
Combined POC: Scan A4 Document and Split into 2x2 Grid
Usage: python scan_and_split.py [output_dir]

This script combines both scanning and splitting functionality.
Requires a physical scanner. For simulation, use simulate_scan.py first.
"""

import sys
from pathlib import Path
from datetime import datetime
from scanners.manager import ScannerManager
from scanners.base import ScanSettings
from smart_split import smart_split_2x2


def scan_and_split(scanner_ip="192.168.1.208", output_dir="output"):
    """
    Scan a document and split it into 2x2 grid.
    
    Args:
        scanner_ip: IP address of eSCL scanner
        output_dir: Directory to save split images
    
    Returns:
        List of split image file paths
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scan_dir = Path(output_dir) / "scans"
    scan_dir.mkdir(parents=True, exist_ok=True)
    temp_scan_path = scan_dir / f"scan_{timestamp}.png"
    
    try:
        # Step 1: Scan document
        print("=" * 60)
        print("STEP 1: Scanning Document")
        print("=" * 60)
        
        manager = ScannerManager()
        scanner_info = manager.get_preferred_scanner()
        
        if scanner_info is None:
            raise Exception("No scanner available")
        
        print(f"\nUsing scanner: {scanner_info.name} ({scanner_info.driver})")
        print(f"Scanning to: {temp_scan_path}")
        
        settings = ScanSettings(
            color_mode="RGB24",
            resolution=300,
            source="Flatbed"
        )
        
        manager.scan(scanner_info, temp_scan_path, settings)
        
        # Step 2: Split into 2x2 grid using smart detection
        print("\n" + "=" * 60)
        print("STEP 2: Smart Splitting into 2x2 Grid")
        print("=" * 60)
        
        split_files = smart_split_2x2(str(temp_scan_path), output_dir)
        
        return split_files
        
    except Exception as e:
        print(f"Error during scan: {e}")
        raise e


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Scanner → 2x2 Split - Complete Workflow POC")
    print("=" * 60)
    print()
    
    # Parse arguments
    scanner_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.208"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    try:
        # Run the complete workflow
        split_files = scan_and_split(scanner_ip, output_dir)
        
        # Summary
        print("\n" + "=" * 60)
        print("✓ WORKFLOW COMPLETE!")
        print("=" * 60)
        print(f"\nGenerated {len(split_files)} split images in: {Path(output_dir).absolute()}")
        print("\nFiles:")
        for i, f in enumerate(split_files, 1):
            size_kb = f.stat().st_size / 1024
            print(f"  [{i}] {f.name} ({size_kb:.1f} KB)")
        
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Error during workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
