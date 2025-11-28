"""
Simulation scanner driver

Generates simulated A4 scans for testing without hardware.
"""

from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from .base import (
    ScannerDriver,
    ScannerInfo,
    ScanSettings,
    ColorMode,
    ScannerError,
)


class SimulationDriver(ScannerDriver):
    """
    Simulation scanner driver.
    
    Generates realistic-looking scanned documents for testing.
    """
    
    def get_driver_name(self) -> str:
        return "Simulation"
    
    def is_available(self) -> bool:
        """Simulation is always available if Pillow is installed"""
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def list_scanners(self) -> List[ScannerInfo]:
        """Return a single simulated scanner"""
        return [
            ScannerInfo(
                id="simulation:virtual",
                name="Simulated A4 Scanner",
                driver="simulation",
                manufacturer="Virtual",
                model="Test Scanner",
                connection="virtual"
            )
        ]
    
    def scan(
        self,
        scanner_id: str,
        output_path: Path,
        settings: Optional[ScanSettings] = None
    ) -> Path:
        """
        Generate a simulated scan.
        
        Args:
            scanner_id: Must be "simulation:virtual"
            output_path: Where to save simulated scan
            settings: Scan settings (resolution, color mode)
        
        Returns:
            Path to saved scan
        """
        if settings is None:
            settings = ScanSettings()
        
        # Calculate image size based on resolution
        # A4 = 210mm x 297mm = 8.27" x 11.69"
        width_inches = 8.27
        height_inches = 11.69
        width_px = int(width_inches * settings.resolution)
        height_px = int(height_inches * settings.resolution)
        
        # Create image based on color mode
        if settings.color_mode == ColorMode.COLOR:
            image = Image.new('RGB', (width_px, height_px), color='white')
        elif settings.color_mode == ColorMode.GRAYSCALE:
            image = Image.new('L', (width_px, height_px), color=255)
        else:  # BLACK_WHITE
            image = Image.new('1', (width_px, height_px), color=1)
        
        # Only add content for color/grayscale
        if settings.color_mode != ColorMode.BLACK_WHITE:
            draw = ImageDraw.Draw(image)
            
            # Draw border
            border_width = int(width_px * 0.02)
            draw.rectangle(
                [(border_width, border_width), 
                 (width_px - border_width, height_px - border_width)],
                outline='black',
                width=3
            )
            
            # Try to use system font
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                               int(settings.resolution / 3.75))
                font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                                 int(settings.resolution / 6))
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 
                                               int(settings.resolution / 7.5))
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add title
            y_pos = int(height_px * 0.1)
            draw.text((width_px // 2, y_pos), "SIMULATED A4 DOCUMENT",
                     fill='black', font=font_large, anchor="mm")
            
            y_pos += int(height_px * 0.08)
            draw.text((width_px // 2, y_pos), "Proof of Concept - Scanner Test",
                     fill='gray', font=font_medium, anchor="mm")
            
            # Add metadata
            y_pos += int(height_px * 0.1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            draw.text((width_px // 2, y_pos), f"Generated: {timestamp}",
                     fill='black', font=font_small, anchor="mm")
            
            y_pos += int(height_px * 0.05)
            draw.text((width_px // 2, y_pos), f"Resolution: {settings.resolution} DPI",
                     fill='black', font=font_small, anchor="mm")
            
            y_pos += int(height_px * 0.04)
            draw.text((width_px // 2, y_pos), f"Size: {width_px} x {height_px} pixels",
                     fill='black', font=font_small, anchor="mm")
            
            y_pos += int(height_px * 0.04)
            draw.text((width_px // 2, y_pos), f"Mode: {settings.color_mode.value}",
                     fill='black', font=font_small, anchor="mm")
            
            # Draw quadrant markers
            mid_x = width_px // 2
            mid_y = height_px // 2
            
            draw.line([(mid_x, border_width), (mid_x, height_px - border_width)],
                     fill='lightgray', width=2)
            draw.line([(border_width, mid_y), (width_px - border_width, mid_y)],
                     fill='lightgray', width=2)
            
            # Label quadrants
            quadrants = [
                ("Q1", mid_x // 2, mid_y // 2),
                ("Q2", mid_x + mid_x // 2, mid_y // 2),
                ("Q3", mid_x // 2, mid_y + mid_y // 2),
                ("Q4", mid_x + mid_x // 2, mid_y + mid_y // 2),
            ]
            
            for label, x, y in quadrants:
                draw.text((x, y), label, fill='lightblue', 
                         font=font_medium, anchor="mm")
            
            # Add footer
            y_pos = int(height_px * 0.85)
            draw.text((width_px // 2, y_pos),
                     "This simulated document will be split into 4 equal parts",
                     fill='black', font=font_small, anchor="mm")
            
            y_pos += int(height_px * 0.04)
            draw.text((width_px // 2, y_pos),
                     "Use for testing without a physical scanner",
                     fill='darkgreen', font=font_small, anchor="mm")
        
        # Save image
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_file, 'PNG', dpi=(settings.resolution, settings.resolution))
        
        return output_file
