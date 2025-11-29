#!/usr/bin/env python3
"""
Smart Photo Splitter V3 - Contour-based Detection
Uses OpenCV contour detection to properly identify and extract photos
separated by white background, handling 1-4 photos of any size/orientation.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import io


def capture_logs(func):
    """Decorator to capture print statements to a log"""
    def wrapper(*args, **kwargs):
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
            result = func(*args, **kwargs)
            return result, log_buffer.getvalue()
        finally:
            sys.stdout = original_stdout
            log_buffer.close()
    
    return wrapper


def load_image(image_path: str) -> np.ndarray:
    """Load image from file"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")
    return img


def detect_photos(img: np.ndarray, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect individual photos using contour detection.
    
    Args:
        img: Original BGR image
        gray: Grayscale version
    
    Returns:
        List of bounding boxes (x, y, w, h) for each detected photo
    """
    print("\nDetecting photos using contour analysis...")
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use adaptive thresholding to handle varying background brightness
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=51,
        C=10
    )
    
    # Morphological operations to clean up and connect photo regions
    kernel = np.ones((15, 15), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area and aspect ratio
    min_area = (img.shape[0] * img.shape[1]) * 0.02  # At least 2% of image
    max_area = (img.shape[0] * img.shape[1]) * 0.9   # At most 90% of image
    
    photo_boxes = []
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        
        if area < min_area or area > max_area:
            continue
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter out very thin/small regions
        if w < 100 or h < 100:
            continue
        
        # Calculate aspect ratio
        aspect_ratio = w / h if h > 0 else 0
        
        # Photos typically have aspect ratio between 0.3 and 3.0
        if aspect_ratio < 0.3 or aspect_ratio > 3.5:
            continue
        
        photo_boxes.append((x, y, w, h))
        print(f"  Found photo {len(photo_boxes)}: pos=({x},{y}) size={w}x{h} area={area:.0f} ratio={aspect_ratio:.2f}")
    
    # Sort by position (top to bottom, left to right)
    photo_boxes.sort(key=lambda box: (box[1], box[0]))
    
    print(f"\n  Total photos detected: {len(photo_boxes)}")
    
    return photo_boxes


def refine_photo_bounds(img: np.ndarray, gray: np.ndarray, x: int, y: int, w: int, h: int) -> Tuple[int, int, int, int]:
    """
    Refine photo boundaries to remove white borders and straighten edges.
    
    Args:
        img: Original BGR image
        gray: Grayscale version
        x, y, w, h: Initial bounding box
    
    Returns:
        Refined (x, y, w, h) bounding box
    """
    # Extract region with some padding
    pad = 20
    y1 = max(0, y - pad)
    y2 = min(gray.shape[0], y + h + pad)
    x1 = max(0, x - pad)
    x2 = min(gray.shape[1], x + w + pad)
    
    region = gray[y1:y2, x1:x2]
    
    # Apply threshold to find content
    _, binary = cv2.threshold(region, 220, 255, cv2.THRESH_BINARY_INV)
    
    # Find content bounds
    rows_with_content = np.any(binary > 0, axis=1)
    cols_with_content = np.any(binary > 0, axis=0)
    
    row_indices = np.where(rows_with_content)[0]
    col_indices = np.where(cols_with_content)[0]
    
    if len(row_indices) == 0 or len(col_indices) == 0:
        # No refinement possible, return original
        return x, y, w, h
    
    # Calculate refined bounds
    new_y1 = y1 + row_indices[0]
    new_y2 = y1 + row_indices[-1]
    new_x1 = x1 + col_indices[0]
    new_x2 = x1 + col_indices[-1]
    
    return new_x1, new_y1, new_x2 - new_x1, new_y2 - new_y1


@capture_logs
def split_photos_smart(
    image_path: str,
    output_dir: str = "photos"
) -> List[str]:
    """
    Split scanned page into individual photos using contour detection.
    Automatically detects 1-4 photos of any size and orientation.
    
    Args:
        image_path: Path to scanned image
        output_dir: Output directory for split photos
    
    Returns:
        List of saved photo file paths
    """
    print("=" * 60)
    print("Smart Photo Splitter V3 - Contour Detection")
    print("=" * 60)
    
    # Load image
    print(f"\nLoading: {image_path}")
    img = load_image(image_path)
    h, w = img.shape[:2]
    print(f"  Size: {w} x {h} pixels")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect photos
    photo_boxes = detect_photos(img, gray)
    
    if len(photo_boxes) == 0:
        print("\n⚠ No photos detected!")
        return []
    
    # Process and save each photo
    print(f"\nExtracting {len(photo_boxes)} photo(s)...")
    output_files = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(image_path).stem
    
    for i, (x, y, w, h) in enumerate(photo_boxes, 1):
        print(f"\n  Photo {i}:")
        print(f"    Initial bounds: ({x},{y}) {w}x{h}")
        
        # Refine boundaries
        x_refined, y_refined, w_refined, h_refined = refine_photo_bounds(img, gray, x, y, w, h)
        print(f"    Refined bounds: ({x_refined},{y_refined}) {w_refined}x{h_refined}")
        
        # Extract photo
        photo = img[y_refined:y_refined+h_refined, x_refined:x_refined+w_refined]
        
        # Save
        output_file = output_path / f"{base_name}_photo_{i}.png"
        cv2.imwrite(str(output_file), photo)
        output_files.append(str(output_file))
        print(f"    ✓ Saved: {output_file}")
    
    print("\n" + "=" * 60)
    print(f"✓ Split complete! Saved {len(output_files)} photo(s)")
    print("=" * 60)
    
    return output_files


def split_photos_grid_smart(
    image_path: str,
    output_dir: str = "photos",
    margin_threshold: int = 220
) -> List[str]:
    """
    Wrapper function for backward compatibility with existing code.
    Calls the new contour-based detection.
    """
    output_files, log_content = split_photos_smart(image_path, output_dir)
    
    # Save log file
    output_path = Path(output_dir)
    base_name = Path(image_path).stem
    log_file = output_path / f"{base_name}_split_log.txt"
    log_file.write_text(log_content)
    
    return output_files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: smart_split.py <scan_image>")
        sys.exit(1)
    
    split_photos_grid_smart(sys.argv[1])
