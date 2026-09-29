'''
Smaller helper functions
'''


def iso_to_dt64(iso_str: str) -> numpy.datetime64:
    ''' Converts valid ISO 8601:2004 string to datetime64. '''
    import numpy as np
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
    import re
    reg = re.match("[^@]+@[^@]+\\.[^@]+", email)
    return bool(reg)

def split_list(value) -> list[str]:
    return [item.strip() for item in str(value).split(',') if item.strip()]