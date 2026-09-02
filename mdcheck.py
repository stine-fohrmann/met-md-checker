import json
import xarray as xr

MINREQSPATH = 'met-md-checker/minimal_attrs.json'

class MDChecker():
    def __init__(self, input_file, minimal_attrs=None, global_attrs=None):
        self.input_file = input_file        # netCDF file to check
        self.minimal_attrs = minimal_attrs  # list of minimal required global attributes
        self.global_attrs = global_attrs
    
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
        width = 60
        indent = '     '

        # Centered title and link to specifications
        print("-" * width)
        print("\n" + 'MET Metadata Compliance Report'.center(width))
        print('https://adc.met.no/submit-data-as-netcdf-cf'.center(width))
        print('\n' + "-" * width)

        # Print file name 
        print(indent + f'File:   {self.input_file}')

        # Print results
        if len(missing_attrs) <= 0:
            print(indent + 'All tests passed. All required attributes are defined.')
            print("-" * width)
        else:
            print(indent + f'Errors: {len(missing_attrs)}')
            print('\n' + "-" * width)

            count = 1
            for attr in missing_attrs:
                print(indent + f'{count:2.0f}) Missing attribute: {attr['name']}')
                count += 1
            print("-" * width)
            
    def checkMinimalReqs(self):
        '''
        Checks whether minimal required attributes are given 
        (doesn't verify formatting)
        '''
        self.getMinimalRequirements()
        self.getGlobalAttrs()

        missing_attrs = []

        for attr in self.minimal_attrs:

            # check whether required attributes exist  
            if not attr['name'] in self.global_attrs:
                missing_attrs.append(attr)
        
        # Print results in terminal
        self.printReport(missing_attrs)


def main(args):
    # Get minimal required attrs
    with open(MINREQSPATH, 'r') as file:
        minimal_attrs = json.load(file)

    checker = MDChecker(input_file=args.input_file, minimal_attrs=minimal_attrs)
    checker.checkMinimalReqs()