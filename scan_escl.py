#!/usr/bin/env python3
"""
eSCL (AirScan) Scanner - Working Method!

This uses the eSCL HTTP protocol which is what NAPS2 uses
when you select "Apple driver". This WORKS!
"""

import requests
import urllib3
from xml.etree import ElementTree as ET
from datetime import datetime
from pathlib import Path
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCANNER_URL = "https://EPSON3BA687.local:443/eSCL"


def scan_with_escl(output_path="scan.jpg", color_mode="RGB24", resolution=300):
    """
    Scan using eSCL protocol.
    
    Args:
        output_path: Where to save scan
        color_mode: RGB24 (color), Grayscale8, or BlackAndWhite1
        resolution: DPI (100, 200, 300, 600, 1200)
    """
    print("=" * 60)
    print("eSCL (AirScan) Scanner")
    print("=" * 60)
    print()
    
    print(f"Scanner: {SCANNER_URL}")
    print(f"Mode: {color_mode}")
    print(f"Resolution: {resolution} DPI")
    print()
    
    # Create scan settings XML
    scan_settings = f"""<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
    <pwg:Version>2.0</pwg:Version>
    <pwg:ScanRegions>
        <pwg:ScanRegion>
            <pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches</pwg:ContentRegionUnits>
            <pwg:XOffset>0</pwg:XOffset>
            <pwg:YOffset>0</pwg:YOffset>
            <pwg:Width>2550</pwg:Width>
            <pwg:Height>3500</pwg:Height>
        </pwg:ScanRegion>
    </pwg:ScanRegions>
    <scan:InputSource>Platen</scan:InputSource>
    <scan:ColorMode>{color_mode}</scan:ColorMode>
    <scan:XResolution>{resolution}</scan:XResolution>
    <scan:YResolution>{resolution}</scan:YResolution>
</scan:ScanSettings>"""
    
    try:
        # POST scan job
        print("Starting scan job...")
        response = requests.post(
            f"{SCANNER_URL}/ScanJobs",
            data=scan_settings,
            headers={'Content-Type': 'text/xml'},
            verify=False,
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"✗ Failed to create scan job: HTTP {response.status_code}")
            print(response.text)
            return None
        
        # Get job location from response headers
        job_url = response.headers.get('Location')
        if not job_url:
            print("✗ No job location in response")
            return None
        
        print(f"✓ Scan job created: {job_url}")
        print()
        print("Scanning... Please wait (this may take 30-60 seconds)")
        print()
        
        # Get the scanned document
        doc_url = f"{job_url}/NextDocument"
        print(f"Retrieving document from: {doc_url}")
        
        response = requests.get(
            doc_url,
            verify=False,
            timeout=120  # 2 minute timeout for scan
        )
        
        if response.status_code == 200:
            # Save the image
            output_file = Path(output_path)
            output_file.write_bytes(response.content)
            
            size_mb = len(response.content) / 1024 / 1024
            print()
            print("✓ Scan complete!")
            print(f"  Saved to: {output_file.absolute()}")
            print(f"  Size: {size_mb:.2f} MB")
            
            return output_file
        else:
            print(f"✗ Failed to get document: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Scan timed out")
        print("  Scanner may be in standby mode - try pressing a button")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Document Scanner - eSCL Method (WORKING!)")
    print("=" * 60)
    print()
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"scan_{timestamp}.jpg"
    
    # Test scanner connectivity first
    print("Testing scanner connectivity...")
    try:
        response = requests.get(
            f"{SCANNER_URL}/ScannerCapabilities",
            verify=False,
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Scanner is online and ready")
            print()
        else:
            print(f"✗ Scanner returned HTTP {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Cannot reach scanner: {e}")
        print()
        print("Make sure:")
        print("  1. Scanner is powered on")
        print("  2. Scanner is on network")
        print("  3. You can ping EPSON3BA687.local")
        sys.exit(1)
    
    # Scan!
    result = scan_with_escl(
        output_path=output_path,
        color_mode="RGB24",  # Color scan
        resolution=300       # 300 DPI
    )
    
    if result:
        print()
        print("✓ Success! Scanner is working with eSCL protocol!")
        print()
        print("Next steps:")
        print(f"  Split the image: uv run poc_split.py {output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
