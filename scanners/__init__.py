"""
Scanner drivers package

This package provides a common interface for different scanner backends:
- eSCL (AirScan) - HTTP-based protocol, works on macOS/Linux/Windows
- SANE - Linux/macOS traditional scanner backend
- WIA - Windows Image Acquisition
- Simulation - For testing without hardware
"""

from .base import ScannerDriver, ScannerInfo, ScanSettings, ColorMode
from .escl_driver import ESCLDriver
from .sane_driver import SANEDriver
from .wia_driver import WIADriver
from .simulation_driver import SimulationDriver
from .manager import ScannerManager

__all__ = [
    'ScannerDriver',
    'ScannerInfo',
    'ScanSettings',
    'ColorMode',
    'ESCLDriver',
    'SANEDriver',
    'WIADriver',
    'SimulationDriver',
    'ScannerManager',
]
