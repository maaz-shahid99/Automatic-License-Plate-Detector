#!/usr/bin/env python3
import argparse
import os
import sys

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from indian_plate_generator.dataset_generator import DatasetGenerator

def main():
    parser = argparse.ArgumentParser(description="Synthetic Indian Number Plate Dataset Generator")
    parser.add_argument("--count", type=int, default=100, help="Number of images to generate")
    parser.add_argument("--output", type=str, default="dataset", help="Output directory")
    parser.add_argument("--backgrounds", type=str, default=None, help="Directory containing background images")
    parser.add_argument("--no-augment", action="store_true", help="Disable augmentations")
    parser.add_argument("--blur-prob", type=float, default=0.0, help="Probability of global image blur (haziness)")
    parser.add_argument("--text-blur-prob", type=float, default=0.0, help="Probability of text-only blur")
    parser.add_argument("--tight-crop", action="store_true", help="Crop image to plate bounds (plus padding) for OCR training")
    
    args = parser.parse_args()
    
    output_dir = os.path.abspath(args.output)
    
    print(f"Starting generation...")
    print(f"Count: {args.count}")
    print(f"Output: {output_dir}")
    print(f"Augmentations: {not args.no_augment}")
    print(f"Blur Prob: {args.blur_prob}, Text Blur Prob: {args.text_blur_prob}")
    print(f"Tight Crop: {args.tight_crop}")
    
    if args.backgrounds:
        print(f"Backgrounds: {args.backgrounds}")
    else:
        print("Backgrounds: using synthetic noise")
        
    generator = DatasetGenerator(
        output_dir=output_dir,
        backgrounds_dir=args.backgrounds
    )
    
    generator.generate(
        num_plates=args.count,
        augment=not args.no_augment,
        blur_prob=args.blur_prob,
        text_blur_prob=args.text_blur_prob,
        tight_crop=args.tight_crop
    )
    
    print("Done!")

if __name__ == "__main__":
    main()
