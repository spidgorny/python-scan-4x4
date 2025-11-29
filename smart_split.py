#!/usr/bin/env python3
"""
Smart Photo Splitter V2 - Grid-based with refinement

Uses a combination of grid splitting and edge detection to accurately
split 2x2 photo layouts, handling white borders and slight misalignment.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

def load_image(image_path: str) -> np.ndarray:
    """Load image from file"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")
    return img

def has_content(gray_section: np.ndarray, threshold: int = 220, min_area_ratio: float = 0.05) -> bool:
    """
    Check if a section has actual photo content (not just white/light gray background).
    Uses adaptive thresholding to handle slightly gray backgrounds.
    
    Args:
        gray_section: Grayscale image section
        threshold: Brightness threshold for detecting background (220 = allows slightly gray)
        min_area_ratio: Minimum ratio of content area to total area (5% default)
    
    Returns:
        True if section contains meaningful photo content
    """
    # Calculate mean brightness to detect overall darkness
    mean_brightness = np.mean(gray_section)
    
    # If section is significantly darker than threshold, it has content
    if mean_brightness < threshold - 20:
        return True
    
    # Also use threshold method for edge detection
    _, binary = cv2.threshold(gray_section, threshold, 255, cv2.THRESH_BINARY_INV)
    content_pixels = np.sum(binary > 0)
    total_pixels = gray_section.shape[0] * gray_section.shape[1]
    content_ratio = content_pixels / total_pixels
    
    return content_ratio > min_area_ratio

