from PIL import Image
import random
import os
import numpy as np

def create_random_background(width, height):
    """Create a random noise background if no file provided"""
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(arr)

def get_random_background(bg_dir, target_size=(500, 500)):
    """
    Load a random background from directory or generate one.
    target_size: Size to resize/crop background to.
    """
    if bg_dir and os.path.exists(bg_dir):
        files = [f for f in os.listdir(bg_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        if files:
            choice = random.choice(files)
            try:
                img = Image.open(os.path.join(bg_dir, choice)).convert("RGB")
                # Random crop or resize
                if img.width > target_size[0] and img.height > target_size[1]:
                    x = random.randint(0, img.width - target_size[0])
                    y = random.randint(0, img.height - target_size[1])
                    return img.crop((x, y, x + target_size[0], y + target_size[1]))
                else:
                    return img.resize(target_size)
            except Exception:
                pass
    
    return create_random_background(*target_size)

def superimpose(plate_img, bg_img, tight_crop=False):
    """
    Superimpose plate onto background.
    tight_crop: if True, returns an image roughly the size of the plate (plus padding),
                instead of the full background size.
    Returns: combined_image, bbox (x, y, w, h)
    """
    bg_w, bg_h = bg_img.size
    
    if tight_crop:
        # For tight crop, we want the plate to be the main subject.
        # We start with the plate size.
        # Add random padding (0 to 20 pixels) to simulate imperfect crop
        pad_x = random.randint(5, 30)
        pad_y = random.randint(5, 30)
        
        target_w = plate_img.width
        target_h = plate_img.height
        
        # Determine strict crop size
        crop_w = target_w + pad_x * 2
        crop_h = target_h + pad_y * 2
        
        # Resize background crop to this size (or taking a crop from bg)
        # If bg is large enough, crop a piece
        if bg_w > crop_w and bg_h > crop_h:
            x = random.randint(0, bg_w - crop_w)
            y = random.randint(0, bg_h - crop_h)
            bg_crop = bg_img.crop((x, y, x + crop_w, y + crop_h))
        else:
            bg_crop = bg_img.resize((crop_w, crop_h))
            
        # Paste plate in center
        paste_x = (crop_w - target_w) // 2
        paste_y = (crop_h - target_h) // 2
        
        # Slight random shift
        paste_x += random.randint(-5, 5)
        paste_y += random.randint(-5, 5)
        
        bg_crop.paste(plate_img, (paste_x, paste_y))
        
        return bg_crop, (paste_x, paste_y, target_w, target_h)

    # ... Normal Superimpose Logic ...
    # Scale plate to be usually 60-90% of background width for OCR efficiency
    # Random scale
    scale_factor = random.uniform(0.6, 0.9)
    
    # Check aspect ratios
    # Maintain plate aspect ratio
    target_w = int(bg_w * scale_factor)
    aspect = plate_img.width / plate_img.height
    target_h = int(target_w / aspect)
    
    if target_h > bg_h:
        # Constrain by height if needed
        target_h = int(bg_h * 0.8)
        target_w = int(target_h * aspect)
        
    resized_plate = plate_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Random position
    max_x = bg_w - target_w
    max_y = bg_h - target_h
    
    x = random.randint(0, max(0, max_x))
    y = random.randint(0, max(0, max_y))
    
    # Create valid mask if plate has transparency (not currently, but good practice)
    mask = resized_plate.convert("RGBA").getchannel("A") if "A" in resized_plate.getbands() else None
    
    bg_img.paste(resized_plate, (x, y), mask)
    
    return bg_img, (x, y, target_w, target_h)
