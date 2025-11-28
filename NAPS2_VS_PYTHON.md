# NAPS2 vs Python-SANE Comparison

## Issue
- NAPS2 can scan successfully
- Python script with python-sane gets "Error during device I/O"

## Possible Differences

### 1. Scanner Backend
**NAPS2 (Windows/Mac):**
- Uses TWAIN or WIA on Windows
- Uses SANE on Linux/Mac
- May use different Epson driver

**Our Script:**
- Uses python-sane (SANE backend)
- Uses epson2 driver
- Network protocol: epson2:net:IP

### 2. Initialization Sequence
**NAPS2 might:**
- Send wake-up command to scanner
- Wait for scanner ready signal
- Perform handshake before scanning
- Use different timeout values

**Our script:**
- Opens scanner
- Sets options
- Immediately tries to scan
- No warm-up delay

### 3. Scanner State
**Possible states:**
- Ready (can scan immediately)
- Standby (needs wake-up)
- Busy (processing previous job)
- Locked (another app has control)

## Solutions Tried

✅ Added retry logic with delays
✅ Flatbed source selection
✅ Minimal configuration test

## Next Steps to Try

### Option 1: Add Warm-up Delay
```python
# After opening scanner, wait before scanning
scanner = sane.open(device)
time.sleep(5)  # Give scanner time to initialize
scanner.start()
```

### Option 2: Use scanimage Command
If Python doesn't work, we can shell out to scanimage:
```python
subprocess.run([
    'scanimage',
    '-d', 'epson2:net:192.168.1.208',
    '--format=png',
    '--mode', 'Color',
    '--resolution', '300',
    '-o', 'output.png'
])
```

### Option 3: Check NAPS2 Logs
Look at NAPS2 logs to see what commands it sends:
- macOS: ~/Library/Logs/NAPS2/
- Check for SANE backend calls
- See what initialization it does

### Option 4: Physical Scanner Action
Since NAPS2 works:
1. Run NAPS2 scan (don't save)
2. Immediately after, run Python script
3. Scanner might stay "warm" between scans

## Recommendation

Try the retry logic first (already added). If that doesn't work:

1. **Use scanimage wrapper** - Most reliable
2. **Check scanner firmware** - May need update
3. **Use NAPS2 as backend** - Call NAPS2 CLI if it has one

## Testing

Run with retries:
```bash
uv run poc_scan.py
```

The script now retries 3 times with 2-second delays.
