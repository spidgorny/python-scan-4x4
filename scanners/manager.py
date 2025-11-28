"""
Scanner Manager

Automatically detects and uses the best available scanner driver.
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .base import ScannerDriver, ScannerInfo, ScanSettings, ScannerError
from .escl_driver import ESCLDriver
from .sane_driver import SANEDriver
from .wia_driver import WIADriver
from .simulation_driver import SimulationDriver


class ScannerManager:
    """
    Manages multiple scanner drivers and automatically selects the best one.
    
    Preference order:
    1. eSCL (most reliable, works everywhere)
    2. SANE (Linux/macOS traditional)
    3. WIA (Windows)
    4. Simulation (fallback for testing)
    """
    
    def __init__(self):
        # Initialize all drivers
        self.drivers = [
            ESCLDriver(),
            SANEDriver(),
            WIADriver(),
            SimulationDriver(),
        ]
    
    def get_available_drivers(self) -> List[ScannerDriver]:
        """Get list of available drivers on this system"""
        return [driver for driver in self.drivers if driver.is_available()]
    
    def list_all_scanners(self) -> List[ScannerInfo]:
        """
        List all scanners from all available drivers.
        
        Returns:
            List of ScannerInfo from all drivers
        """
        all_scanners = []
        
        for driver in self.get_available_drivers():
            try:
                scanners = driver.list_scanners()
                all_scanners.extend(scanners)
            except Exception:
                # Driver failed to list scanners, skip it
                continue
        
        return all_scanners
    
    def get_preferred_scanner(self) -> Optional[ScannerInfo]:
        """
        Get the preferred scanner (first non-simulation scanner found).
        
        Returns:
            ScannerInfo or None if no scanner found
        """
        scanners = self.list_all_scanners()
        
        # Prefer non-simulation scanners
        for scanner in scanners:
            if scanner.driver != "simulation":
                return scanner
        
        # Return simulation if nothing else
        return scanners[0] if scanners else None
    
    def get_driver_for_scanner(self, scanner_info: ScannerInfo) -> Optional[ScannerDriver]:
        """
        Get the driver instance for a specific scanner.
        
        Args:
            scanner_info: Scanner information
        
        Returns:
            ScannerDriver instance or None
        """
        for driver in self.drivers:
            if driver.get_driver_name().lower() == scanner_info.driver.lower():
                return driver
        return None
    
    def scan(
        self,
        scanner_info: Optional[ScannerInfo] = None,
        output_path: Optional[Path] = None,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Scan using the specified scanner or auto-select one.
        
        Args:
            scanner_info: Scanner to use (None = auto-select)
            output_path: Where to save (None = generate timestamped filename)
            settings: Scan settings (None = use defaults)
        
        Returns:
            Path to scanned image
        
        Raises:
            ScannerError: If scan fails or no scanner available
        """
        # Auto-select scanner if not specified
        if scanner_info is None:
            scanner_info = self.get_preferred_scanner()
            if scanner_info is None:
                raise ScannerError("No scanners available")
        
        # Generate output path if not specified
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"scan_{timestamp}.png")
        
        # Get driver for this scanner
        driver = self.get_driver_for_scanner(scanner_info)
        if driver is None:
            raise ScannerError(f"No driver available for {scanner_info.driver}")
        
        # Perform scan
        return driver.scan(scanner_info.id, output_path, settings)
    
    def print_available_scanners(self):
        """Print information about available scanners"""
        print("=" * 60)
        print("Available Scanner Drivers")
        print("=" * 60)
        print()
        
        available_drivers = self.get_available_drivers()
        
        if not available_drivers:
            print("✗ No scanner drivers available!")
            print("\nInstall:")
            print("  macOS/Linux: brew install sane-backends && uv add python-sane")
            print("  Windows: uv add pywin32")
            return
        
        for driver in available_drivers:
            print(f"✓ {driver.get_driver_name()} driver available")
        
        print()
        print("=" * 60)
        print("Detected Scanners")
        print("=" * 60)
        print()
        
        scanners = self.list_all_scanners()
        
        if not scanners:
            print("✗ No scanners found!")
            print("\nMake sure:")
            print("  - Scanner is powered on")
            print("  - Scanner is connected (USB/network)")
            print("  - Scanner drivers are installed")
            return
        
        for i, scanner in enumerate(scanners, 1):
            print(f"[{i}] {scanner.name}")
            print(f"    Driver: {scanner.driver}")
            print(f"    ID: {scanner.id}")
            if scanner.manufacturer:
                print(f"    Manufacturer: {scanner.manufacturer}")
            if scanner.model:
                print(f"    Model: {scanner.model}")
            if scanner.connection:
                print(f"    Connection: {scanner.connection}")
            print()
