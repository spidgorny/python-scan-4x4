#!/usr/bin/env python3
"""
Test eSCL (AirScan) scanner protocol
eSCL is a simple HTTP-based scanning protocol
"""

import requests
import urllib3
from xml.etree import ElementTree as ET

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Scanner endpoint
SCANNER_URL = "https://EPSON3BA687.local:443/eSCL"

print("=" * 60)
print("Testing eSCL (AirScan) Scanner Protocol")
print("=" * 60)
print()

print(f"Scanner URL: {SCANNER_URL}")
print()

# Test 1: Get scanner capabilities
print("1. Getting scanner capabilities...")
try:
    response = requests.get(
        f"{SCANNER_URL}/ScannerCapabilities",
        verify=False,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✓ Scanner responded!")
        print()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract namespace
        ns = {'scan': 'http://schemas.hp.com/imaging/escl/2011/05/03'}
        
        # Get scanner info
        make = root.find('.//scan:Make', ns)
        model = root.find('.//scan:Model', ns)
        
        if make is not None and model is not None:
            print(f"  Make: {make.text}")
            print(f"  Model: {model.text}")
        
        # Get supported sources
        print("\n  Supported sources:")
        for source in root.findall('.//scan:InputSource', ns):
            source_name = source.text
            print(f"    - {source_name}")
        
        # Get supported color modes
        print("\n  Supported color modes:")
        for mode in root.findall('.//scan:ColorMode', ns):
            print(f"    - {mode.text}")
        
        # Get supported resolutions
        print("\n  Supported resolutions:")
        for res in root.findall('.//scan:DiscreteResolution', ns):
            x_res = res.find('.//scan:XResolution', ns)
            y_res = res.find('.//scan:YResolution', ns)
            if x_res is not None and y_res is not None:
                print(f"    - {x_res.text} x {y_res.text} DPI")
        
        print("\n✓ eSCL scanner is working!")
        
    else:
        print(f"✗ Error: HTTP {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("✗ Could not connect to scanner")
    print("  Make sure scanner is on and network accessible")
except Exception as e:
    print(f"✗ Error: {e}")

print()
print("=" * 60)
