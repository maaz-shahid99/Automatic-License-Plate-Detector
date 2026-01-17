from PIL import Image, ImageDraw, ImageFont
import os
import random
from .config import (
    PLATE_WIDTH_CAR, PLATE_HEIGHT_CAR,
    PLATE_WIDTH_BIKE, PLATE_HEIGHT_BIKE,
    COLOR_PLAT_BG, COLOR_TEXT, COLOR_BORDER,
    DEFAULT_FONT, FONT_SEARCH_PATHS
)

class PlateRenderer:
    def __init__(self, font_path=None):
        self.font_path = font_path or self._find_best_font()
        
    def _find_best_font(self):
        # Specific overrides found in environment
        candidates = [
            "/usr/share/fonts/open-sans/OpenSans-Semibold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/gnu-free/FreeSansBold.ttf"
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        # Fallback to simple name (might work if OS handles it)
        return "arial.ttf"

    def _load_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except IOError:
            # Fallback for PIL default (usually ugly but works)
            return ImageFont.load_default()

    def generate_image(self, plate_data, add_details=True, text_scale=1.0, blur_text=False):
        """
        Render a plate image from plate_data dictionary.
        plate_data: {'text': 'MH 01 AB 1234', ...}
        text_scale: Float 0.0-1.0, 1.0 means fill space max possible, <1.0 means smaller text
        blur_text: Boolean or float (intensity), apply blur specifically to text layer
        """
        text = plate_data['text']
        
        # Determine dimensions (Car usually)
        width, height = PLATE_WIDTH_CAR, PLATE_HEIGHT_CAR
        
        # Generate random off-white background
        # R, G, B range 200-255 (never pure white, slightly grayish/yellowish)
        base_color_val = random.randint(220, 255)
        # Add slight yellow/gray tint
        r = base_color_val
        g = base_color_val - random.randint(0, 10)
        b = base_color_val - random.randint(0, 20)
        bg_color = (r, g, b)
        
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Draw Border
        border_width = 5
        draw.rectangle(
            [0, 0, width-1, height-1], 
            outline=COLOR_BORDER, 
            width=border_width
        )
        
        # Calculate max possible font size first
        target_height = height * 0.6
        font_size = 60 # start guess
        font = self._load_font(font_size)
        
        # Optimize font size
        target_text_width = width * 0.85
        
        for size in range(60, 150):
            font = self._load_font(size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width > target_text_width or text_height > target_height:
                font = self._load_font(size - 2)
                break
                
        # Apply scaling factor to font size
        final_size = int(font.size * text_scale)
        font = self._load_font(final_size)
        
        # Recalculate size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add "IND" element if requested
        if add_details and random.random() > 0.3:
            self._draw_ind_element(draw, x, y, height)

        # Draw Text
        # Note: If we really want "text blur" separate from plate, we might need a separate layer
        if blur_text:
             # Create a transparent layer for text
            txt_layer = Image.new('RGBA', (width, height), (0,0,0,0))
            txt_draw = ImageDraw.Draw(txt_layer)
            txt_draw.text((x, y), text, fill=COLOR_TEXT, font=font)
            
            # Apply blur to this layer
            from PIL import ImageFilter
            # radius 0-2
            blur_radius = random.uniform(0.5, 1.5)
            txt_layer = txt_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            
            # Composite
            image.paste(txt_layer, (0,0), txt_layer)
        else:
            draw.text((x, y), text, fill=COLOR_TEXT, font=font)
        
        # Add mild grain/dirt to the plate itself before returning
        self._add_plate_texture(draw, width, height)
        
        return image, (x, y, text_width, text_height)

    def _add_plate_texture(self, draw, w, h):
        """Add random speckles/noise to simulate dirty plate surface"""
        if random.random() > 0.5:
            return 
            
        for _ in range(random.randint(50, 200)):
            x = random.randint(1, w-2)
            y = random.randint(1, h-2)
            # Semi-transparent dark dot
            fill = random.randint(150, 200)
            draw.point((x, y), fill=(fill, fill, fill))

    def _draw_ind_element(self, draw, text_x, text_y, plate_height):
        # Draw small "IND" text on the left of the plate or left of text
        # Simplistic implementation: Blue text "IND"
        ind_font_size = 15
        ind_font = self._load_font(ind_font_size)
        
        # Position: Left side of the plate, vertically centered or top-left of text
        # Let's put it on the far left with a small blue circle (chakra)
        
        ind_x = 20
        ind_y = (plate_height - 30) // 2
        
        # Blue Chakra Circle
        chakra_radius = 5
        cx, cy = ind_x + 10, ind_y
        draw.ellipse([cx-chakra_radius, cy-chakra_radius, cx+chakra_radius, cy+chakra_radius], outline=(0,0,139), width=1)
        
        # IND Text below chakra
        draw.text((ind_x + 2, ind_y + 10), "IND", fill=(0,0,139), font=ind_font)
