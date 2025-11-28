#!/usr/bin/env python3
"""Test script to explore scanner options and sources."""

import sane

print("Initializing SANE...")
sane.init()

devices = sane.get_devices()
if not devices:
    print("No scanners found!")
    sane.exit()
    exit(1)

print(f"\nFound {len(devices)} scanner(s)")
print(f"Using: {devices[0][0]}\n")

scanner = sane.open(devices[0][0])

print("=" * 60)
print("Scanner Options:")
print("=" * 60)

# List all available options
for opt_name in scanner.opt.keys():
    try:
        opt = scanner.opt[opt_name]
        print(f"\n{opt_name}:")
        print(f"  Title: {opt.title}")
        print(f"  Type: {opt.type}")
        print(f"  Unit: {opt.unit}")
        
        # Check for constraints (possible values)
        if hasattr(opt, 'constraint') and opt.constraint:
            print(f"  Possible values: {opt.constraint}")
        
        # Try to get current value
        try:
            if hasattr(scanner, opt_name):
                current = getattr(scanner, opt_name)
                print(f"  Current value: {current}")
        except:
            pass
            
    except Exception as e:
        print(f"  Error reading option: {e}")

# Specifically check for source option
print("\n" + "=" * 60)
print("Source/Feeder Options:")
print("=" * 60)

for opt_name in ['source', 'doc-source', 'adf-mode', 'duplex', 'feeder']:
    if opt_name in scanner.opt:
        print(f"\n✓ {opt_name} option available:")
        try:
            opt = scanner.opt[opt_name]
            print(f"  Current: {getattr(scanner, opt_name, 'N/A')}")
            if hasattr(opt, 'constraint'):
                print(f"  Choices: {opt.constraint}")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print(f"✗ {opt_name} - not available")

scanner.close()
sane.exit()

print("\n" + "=" * 60)
print("Done!")
