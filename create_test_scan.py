#!/usr/bin/env python3
"""
Generate a realistic simulated scan with 4 separate photos
"""

import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_test_scan_with_photos(output_path: str = "output/test_4photos.png"):
    """
    Create a simulated A4 scan with 4 distinct photos arranged in 2x2 grid.
    Photos will have clear edges and slight rotation for testing.
    """
    print("Creating test scan with 4 distinct photos...")
    
    # A4 at 300 DPI
    width = 2480
    height = 3508
    
    # Create white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Define 2x2 grid with spacing
    margin = 200
    spacing = 100
    
    photo_width = (width - 2 * margin - spacing) // 2
    photo_height = (height - 2 * margin - spacing) // 2
    
    # Define 4 photo positions (with slight rotation)
    photos = [
        # Top-left
        {
            'x': margin,
            'y': margin,
            'width': photo_width,
            'height': photo_height,
            'rotation': 2,
            'color': (240, 230, 220),
            'label': 'Photo 1'
        },
        # Top-right
        {
            'x': margin + photo_width + spacing,
            'y': margin,
            'width': photo_width,
            'height': photo_height,
            'rotation': -1,
            'color': (220, 235, 240),
            'label': 'Photo 2'
        },
        # Bottom-left
        {
            'x': margin,
            'y': margin + photo_height + spacing,
            'width': photo_width,
            'height': photo_height,
            'rotation': -2,
            'color': (235, 220, 240),
            'label': 'Photo 3'
        },
        # Bottom-right
        {
            'x': margin + photo_width + spacing,
            'y': margin + photo_height + spacing,
            'width': photo_width,
            'height': photo_height,
            'rotation': 1,
            'color': (240, 240, 220),
            'label': 'Photo 4'
        },
    ]
    
    # Draw each photo
    for photo_info in photos:
        # Create individual photo
        photo = Image.new('RGB', (photo_info['width'], photo_info['height']), 
                         color=photo_info['color'])
        photo_draw = ImageDraw.Draw(photo)
        
        # Add border
        border_width = 15
        photo_draw.rectangle(
            [(border_width, border_width),
             (photo_info['width'] - border_width, photo_info['height'] - border_width)],
            outline='gray',
            width=10
        )
        
        # Add label
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        except:
            font = ImageFont.load_default()
        
        # Get text size for centering
        bbox = photo_draw.textbbox((0, 0), photo_info['label'], font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (photo_info['width'] - text_width) // 2
        text_y = (photo_info['height'] - text_height) // 2
        
        photo_draw.text(
            (text_x, text_y),
            photo_info['label'],
            fill='black',
            font=font
        )
        
        # Add some visual elements (simulated photo content)
        # Draw a rectangle pattern
        for i in range(3):
            offset = 60 + i * 40
            photo_draw.rectangle(
                [(offset, offset),
                 (photo_info['width'] - offset, photo_info['height'] - offset)],
                outline=(100, 100, 100),
                width=2
            )
        
        # Rotate slightly
        if photo_info['rotation'] != 0:
            photo = photo.rotate(photo_info['rotation'], expand=True, fillcolor='white')
        
        # Paste onto main image
        paste_x = photo_info['x']
        paste_y = photo_info['y']
        
        # Adjust position if rotated (rotation expands the image)
        if photo_info['rotation'] != 0:
            paste_x -= (photo.width - photo_info['width']) // 2
            paste_y -= (photo.height - photo_info['height']) // 2
        
        image.paste(photo, (paste_x, paste_y))
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file, 'PNG', dpi=(300, 300))
    
    print(f"✓ Created: {output_file}")
    print(f"  Size: {width}x{height} pixels")
    print(f"  4 photos with slight rotation (±1-2°)")
    
    return output_file


if __name__ == "__main__":
    import sys
    
    output = sys.argv[1] if len(sys.argv) > 1 else "output/test_4photos.png"
    create_test_scan_with_photos(output)
