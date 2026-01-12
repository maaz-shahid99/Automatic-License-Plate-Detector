"""
Demo script to test the Edge-Based Plate Straightener
This works with cropped plate images (from YOLO or snapshots)
"""

import cv2
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from plate_straightener import PlateStraightener


def main():
    """Main demo function"""
    print("\n" + "="*70)
    print(" PLATE STRAIGHTENER DEMONSTRATION (EDGE-BASED)")
    print("="*70)
    print("\nThis module takes cropped plate images from YOLO detection")
    print("and straightens them using top/bottom edge alignment.")
    print("\nNote: This is a STANDALONE module and is NOT integrated")
    print("      with the main ALPR pipeline.\n")
    
    # Check if image path is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Try to find a snapshot
        import glob
        # Look in parent directory's snapshots folder
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        snapshot_pattern = os.path.join(parent_dir, "snapshots", "*.jpg")
        snapshots = glob.glob(snapshot_pattern)
        
        if snapshots:
            image_path = snapshots[0]
            print(f"No image specified. Using: {image_path}\n")
        else:
            print("[ERROR] No image path provided and no snapshots found.")
            print("\nUsage: python demo_straightener.py <image_path>")
            print("Example: python demo_straightener.py ../snapshots/MH20EJ0364_20260106_010636.jpg")
            print("Example: python demo_straightener.py \"C:\\path\\to\\image.jpg\"")
            return
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"[ERROR] File not found: {image_path}")
        return
    
    print(f"[OK] Loading image: {image_path}")
    
    try:
        # Load the cropped plate image
        # In real use, this would be the output from YOLO detection
        plate_image = cv2.imread(image_path)
        
        if plate_image is None:
            print(f"[ERROR] Could not load image: {image_path}")
            return
        
        print(f"  Image size: {plate_image.shape}")
        
        # Create straightener instance
        print("\n[OK] Creating PlateStraightener instance...")
        straightener = PlateStraightener(min_angle_threshold=1.0)
        
        print("[OK] Detecting edges and calculating angle...")
        
        # Process the image
        print("\n" + "-"*70)
        print("Processing...")
        print("-"*70)
        straightened, angle, debug_info = straightener.process(plate_image)
        
        # Display results
        print("\n[OK] Displaying results...")
        straightener.display_results(plate_image, straightened, angle, debug_info)
        
        print("\n[OK] Demo complete!")
        
        # Optionally save the straightened image
        if debug_info['needs_correction']:
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(os.path.dirname(__file__), f"{name}_straightened{ext}")
            cv2.imwrite(output_path, straightened)
            print(f"\n[OK] Saved straightened image to: {output_path}")
        
    except Exception as e:
        print(f"\n[ERROR] Error during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
