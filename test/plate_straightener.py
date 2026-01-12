"""
License Plate Straightener Module - Edge-Based Alignment
=========================================================
This module takes a cropped license plate image (from YOLO detection)
and straightens it using the top and bottom edges for horizontal alignment.

Note: This is a standalone module for demonstration purposes.
It is NOT integrated with the main ALPR pipeline.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import math


class PlateStraightener:
    """Straightens angled license plate images using edge-based alignment"""
    
    def __init__(self, min_angle_threshold: float = 1.0):
        """
        Initialize the plate straightener
        
        Args:
            min_angle_threshold: Minimum angle (degrees) to trigger straightening
        """
        self.min_angle_threshold = min_angle_threshold
        
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """
        Detect edges in the plate image
        
        Args:
            image: Input plate image (RGB or grayscale)
            
        Returns:
            Edge image
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        return edges
    
    def find_horizontal_lines(self, edges: np.ndarray) -> List[Tuple[float, float]]:
        """
        Find horizontal lines in the edge image using Hough transform
        
        Args:
            edges: Edge image from Canny
            
        Returns:
            List of (rho, theta) for detected lines
        """
        # Use Hough Line Transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=50)
        
        if lines is None:
            return []
        
        horizontal_lines = []
        
        # Filter for horizontal lines (theta close to 0 or pi)
        for line in lines:
            rho, theta = line[0]
            
            # Check if line is close to horizontal
            # Horizontal lines have theta close to 0 or pi (±15 degrees tolerance)
            angle_deg = math.degrees(theta)
            
            # Normalize angle to [-90, 90] range
            if angle_deg > 90:
                angle_deg -= 180
            
            # Keep lines that are mostly horizontal (within ±30 degrees)
            if abs(angle_deg) < 30 or abs(angle_deg - 180) < 30:
                horizontal_lines.append((rho, theta))
        
        return horizontal_lines
    
    def calculate_angle_from_edges(self, image: np.ndarray) -> Tuple[float, Optional[np.ndarray]]:
        """
        Calculate rotation angle based on top and bottom edges
        
        Args:
            image: Input plate image
            
        Returns:
            Tuple of (angle_in_degrees, debug_image)
        """
        h, w = image.shape[:2]
        
        # Detect edges
        edges = self.detect_edges(image)
        
        # Find horizontal lines
        lines = self.find_horizontal_lines(edges)
        
        if not lines:
            # Fallback: use contour-based detection
            return self._calculate_angle_from_contour(image)
        
        # Calculate average angle from detected lines
        angles = []
        
        for rho, theta in lines:
            # Convert theta to degrees
            angle_deg = math.degrees(theta)
            
            # Normalize to [-90, 90]
            if angle_deg > 90:
                angle_deg -= 180
            
            # For horizontal alignment, we want the angle to be 0
            # So we calculate how much we need to rotate
            angles.append(angle_deg)
        
        if not angles:
            return 0.0, edges
        
        # Use median angle for robustness
        median_angle = np.median(angles)
        
        # The angle we need to rotate is the negative of the detected angle
        rotation_angle = -median_angle
        
        # Create debug image with lines drawn
        debug_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        for rho, theta in lines[:10]:  # Draw first 10 lines
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        return rotation_angle, debug_img
    
    def _calculate_angle_from_contour(self, image: np.ndarray) -> Tuple[float, Optional[np.ndarray]]:
        """
        Fallback method: Calculate angle using contour detection
        
        Args:
            image: Input plate image
            
        Returns:
            Tuple of (angle, debug_image)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.0, None
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get minimum area rectangle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Adjust angle
        if angle < -45:
            angle = 90 + angle
        
        # Get box for debug
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        debug_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(debug_img, [box], 0, (0, 255, 0), 2)
        
        return angle, debug_img
    
    def straighten_plate(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Straighten the plate by rotating it
        
        Args:
            image: Input plate image
            angle: Rotation angle in degrees
            
        Returns:
            Straightened plate image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Get rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new image dimensions
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Adjust rotation matrix to account for translation
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        # Perform rotation with white background
        straightened = cv2.warpAffine(image, M, (new_w, new_h),
                                       flags=cv2.INTER_CUBIC,
                                       borderMode=cv2.BORDER_CONSTANT,
                                       borderValue=(255, 255, 255))
        
        return straightened
    
    def crop_to_content(self, image: np.ndarray) -> np.ndarray:
        """
        Crop the image to remove excess white borders
        
        Args:
            image: Input image
            
        Returns:
            Cropped image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Threshold to find content
        _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image
        
        # Get bounding box of all content
        x, y, w, h = cv2.boundingRect(np.concatenate(contours))
        
        # Add small padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Crop
        cropped = image[y:y+h, x:x+w]
        
        return cropped
    
    def process(self, plate_image: np.ndarray) -> Tuple[np.ndarray, float, dict]:
        """
        Main processing function to straighten a license plate
        
        Args:
            plate_image: Cropped plate image from YOLO detection (RGB)
            
        Returns:
            Tuple of (straightened_image, detected_angle, debug_info)
        """
        debug_info = {
            'original_shape': plate_image.shape,
            'method': 'edge_based'
        }
        
        # Detect angle using edges
        angle, debug_img = self.calculate_angle_from_edges(plate_image)
        
        debug_info['detected_angle'] = angle
        debug_info['needs_correction'] = abs(angle) > self.min_angle_threshold
        debug_info['debug_edges'] = debug_img
        
        # Check if straightening is needed
        if abs(angle) < self.min_angle_threshold:
            print(f"[OK] Plate is already straight (angle: {angle:.2f} degrees)")
            debug_info['action'] = 'none'
            return plate_image.copy(), angle, debug_info
        
        print(f"[WARNING] Plate is tilted by {angle:.2f} degrees - straightening...")
        
        # Straighten the plate
        straightened = self.straighten_plate(plate_image, angle)
        
        # Crop to remove excess borders
        straightened = self.crop_to_content(straightened)
        
        debug_info['action'] = 'straightened'
        debug_info['straightened_shape'] = straightened.shape
        
        return straightened, angle, debug_info
    
    def display_results(self, original: np.ndarray, straightened: np.ndarray,
                       angle: float, debug_info: dict, window_name: str = "Plate Straightener"):
        """
        Display original and straightened images side by side
        
        Args:
            original: Original plate image
            straightened: Straightened plate image
            angle: Detected angle
            debug_info: Debug information dictionary
            window_name: Name of the display window
        """
        # Ensure both images are in BGR format
        if len(original.shape) == 2:
            original_display = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
        else:
            original_display = original.copy()
            
        if len(straightened.shape) == 2:
            straightened_display = cv2.cvtColor(straightened, cv2.COLOR_GRAY2BGR)
        else:
            straightened_display = straightened.copy()
        
        # Resize images to same height for side-by-side display
        target_height = 300
        
        h1, w1 = original_display.shape[:2]
        scale1 = target_height / h1
        original_resized = cv2.resize(original_display,
                                      (int(w1 * scale1), target_height),
                                      interpolation=cv2.INTER_CUBIC)
        
        h2, w2 = straightened_display.shape[:2]
        scale2 = target_height / h2
        straightened_resized = cv2.resize(straightened_display,
                                          (int(w2 * scale2), target_height),
                                          interpolation=cv2.INTER_CUBIC)
        
        # Add text labels
        cv2.putText(original_resized, f"Original (Angle: {angle:.2f}deg)",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(straightened_resized, f"Straightened (Edge-based)",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add status text
        status = "No correction needed" if not debug_info['needs_correction'] else "Corrected"
        cv2.putText(straightened_resized, status,
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Combine images horizontally
        separator = np.ones((target_height, 30, 3), dtype=np.uint8) * 128
        combined = np.hstack([original_resized, separator, straightened_resized])
        
        # Show debug edges if available
        if debug_info.get('debug_edges') is not None and debug_info['debug_edges'] is not None:
            debug_edges = debug_info['debug_edges']
            if len(debug_edges.shape) == 2:
                debug_edges = cv2.cvtColor(debug_edges, cv2.COLOR_GRAY2BGR)
            
            h3, w3 = debug_edges.shape[:2]
            scale3 = target_height / h3
            debug_resized = cv2.resize(debug_edges,
                                      (int(w3 * scale3), target_height),
                                      interpolation=cv2.INTER_CUBIC)
            
            cv2.putText(debug_resized, "Detected Edges",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            combined = np.hstack([combined, separator, debug_resized])
        
        # Create window and display
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, combined)
        
        print(f"\n{'='*60}")
        print(f"PLATE STRAIGHTENING RESULTS (EDGE-BASED)")
        print(f"{'='*60}")
        print(f"Original size:      {debug_info['original_shape']}")
        print(f"Detected angle:     {angle:.2f} degrees")
        print(f"Needs correction:   {debug_info['needs_correction']}")
        print(f"Method used:        {debug_info['action']}")
        if 'straightened_shape' in debug_info:
            print(f"Straightened size:  {debug_info['straightened_shape']}")
        print(f"{'='*60}")
        print(f"Press any key to close the window...")
        
        # Wait for key press
        cv2.waitKey(0)
        try:
            cv2.destroyWindow(window_name)
        except:
            pass
        cv2.destroyAllWindows()


def test_with_yolo_crop(image_path: str) -> np.ndarray:
    """
    Test function that simulates getting a cropped plate from YOLO
    and straightens it
    
    Args:
        image_path: Path to an image containing a license plate
        
    Returns:
        Straightened plate image
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    print(f"\n[OK] Loaded image: {image_path}")
    print(f"  Image size: {image.shape}")
    
    # For testing: treat the whole image as the cropped plate
    # In real use, this would be the output from YOLO detection
    plate_crop = image
    
    # Create straightener
    straightener = PlateStraightener(min_angle_threshold=1.0)
    
    # Process
    straightened, angle, debug_info = straightener.process(plate_crop)
    
    # Display results
    straightener.display_results(plate_crop, straightened, angle, debug_info)
    
    return straightened


if __name__ == "__main__":
    """
    Standalone module - run test
    """
    import sys
    
    if len(sys.argv) > 1:
        # Test with provided image path
        image_path = sys.argv[1]
        test_with_yolo_crop(image_path)
    else:
        print("\n" + "="*60)
        print("PLATE STRAIGHTENER MODULE (EDGE-BASED)")
        print("="*60)
        print("\nUsage:")
        print("  python plate_straightener.py <image_path>")
        print("\nExample:")
        print("  python plate_straightener.py ../snapshots/MH20EJ0364_20260106_010636.jpg")
        print("\nThis version works with cropped plate images from YOLO")
        print("and uses top/bottom edges for horizontal alignment.")
