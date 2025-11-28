# Smart Photo Splitter - Edge Detection

## Overview

The smart photo splitter automatically detects photo edges in scanned A4 documents and extracts individual photos. It handles:

- ✅ **Automatic edge detection** - No manual positioning needed
- ✅ **Rotation correction** - Straightens misaligned photos
- ✅ **2x2 photo grids** - Detects up to 4 photos per scan
- ✅ **Robust algorithms** - Works with various photo sizes and layouts

## How It Works

### 1. Edge Detection Pipeline

```
Input Image
    ↓
Preprocessing
  - Grayscale conversion
  - Bilateral filtering (noise reduction)
  - Adaptive thresholding
  - Morphological operations
    ↓
Contour Detection
  - Find external contours
  - Filter by area (min 5% of image)
  - Filter by aspect ratio (not too thin)
    ↓
Photo Region Extraction
  - Get minimum area rectangles
  - Calculate rotation angles
  - Sort by position
    ↓
Straightening & Cropping
  - Rotate to align axis
  - Extract photo region
  - Add padding
    ↓
Output Images
```

### 2. Technologies Used

- **OpenCV** - Image processing and contour detection
- **NumPy** - Matrix operations
- **scikit-image** - Advanced image processing

## Usage

### Basic Usage

```bash
uv run python smart_split.py scan.png
```

Output: `output/scan_photo1.png`, `scan_photo2.png`, etc.

### With Custom Output Directory

```bash
uv run python smart_split.py scan.png photos/
```

### With Debug Visualization

```bash
uv run python smart_split.py scan.png output --debug
```

This creates `output/scan_debug.png` showing detected edges and regions.

### Programmatic Usage

```python
from smart_split import split_photos_smart

output_files = split_photos_smart(
    "scan.png",
    output_dir="../output",
    debug=True
)

for photo_file in output_files:
    print(f"Extracted: {photo_file}")
```

## Algorithm Details

### Preprocessing

1. **Grayscale Conversion**
   - Simplifies processing
   - Reduces data from 3 channels to 1

2. **Bilateral Filter**
   - Reduces noise while preserving edges
   - Parameters: diameter=9, sigma=75

3. **Adaptive Thresholding**
   - Converts to binary (black/white)
   - Adapts to local lighting conditions
   - Block size: 11, constant: 2

4. **Morphological Closing**
   - Fills small gaps in edges
   - Connects nearby edge segments
   - Kernel: 5x5 rectangle

### Contour Detection

```python
contours, _ = cv2.findContours(
    processed, 
    cv2.RETR_EXTERNAL,  # Only outer contours
    cv2.CHAIN_APPROX_SIMPLE  # Compress contours
)
```

### Filtering

- **Area Filter**: `area > image_area * 0.05` (5% minimum)
- **Aspect Ratio Filter**: `ratio < 10` (not too thin)
- **Count Filter**: Take top 4 largest regions

### Rotation Correction

Uses `cv2.minAreaRect()` to find:
- Center point
- Width & height
- Rotation angle

Then applies rotation matrix to straighten the photo.

## Parameters

### `detect_photo_regions()`

- `min_area_ratio` (default: 0.05)
  - Minimum photo area as fraction of image
  - Lower = detect smaller photos
  - Higher = only large photos

### `extract_and_straighten_photo()`

- `padding` (default: 10 pixels)
  - Extra space around extracted photo
  - Prevents edge clipping

## Output

### Photo Files

- Format: `{basename}_photo{N}.png`
- Numbered 1-4 based on position (top-left → bottom-right)
- Straightened and cropped
- White background padding

### Debug Visualization

When `--debug` flag is used:
- Green contours show detected edges
- Red dots show photo centers
- Blue labels show photo numbers
- Filename: `{basename}_debug.png`

## Error Handling

### No Photos Detected

```
✗ No photos detected!

Try:
  - Check image has clear photo edges
  - Use grid split: uv run poc_split.py
```

**Causes:**
- Photos too small (< 5% of image)
- Poor contrast between photos and background
- Photos touching edges

**Solutions:**
- Adjust `min_area_ratio` parameter
- Improve scan quality
- Use grid-based split as fallback

### Detection Issues

If photos are not detected correctly:

1. **Check debug visualization**
   ```bash
   uv run python smart_split.py scan.png output --debug
   open output/scan_debug.png
   ```

2. **Adjust preprocessing**
   - Modify threshold parameters
   - Change morphological kernel size

3. **Use grid split**
   ```bash
   uv run poc_split.py scan.png
   ```

## Comparison: Smart vs Grid Split

### Smart Split (Edge Detection)

**Advantages:**
- ✅ Handles rotation automatically
- ✅ Works with irregular layouts
- ✅ Precise photo boundaries
- ✅ No wasted space

**Disadvantages:**
- ❌ Requires clear edges
- ❌ More processing time
- ❌ May fail with poor scans

**Best for:**
- Photos with clear borders
- Slightly misaligned scans
- Varying photo sizes

### Grid Split (Simple Division)

**Advantages:**
- ✅ Always works
- ✅ Very fast
- ✅ Simple and predictable

**Disadvantages:**
- ❌ No rotation correction
- ❌ Fixed grid positions
- ❌ Includes margins

**Best for:**
- Perfectly aligned scans
- Consistent photo sizes
- Quick processing

## Integration

### In main.py

```python
from smart_split import split_photos_smart

# After scanning
split_files = split_photos_smart(
    str(scanned_file),
    str(output_dir),
    debug=True
)
```

### Fallback Strategy

```python
try:
    # Try smart split first
    photos = split_photos_smart(scan_path, output_dir)
except Exception:
    # Fall back to grid split
    photos = split_image_2x2(scan_path, output_dir)
```

## Testing

### Test with Simulated Scan

```bash
# Create test scan with 4 photos
uv run python create_test_scan.py

# Run smart split
uv run python smart_split.py output/test_4photos.png output --debug

# View results
open output/
```

### Expected Output

```
Detecting photo edges...
  Found 4 potential photo regions
  Detected 4 photos

Extracting photos...
  Photo 1:
    Position: (694, 951)
    Angle: 88.0°
    Saved: test_4photos_photo1.png (1522x1008)
  Photo 2:
    Position: (1784, 951)
    Angle: 1.0°
    Saved: test_4photos_photo2.png (1522x1008)
  ...
```

## Performance

### Typical Processing Time

- **A4 scan at 300 DPI**: ~1-2 seconds
- **Edge detection**: ~500ms
- **Photo extraction**: ~100ms per photo

### Memory Usage

- **Input image (A4 @ 300 DPI)**: ~25 MB
- **Processed data**: ~50 MB
- **Total peak**: ~75 MB

## Future Enhancements

- [ ] Support for more than 4 photos
- [ ] Machine learning-based edge detection
- [ ] Automatic white balance
- [ ] Color correction
- [ ] Perspective correction (3D rotation)
- [ ] Batch processing
- [ ] GPU acceleration

## Dependencies

```
opencv-python==4.12.0.88
numpy==2.2.6
scikit-image==0.25.2
scipy==1.16.3
```

Install with:
```bash
uv add opencv-python scikit-image
```

## License

Part of python-scan-4x4 project.
