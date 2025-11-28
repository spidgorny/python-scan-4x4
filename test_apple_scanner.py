#!/usr/bin/env python3
"""
Test accessing scanner via Apple's Image Capture framework
"""

import objc
from Foundation import NSBundle
import time

print("=" * 60)
print("Testing Apple Image Capture Scanner Access")
print("=" * 60)
print()

# Load ImageCaptureCore framework
print("1. Loading ImageCaptureCore framework...")
bundle_path = '/System/Library/Frameworks/ImageCaptureCore.framework'
bundle = NSBundle.bundleWithPath_(bundle_path)

if not bundle:
    print(f"✗ Could not find bundle at {bundle_path}")
    exit(1)

if not bundle.load():
    print("✗ Could not load ImageCaptureCore framework")
    exit(1)

print("✓ ImageCaptureCore loaded")
print()

# Get the device browser class
print("2. Getting ICDeviceBrowser class...")
try:
    ICDeviceBrowser = objc.lookUpClass('ICDeviceBrowser')
    print("✓ ICDeviceBrowser found")
except:
    print("✗ ICDeviceBrowser not found")
    exit(1)

print()
print("3. Creating device browser...")
browser = ICDeviceBrowser.alloc().init()
print(f"✓ Browser created: {browser}")

print()
print("4. Starting browser to detect scanners...")
browser.start()
print("✓ Browser started")

print()
print("5. Waiting for devices (5 seconds)...")
time.sleep(5)

print()
print("6. Checking for devices...")
devices = browser.devices()
if devices:
    print(f"✓ Found {len(devices)} device(s):")
    for i, device in enumerate(devices):
        print(f"\n  Device {i+1}:")
        print(f"    Name: {device.name()}")
        print(f"    Type: {device.type()}")
        try:
            print(f"    UUID: {device.UUIDString()}")
        except:
            pass
else:
    print("✗ No devices found")
    print("\nNote: Make sure scanner is:")
    print("  - Powered on")
    print("  - Connected to network")
    print("  - Visible in System Settings > Printers & Scanners")

browser.stop()
print()
print("=" * 60)
print("Test complete")
print("=" * 60)
