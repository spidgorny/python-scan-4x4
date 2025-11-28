# Changelog

## [0.1.1] - 2024-11-28

### Changed
- **Removed Enter prompt for single scanner setups** - When only one scanner is detected, the scan proceeds immediately without waiting for user input
- Enter prompt is still shown when multiple scanners are detected

### Added
- `troubleshoot_scanner.py` - Comprehensive scanner I/O error troubleshooting guide
- Automatic flatbed source selection (prefers Flatbed over ADF)
- `test_source_selection.py` - Test script for scanner source detection
- `simulate_scan.py` - Standalone simulation mode script
- `FLATBED_FEATURE.md` - Documentation for flatbed selection feature
- `REFACTORING.md` - Documentation of simulation code extraction

### Fixed
- Removed duplicate code in `list_scanners()` function
- Extracted simulation code to separate script for clearer separation of concerns
- Better error messages with actionable guidance

### Improved
- Faster workflow for single scanner setups (no unnecessary prompts)
- Clear distinction between real scanner and simulation modes
- Better troubleshooting information for I/O errors

## [0.1.0] - 2024-11-28

### Added
- Initial POC implementation
- Scanner detection via SANE (Linux/macOS)
- Image splitting into 2x2 grid
- Simulation mode for testing without hardware
- Complete documentation suite

### Features
- A4 scanning at 300 DPI
- Automatic 2x2 image splitting
- Cross-platform support (macOS, Linux)
- Modern package management with uv
