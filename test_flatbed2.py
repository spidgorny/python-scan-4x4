#!/usr/bin/env python3
"""Test improved flatbed source selection."""

import sane

print("Testing improved flatbed source selection...\n")

sane.init()
devices = sane.get_devices()

if not devices:
    print("No scanner found!")
    sane.exit()
    exit(1)

print(f"Scanner: {devices[0][0]}\n")

scanner = sane.open(devices[0][0])

print("Configuring scanner...")

# Try to set source (with proper error handling)
if 'source' in scanner.opt:
    try:
        available_sources = scanner.opt['source'].constraint
        print(f"  Available sources: {available_sources}")
        
        # Check if option is active
        is_active = scanner.opt['source'].is_active()
        print(f"  Source option is_active: {is_active}")
        
        if is_active:
            # Try to set to Flatbed
            flatbed_names = ['Flatbed', 'FlatBed', 'Platen', 'Normal']
            
            for source_name in flatbed_names:
                if source_name in available_sources:
                    try:
                        scanner.source = source_name
                        print(f"  ✓ Source set to: {scanner.source}")
                        break
                    except AttributeError as e:
                        print(f"  Could not set {source_name}: {e}")
        else:
            # Option inactive - auto-selected
            if len(available_sources) == 1:
                print(f"  Source: {available_sources[0]} (auto-selected)")
            else:
                print(f"  Source: Auto-detected (inactive)")
                
    except Exception as e:
        print(f"  Error with source: {e}")

# Set mode and resolution
scanner.mode = 'Color'
scanner.resolution = 300

print("\nFinal configuration:")
print(f"  Mode: {scanner.mode}")
print(f"  Resolution: {scanner.resolution} DPI")

scanner.close()
sane.exit()

print("\n✓ Test complete!")
