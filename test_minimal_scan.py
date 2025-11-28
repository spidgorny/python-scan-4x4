#!/usr/bin/env python3
"""Minimal scan test"""
import sane

print("1. Init SANE...")
sane.init()

print("2. Get devices...")
devices = sane.get_devices()
print(f"   Found: {devices[0][0]}")

print("3. Open scanner...")
scanner = sane.open(devices[0][0])

print("4. Check current settings...")
print(f"   Mode: {scanner.mode}")
print(f"   Resolution: {scanner.resolution}")

print("5. Try scan with DEFAULTS (no changes)...")
try:
    scanner.start()
    print("   ✓ start() worked")
    img = scanner.snap()
    print(f"   ✓ snap() worked: {img.size}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

scanner.close()
sane.exit()
