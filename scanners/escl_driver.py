"""
eSCL (AirScan) scanner driver

Uses HTTP-based eSCL protocol. Works on macOS, Linux, and Windows.
This is what NAPS2 uses for "Apple driver" on macOS.
"""

import requests
import urllib3
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET

from .base import (
    ScannerDriver,
    ScannerInfo,
    ScanSettings,
    ColorMode,
    ScannerError,
    ScannerNotFoundError,
    ScannerIOError,
)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ESCLDriver(ScannerDriver):
    """
    eSCL (AirScan) scanner driver.
    
    Uses HTTP-based protocol to communicate with network scanners.
    """
    
    def __init__(self):
        self.timeout = 10  # Default timeout for HTTP requests
        self.scan_timeout = 120  # Timeout for actual scanning
    
    def get_driver_name(self) -> str:
        return "eSCL"
    
    def is_available(self) -> bool:
        """eSCL is available if requests library is installed"""
        try:
            import requests
            return True
        except ImportError:
            return False
    
    def list_scanners(self) -> List[ScannerInfo]:
        """
        Discover eSCL scanners via mDNS/Bonjour.
        
        For now, returns known scanner. Future: implement mDNS discovery.
        """
        # TODO: Implement proper mDNS discovery using zeroconf library
        # For now, return the known Epson scanner
        
        scanners = []
        
        # Try known scanner
        scanner_url = "https://EPSON3BA687.local:443/eSCL"
        try:
            response = requests.get(
                f"{scanner_url}/ScannerCapabilities",
                verify=False,
                timeout=5
            )
            
            if response.status_code == 200:
                # Parse scanner info from capabilities
                root = ET.fromstring(response.content)
                ns = {'scan': 'http://schemas.hp.com/imaging/escl/2011/05/03'}
                
                make = root.find('.//scan:Make', ns)
                model = root.find('.//scan:Model', ns)
                
                scanner_info = ScannerInfo(
                    id=scanner_url,
                    name=f"{make.text if make is not None else 'Unknown'} {model.text if model is not None else 'Scanner'}",
                    driver="escl",
                    manufacturer=make.text if make is not None else None,
                    model=model.text if model is not None else None,
                    connection="network"
                )
                scanners.append(scanner_info)
        except Exception:
            # Scanner not available or not responding
            pass
        
        return scanners
    
    def scan(
        self,
        scanner_id: str,
        output_path: Path,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Scan using eSCL protocol.
        
        Args:
            scanner_id: eSCL URL (e.g., https://scanner.local:443/eSCL)
            output_path: Where to save scan
            settings: Scan settings
        
        Returns:
            Path to saved scan
        """
        if settings is None:
            settings = ScanSettings()
        
        # Map color mode to eSCL
        escl_color_mode = {
            ColorMode.COLOR: "RGB24",
            ColorMode.GRAYSCALE: "Grayscale8",
            ColorMode.BLACK_WHITE: "BlackAndWhite1"
        }.get(settings.color_mode, "RGB24")
        
        # A4 dimensions in 1/300ths of an inch
        # A4 = 210mm x 297mm = 8.27" x 11.69"
        width_300ths = int(8.27 * 300) if settings.width is None else int(settings.width / 25.4 * 300)
        height_300ths = int(11.69 * 300) if settings.height is None else int(settings.height / 25.4 * 300)
        
        # Create scan settings XML
        scan_settings_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
    <pwg:Version>2.0</pwg:Version>
    <pwg:ScanRegions>
        <pwg:ScanRegion>
            <pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches</pwg:ContentRegionUnits>
            <pwg:XOffset>{int(settings.x_offset / 25.4 * 300) if settings.x_offset else 0}</pwg:XOffset>
            <pwg:YOffset>{int(settings.y_offset / 25.4 * 300) if settings.y_offset else 0}</pwg:YOffset>
            <pwg:Width>{width_300ths}</pwg:Width>
            <pwg:Height>{height_300ths}</pwg:Height>
        </pwg:ScanRegion>
    </pwg:ScanRegions>
    <scan:InputSource>Platen</scan:InputSource>
    <scan:ColorMode>{escl_color_mode}</scan:ColorMode>
    <scan:XResolution>{settings.resolution}</scan:XResolution>
    <scan:YResolution>{settings.resolution}</scan:YResolution>
</scan:ScanSettings>"""
        
        try:
            # POST scan job
            response = requests.post(
                f"{scanner_id}/ScanJobs",
                data=scan_settings_xml,
                headers={'Content-Type': 'text/xml'},
                verify=False,
                timeout=self.timeout
            )
            
            if response.status_code != 201:
                raise ScannerIOError(f"Failed to create scan job: HTTP {response.status_code}")
            
            # Get job location
            job_url = response.headers.get('Location')
            if not job_url:
                raise ScannerIOError("No job location in response")
            
            # Get the scanned document
            doc_url = f"{job_url}/NextDocument"
            response = requests.get(
                doc_url,
                verify=False,
                timeout=self.scan_timeout
            )
            
            if response.status_code != 200:
                # Clean up job before raising error
                try:
                    requests.delete(job_url, verify=False, timeout=5)
                except:
                    pass
                raise ScannerIOError(f"Failed to get document: HTTP {response.status_code}")
            
            # Check content type and convert if needed
            content_type = response.headers.get('Content-Type', '').lower()
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # If scanner returns PDF or JPEG, convert to PNG if requested
                if 'pdf' in content_type and str(output_file).lower().endswith('.png'):
                    # Convert PDF to PNG
                    try:
                        from PIL import Image
                        import io
                        from pdf2image import convert_from_bytes
                        
                        # Convert PDF to images (usually just one page for scanner)
                        images = convert_from_bytes(response.content)
                        if images:
                            images[0].save(output_file, 'PNG')
                        else:
                            raise ScannerError("PDF conversion resulted in no images")
                    except ImportError:
                        # pdf2image not available, save as-is but warn
                        raise ScannerError(
                            "Scanner returned PDF but pdf2image not installed. "
                            "Install with: uv add pdf2image pillow"
                        )
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    # If scanner returns JPEG, convert to PNG if needed
                    if str(output_file).lower().endswith('.png'):
                        from PIL import Image
                        import io
                        
                        image = Image.open(io.BytesIO(response.content))
                        image.save(output_file, 'PNG')
                    else:
                        output_file.write_bytes(response.content)
                else:
                    # Save as-is
                    output_file.write_bytes(response.content)
            finally:
                # Always delete the scan job to clean up and reset scanner state
                try:
                    requests.delete(job_url, verify=False, timeout=5)
                except:
                    pass  # Ignore errors during cleanup
            
            return output_file
            
        except requests.exceptions.Timeout:
            raise ScannerIOError("Scan timed out - scanner may be in standby mode")
        except requests.exceptions.ConnectionError:
            raise ScannerNotFoundError(f"Cannot connect to scanner at {scanner_id}")
        except Exception as e:
            if isinstance(e, ScannerError):
                raise
            raise ScannerError(f"Scan failed: {e}")
