#!/usr/bin/env python3
"""
Scanner I/O Error Troubleshooting Guide

This error typically occurs when:
1. Scanner is in standby/sleep mode
2. Scanner lid is open
3. No document on scanner bed (some models require this)
4. Scanner busy with another application
5. Scanner needs physical button press
"""

import subprocess
import sys

def check_scanner():
    print("=" * 60)
    print("Scanner I/O Error Troubleshooting")
    print("=" * 60)
    print()
    
    # Check network connectivity
    print("1. Checking network connectivity...")
    result = subprocess.run(
        ["ping", "-c", "2", "192.168.1.208"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("   ✓ Scanner is reachable on network")
    else:
        print("   ✗ Scanner not reachable!")
        print("   → Check scanner is powered on")
        print("   → Check network connection")
        return
    
    print()
    print("2. Checking SANE can detect scanner...")
    result = subprocess.run(
        ["scanimage", "-L"],
        capture_output=True,
        text=True
    )
    if "epson2:net:192.168.1.208" in result.stdout:
        print("   ✓ Scanner detected by SANE")
    else:
        print("   ✗ Scanner not detected")
        return
    
    print()
    print("=" * 60)
    print("Common Causes of 'Error during device I/O':")
    print("=" * 60)
    print()
    
    causes = [
        ("Scanner in Standby/Sleep Mode", [
            "Press a button on the scanner to wake it up",
            "Wait 10-15 seconds for scanner to warm up",
            "Look for power LED to be solid (not blinking)"
        ]),
        ("Scanner Lid Open", [
            "Close the scanner lid completely",
            "Some scanners won't scan with lid open"
        ]),
        ("No Document on Scanner Bed", [
            "Some scanner models require a document to be present",
            "Place any paper on the scanner glass",
            "Even a blank page can help"
        ]),
        ("Scanner Locked/In Use", [
            "Close any other scanning software (Photos, Preview, etc.)",
            "Wait a few seconds and try again",
            "Restart the scanner if needed"
        ]),
        ("Button Press Required", [
            "Some Epson models require pressing the scan button",
            "Check if scanner has a 'Scan' button to press",
            "Try pressing it before or after starting the scan"
        ]),
        ("Network Scanner Timeout", [
            "Network scanner may need more time to respond",
            "Try scanning again after 30 seconds",
            "Power cycle the scanner if problem persists"
        ])
    ]
    
    for i, (cause, solutions) in enumerate(causes, 1):
        print(f"{i}. {cause}")
        for solution in solutions:
            print(f"   → {solution}")
        print()
    
    print("=" * 60)
    print("Recommended Steps:")
    print("=" * 60)
    print()
    print("1. Wake up the scanner:")
    print("   - Press any button on the scanner")
    print("   - Wait 15 seconds")
    print()
    print("2. Prepare for scanning:")
    print("   - Place a document on the scanner glass")
    print("   - Close the scanner lid completely")
    print()
    print("3. Try scanning again:")
    print("   - Run: uv run poc_scan.py")
    print("   - Press Enter when prompted")
    print()
    print("4. If still failing:")
    print("   - Power cycle the scanner (turn off, wait 10s, turn on)")
    print("   - Wait 30 seconds for full boot up")
    print("   - Try again")
    print()
    print("5. Test with system command:")
    print("   - Run: scanimage -d 'epson2:net:192.168.1.208' > test.pnm")
    print("   - If this also fails, it's a scanner/network issue")
    print()
    print("=" * 60)
    print("Alternative: Use Simulation Mode")
    print("=" * 60)
    print()
    print("While troubleshooting the scanner, you can use:")
    print("  uv run simulate_scan.py")
    print("  uv run poc_split.py simulated_scan_*.png")
    print()


if __name__ == "__main__":
    check_scanner()
