'''
Smaller helper functions
'''


def iso_to_dt64(iso_str):
    ''' Converts valid ISO 8601:2004 string to datetime64

    Parameters:
    -----------
    iso_str : string
        Valid time in ISO 8601:2004 format
    
    Returns:
    --------
    numpy.datetime64
        Same time stamp as datetime64
    '''
    import numpy as np

    ymd = iso_str.split('T')[0]
    hms = iso_str.split('T')[1][:-1]
    dt64 = np.datetime64('T'.join([ymd, hms]))
    return dt64

def is_valid_url(url: str):
    from urllib.parse import urlparse
    ''' Checks whether a URL is valid
    
    Parameters:
    -----------
    url : string
        the URL to be validated
    
    Returns:
    --------
    boolean
    '''
    tokens = urlparse(url)
    return all(getattr(tokens, attr) for attr in ('scheme', 'netloc'))

def is_valid_email(email: str):
    ''' Checks whether a URL is valid
    
    Parameters:
    -----------
    email : string
        the email address to be validated
    
    Returns:
    --------
    boolean
    '''
    import re
    reg = re.match("[^@]+@[^@]+\\.[^@]+", email)

    return bool(reg)

def split_list(value) -> list[str]:
    return [item.strip() for item in str(value).split(',') if item.strip()]