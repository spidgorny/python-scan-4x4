"""
SANE scanner driver

Uses SANE backend for scanning on Linux and macOS.
"""

from pathlib import Path
from typing import List, Optional

from .base import (
    ScannerDriver,
    ScannerInfo,
    ScanSettings,
    ColorMode,
    ScannerError,
    ScannerNotFoundError,
    ScannerIOError,
    ScannerNotAvailableError,
)


class SANEDriver(ScannerDriver):
    """
    SANE scanner driver.
    
    Uses python-sane library to interface with SANE backends.
    """
    
    def __init__(self):
        self._sane_available = False
        self._sane = None
        
        try:
            import sane
            self._sane = sane
            self._sane_available = True
        except ImportError:
            pass
    
    def get_driver_name(self) -> str:
        return "SANE"
    
    def is_available(self) -> bool:
        """SANE is available if python-sane is installed"""
        return self._sane_available
    
    def list_scanners(self) -> List[ScannerInfo]:
        """List all SANE scanners"""
        if not self._sane_available:
            return []
        
        scanners = []
        
        try:
            self._sane.init()
            devices = self._sane.get_devices()
            
            for device_id, manufacturer, model, device_type in devices:
                scanner_info = ScannerInfo(
                    id=device_id,
                    name=f"{manufacturer} {model}",
                    driver="sane",
                    manufacturer=manufacturer,
                    model=model,
                    connection="network" if "net:" in device_id else "usb"
                )
                scanners.append(scanner_info)
            
            self._sane.exit()
            
        except Exception:
            # SANE initialization failed
            pass
        
        return scanners
    
    def scan(
        self,
        scanner_id: str,
        output_path: Path,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Scan using SANE.
        
        Args:
            scanner_id: SANE device ID (e.g., epson2:net:192.168.1.208)
            output_path: Where to save scan
            settings: Scan settings
        
        Returns:
            Path to saved scan
        """
        if not self._sane_available:
            raise ScannerNotAvailableError("SANE is not available")
        
        if settings is None:
            settings = ScanSettings()
        
        # Map color mode to SANE
        sane_mode = {
            ColorMode.COLOR: "Color",
            ColorMode.GRAYSCALE: "Gray",
            ColorMode.BLACK_WHITE: "Lineart"
        }.get(settings.color_mode, "Color")
        
        try:
            self._sane.init()
            
            # Open scanner
            scanner = self._sane.open(scanner_id)
            
            # Configure scanner
            # Set source to Flatbed if available
            if 'source' in scanner.opt:
                available_sources = scanner.opt['source'].constraint
                if scanner.opt['source'].is_active():
                    flatbed_names = ['Flatbed', 'FlatBed', 'Platen', 'Normal']
                    for source_name in flatbed_names:
                        if source_name in available_sources:
                            try:
                                scanner.source = source_name
                                break
                            except AttributeError:
                                pass
            
            # Set mode and resolution
            scanner.mode = sane_mode
            scanner.resolution = settings.resolution
            
            # Scan with retry logic (scanner may need warm-up)
            max_retries = 3
            retry_delay = 2
            
            image = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        import time
                        time.sleep(retry_delay)
                    
                    scanner.start()
                    image = scanner.snap()
                    break
                    
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise
            
            if image is None:
                raise ScannerIOError(f"Scan failed: {last_error}")
            
            # Save image
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_file)
            
            scanner.close()
            self._sane.exit()
            
            return output_file
            
        except Exception as e:
            if isinstance(e, ScannerError):
                raise
            
            # Try to clean up
            try:
                self._sane.exit()
            except:
                pass
            
            # Map SANE errors to our exceptions
            error_msg = str(e).lower()
            if "device i/o" in error_msg:
                raise ScannerIOError(
                    "Scanner I/O error - scanner may be in standby mode. "
                    "Try pressing a button on the scanner to wake it up."
                )
            elif "invalid argument" in error_msg or "not found" in error_msg:
                raise ScannerNotFoundError(f"Scanner not found: {scanner_id}")
            else:
                raise ScannerError(f"SANE scan failed: {e}")
