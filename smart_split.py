#!/usr/bin/env python3
"""
Smart Photo Splitter with Edge Detection

Automatically detects photo edges in a scanned A4 document with 2x2 photos.
Handles rotation and misalignment automatically.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhotoRegion:
    """Represents a detected photo region"""
    contour: np.ndarray
    center: Tuple[int, int]
    angle: float
    bounding_rect: Tuple[int, int, int, int]  # x, y, w, h
    area: float


def load_image(image_path: str) -> np.ndarray:
    """Load image from file"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")
    return img


def preprocess_for_edge_detection(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image for better edge detection.
    
    Args:
        image: Input BGR image
    
    Returns:
        Preprocessed grayscale image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 2
    )
    
    # Morphological operations to close gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return closed


def detect_photo_regions(image: np.ndarray, min_area_ratio: float = 0.05) -> List[PhotoRegion]:
    """
    Detect photo regions in the scanned image.
    
    Args:
        image: Input BGR image
        min_area_ratio: Minimum area ratio (relative to image size) for a valid photo
    
    Returns:
        List of detected photo regions
    """
    print("Detecting photo edges...")
    
    # Preprocess
    processed = preprocess_for_edge_detection(image)
    
    # Find contours
    contours, _ = cv2.findContours(
        processed, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Calculate minimum area
    image_area = image.shape[0] * image.shape[1]
    min_area = image_area * min_area_ratio
    
    photo_regions = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area
        if area < min_area:
            continue
        
        # Get minimum area rectangle (handles rotation)
        rect = cv2.minAreaRect(contour)
        center, (width, height), angle = rect
        
        # Skip very thin regions (likely borders or artifacts)
        if width > 0 and height > 0:
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 10:  # Too thin
                continue
        
        # Get axis-aligned bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        photo_regions.append(PhotoRegion(
            contour=contour,
            center=(int(center[0]), int(center[1])),
            angle=angle,
            bounding_rect=(x, y, w, h),
            area=area
        ))
    
    print(f"  Found {len(photo_regions)} potential photo regions")
    
    # Sort by area (largest first) and take top 4
    photo_regions.sort(key=lambda r: r.area, reverse=True)
    photo_regions = photo_regions[:4]
    
    # Sort by position (top to bottom, left to right)
    photo_regions.sort(key=lambda r: (r.center[1], r.center[0]))
    
    return photo_regions


def extract_and_straighten_photo(
    image: np.ndarray, 
    region: PhotoRegion,
    padding: int = 10
) -> np.ndarray:
    """
    Extract and straighten a photo region.
    
    Args:
        image: Source image
        region: Photo region to extract
        padding: Padding around the photo (pixels)
    
    Returns:
        Extracted and straightened photo
    """
    # Get the rotated rectangle
    rect = cv2.minAreaRect(region.contour)
    center, (width, height), angle = rect
    
    # Ensure width > height (landscape orientation)
    if width < height:
        width, height = height, width
        angle += 90
    
    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calculate new image dimensions (large enough to fit rotated image)
    img_height, img_width = image.shape[:2]
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    
    new_width = int(img_height * sin + img_width * cos)
    new_height = int(img_height * cos + img_width * sin)
    
    # Adjust rotation matrix for new center
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # Rotate image
    rotated = cv2.warpAffine(
        image, 
        rotation_matrix, 
        (new_width, new_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )
    
    # Calculate crop box in rotated image
    center_x = new_width // 2
    center_y = new_height // 2
    
    half_width = int(width / 2) + padding
    half_height = int(height / 2) + padding
    
    x1 = max(0, center_x - half_width)
    y1 = max(0, center_y - half_height)
    x2 = min(new_width, center_x + half_width)
    y2 = min(new_height, center_y + half_height)
    
    # Crop
    cropped = rotated[y1:y2, x1:x2]
    
    return cropped


def split_photos_smart(
    input_path: str,
    output_dir: str = "photos",
    debug: bool = False
) -> List[Path]:
    """
    Smart split: Detect photo edges and extract individual photos.
    
    Args:
        input_path: Path to scanned image
        output_dir: Output directory for split images
        debug: If True, save debug visualization
    
    Returns:
        List of paths to extracted photos
    """
    print("=" * 60)
    print("Smart Photo Splitter - Edge Detection")
    print("=" * 60)
    print()
    
    # Load image
    print(f"Loading: {input_path}")
    image = load_image(input_path)
    print(f"  Size: {image.shape[1]} x {image.shape[0]} pixels")
    print()
    
    # Detect photo regions
    regions = detect_photo_regions(image)
    
    if len(regions) == 0:
        print("✗ No photos detected!")
        print("\nTry:")
        print("  - Check image has clear photo edges")
        print("  - Use grid split: uv run poc_split.py")
        sys.exit(1)
    
    print(f"  Detected {len(regions)} photos")
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate base filename
    input_file = Path(input_path)
    base_name = input_file.stem
    
    # Extract and save photos
    output_files = []
    
    print("Extracting photos...")
    for i, region in enumerate(regions, 1):
        print(f"  Photo {i}:")
        print(f"    Position: ({region.center[0]}, {region.center[1]})")
        print(f"    Angle: {region.angle:.1f}°")
        
        # Extract and straighten
        photo = extract_and_straighten_photo(image, region)
        
        # Save
        output_file = output_path / f"{base_name}_photo{i}.png"
        cv2.imwrite(str(output_file), photo)
        output_files.append(output_file)
        
        print(f"    Saved: {output_file.name} ({photo.shape[1]}x{photo.shape[0]})")
    
    # Debug visualization
    if debug:
        debug_image = image.copy()
        
        for i, region in enumerate(regions, 1):
            # Draw contour
            cv2.drawContours(debug_image, [region.contour], -1, (0, 255, 0), 3)
            
            # Draw center
            cv2.circle(debug_image, region.center, 10, (0, 0, 255), -1)
            
            # Draw label
            cv2.putText(
                debug_image,
                f"Photo {i}",
                (region.center[0] - 40, region.center[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 0, 0),
                2
            )
        
        debug_file = output_path / f"{base_name}_debug.png"
        cv2.imwrite(str(debug_file), debug_image)
        print()
        print(f"Debug visualization: {debug_file}")
    
    print()
    print("✓ Complete!")
    print(f"  Extracted {len(output_files)} photos to: {output_dir}/")
    
    return output_files


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python smart_split.py <input_image> [output_dir] [--debug]")
        print()
        print("Example:")
        print("  python smart_split.py scan.png")
        print("  python smart_split.py scan.png photos --debug")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "photos"
    debug = "--debug" in sys.argv
    
    try:
        output_files = split_photos_smart(input_path, output_dir, debug)
        
        print()
        print("Output files:")
        for f in output_files:
            print(f"  - {f}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
