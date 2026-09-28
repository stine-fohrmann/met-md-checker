import os, json, re
LICENSES_PATH = os.environ.get('METADATA_LICENSES_FILE', 'met-md-checker/data/licenses.json')
GCMDSK_PATH   = os.environ.get('METADATA_LICENSES_FILE', 'met-md-checker/data/sciencekeywords.csv')

CHECK_FUNCS = {}
CROSSCHECK_FUNCS = {}

def register_check(name: str):
    '''Decorator to register check functions'''
    def decorator(func):
        CHECK_FUNCS[name] = func
        return func
    return decorator

def register_crosscheck(name: str):
    '''Decorator to register cross-check functions'''
    def decorator(func):
        CROSSCHECK_FUNCS[name] = func
        return func
    return decorator


'''--------- General checks (reused for multiple attributes) ---------'''

@register_check('exists')
def check_exists(value: str) -> bool:
    ''' Checks whether an attribute is defined (i.e. not None). '''
    return value is not None

@register_check('nonempty')
def check_nonempty(value: str) -> bool:
    ''' Checks whether a string is nonempty. '''
    return not str(value).strip() == ''

@register_check('entries_nonempty')
def check_entries_nonempty(value: str) -> bool:
    ''' Checks whether a comma separated list has only nonempty elements. '''
    for pair in value.split(','):
        if not pair.strip():
            return False
    return True

@register_check('entries_prefixed')
def check_entries_prefixed(value: str) -> bool:
    ''' Checks whether a comma separated list has only prefixed elements. '''
    for pair in value.split(','):
        if not pair:
            continue
        if ':' not in pair:
            return False
    return True

@register_check('is_between')
def check_is_between(value: str, args: dict) -> bool:
    ''' Checks whether a value is a number between min and max. '''
    try:
        val = float(value)
        return args['min'] <= val <= args['max']
    except ValueError, TypeError:
        return False

@register_check('min_decimals')
def check_min_decs(value: str, args: dict) -> bool:
    ''' Checks whether a given number has at least specified amount of decimal points. '''
    try:
        num_decs = len(str(value).split('.')[1])
        return num_decs >= int(args['min_decs'])
    except ValueError, TypeError:
        return False

@register_check('iso_8601_2004')
def check_iso_8601_2004_time_format(value: str) -> bool:
    ''' Checks whether a string uses ISO 8601:2004 extended date format, i.e. YYYY-MM-DDTHH:MM:SSZ. '''
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    return bool(re.match(pattern, value))

@register_check('valid_date_time')
def check_valid_date_time(value: str) -> bool:
    ''' Checks whether a string's datetime is valid.
        Assumes the string is in ISO 8601:2004 format. '''
    from utils import iso_to_dt64
    try:
        iso_to_dt64(iso_str=value)
        return True
    except ValueError: # Catches if invalid date/time -> check fails
        return False

@register_check('email_addresses_valid')
def check_email_addresses_valid(value: str) -> bool:
    ''' Checks whether each given entry is a "valid" email.
    See the function `is_valid_email` in `utils.py` for what is considered "valid". '''
    from utils import is_valid_email
    for email in value.split(','):
        # Skip empty values
        if not email.strip():
            continue
        if not is_valid_email(email.strip()):
            return False
    return True


'''--------- Specific checks (used for single attributes) ---------'''

@register_check('gcmdsk_present')
def check_gcmdsk_present(value: str) -> bool:
    ''' Checks whether a comma separated list contains at least one element prefixed by "GCMDSK:". '''
    # Separate keywords and prefixes
    kws = {}
    for pair in value.split(','):
        if not pair:
            continue
        if ':' not in pair:
            continue
        key, elements = pair.split(':', 1)
        key = key.strip()
        if not key:
            return False
        
        element_list = [e.strip() for e in elements.split('>') if e.strip()]
        if not element_list:
            return False
        kws.setdefault(key, []).append(element_list)

    # Verify GCMDSK prefix present
    return 'GCMDSK' in kws

@register_check('valid_gcmdsk')
def check_valid_gcmdsk(value: str) -> bool:
    ''' Checks whether each element prefixed by "GCMDSK:" in a 
        comma separated list is a valid GCMD science keyword. '''
    from gcmd_tools import make_gcmd_tree
    sktree = make_gcmd_tree(GCMDSK_PATH)
    # Separate keywords and prefixes
    kws = {}
    for pair in value.split(','):
        key, elements = pair.split(':', 1)
        key = key.strip()
        element_list = [e.strip() for e in elements.split('>') if e.strip()]
        kws.setdefault(key, []).append(element_list)
    if 'GCMDSK' not in kws:
        return False
    for chain in kws.get('GCMDSK'):
        if not sktree.contains(*chain):
            return False
    return True

@register_check('license_formatted_correctly')
def check_license_formatted(value: str) -> bool:
    ''' Checks whether a string has format <URL> (<Identifier>). '''
    pattern = r'^https?://(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}(?:/[^\s]*)? \(([^)]+)\)$'
    match = re.match(pattern, value.strip())
    return bool(match)

@register_check('spdx_license')
def check_spdx_license(value: str) -> bool:
    ''' Checks whether a string is a SPDX license. '''
    # Read licenses from file
    with open(LICENSES_PATH, 'r') as file:
        lic_file = json.load(file)

    # Extract SPDX license IDs and URLS
    spdx_lics = {}
    for l in lic_file['licenses']:
        spdx_lics[l['licenseId']] = l['reference']

    # Extract given URL and ID
    pattern = r'^([^(]+)\s*\((.+?)\)$'
    match = re.match(pattern, value.strip())
    if not match:
        return False
    lic_ref = match.group(1).strip()
    lic_id  = match.group(2).strip()

    # Try to find license ID in SPDX licenses
    if spdx_lics.get(lic_id):
        # Match given URL to SPDX reference
        lic_ref = lic_ref if lic_ref.endswith('.html') else lic_ref + '.html'
        return lic_ref == spdx_lics[lic_id]
    else:
        return False

@register_check('creator_types_valid')
def check_creator_types_valid(value: str) -> bool:
    ''' Check whether each entry in a comma separated list is one
    of 'person', 'group', 'institution', or 'position'. '''
    valid_types = ['person', 'group', 'institution', 'position']

    for given_type in value.split(','):
        if given_type.strip() not in valid_types:
            return False
    return True


'''--------- Cross-checks ---------'''

@register_crosscheck('keywords_map_to_vocabulary')
def check_keywords_map_to_vocab(values: [str]) -> bool:
    ''' Checks whether each prefix in 'keywords' is used in 'keywords_vocabulary' and vice versa. '''

    # Helper function for selecting unique prefixes
    def collect_prefixes(vals: []) -> set:
        prefixes = set()
        for pair in vals.split(','):
            key, elements = pair.split(':', 1)
            key = key.strip()
            prefixes.add(key)
        return prefixes

    # Collect and compare unique prefixes
    return collect_prefixes(values[0]) == collect_prefixes(values[1])

@register_crosscheck('same_length')
def check_same_length(values: [str])-> bool:
    ''' Checks whether the number of entries in the input attributes is consistent. '''
    return len(set([len(val.split(',')) for val in values])) == 1