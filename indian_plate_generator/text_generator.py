import random
from .config import STATES, VALID_CHARS, BHARAT_SERIES_YEARS

def get_random_state():
    return random.choice(STATES)

def get_random_rto_code():
    return f"{random.randint(1, 99):02d}"

def get_random_series(length=None):
    if length is None:
        length = random.choices([1, 2, 3], weights=[0.1, 0.8, 0.1])[0]
    return "".join(random.choices(VALID_CHARS, k=length))

def get_random_number():
    return f"{random.randint(1, 9999):04d}"

def generate_standard_plate():
    """
    Generates a standard Indian number plate text.
    Format: StateCode + RTO + Series + Number
    Example: MH 02 AB 1234
    """
    state = get_random_state()
    rto = get_random_rto_code()
    series = get_random_series()
    number = get_random_number()
    
    # Text with spaces
    text = f"{state} {rto} {series} {number}"
    
    # Compact text (for filename/label if needed)
    code = f"{state}{rto}{series}{number}"
    
    return {
        "text": text,
        "code": code,
        "type": "standard",
        "state": state
    }

def generate_bharat_series():
    """
    Generates a Bharat Series number plate text.
    Format: YY BH #### XX
    Example: 21 BH 1232 XX
    """
    year = random.choice(BHARAT_SERIES_YEARS)
    series_code = "BH"
    number = get_random_number()
    suffix = get_random_series(length=2)
    
    text = f"{year} {series_code} {number} {suffix}"
    code = f"{year}{series_code}{number}{suffix}"
    
    return {
        "text": text,
        "code": code,
        "type": "bharat_series",
        "state": "BH"
    }

def generate_random_plate(bharat_probability=0.2):
    """
    Generate either standard or Bharat series based on probability.
    """
    if random.random() < bharat_probability:
        return generate_bharat_series()
    return generate_standard_plate()
