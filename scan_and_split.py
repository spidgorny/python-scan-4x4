#!/usr/bin/env python3
"""
Combined POC: Scan A4 Document and Split into 2x2 Grid
Usage: python scan_and_split.py [output_dir]

This script combines both scanning and splitting functionality.
"""

import sys
from pathlib import Path
from datetime import datetime
from poc_scan import scan_document_sane, scan_document_wia, create_simulated_scan, list_scanners, USE_SANE, USE_WIA, USE_PIL
from poc_split import split_image_2x2


def scan_and_split(output_dir="output", use_simulation=None):
    """
    Scan a document and split it into 2x2 grid.
    
    Args:
        output_dir: Directory to save split images
        use_simulation: If True, force simulation mode. If None, auto-detect.
    
    Returns:
        List of split image file paths
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_scan_path = f"temp_scan_{timestamp}.png"
    
    try:
        # Step 1: Scan document
        print("=" * 60)
        print("STEP 1: Scanning Document")
        print("=" * 60)
        
        if use_simulation or (not USE_SANE and not USE_WIA):
            # Simulation mode
            scanned_file = create_simulated_scan(temp_scan_path)
        elif USE_SANE:
            # Real SANE scanner
            devices = list_scanners()
            if not devices:
                print("\nNo scanners found. Using simulation mode instead.")
                scanned_file = create_simulated_scan(temp_scan_path)
            else:
                print("\nPress Enter to start scanning (or Ctrl+C to cancel)...")
                print("(Or type 's' + Enter to use simulation mode)")
                response = input()
                
                if response.lower() == 's':
                    print("\nUsing simulation mode...")
                    scanned_file = create_simulated_scan(temp_scan_path)
                else:
                    try:
                        scanned_file = scan_document_sane(temp_scan_path, device_index=0)
                    except Exception as scan_error:
                        print(f"\n⚠️  Scanner error: {scan_error}")
                        print("\nPossible reasons:")
                        print("  - No document on scanner bed")
                        print("  - Scanner in standby/power save mode")
                        print("  - Scanner busy with another application")
                        print("\nFalling back to simulation mode...")
                        scanned_file = create_simulated_scan(temp_scan_path)
        elif USE_WIA:
            # Windows WIA scanner
            scanned_file = scan_document_wia(temp_scan_path)
        
        # Step 2: Split into 2x2 grid
        print("\n" + "=" * 60)
        print("STEP 2: Splitting into 2x2 Grid")
        print("=" * 60)
        
        split_files = split_image_2x2(str(scanned_file), output_dir)
        
        # Step 3: Clean up temporary scan
        print(f"\nCleaning up temporary file: {scanned_file.name}")
        scanned_file.unlink()
        
        return split_files
        
    except Exception as e:
        # Clean up temp file if it exists
        temp_file = Path(temp_scan_path)
        if temp_file.exists():
            temp_file.unlink()
        raise e


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Scanner → 2x2 Split - Complete Workflow POC")
    print("=" * 60)
    print()
    
    # Parse arguments
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    
    try:
        # Run the complete workflow
        split_files = scan_and_split(output_dir)
        
        # Summary
        print("\n" + "=" * 60)
        print("✓ WORKFLOW COMPLETE!")
        print("=" * 60)
        print(f"\nGenerated {len(split_files)} split images in: {Path(output_dir).absolute()}")
        print("\nFiles:")
        for i, f in enumerate(split_files, 1):
            size_kb = f.stat().st_size / 1024
            print(f"  [{i}] {f.name} ({size_kb:.1f} KB)")
        
        print("\n💡 Next Steps:")
        print("  1. Review the split images in the output/ directory")
        print("  2. Test with a real scanner (install SANE if needed)")
        print("  3. Proceed to build the web application interface")
        
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
