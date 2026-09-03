import json
import xarray as xr

MINREQSPATH = 'met-md-checker/minimal_attrs.json'
INDENT = '     '
REPORT_WIDTH = 60

class MDChecker():
    def __init__(self, input_file, minimal_attrs=None, global_attrs=None):
        self.input_file = input_file        # netCDF file to check
        self.minimal_attrs = minimal_attrs  # list of minimal required global attributes
        self.global_attrs = global_attrs
        self.missing_attrs = []
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
        self.global_attrs = ds.attrs
    
    def printReport(self, missing_attrs):
        # Centered title and link to specifications
        print("-" * REPORT_WIDTH)
        print("\n" + 'MET Metadata Compliance Report'.center(REPORT_WIDTH))
        print('https://adc.met.no/submit-data-as-netcdf-cf'.center(REPORT_WIDTH))
        print('\n' + "-" * REPORT_WIDTH)

        # Print file name 
        print(INDENT + f'File:   {self.input_file}')

        # Print results
        if len(missing_attrs) <= 0:
            print(INDENT + 'All tests passed. All required attributes are defined.')
            print("-" * REPORT_WIDTH)
        else:
            print(INDENT + f'Errors: {len(missing_attrs)}')
            print('\n' + "-" * REPORT_WIDTH)

            count = 1
            for attr in missing_attrs:
                print(INDENT + f'{count:2.0f}) Missing attribute: {attr['name']}')
                count += 1
            print("-" * REPORT_WIDTH)
            
    def checkMinimalReqs(self):
        '''
        Checks whether minimal required attributes are given 
        (doesn't verify formatting)
        '''
        self.getMinimalRequirements()
        self.getGlobalAttrs()

        for attr in self.minimal_attrs:

            # check whether required attributes exist  
            if not attr['name'] in self.global_attrs:
                self.missing_attrs.append(attr)
        
        # Print results in terminal
        self.printReport(self.missing_attrs)
    
    def checkTimeFormat(self, attr_str):
        from utils import iso_to_dt64

        try:    # check if attribute defined
            time_str = self.global_attrs[attr_str]
            try:    # check if valid ISO format
                iso_to_dt64(time_str)
            except: # return error if invalid date or format
                return Error(attr=attr_str, message='is invalid date or date format')
        except: # return error if attribute not defined
            return Error(attr=attr_str, message='is not defined')
    
    def checkTimeAttrs(self):
        # time_coverage_start
        # time_coverage_end
        # date_created

        required_time_attrs = ['time_coverage_start', 'time_coverage_end', 'date_created']

        for attr_str in required_time_attrs:
            result = self.checkTimeFormat(attr_str)
            if isinstance(result, Error):
                self.errors.append(result)
    
    def printErrors(self):
        print(INDENT + f'Errors: {len(self.errors)}')
        print("-" * REPORT_WIDTH)
        for e in self.errors:
            e.printFull(INDENT)


class Error():
    def __init__(self, attr, message=None):
        self.message = message
        self.attr = attr
    
    def printFull(self, INDENT=''):
        print(INDENT + f'Error: {self.attr} {self.message}')


def main(args):
    # Get minimal required attrs
    with open(MINREQSPATH, 'r') as file:
        minimal_attrs = json.load(file)

    checker = MDChecker(input_file=args.input_file, minimal_attrs=minimal_attrs)
    checker.checkMinimalReqs()