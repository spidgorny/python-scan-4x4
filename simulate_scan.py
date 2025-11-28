#!/usr/bin/env python3
"""
Simulation Mode: Create Simulated A4 Scans
Usage: python simulate_scan.py [output_path]

This script generates realistic A4 document scans for testing
without requiring scanner hardware.
"""

import sys
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_simulated_scan(output_path="scanned_document.png"):
    """
    Create a simulated A4 scan for demonstration purposes.
    This is used when no actual scanner hardware is available.
    
    Args:
        output_path: Where to save the simulated scan
    
    Returns:
        Path object to the saved file
    """
    print("\n📝 SIMULATION MODE - Generating A4 document...")
    print("(No scanner hardware required)\n")
    
    # A4 at 300 DPI: 2480 x 3508 pixels
    width, height = 2480, 3508
    
    # Create white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add some text and shapes to simulate a document
    # Draw a border
    border_width = 50
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline='black',
        width=3
    )
    
    # Add title text
    try:
        # Try to use a default font, fall back to default if not available
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add document content
    y_position = 200
    
    draw.text((width // 2, y_position), "SIMULATED A4 DOCUMENT", 
              fill='black', font=font_large, anchor="mm")
    
    y_position += 150
    draw.text((width // 2, y_position), "Proof of Concept - Scanner Demo", 
              fill='gray', font=font_medium, anchor="mm")
    
    y_position += 200
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((width // 2, y_position), f"Generated: {timestamp}", 
              fill='black', font=font_small, anchor="mm")
    
    y_position += 100
    draw.text((width // 2, y_position), "Resolution: 300 DPI", 
              fill='black', font=font_small, anchor="mm")
    
    y_position += 80
    draw.text((width // 2, y_position), f"Size: {width} x {height} pixels", 
              fill='black', font=font_small, anchor="mm")
    
    # Add quadrant markers (to help visualize 2x2 split)
    mid_x = width // 2
    mid_y = height // 2
    
    # Draw center cross
    draw.line([(mid_x, border_width), (mid_x, height - border_width)], 
              fill='lightgray', width=2)
    draw.line([(border_width, mid_y), (width - border_width, mid_y)], 
              fill='lightgray', width=2)
    
    # Label quadrants
    quadrant_labels = [
        ("Quadrant 1", mid_x // 2, mid_y // 2),
        ("Quadrant 2", mid_x + mid_x // 2, mid_y // 2),
        ("Quadrant 3", mid_x // 2, mid_y + mid_y // 2),
        ("Quadrant 4", mid_x + mid_x // 2, mid_y + mid_y // 2),
    ]
    
    for label, x, y in quadrant_labels:
        draw.text((x, y), label, fill='lightblue', font=font_medium, anchor="mm")
    
    # Add some sample content blocks
    y_position = height - 400
    draw.text((width // 2, y_position), 
              "This simulated document will be split into 4 equal parts", 
              fill='black', font=font_small, anchor="mm")
    
    y_position += 80
    draw.text((width // 2, y_position), 
              "Use this for testing without a physical scanner", 
              fill='darkgreen', font=font_small, anchor="mm")
    
    # Save the simulated scan
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_file, 'PNG', dpi=(300, 300))
    
    print(f"✓ Simulated scan complete!")
    print(f"  Saved to: {output_file.absolute()}")
    print(f"  Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"  Dimensions: {image.size[0]} x {image.size[1]} pixels")
    print(f"  DPI: 300 x 300")
    
    return output_file


def main():
    """Main entry point."""
    print("=" * 60)
    print("A4 Document Simulator")
    print("=" * 60)
    
    # Generate output filename with timestamp
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"simulated_scan_{timestamp}.png"
    
    try:
        create_simulated_scan(output_path)
        
        print("\n💡 Next Steps:")
        print(f"  Split the image: uv run poc_split.py {output_path}")
        print(f"  Or use workflow: uv run scan_and_split.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
