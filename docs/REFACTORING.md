# Refactoring: Simulation Code Extracted

## Changes Made

### 1. Created `simulate_scan.py`
**New standalone script** for simulation mode:
- Generates realistic A4 documents (2480×3508 @ 300 DPI)
- No dependencies on scanner libraries
- Can be run independently: `uv run simulate_scan.py`

### 2. Updated `poc_scan.py`
**Now requires physical scanner**:
- Removed `create_simulated_scan()` function
- Removed simulation fallback logic
- Fails with clear error messages if no scanner detected
- Suggests using `simulate_scan.py` as alternative

### 3. Updated `scan_and_split.py`
**No more simulation mode**:
- Requires physical scanner
- Removed simulation fallback
- Clearer error messages pointing to `simulate_scan.py`

### 4. Updated `.gitignore`
Added `simulated_scan_*.png` to ignore list

### 5. Updated Documentation
- README.md - New usage examples
- Simulation mode now documented as separate workflow

## Rationale

### Before (Confusing)
```
uv run poc_scan.py
# Could use either real scanner OR simulation
# Hard to predict behavior
```

### After (Clear)
```
# Real scanner (fails if no hardware)
uv run poc_scan.py

# Simulation (always works)
uv run simulate_scan.py
```

## Benefits

1. **Explicit Intent**: Users must choose scanner vs simulation
2. **Clear Errors**: No hidden fallbacks, clear error messages
3. **Separation of Concerns**: Scanner code doesn't need PIL/simulation logic
4. **Better Testing**: Easy to test with/without scanner
5. **Documentation**: Clearer usage instructions

## New Workflows

### Development/Testing (No Scanner)
```bash
# Generate test scan
uv run simulate_scan.py

# Split it
uv run poc_split.py simulated_scan_*.png
```

### Production (With Scanner)
```bash
# Scan from hardware
uv run poc_scan.py

# Or complete workflow
uv run scan_and_split.py
```

### Mixed (Test then Real)
```bash
# Test with simulation first
uv run simulate_scan.py
uv run poc_split.py simulated_scan_*.png

# Then use real scanner
uv run scan_and_split.py
```

## Error Messages

### No Scanner Detected (poc_scan.py)
```
✗ ERROR: No scanners detected!

Troubleshooting:
  1. Check scanner is powered on and connected
  2. Run: scanimage -L
  3. Check permissions (may need sudo)

Or use simulation mode:
  uv run simulate_scan.py
```

### No SANE Library (poc_scan.py)
```
✗ ERROR: No scanning library available!

Install dependencies:
  Linux/macOS: brew install sane-backends && uv add python-sane
  Windows: uv add pywin32

Or use simulation mode:
  uv run simulate_scan.py
```

## File Changes

### New Files
- ✅ `simulate_scan.py` - Standalone simulation script

### Modified Files
- ✅ `poc_scan.py` - Removed simulation code
- ✅ `scan_and_split.py` - Removed simulation fallback
- ✅ `README.md` - Updated usage examples
- ✅ `.gitignore` - Added simulated_scan_*.png

### Removed Code
- ❌ `create_simulated_scan()` function from poc_scan.py
- ❌ Simulation fallback logic
- ❌ 's' key prompt for simulation mode
- ❌ PIL imports in poc_scan.py

## Testing

```bash
# Test simulation
uv run simulate_scan.py
# Should create: simulated_scan_YYYYMMDD_HHMMSS.png

# Test splitting simulation
uv run poc_split.py simulated_scan_*.png
# Should create 4 split images

# Test real scanner (if available)
uv run poc_scan.py
# Should scan or fail with helpful message

# Test workflow (if scanner available)
uv run scan_and_split.py
# Should scan and split
```

## Migration Guide

### Old Way (Deprecated)
```bash
# This no longer works
echo "s" | uv run poc_scan.py
```

### New Way
```bash
# Use explicit simulation script
uv run simulate_scan.py
uv run poc_split.py simulated_scan_*.png
```

## Summary

✅ **Cleaner separation** between simulation and real scanning  
✅ **Explicit user choice** - no hidden fallbacks  
✅ **Better error messages** - clear guidance  
✅ **Easier to maintain** - less conditional logic  
✅ **Better documentation** - clearer workflows  

---

**Date**: 2024-11-28  
**Version**: 0.1.1  
**Status**: ✅ Complete
