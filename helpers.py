'''
Smaller helper functions
'''
import numpy as np
from email_validator import validate_email, EmailNotValidError

def iso_to_dt64(iso_str: str) -> np.datetime64:
    ''' Converts valid ISO 8601:2004 string to datetime64. '''
    ymd = iso_str.split('T')[0]
    hms = iso_str.split('T')[1][:-1]
    dt64 = np.datetime64('T'.join([ymd, hms]))
    return dt64

def is_valid_url(url: str) -> bool:
    ''' Checks whether a URL is valid. '''
    from urllib.parse import urlparse
    tokens = urlparse(url)
    return all(getattr(tokens, attr) for attr in ('scheme', 'netloc'))

def is_valid_email(email: str) -> bool:
    ''' Checks whether an email address is valid. '''
    try:
        val_email = validate_email(email)
        return True
    except EmailNotValidError:
        return False

def split_list(value: str) -> list[str]:
    return [item.strip() for item in str(value).split(',') if item.strip()]