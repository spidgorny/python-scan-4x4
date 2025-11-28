# Scanner Driver Architecture

## Overview

The scanner functionality is now split into a modular driver architecture with a common interface. This allows supporting multiple scanner backends transparently.

## Architecture

```
scanners/
├── __init__.py           # Package exports
├── base.py               # Base classes and interfaces
├── escl_driver.py        # eSCL (AirScan) driver
├── sane_driver.py        # SANE driver (Linux/macOS)
├── wia_driver.py         # WIA driver (Windows)
├── simulation_driver.py  # Simulation driver (testing)
└── manager.py            # Scanner manager (auto-selection)
```

## Common Interface

All drivers implement the `ScannerDriver` interface:

```python
class ScannerDriver(ABC):
    def list_scanners() -> List[ScannerInfo]
    def scan(scanner_id, output_path, settings) -> Path
    def is_available() -> bool
    def get_driver_name() -> str
```

## Drivers

### 1. eSCL Driver (✅ Recommended)

**Protocol**: HTTP-based eSCL (AirScan)  
**Platforms**: macOS, Linux, Windows  
**Status**: ✅ Working!

**Advantages**:
- Simple HTTP REST protocol
- No complex driver dependencies
- Works across all platforms
- Same protocol NAPS2 uses for "Apple driver"
- Bypasses SANE I/O issues

**Usage**:
```python
from scanners import ESCLDriver

driver = ESCLDriver()
scanners = driver.list_scanners()
driver.scan(scanners[0].id, "output.jpg")
```

### 2. SANE Driver

**Protocol**: SANE (Scanner Access Now Easy)  
**Platforms**: Linux, macOS  
**Status**: ⚠️ Has I/O issues with network scanners

**Advantages**:
- Wide scanner support
- Traditional Unix scanner interface

**Issues**:
- "Device I/O" errors with network scanners
- Scanners need to be "warmed up"
- Timing sensitive

**Usage**:
```python
from scanners import SANEDriver

driver = SANEDriver()
scanners = driver.list_scanners()
driver.scan(scanners[0].id, "output.png")
```

### 3. WIA Driver

**Protocol**: Windows Image Acquisition  
**Platforms**: Windows only  
**Status**: ✅ Implemented (not tested)

**Usage**:
```python
from scanners import WIADriver

driver = WIADriver()
scanners = driver.list_scanners()
driver.scan(scanners[0].id, "output.png")
```

### 4. Simulation Driver

**Protocol**: Virtual (generates fake scans)  
**Platforms**: All (requires Pillow)  
**Status**: ✅ Working

**Purpose**: Testing without hardware

**Usage**:
```python
from scanners import SimulationDriver

driver = SimulationDriver()
scanners = driver.list_scanners()
driver.scan(scanners[0].id, "output.png")
```

## Scanner Manager

The `ScannerManager` automatically selects the best available driver:

**Priority Order**:
1. eSCL (most reliable)
2. SANE (traditional)
3. WIA (Windows)
4. Simulation (testing)

**Usage**:
```python
from scanners import ScannerManager, ScanSettings, ColorMode

manager = ScannerManager()

# List all scanners
scanners = manager.list_all_scanners()

# Auto-select and scan
settings = ScanSettings(
    resolution=300,
    color_mode=ColorMode.COLOR
)

result = manager.scan(settings=settings)
```

## Data Classes

### ScannerInfo
```python
@dataclass
class ScannerInfo:
    id: str                    # Unique identifier
    name: str                  # Human-readable name
    driver: str                # Driver type
    manufacturer: str          # Manufacturer
    model: str                 # Model name
    connection: str            # Connection type
```

### ScanSettings
```python
@dataclass
class ScanSettings:
    resolution: int = 300      # DPI
    color_mode: ColorMode      # COLOR, GRAYSCALE, BLACK_WHITE
    format: str = "PNG"        # Output format
    width: float = None        # Scan area width (mm)
    height: float = None       # Scan area height (mm)
```

## Example Usage

### Basic Scan
```python
from scanners import ScannerManager

manager = ScannerManager()
manager.scan()  # Auto-select scanner, scan to timestamped file
```

### Advanced Scan
```python
from scanners import ScannerManager, ScanSettings, ColorMode
from pathlib import Path

manager = ScannerManager()

# Get preferred scanner
scanner = manager.get_preferred_scanner()
print(f"Using: {scanner.name} ({scanner.driver})")

# Configure settings
settings = ScanSettings(
    resolution=600,
    color_mode=ColorMode.GRAYSCALE
)

# Scan
output = manager.scan(
    scanner_info=scanner,
    output_path=Path("my_scan.png"),
    settings=settings
)
```

### List Scanners
```python
from scanners import ScannerManager

manager = ScannerManager()

# Show all available scanners
manager.print_available_scanners()

# Get list programmatically
for scanner in manager.list_all_scanners():
    print(f"{scanner.name} - {scanner.driver}")
```

## Error Handling

```python
from scanners import (
    ScannerManager,
    ScannerError,
    ScannerNotFoundError,
    ScannerIOError
)

manager = ScannerManager()

try:
    manager.scan()
except ScannerNotFoundError:
    print("Scanner not available")
except ScannerIOError:
    print("Scanner I/O error - may be in standby")
except ScannerError as e:
    print(f"Scan failed: {e}")
```

## Benefits

✅ **Flexibility**: Easy to add new drivers  
✅ **Portability**: Works across platforms  
✅ **Testability**: Simulation mode for testing  
✅ **Maintainability**: Clean separation of concerns  
✅ **Reliability**: Automatic fallback to working drivers  

## Current Status

| Driver     | Status | Platform       | Notes                    |
|------------|--------|----------------|--------------------------|
| eSCL       | ✅ Working | All        | **Recommended**          |
| SANE       | ⚠️ Issues  | macOS/Linux | I/O errors               |
| WIA        | ✅ Ready   | Windows    | Not tested               |
| Simulation | ✅ Working | All        | For testing              |

## Next Steps

- [ ] Implement mDNS scanner discovery for eSCL
- [ ] Add scanner capability detection
- [ ] Support ADF (document feeder)
- [ ] Add duplex scanning support
- [ ] Create web UI using driver architecture
- [ ] Add scanner settings profiles

