#!/usr/bin/env python3
"""
Demonstrate scanner source selection (Flatbed vs ADF).

This script shows how the POC handles scanners with multiple sources:
- Flatbed (glass platen)
- ADF (Automatic Document Feeder)
- Duplex ADF

The POC will automatically select Flatbed when available.
"""

import sane

def test_source_selection():
    """Test and demonstrate source selection logic."""
    
    print("=" * 60)
    print("Scanner Source Selection Test")
    print("=" * 60)
    print()
    
    # Initialize SANE
    sane.init()
    devices = sane.get_devices()
    
    if not devices:
        print("❌ No scanners found!")
        print("\nThis test requires a physical scanner.")
        print("Your scanner must support SANE.")
        sane.exit()
        return
    
    print(f"✓ Found {len(devices)} scanner(s)\n")
    
    for i, dev in enumerate(devices):
        print(f"[{i}] {dev[0]}")
        print(f"    Manufacturer: {dev[1]}")
        print(f"    Type: {dev[2]}")
        print()
    
    # Use first scanner
    device_name = devices[0][0]
    print(f"Testing with: {device_name}\n")
    
    scanner = sane.open(device_name)
    
    # Check for source option
    print("=" * 60)
    print("Source Configuration")
    print("=" * 60)
    
    if 'source' in scanner.opt:
        opt = scanner.opt['source']
        available_sources = opt.constraint
        is_active = opt.is_active()
        
        print(f"\n✓ Scanner has 'source' option")
        print(f"  Available sources: {available_sources}")
        print(f"  Is active: {is_active}")
        print(f"  Title: {opt.title}")
        
        if available_sources:
            print(f"\n  Analysis:")
            
            # Check for flatbed
            flatbed_options = [s for s in available_sources if s.lower() in ['flatbed', 'platen', 'normal']]
            adf_options = [s for s in available_sources if 'adf' in s.lower() or 'feeder' in s.lower()]
            
            if flatbed_options:
                print(f"    ✓ Flatbed available: {flatbed_options}")
            else:
                print(f"    ✗ No flatbed option found")
            
            if adf_options:
                print(f"    ℹ ADF available: {adf_options}")
            else:
                print(f"    ℹ No ADF/feeder option")
            
            # Show what POC will do
            print(f"\n  POC Behavior:")
            
            if not is_active:
                if len(available_sources) == 1:
                    print(f"    → Will use: {available_sources[0]} (auto-selected)")
                else:
                    print(f"    → Option inactive, scanner will auto-select")
            else:
                # Try to set flatbed
                flatbed_names = ['Flatbed', 'FlatBed', 'Platen', 'Normal']
                selected = None
                
                for name in flatbed_names:
                    if name in available_sources:
                        selected = name
                        break
                
                if selected:
                    print(f"    → Will set to: {selected} (Flatbed preferred)")
                else:
                    print(f"    → Will use: {available_sources[0]} (default)")
                    
                # Try to actually set it
                if selected:
                    try:
                        scanner.source = selected
                        print(f"    ✓ Successfully set to: {scanner.source}")
                    except Exception as e:
                        print(f"    ⚠ Could not set: {e}")
        
    else:
        print("\n✗ Scanner does not have 'source' option")
        print("  → POC will use scanner's default source")
    
    print()
    print("=" * 60)
    print("Other Scanner Capabilities")
    print("=" * 60)
    
    # Show other relevant options
    interesting_opts = {
        'mode': 'Scan mode (Color/Gray/Lineart)',
        'resolution': 'Scan resolution (DPI)',
        'adf-mode': 'ADF mode (simplex/duplex)',
        'duplex': 'Duplex scanning',
        'batch-scan': 'Batch scanning support'
    }
    
    for opt_name, description in interesting_opts.items():
        if opt_name in scanner.opt:
            opt = scanner.opt[opt_name]
            print(f"\n✓ {opt_name}: {description}")
            if hasattr(opt, 'constraint') and opt.constraint:
                print(f"  Options: {opt.constraint}")
            try:
                current = getattr(scanner, opt_name, None)
                if current:
                    print(f"  Current: {current}")
            except:
                pass
    
    scanner.close()
    sane.exit()
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The POC script will:
1. Check if scanner has a 'source' option
2. If available, prefer 'Flatbed' over ADF/Feeder
3. If only one source, auto-select it
4. If source option is inactive, use scanner default

This ensures documents are scanned from the flatbed glass
(suitable for photos, books, and single documents) rather
than the automatic document feeder.

For production use, you may want to:
- Add command-line option to choose source
- Support batch scanning with ADF
- Detect paper in feeder vs flatbed
""")
    
    print("\n✓ Test complete!\n")


if __name__ == "__main__":
    test_source_selection()
