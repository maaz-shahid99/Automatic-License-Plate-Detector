import os
import csv
import json
import random
from tqdm import tqdm
from .config import STATES
from .text_generator import generate_random_plate
from .plate_renderer import PlateRenderer
from .augmentations import apply_augmentations
from .superimpose import get_random_background, superimpose

class DatasetGenerator:
    def __init__(self, output_dir, backgrounds_dir=None):
        self.output_dir = output_dir
        self.bg_dir = backgrounds_dir
        self.renderer = PlateRenderer()
        self.setup_directories()
        
    def setup_directories(self):
        for split in ['train', 'val', 'test']:
            os.makedirs(os.path.join(self.output_dir, 'images', split), exist_ok=True)
            
        os.makedirs(os.path.join(self.output_dir, 'annotations'), exist_ok=True)

    def generate(self, num_plates=1000, augment=True, blur_prob=0.0, text_blur_prob=0.0, tight_crop=False):
        annotations = []
        
        # Split ratio
        splits = ['train'] * int(num_plates * 0.8) + \
                 ['val'] * int(num_plates * 0.1) + \
                 ['test'] * int(num_plates * 0.1)
        
        # Fill/Trunucate to match exact num_plates
        if len(splits) < num_plates:
            splits += ['train'] * (num_plates - len(splits))
        elif len(splits) > num_plates:
            splits = splits[:num_plates]
            
        random.shuffle(splits)
        
        print(f"Generating {num_plates} plates...")
        
        for i, split in enumerate(tqdm(splits)):
            # 1. Generate Data
            data = generate_random_plate()
            plate_text = data['code'] # Compact version for loading
            display_text = data['text']
            
            # 2. Render Plate
            # Random text scale: usually 0.85 to 1.0 (some varying size)
            text_scale = random.uniform(0.85, 1.0)
            
            # Text blur: do we apply it for this plate?
            do_text_blur = (random.random() < text_blur_prob)
            
            plate_img, _ = self.renderer.generate_image(
                data, 
                text_scale=text_scale,
                blur_text=do_text_blur
            )
            
            # 3. Get Background & Superimpose
            bg_img = get_random_background(self.bg_dir)
            final_img, bbox = superimpose(plate_img, bg_img, tight_crop=tight_crop)
            
            # 4. Augmentations (Global)
            if augment:
                # Intensity of other augs (perspective/noise)
                intensity = 0.4
                # Pass explicit blur_prob
                final_img = apply_augmentations(final_img, intensity=intensity, blur_prob=blur_prob)
            
            # 5. Save
            filename = f"{split}_{i:06d}_{plate_text}.jpg"
            save_path = os.path.join(self.output_dir, 'images', split, filename)
            final_img.save(save_path, quality=90)
            
            # 6. Record Annotation
            # x, y, w, h
            annotations.append({
                'filename': filename,
                'text': data['text'], # "MH 01 AB 1234"
                'code': plate_text,   # "MH01AB1234"
                'bbox': list(bbox),
                'split': split,
                'width': final_img.width,
                'height': final_img.height
            })
            
        self.save_annotations(annotations)
        
    def save_annotations(self, annotations):
        # Save CSVs per split
        splits = ['train', 'val', 'test']
        header = ['filename', 'text', 'code', 'xmin', 'ymin', 'xmax', 'ymax', 'width', 'height']
        
        for split in splits:
            split_data = [a for a in annotations if a['split'] == split]
            csv_path = os.path.join(self.output_dir, 'annotations', f'{split}.csv')
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for item in split_data:
                    x, y, w, h = item['bbox']
                    writer.writerow([
                        item['filename'],
                        item['text'],
                        item['code'],
                        x, y, x+w, y+h,
                        item['width'], item['height']
                    ])
        
        # Save master JSON
        with open(os.path.join(self.output_dir, 'labels.json'), 'w') as f:
            json.dump(annotations, f, indent=2)
            
        print(f"Saved annotations to {self.output_dir}/annotations/")
