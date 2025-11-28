#!/usr/bin/env python3
"""
Test script for smart photo splitting with debug visualization
"""
import cv2
import numpy as np
from pathlib import Path

def test_edge_detection(image_path: str):
    """Test edge detection with various parameters and visualizations"""
    print("=" * 60)
    print("Smart Photo Splitter - Debug Test")
    print("=" * 60)
    
    # Load image
    print(f"\nLoading: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("✗ Failed to load image!")
        return
    
    h, w = img.shape[:2]
    print(f"  Size: {w} x {h} pixels")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Try different edge detection parameters
    print("\nTesting edge detection parameters...")
    
    # Method 1: Canny with different thresholds
    print("\n1. Canny Edge Detection:")
    thresholds = [(50, 150), (30, 100), (100, 200)]
    for low, high in thresholds:
        edges = cv2.Canny(gray, low, high)
        edge_pixels = np.sum(edges > 0)
        print(f"  Threshold ({low}, {high}): {edge_pixels} edge pixels")
    
    # Method 2: Adaptive thresholding
    print("\n2. Adaptive Threshold:")
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
    adaptive_pixels = np.sum(adaptive == 0)
    print(f"  Black pixels: {adaptive_pixels}")
    
    # Method 3: Contour detection with different approaches
    print("\n3. Contour Detection:")
    
    # Use bilateral filter to reduce noise while keeping edges sharp
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Canny edge detection
    edges = cv2.Canny(blurred, 30, 100)
    
    # Dilate to connect nearby edges
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"  Found {len(contours)} contours")
    
    # Filter contours by area
    min_area = (w * h) * 0.02  # At least 2% of image
    max_area = (w * h) * 0.30  # At most 30% of image
    
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            # Check aspect ratio
            rect = cv2.minAreaRect(cnt)
            _, (width, height), _ = rect
            if width > 0 and height > 0:
                aspect_ratio = max(width, height) / min(width, height)
                if aspect_ratio > 5:
                    continue
            if width < 100 or height < 100:
                continue
            
            valid_contours.append(cnt)
            x, y, cw, ch = cv2.boundingRect(cnt)
            print(f"    Contour: area={area:.0f}, bbox=({x}, {y}, {cw}, {ch}), w={width:.0f}, h={height:.0f}")
    
    print(f"\n  Valid contours (area {min_area:.0f} - {max_area:.0f}): {len(valid_contours)}")
    
    # Save debug images
    output_dir = Path("output/debug")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving debug images to {output_dir}/")
    cv2.imwrite(str(output_dir / "1_gray.png"), gray)
    cv2.imwrite(str(output_dir / "2_blurred.png"), blurred)
    cv2.imwrite(str(output_dir / "3_edges.png"), edges)
    cv2.imwrite(str(output_dir / "4_dilated.png"), dilated)
    
    # Draw contours on original image
    debug_img = img.copy()
    cv2.drawContours(debug_img, valid_contours, -1, (0, 255, 0), 3)
    for i, cnt in enumerate(valid_contours):
        x, y, cw, ch = cv2.boundingRect(cnt)
        cv2.rectangle(debug_img, (x, y), (x + cw, y + ch), (255, 0, 0), 2)
        cv2.putText(debug_img, f"#{i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.9, (255, 0, 0), 2)
    
    cv2.imwrite(str(output_dir / "5_contours.png"), debug_img)
    
    print("\nDebug images saved:")
    print("  1_gray.png - Grayscale")
    print("  2_blurred.png - Bilateral filter")
    print("  3_edges.png - Canny edges")
    print("  4_dilated.png - Dilated edges")
    print("  5_contours.png - Detected contours")

if __name__ == "__main__":
    test_edge_detection("output/scans/scan_20251128_205005.png")
