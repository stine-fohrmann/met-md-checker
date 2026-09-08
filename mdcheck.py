import json
import xarray as xr

MINREQSPATH = 'met-md-checker/minimal_attrs.json'
INDENT = '     '
REPORT_WIDTH = 60

class MDChecker():
    def __init__(self, input_file, minimal_attrs=None, given_attrs=None):
        self.input_file = input_file        # netCDF file to check
        self.minimal_attrs = minimal_attrs  # list of minimal required global attributes
        self.given_attrs = given_attrs
        self.errors = []
    
    def getMinimalRequirements(self):
        # Get minimal required attrs
        if not self.minimal_attrs:
            with open(MINREQSPATH, 'r') as file:
                self.minimal_attrs = json.load(file)
    
    def getGlobalAttrs(self):
        # open netCDF file
        ds = xr.open_dataset(
            self.input_file,
            decode_times=False,
        )
        # get attributes
        self.given_attrs = ds.attrs
    
    def printReport(self):
        # Centered title and link to specifications
        print("-" * REPORT_WIDTH)
        print("\n" + 'MET Metadata Compliance Report'.center(REPORT_WIDTH))
        print('https://adc.met.no/submit-data-as-netcdf-cf'.center(REPORT_WIDTH))
        print('\n' + "-" * REPORT_WIDTH)

        # Print file name 
        print(INDENT + f'File:   {self.input_file}')

        # Print results
        if len(self.errors) <= 0:
            print(INDENT + 'All tests passed. All required attributes are defined.')
            print("-" * REPORT_WIDTH)
        else:
            self.printErrors()
            print("-" * REPORT_WIDTH)
            
    def checkMinimalReqs(self):
        '''
        Checks whether minimal required attributes are given 
        (doesn't verify formatting)
        '''
        self.getMinimalRequirements()
        self.getGlobalAttrs()

        # verify geospatial attributes are given and formatted correctly
        self.checkGeospatial()
        # verify time attributes are given and formatted correctly
        self.checkTimeAttrs()
        self.checkLicense()
        self.checkCreator()
        # verify publisher info is given and valid format
        self.checkPublisher()

        # remove time attributes from list to be checked
        # TODO get time attrs from json instead (?)
        required_geo_attrs = ['geospatial_lat_min', 'geospatial_lat_max', 'geospatial_lon_min', 'geospatial_lon_max']
        required_time_attrs = ['time_coverage_start', 'time_coverage_end', 'date_created']
        req_creator_attrs = ['creator_type', 'creator_name', 'creator_institution', 'creator_email']
        req_publisher_attrs = ['publisher_name', 'publisher_url', 'publisher_institution', 'publisher_email']
        other = ['license']

        # verify other attributes are given
        for attr in self.minimal_attrs:
            # skip time attrs
            if attr['name'] in required_geo_attrs+required_time_attrs+req_publisher_attrs+req_creator_attrs+other:
                continue

            # check whether required attributes exist  
            if not attr['name'] in self.given_attrs:
                self.errors.append(Error(attr['name'], message='is not defined'))
        
        # Print results in terminal
        self.printReport()

    
    def _check(self, attr: str, validate=None) -> None:
        try:
            val = self.given_attrs[attr]
            # verify not empty
            if val.strip() == '':
                self.errors.append(Error(attr=attr, message=f'is empty'))
                return
        except KeyError:
            self.errors.append(Error(attr, message='is not defined'))
            return
        
        if validate:
            validate(val)

    def _validate_geo(self, attr: str, val):
        v = float(val)
        # verify at least 2 decimal points
        if len(str(v).split('.')[1]) < 2:
            self.errors.append(Error(attr, message=f'"{val}" has too few decimal places. Include at least 2 decimal places.'))
        
        # verify latitude between -90 and 90
        if attr.startswith('geospatial_lat') and not -90 <= v <= 90:
            self.errors.append(Error(attr, message=f'"{val}" is invalid. Must be between -90 and 90.'))
        
        # verify longitude between -180 and 180
        if attr.startswith('geospatial_lon') and not -180 <= v <= 180:
            self.errors.append(Error(attr, message=f'"{val}" is invalid. Must be between -180 and 180.'))
    
    def checkGeospatial(self):
        '''Checks whether the geospatial bounds are given and are valid values'''
        required_geo_attrs = ['geospatial_lat_min', 'geospatial_lat_max', 'geospatial_lon_min', 'geospatial_lon_max']
        for attr in required_geo_attrs:
            self._check(attr, lambda v, a=attr: self._validate_geo(a, v))
    
    def _validate_time(self, attr: str, val):
        from utils import iso_to_dt64

        # validate ISO format
        try:
            iso_to_dt64(val)
        except ValueError:
            self.errors.append(Error(attr=attr, message=f'"{val}" is an invalid date or date format'))

    def checkTimeAttrs(self):
        ''' Checks whether the required time attributes are given and formatted in ISO 8601:2004 '''
        required_time_attrs = ['time_coverage_start', 'time_coverage_end', 'date_created']
        for attr in required_time_attrs:
            self._check(attr, lambda v, a=attr: self._validate_time(a, v))
    
    def _validate_license(self, attr: str, val):
        # split into url and id
        licenselist = [string.replace(')', '').strip() for string in val.split('(')]

        is_valid_license = False
        
        if len(licenselist) == 2:
            lic_url = licenselist[0]
            lic_id = licenselist[1]

            # process url to match reference urls
            lic_url = lic_url.replace('http://', 'https://')
            if not lic_url.endswith('.html'):
                lic_url += '.html'

            with open('met-md-checker/data/licenses.json', 'r') as file:
                licenses = json.load(file)
            
            for l in licenses['licenses']:
                if l['licenseId'] == lic_id:
                    # if license id found, check link
                    if l['reference'] == lic_url:
                        is_valid_license = True

        if not is_valid_license:
            self.errors.append(Error(attr, message=f'"{val}" is not a valid standard license. Provide the license as "URL (identifier)".'))

    def checkLicense(self):
        # validate existence and format of each individual attribute
        attr = 'license'
        self._check(attr, lambda v, a=attr: self._validate_license(a, v))

    def _validate_creator(self, attr: str, val):
        from utils import is_valid_email
        # validate email address
        if attr == 'creator_email' and not is_valid_email(val):
            self.errors.append(Error(attr=attr, message=f'"{val}" is not a valid email address'))
     
    def checkCreator(self):
        '''Checks whether creator information is given correctly'''
        from utils import split_list
        req_creator_attrs = ['creator_type', 'creator_name', 'creator_institution', 'creator_email']

        # validate existence and format of each individual attribute
        for attr in req_creator_attrs:
            self._check(attr, lambda v, a=attr: self._validate_creator(a, v))
        
        # cross-attribute: validate lists have same length
        num_creators = set()
        for attr in req_creator_attrs:
            try:
                val = self.given_attrs[attr]
                num_creators.add(len(split_list(val)))
            except KeyError:
                continue
        if not len(num_creators) == 1:
            self.errors.append(InconsistentLengthError(attrs=req_creator_attrs))
    
    def _validate_pub(self, attr: str, val):
        from utils import is_valid_url, is_valid_email

        # validate url
        if attr == 'publisher_url' and not is_valid_url(val):
            self.errors.append(Error(attr=attr, message=f'"{val}" is not a valid URL'))

        # validate email address
        if attr == 'publisher_email' and not is_valid_email(val):
            self.errors.append(Error(attr=attr, message=f'"{val}" is not a valid email address'))
    
    def checkPublisher(self):
        '''Checks whether the publisher information is given correctly'''
        req_publisher_attrs = ['publisher_name', 'publisher_url', 'publisher_institution', 'publisher_email']
        for attr in req_publisher_attrs:
            self._check(attr, lambda v, a=attr: self._validate_pub(a, v))

    def printErrors(self):
        print(INDENT + f'Errors: {len(self.errors)}')
        print("-" * REPORT_WIDTH)
        for e in self.errors:
            e.printFull(INDENT)
    
    def printGivenAttrs(self):
        for key, val in self.given_attrs.items():
            print(f'{key}: {val}')

class Error():
    def __init__(self, attr, message=None):
        self.message = message
        self.attr = attr
    
    def printFull(self, INDENT=''):
        print(INDENT + f'Error: {self.attr} {self.message}')

class InconsistentLengthError(Error):
    def __init__(self, attrs: list, message='don\'t have the same number of elements.'):
        self.attrs = attrs
        self.message = message
    
    def printFull(self, INDENT=''):
        print(INDENT + f'Error: {", ".join([a for a in self.attrs])} {self.message}')

def main(args):
    # Get minimal required attrs
    with open(MINREQSPATH, 'r') as file:
        minimal_attrs = json.load(file)

    checker = MDChecker(input_file=args.input_file, minimal_attrs=minimal_attrs)
    checker.checkMinimalReqs()