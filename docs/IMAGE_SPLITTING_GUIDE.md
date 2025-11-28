# Image Splitting Guide - 2x2 Grid

## Objective
Split a scanned A4 document into 4 equal parts (2x2 grid) using Pillow.

## Concept
```
Original A4 Image (2480 x 3508 @ 300 DPI)
┌─────────────────────────┐
│                         │
│    Top-Left   Top-Right │
│       [1]        [2]    │
│                         │
├───────────┬─────────────┤
│                         │
│  Bottom-Left Bottom-Right│
│       [3]        [4]    │
│                         │
└─────────────────────────┘

Each quadrant: 1240 x 1754 pixels
```

## Algorithm

### 1. Load Image
```python
from PIL import Image

img = Image.open("scanned_document.png")
width, height = img.size
```

### 2. Calculate Split Points
```python
# Divide into 2 equal columns and 2 equal rows
mid_x = width // 2
mid_y = height // 2

# Define crop boxes (left, top, right, bottom)
boxes = {
    "top_left": (0, 0, mid_x, mid_y),
    "top_right": (mid_x, 0, width, mid_y),
    "bottom_left": (0, mid_y, mid_x, height),
    "bottom_right": (mid_x, mid_y, width, height)
}
```

### 3. Crop and Save
```python
for name, box in boxes.items():
    cropped = img.crop(box)
    cropped.save(f"output_{name}.png")
```

## POC Script: `poc_split.py`

```python
#!/usr/bin/env python3
"""
Proof of Concept: Split Scanned Image into 2x2 Grid
Usage: python poc_split.py <input_image>
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
        print("  python poc_split.py scan_20251128_172859.png")
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
```

## Advanced Features

### Handle Different Aspect Ratios
```python
def split_image_2x2_exact(img, overlap_px=0):
    """Split with optional overlap to avoid cutting content."""
    width, height = img.size
    mid_x = width // 2
    mid_y = height // 2
    
    quadrants = {
        "top_left": (0, 0, mid_x + overlap_px, mid_y + overlap_px),
        "top_right": (mid_x - overlap_px, 0, width, mid_y + overlap_px),
        "bottom_left": (0, mid_y - overlap_px, mid_x + overlap_px, height),
        "bottom_right": (mid_x - overlap_px, mid_y - overlap_px, width, height)
    }
    
    return quadrants
```

### Add Margins/Padding
```python
def split_with_margin(img, margin_percent=5):
    """Split with margin to avoid edge content loss."""
    width, height = img.size
    margin_x = int(width * margin_percent / 100)
    margin_y = int(height * margin_percent / 100)
    
    # Crop out margins first
    img_cropped = img.crop((
        margin_x,
        margin_y,
        width - margin_x,
        height - margin_y
    ))
    
    # Then split
    return split_image_2x2(img_cropped)
```

### Quality Control
```python
def split_with_quality(input_path, output_dir, quality=95):
    """Split and save with specific JPEG quality."""
    # ... crop as before ...
    
    for name, box in quadrants.items():
        cropped = img.crop(box)
        output_file = output_path / f"{base_name}_{name}.jpg"
        
        cropped.save(
            output_file,
            "JPEG",
            quality=quality,
            optimize=True
        )
```

### Maintain DPI Information
```python
def split_preserve_dpi(input_path, output_dir):
    """Split while preserving DPI metadata."""
    img = Image.open(input_path)
    
    # Get DPI info
    dpi = img.info.get('dpi', (300, 300))
    
    for name, box in quadrants.items():
        cropped = img.crop(box)
        
        cropped.save(
            output_file,
            dpi=dpi  # Preserve original DPI
        )
```

## Testing Checklist

- [ ] Splits A4 portrait (2480x3508) correctly
- [ ] Splits A4 landscape (3508x2480) correctly
- [ ] Handles odd dimensions (e.g., 2481x3507)
- [ ] Preserves image quality
- [ ] Handles different formats (PNG, JPEG, TIFF)
- [ ] Handles grayscale and color images
- [ ] Creates output directory if missing
- [ ] Doesn't overwrite existing files (or asks)
- [ ] Shows clear error messages

## Performance Notes

- A4 @ 300 DPI = ~25 MB PNG → splits in <1 second
- A4 @ 600 DPI = ~100 MB PNG → splits in 2-3 seconds
- Memory usage: ~2x image size during processing
- Consider async/threading for batch processing

## Usage Example

```bash
# Install Pillow
uv add pillow

# Create test image (if needed)
uv run python -c "from PIL import Image; Image.new('RGB', (2480, 3508), 'white').save('test_a4.png')"

# Split an image
uv run python poc_split.py scan_20251128_172859.png

# Split with custom output directory
uv run python poc_split.py scan.png my_splits/
```

## Integration with Scanner POC

Create combined script `scan_and_split.py`:

```python
from poc_scan import scan_document_sane
from poc_split import split_image_2x2

def scan_and_split():
    # Scan document
    scanned_file = scan_document_sane("temp_scan.png")
    
    # Split into 2x2 grid
    output_files = split_image_2x2(scanned_file, "output")
    
    # Clean up temp file
    scanned_file.unlink()
    
    return output_files
```
