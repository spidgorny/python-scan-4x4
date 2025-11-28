#!/usr/bin/env python3
"""
Proof of Concept: Split Scanned Image into 2x2 Grid
Usage: python poc_split.py <input_image> [output_dir]
"""

import sys
from pathlib import Path
from PIL import Image


def split_image_2x2(input_path, output_dir="output"):
    """
    Split an image into a 2x2 grid (4 equal parts).
    
    Args:
        input_path: Path to input image
        output_dir: Directory to save split images
    
    Returns:
        List of output file paths
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"Loading image: {input_file.name}")
    img = Image.open(input_file)
    width, height = img.size
    print(f"  Dimensions: {width} x {height} pixels")
    print(f"  Mode: {img.mode}")
    print(f"  Format: {img.format}")
    
    # Calculate split points
    mid_x = width // 2
    mid_y = height // 2
    
    print(f"\nSplitting into 2x2 grid...")
    print(f"  Each part: {mid_x} x {mid_y} pixels")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Define quadrants
    # Format: (left, top, right, bottom)
    quadrants = {
        "1_top_left": (0, 0, mid_x, mid_y),
        "2_top_right": (mid_x, 0, width, mid_y),
        "3_bottom_left": (0, mid_y, mid_x, height),
        "4_bottom_right": (mid_x, mid_y, width, height)
    }
    
    output_files = []
    
    # Crop and save each quadrant
    for name, box in quadrants.items():
        print(f"  Cropping {name}... ", end="")
        
        cropped = img.crop(box)
        
        # Generate output filename
        base_name = input_file.stem  # filename without extension
        output_file = output_path / f"{base_name}_{name}.png"
        
        cropped.save(output_file, "PNG")
        output_files.append(output_file)
        
        file_size = output_file.stat().st_size / 1024  # KB
        print(f"✓ ({file_size:.1f} KB)")
    
    img.close()
    
    return output_files


def main():
    """Main entry point."""
    print("=" * 60)
    print("Image Splitter - 2x2 Grid POC")
    print("=" * 60)
    print()
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python poc_split.py <input_image> [output_dir]")
        print()
        print("Example:")
        print("  python poc_split.py scan_20241128_173000.png")
        print("  python poc_split.py scan.png output_images/")
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    try:
        output_files = split_image_2x2(input_image, output_dir)
        
        print(f"\n✓ Split complete!")
        print(f"  Output directory: {Path(output_dir).absolute()}")
        print(f"  Generated {len(output_files)} images:")
        for f in output_files:
            print(f"    - {f.name}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
