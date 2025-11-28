#!/usr/bin/env python3
"""
Scanner using scanimage command (fallback method)

This uses the scanimage command-line tool directly instead of python-sane.
If NAPS2 works, this should work too since both use SANE backend.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def scan_with_scanimage(output_path="scanned_document.png", device="epson2:net:192.168.1.208"):
    """
    Scan using scanimage command directly.
    
    This is more reliable than python-sane for network scanners
    that may have timing/initialization issues.
    """
    print("=" * 60)
    print("Scanning with scanimage command")
    print("=" * 60)
    print()
    
    print(f"Device: {device}")
    print(f"Output: {output_path}")
    print()
    
    # Build scanimage command
    cmd = [
        'scanimage',
        '-d', device,
        '--format=png',
        '--mode', 'Color',
        '--resolution', '300',
        '-o', output_path
    ]
    
    print("Command:", ' '.join(cmd))
    print()
    print("Scanning... Please wait.")
    print("(This may take 30-60 seconds for A4 at 300 DPI)")
    print()
    
    try:
        # Run scanimage
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            output_file = Path(output_path)
            if output_file.exists():
                size_mb = output_file.stat().st_size / 1024 / 1024
                print(f"✓ Scan complete!")
                print(f"  Saved to: {output_file.absolute()}")
                print(f"  Size: {size_mb:.2f} MB")
                return output_file
            else:
                print(f"✗ Command succeeded but file not found: {output_path}")
                return None
        else:
            print(f"✗ scanimage failed with code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("✗ Scan timed out after 2 minutes")
        print("   Scanner may be in standby mode")
        return None
        
    except FileNotFoundError:
        print("✗ scanimage command not found!")
        print("   Install with: brew install sane-backends")
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Document Scanner - Scanimage Method")
    print("=" * 60)
    print()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"scan_{timestamp}.png"
    
    # Check if scanimage is available
    try:
        result = subprocess.run(['scanimage', '--version'], capture_output=True)
        if result.returncode != 0:
            print("✗ scanimage not available")
            print("Install with: brew install sane-backends")
            sys.exit(1)
    except FileNotFoundError:
        print("✗ scanimage not found")
        print("Install with: brew install sane-backends")
        sys.exit(1)
    
    # List available scanners
    print("Detecting scanners...")
    result = subprocess.run(
        ['scanimage', '-L'],
        capture_output=True,
        text=True
    )
    
    if 'epson2:net:192.168.1.208' in result.stdout:
        print(f"✓ Found scanner: epson2:net:192.168.1.208")
    else:
        print("Available scanners:")
        print(result.stdout)
    
    print()
    
    # Scan
    scan_with_scanimage(output_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
