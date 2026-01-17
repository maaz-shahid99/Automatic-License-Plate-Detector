import os

# State and UT codes
STATES = [
    "MH",  # Maharashtra
    "DL",  # Delhi
    "UP",  # Uttar Pradesh
    "KA",  # Karnataka
    "TN",  # Tamil Nadu
    "GJ",  # Gujarat
    "WB",  # West Bengal
    "TS",  # Telangana
    "AP",  # Andhra Pradesh
    "MP",  # Madhya Pradesh
    "RJ",  # Rajasthan
    "HR",  # Haryana
    "PB",  # Punjab
    "KL",  # Kerala
    "BR",  # Bihar
    "OD",  # Odisha
    "JH",  # Jharkhand
    "CG",  # Chhattisgarh
    "HP",  # Himachal Pradesh
    "UK",  # Uttarakhand
    "JK",  # Jammu & Kashmir
    "AS",  # Assam
    "GA",  # Goa
    "SK",  # Sikkim
    "TR",  # Tripura
    "ML",  # Meghalaya
    "MN",  # Manipur
    "NL",  # Nagaland
    "AR",  # Arunachal Pradesh
    "MZ",  # Mizoram
    "CH",  # Chandigarh
    "PY",  # Puducherry
    "AN",  # Andaman & Nicobar
    "LA",  # Ladakh
    "DN",  # Dadra and Nagar Haveli and Daman and Diu
]

# Exclude I and O from series to avoid confusion with 1 and 0
VALID_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ"

# Bharat Series
BHARAT_SERIES_YEARS = ["21", "22", "23", "24", "25"]

# Plate Config
PLATE_WIDTH_CAR = 500
PLATE_HEIGHT_CAR = 120

PLATE_WIDTH_BIKE = 285
PLATE_HEIGHT_BIKE = 200

# Colors (RGB)
COLOR_PLAT_BG = (255, 255, 255)
COLOR_TEXT = (0, 0, 0)
COLOR_BORDER = (0, 0, 0)

# IND Feature Colors
COLOR_IND_BLUE = (0, 0, 139) # Strip color? Actually strip is usually holographic/light, text is blue? 
# Usually high security plates have a blue strip on the left with "IND" in white?
# Let's approximate: Blue text "IND" + Chakra. 
# Or sometimes a blue patch on left.
# Standard HSRP:
# Left side: Blue band (top to bottom).
# Inside blue band: Top "IND", Middle Chakra (Hologram).
COLOR_HSRP_STRIP = (240, 240, 255) # Light blueish/holographic look or just plain white in simple models?
# Real HSRP has a blue rectangle on the left.
COLOR_STRIP_BLUE = (10, 50, 160) # Dark blue for the strip background if we go that route, or text.
# Let's stick to simple "IND" text for now, can be sophisticated later.

# Fonts
# Try to find a system font, otherwise fallback
FONT_SEARCH_PATHS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "~/.fonts"
]

DEFAULT_FONT = "DejaVuSans-Bold.ttf" # Common on Linux
ALT_FONT = "Arial_Bold.ttf"
