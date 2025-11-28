#!/usr/bin/env python3
"""Test flatbed source selection."""

import sane

print("Testing flatbed source selection...\n")

sane.init()
devices = sane.get_devices()

if not devices:
    print("No scanner found!")
    sane.exit()
    exit(1)

print(f"Scanner: {devices[0][0]}\n")

scanner = sane.open(devices[0][0])

print("Before configuration:")
print(f"  Source: {scanner.opt['source'].constraint}")
try:
    print(f"  Current: {scanner.source}")
except:
    print(f"  Current: (not set)")

print("\nSetting source to Flatbed...")

# Try to set source
if 'source' in scanner.opt:
    available_sources = scanner.opt['source'].constraint
    print(f"  Available: {available_sources}")
    
    if 'Flatbed' in available_sources:
        scanner.source = 'Flatbed'
        print(f"  ✓ Set to: {scanner.source}")
    else:
        print(f"  ✗ Flatbed not available, using: {available_sources[0]}")
        scanner.source = available_sources[0]
        print(f"  Set to: {scanner.source}")

# Also set mode and resolution
scanner.mode = 'Color'
scanner.resolution = 300

print("\nFinal configuration:")
print(f"  Source: {scanner.source}")
print(f"  Mode: {scanner.mode}")
print(f"  Resolution: {scanner.resolution} DPI")

scanner.close()
sane.exit()

print("\n✓ Test complete!")
