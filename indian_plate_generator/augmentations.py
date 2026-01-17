import cv2
import numpy as np
from PIL import Image
import random

def cv2_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def pil_to_cv2(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def add_noise(img_cv):
    """Add Gaussian noise"""
    row, col, ch = img_cv.shape
    mean = 0
    var = random.randint(10, 100)
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noisy = img_cv + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)

def add_blur(img_cv):
    """Add Gaussian or Motion Blur"""
    ksize = random.choice([3, 5, 7])
    if random.random() > 0.5:
        # Gaussian
        return cv2.GaussianBlur(img_cv, (ksize, ksize), 0)
    else:
        # Motion (approximated)
        kernel = np.zeros((ksize, ksize))
        kernel[int((ksize-1)/2), :] = np.ones(ksize)
        kernel /= ksize
        return cv2.filter2D(img_cv, -1, kernel)

def adjust_brightness_contrast(img_cv, brightness_range=(-30, 30), contrast_range=(0.7, 1.3)):
    alpha = random.uniform(*contrast_range) # Contrast
    beta = random.randint(*brightness_range)   # Brightness
    return cv2.convertScaleAbs(img_cv, alpha=alpha, beta=beta)

def random_perspective(img_cv):
    """Apply random perspective perspective transform"""
    rows, cols, ch = img_cv.shape
    
    # Source points (corners)
    src_pts = np.float32([[0, 0], [cols-1, 0], [0, rows-1], [cols-1, rows-1]])
    
    # Destination points (perturbed corners)
    # Move corners by up to 10-20% of dims
    dx = cols * 0.1
    dy = rows * 0.1
    
    dst_pts = np.float32([
        [random.uniform(0, dx), random.uniform(0, dy)],
        [cols - random.uniform(0, dx), random.uniform(0, dy)],
        [random.uniform(0, dx), rows - random.uniform(0, dy)],
        [cols - random.uniform(0, dx), rows - random.uniform(0, dy)]
    ])
    
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    
    # Output size can be same or slightly large to fit?
    # For OCR chips, usually we want tight crop around plate, but here we might wrap it.
    # We'll return the warped image with black borders potentially.
    dst = cv2.warpPerspective(img_cv, M, (cols, rows), borderValue=(255,255,255))
    return dst

def apply_augmentations(image_pil, intensity=0.5, blur_prob=0.0):
    """
    Apply a chain of augmentations.
    intensity: probability of applying each geometric/noise effect (e.g. 0.5)
    blur_prob: specific probability for blur (default 0.0 for 'non-hazy')
    """
    img_cv = pil_to_cv2(image_pil)
    
    # Geometric transforms (Perspective)
    # We want these even if "non-hazy" usually, unless specifically disabled.
    # But usually "non-hazy" refers to image quality, not perspective.
    if random.random() < intensity:
        img_cv = random_perspective(img_cv)
    
    # Noise (Grain)
    if random.random() < intensity:
        img_cv = add_noise(img_cv)
        
    # Blur (Haziness) -> Controlled by blur_prob now
    if random.random() < blur_prob:
        img_cv = add_blur(img_cv)
        
    # Lighting (Brightness/Contrast) -> Always apply some variation for realism
    # unless intensity is 0 (which means clean plate)
    # But user asked for specific "randomness on brightness".
    # So we apply it with high probability but controllable range.
    if intensity > 0:
        # Use wider range if intensity is high
        b_range = (-50, 50) if intensity > 0.6 else (-30, 30)
        c_range = (0.6, 1.4) if intensity > 0.6 else (0.8, 1.2)
        img_cv = adjust_brightness_contrast(img_cv, b_range, c_range)
        
    return cv2_to_pil(img_cv)
