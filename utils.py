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