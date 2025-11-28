"""
WIA (Windows Image Acquisition) scanner driver

Uses WIA for scanning on Windows.
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


class WIADriver(ScannerDriver):
    """
    Windows Image Acquisition scanner driver.
    
    Uses win32com to interface with WIA.
    Only available on Windows.
    """
    
    def __init__(self):
        self._wia_available = False
        
        try:
            import win32com.client
            self._wia_available = True
        except ImportError:
            pass
    
    def get_driver_name(self) -> str:
        return "WIA"
    
    def is_available(self) -> bool:
        """WIA is only available on Windows with pywin32"""
        return self._wia_available
    
    def list_scanners(self) -> List[ScannerInfo]:
        """List all WIA scanners"""
        if not self._wia_available:
            return []
        
        scanners = []
        
        try:
            import win32com.client
            
            device_manager = win32com.client.Dispatch("WIA.DeviceManager")
            
            for i in range(1, device_manager.DeviceInfos.Count + 1):
                device_info = device_manager.DeviceInfos[i]
                
                try:
                    name = device_info.Properties('Name').Value
                    device_id = str(i)  # Use index as ID
                    
                    scanner_info = ScannerInfo(
                        id=device_id,
                        name=name,
                        driver="wia",
                        manufacturer=None,  # Could extract from name
                        model=None,
                        connection="unknown"
                    )
                    scanners.append(scanner_info)
                except:
                    continue
                    
        except Exception:
            # WIA initialization failed
            pass
        
        return scanners
    
    def scan(
        self,
        scanner_id: str,
        output_path: Path,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Scan using WIA.
        
        Args:
            scanner_id: WIA device index
            output_path: Where to save scan
            settings: Scan settings
        
        Returns:
            Path to saved scan
        """
        if not self._wia_available:
            raise ScannerNotAvailableError("WIA is not available (Windows only)")
        
        if settings is None:
            settings = ScanSettings()
        
        try:
            import win32com.client
            
            device_manager = win32com.client.Dispatch("WIA.DeviceManager")
            
            # Get device by ID (index)
            device_index = int(scanner_id)
            if device_index < 1 or device_index > device_manager.DeviceInfos.Count:
                raise ScannerNotFoundError(f"Invalid scanner ID: {scanner_id}")
            
            device_info = device_manager.DeviceInfos[device_index]
            device = device_info.Connect()
            
            # Get scanner item
            item = device.Items[1]
            
            # Configure scanner
            # Note: WIA property IDs:
            # 6146 = Color mode (1=BW, 2=Gray, 4=Color)
            # 6147 = Resolution
            
            try:
                if settings.color_mode == ColorMode.COLOR:
                    item.Properties("6146").Value = 4
                elif settings.color_mode == ColorMode.GRAYSCALE:
                    item.Properties("6146").Value = 2
                elif settings.color_mode == ColorMode.BLACK_WHITE:
                    item.Properties("6146").Value = 1
                
                item.Properties("6147").Value = settings.resolution
            except:
                # Some scanners don't support these properties
                pass
            
            # Scan
            # {B96B3CAE-0728-11D3-9D7B-0000F81EF32E} = PNG format
            # {B96B3CAF-0728-11D3-9D7B-0000F81EF32E} = JPEG format
            format_guid = "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}"  # PNG
            
            image = item.Transfer(format_guid)
            
            # Save
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            image.SaveFile(str(output_file.absolute()))
            
            return output_file
            
        except Exception as e:
            if isinstance(e, ScannerError):
                raise
            raise ScannerError(f"WIA scan failed: {e}")