def find_content_bounds(gray_section: np.ndarray, threshold: int = 220) -> Tuple[int, int, int, int]:
    """
    Find actual content bounds within a section by detecting non-background areas.
    Uses adaptive approach to handle slightly gray backgrounds.
    
    Returns: (top, bottom, left, right) margins from edges
    """
    # Use adaptive threshold to handle varying background brightness
    # This works better than fixed threshold for slightly gray backgrounds
    binary = cv2.adaptiveThreshold(
        gray_section,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=51,  # Large block size for smoother detection
        C=-10  # Negative constant to be more aggressive
    )
    
    # Also use fixed threshold and combine
    _, binary_fixed = cv2.threshold(gray_section, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # Combine both methods (OR operation)
    binary = cv2.bitwise_or(binary, binary_fixed)
    
    # Apply morphological closing to connect nearby content
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Find where content exists
    rows_with_content = np.any(binary > 0, axis=1)
    cols_with_content = np.any(binary > 0, axis=0)
    
    # Find first and last rows/cols with content
    row_indices = np.where(rows_with_content)[0]
    col_indices = np.where(cols_with_content)[0]
    
    if len(row_indices) == 0 or len(col_indices) == 0:
        # No content found
        return 0, gray_section.shape[0], 0, gray_section.shape[1]
    
    top = row_indices[0]
    bottom = gray_section.shape[0] - row_indices[-1]
    left = col_indices[0]
    right = gray_section.shape[1] - col_indices[-1]
    
    return top, bottom, left, right

def detect_layout(img: np.ndarray, gray: np.ndarray, margin_threshold: int = 220) -> str:
    """
    Detect the layout of photos on the page (1, 2, 3, or 4 photos).
    Note: Expects pre-cropped image with page margins already removed.
    
    Args:
        img: Original BGR image (already cropped to content)
        gray: Grayscale version of image (already cropped to content)
        margin_threshold: Brightness threshold for detecting white areas
    
    Returns:
        Layout type: "2x2", "3_photos", "2x1", "1x2", or "1x1"
    """
    h, w = gray.shape
    
    # For single photo detection, check if content spans multiple quadrants
    # by looking at thirds instead of halves to handle larger photos
    third_h = h // 3
    third_w = w // 3
    
    # Check each quadrant for content
    mid_h = h // 2
    mid_w = w // 2
    
    quadrants = {
        'top_left': gray[0:mid_h, 0:mid_w],
        'top_right': gray[0:mid_h, mid_w:w],
        'bottom_left': gray[mid_h:h, 0:mid_w],
        'bottom_right': gray[mid_h:h, mid_w:w],
    }
    
    content_map = {
        name: has_content(section, margin_threshold)
        for name, section in quadrants.items()
    }
    
    content_count = sum(content_map.values())
    
    print(f"\n  Content detection:")
    for name, has_c in content_map.items():
        print(f"    {name}: {'✓ Photo' if has_c else '✗ Empty'}")
    
    # Determine layout
    if content_count == 4:
        return "2x2"
    elif content_count == 3:
        # Three photos - treat as 2x2 and filter empty quadrant
        return "3_photos"
    elif content_count == 2:
        # Check if horizontal or vertical
        if content_map['top_left'] and content_map['top_right']:
            return "1x2_top"
        elif content_map['bottom_left'] and content_map['bottom_right']:
            return "1x2_bottom"
        elif content_map['top_left'] and content_map['bottom_left']:
            return "2x1_left"
        elif content_map['top_right'] and content_map['bottom_right']:
            return "2x1_right"
        else:
            # Diagonal - treat as 2x2 but will filter empty ones
            return "2x2"
    elif content_count == 1:
        # Single photo - return which quadrant it's in for smarter cropping
        if content_map['top_left']:
            return "1x1_top_left"
        elif content_map['top_right']:
            return "1x1_top_right"
        elif content_map['bottom_left']:
            return "1x1_bottom_left"
        elif content_map['bottom_right']:
            return "1x1_bottom_right"
        else:
            return "1x1"
    else:
        # Default to 2x2 if detection is unclear
        return "2x2"

def split_photos_grid_smart(
    image_path: str,
    output_dir: str = "photos",
    margin_threshold: int = 220
) -> List[str]:
    """
    Split scanned A4 with photos using smart detection + cropping.
    Automatically detects if there are 1, 2, 3, or 4 photos on the page.
    
    Args:
        image_path: Path to scanned image
        output_dir: Output directory for split photos
        margin_threshold: Brightness threshold for detecting white margins (0-255)
    
    Returns:
        List of saved photo file paths
    """
    # Capture logs
    import io
    import sys
    
    log_buffer = io.StringIO()
    original_stdout = sys.stdout
    
    class TeeOutput:
        def __init__(self, *outputs):
            self.outputs = outputs
        def write(self, text):
            for output in self.outputs:
                output.write(text)
        def flush(self):
            for output in self.outputs:
                output.flush()
    
    sys.stdout = TeeOutput(original_stdout, log_buffer)
    
    try:
        print("=" * 60)
        print("Smart Photo Splitter V2 - Adaptive Layout")
        print("=" * 60)
        
        # Load image
        print(f"\nLoading: {image_path}")
        img = load_image(image_path)
        h, w = img.shape[:2]
        print(f"  Size: {w} x {h} pixels")
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # FIRST: Remove white borders from entire scan
        print("\nRemoving page margins...")
        page_top, page_bottom, page_left, page_right = find_content_bounds(gray, margin_threshold)
        
        # Crop to actual content area
        img = img[page_top:h-page_bottom, page_left:w-page_right]
        gray = gray[page_top:h-page_bottom, page_left:w-page_right]
        
        h, w = img.shape[:2]
        print(f"  Cropped to content area: {w} x {h} pixels")
        print(f"  Removed margins: top={page_top}, bottom={page_bottom}, left={page_left}, right={page_right}")
        
        # THEN: Detect layout
        print("\nDetecting layout...")
        layout = detect_layout(img, gray, margin_threshold)
        print(f"\n  Detected layout: {layout}")
        
        # Define sections based on layout
        mid_h = h // 2
        mid_w = w // 2
        
        sections = []
        
        if layout.startswith("1x1"):
            # Single photo - use full content area (already cropped from page margins)
            # Don't subdivide, just crop to actual photo bounds
            sections = [
                ((0, h), (0, w), "single"),
            ]
        elif layout == "1x2_top":
            # Two photos side by side at top
            sections = [
                ((0, h), (0, mid_w), "left"),
                ((0, h), (mid_w, w), "right"),
            ]
        elif layout == "1x2_bottom":
            # Two photos side by side at bottom
            sections = [
                ((0, h), (0, mid_w), "left"),
                ((0, h), (mid_w, w), "right"),
            ]
        elif layout == "2x1_left":
            # Two photos stacked on left
            sections = [
                ((0, mid_h), (0, w), "top"),
                ((mid_h, h), (0, w), "bottom"),
            ]
        elif layout == "2x1_right":
            # Two photos stacked on right
            sections = [
                ((0, mid_h), (0, w), "top"),
                ((mid_h, h), (0, w), "bottom"),
            ]
        elif layout == "3_photos":
            # Three photos - use 2x2 grid and skip empty quadrant
            sections = [
                ((0, mid_h), (0, mid_w), "top-left"),
                ((0, mid_h), (mid_w, w), "top-right"),
                ((mid_h, h), (0, mid_w), "bottom-left"),
                ((mid_h, h), (mid_w, w), "bottom-right"),
            ]
        else:  # 2x2 or default
            # Four photos in 2x2 grid
            sections = [
                ((0, mid_h), (0, mid_w), "top-left"),
                ((0, mid_h), (mid_w, w), "top-right"),
                ((mid_h, h), (0, mid_w), "bottom-left"),
                ((mid_h, h), (mid_w, w), "bottom-right"),
            ]
        
        # Process each section
        print(f"\nProcessing {len(sections)} section(s)...")
        output_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(image_path).stem
        photo_num = 1
        
        for ((y1, y2), (x1, x2), position) in sections:
            print(f"\n  Section {position}:")
            print(f"    Grid bounds: ({x1}, {y1}) to ({x2}, {y2})")
            
            # Extract section
            section = img[y1:y2, x1:x2]
            gray_section = gray[y1:y2, x1:x2]
            
            # Check if this section has content
            if not has_content(gray_section, margin_threshold):
                print(f"    ✗ Skipping - no content detected")
                continue
            
            # Find content bounds (remove white borders)
            top, bottom, left, right = find_content_bounds(gray_section, margin_threshold)
            
            print(f"    Margins: top={top}, bottom={bottom}, left={left}, right={right}")
            
            # Crop to content
            cropped = section[top:section.shape[0]-bottom, left:section.shape[1]-right]
            
            print(f"    Final size: {cropped.shape[1]} x {cropped.shape[0]}")
            
            # Save
            output_file = output_path / f"{base_name}_photo_{photo_num}.png"
            cv2.imwrite(str(output_file), cropped)
            output_files.append(str(output_file))
            print(f"    ✓ Saved: {output_file}")
            photo_num += 1
        
        print("\n" + "=" * 60)
        print(f"✓ Split complete! Saved {len(output_files)} photo(s)")
        print("=" * 60)
        
    finally:
        # Restore stdout and save log
        sys.stdout = original_stdout
        log_content = log_buffer.getvalue()
        log_buffer.close()
        
        # Save log file
        log_file = output_path / f"{base_name}_split_log.txt"
        log_file.write_text(log_content)
    
    return output_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: smart_split_v2.py <scan_image>")
        sys.exit(1)
    
    split_photos_grid_smart(sys.argv[1])
