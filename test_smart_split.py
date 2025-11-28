#!/usr/bin/env python3
"""
Test smart photo splitting with a simulated scan
"""

import sys
from pathlib import Path

# Generate a test scan with 4 photos
print("Generating test scan with 4 photos...")
from simulate_scan import create_simulated_scan

output_path = Path("output/test_scan.png")
output_path.parent.mkdir(exist_ok=True)

scan_file = create_simulated_scan(str(output_path))

print(f"✓ Generated: {scan_file}")
print()

# Test smart split
print("Testing smart photo detection...")
from smart_split import split_photos_smart

split_files = split_photos_smart(
    str(scan_file),
    "output",
    debug=True
)

print()
print("=" * 60)
print("Test complete!")
print("=" * 60)
print()
print("Files created:")
print(f"  Scan: {scan_file}")
for f in split_files:
    print(f"  Photo: {f}")
print()
print("Check output/ folder for results!")
