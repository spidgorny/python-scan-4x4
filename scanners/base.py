"""
Base scanner driver interface

All scanner drivers must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from enum import Enum


class ColorMode(Enum):
    """Scan color modes"""
    COLOR = "color"
    GRAYSCALE = "grayscale"
    BLACK_WHITE = "bw"


@dataclass
class ScanSettings:
    """Scanner settings for a scan job"""
    resolution: int = 300  # DPI
    color_mode: ColorMode = ColorMode.COLOR
    format: str = "PNG"  # Output format (PNG, JPEG)
    
    # Optional scan area (in mm, None = full area)
    width: Optional[float] = None
    height: Optional[float] = None
    x_offset: Optional[float] = 0
    y_offset: Optional[float] = 0


@dataclass
class ScannerInfo:
    """Information about a detected scanner"""
    id: str  # Unique identifier
    name: str  # Human-readable name
    driver: str  # Driver type (escl, sane, wia, simulation)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    connection: Optional[str] = None  # network, usb, etc.


class ScannerDriver(ABC):
    """
    Abstract base class for scanner drivers.
    
    All scanner drivers (eSCL, SANE, WIA, etc.) must implement this interface.
    """
    
    @abstractmethod
    def list_scanners(self) -> List[ScannerInfo]:
        """
        List all available scanners for this driver.
        
        Returns:
            List of ScannerInfo objects
        """
        pass
    
    @abstractmethod
    def scan(
        self,
        scanner_id: str,
        output_path: Path,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Scan a document.
        
        Args:
            scanner_id: Scanner identifier from list_scanners()
            output_path: Where to save the scanned image
            settings: Scan settings (resolution, color mode, etc.)
        
        Returns:
            Path to the saved scan
        
        Raises:
            ScannerNotFoundError: If scanner_id is not found
            ScannerError: If scan fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this driver is available on the current system.
        
        Returns:
            True if driver can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_driver_name(self) -> str:
        """
        Get the name of this driver.
        
        Returns:
            Driver name (e.g., "eSCL", "SANE", "WIA")
        """
        pass


class ScannerError(Exception):
    """Base exception for scanner errors"""
    pass


class ScannerNotFoundError(ScannerError):
    """Scanner not found or not available"""
    pass


class ScannerIOError(ScannerError):
    """Scanner I/O error (communication, hardware issue)"""
    pass


class ScannerNotAvailableError(ScannerError):
    """Driver not available on this system"""
    pass
