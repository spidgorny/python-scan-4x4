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
from typing import List, Tuple

def load_image(image_path: str) -> np.ndarray:
    """Load image from file"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")
    return img

def find_content_bounds(gray_section: np.ndarray, threshold: int = 240) -> Tuple[int, int, int, int]:
    """
    Find actual content bounds within a section by detecting non-white areas.
    
    Returns: (top, bottom, left, right) margins from edges
    """
    # Threshold to find non-white areas
    _, binary = cv2.threshold(gray_section, threshold, 255, cv2.THRESH_BINARY_INV)
    
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

def split_photos_grid_smart(
    image_path: str,
    output_dir: str = "photos",
    margin_threshold: int = 240
) -> List[str]:
    """
    Split scanned A4 with 2x2 photos using grid + smart cropping.
    
    Args:
        image_path: Path to scanned image
        output_dir: Output directory for split photos
        margin_threshold: Brightness threshold for detecting white margins (0-255)
    
    Returns:
        List of saved photo file paths
    """
    print("=" * 60)
    print("Smart Photo Splitter V2 - Grid + Refinement")
    print("=" * 60)
    
    # Load image
    print(f"\nLoading: {image_path}")
    img = load_image(image_path)
    h, w = img.shape[:2]
    print(f"  Size: {w} x {h} pixels")
    
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Initial grid split (2x2)
    print("\nSplitting into 2x2 grid...")
    mid_h = h // 2
    mid_w = w // 2
    
    # Define grid sections
    sections = [
        ((0, mid_h), (0, mid_w), "top-left"),
        ((0, mid_h), (mid_w, w), "top-right"),
        ((mid_h, h), (0, mid_w), "bottom-left"),
        ((mid_h, h), (mid_w, w), "bottom-right"),
    ]
    
    # Process each section
    output_files = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(image_path).stem
    
    for i, ((y1, y2), (x1, x2), position) in enumerate(sections, 1):
        print(f"\n  Photo {i} ({position}):")
        print(f"    Grid bounds: ({x1}, {y1}) to ({x2}, {y2})")
        
        # Extract section
        section = img[y1:y2, x1:x2]
        gray_section = gray[y1:y2, x1:x2]
        
        # Find content bounds (remove white borders)
        top, bottom, left, right = find_content_bounds(gray_section, margin_threshold)
        
        print(f"    Margins: top={top}, bottom={bottom}, left={left}, right={right}")
        
        # Crop to content
        cropped = section[top:section.shape[0]-bottom, left:section.shape[1]-right]
        
        print(f"    Final size: {cropped.shape[1]} x {cropped.shape[0]}")
        
        # Save
        output_file = output_path / f"{base_name}_photo_{i}.png"
        cv2.imwrite(str(output_file), cropped)
        output_files.append(str(output_file))
        print(f"    ✓ Saved: {output_file}")
    
    print("\n" + "=" * 60)
    print(f"✓ Split complete! Saved {len(output_files)} photos")
    print("=" * 60)
    
    return output_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: smart_split_v2.py <scan_image>")
        sys.exit(1)
    
    split_photos_grid_smart(sys.argv[1])
