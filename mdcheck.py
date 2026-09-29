REQSPATH = 'met-md-checker/configs/mdreqs.yaml'
INDENT = '     '
REPORT_WIDTH = 60

class MDChecker():
    def __init__(self, input_file):
        self.input_file = input_file    # netCDF file to check
        self.errors = []                # list for storing errors
        self.warnings = []              # list for storing warnings
        self.checks_tracker = {}        # dict for tracking which checks were performed & their results
    
    def getAttrs(self):
        '''Get global attributes from input file'''
        import xarray as xr
        ds = xr.open_dataset(self.input_file, decode_times=False)
        self.attrs = ds.attrs
    
    def setAttrs(self, attrs: dict):
        '''Manually set the attribute dict to be validated'''
        self.attrs = attrs
    
    def printAttrs(self):
        '''Prints the attributes to be validated'''
        for key, val in self.attrs.items():
            print(f'{key}: {val}')

    def printReport(self):
        # Centered title and link to specifications
        print("-" * REPORT_WIDTH)
        print("\n" + 'MET Metadata Compliance Report'.center(REPORT_WIDTH))
        print('https://adc.met.no/submit-data-as-netcdf-cf'.center(REPORT_WIDTH))
        print('\n' + "-" * REPORT_WIDTH)

        # Print file name
        print(INDENT + f'File:     {self.input_file}')
        print(INDENT + f'Errors:   {len(self.errors)}')
        print(INDENT + f'Warnings: {len(self.warnings)}')

        # Print results
        if (len(self.errors) <= 0) and (len(self.warnings) <= 0):
            print(INDENT + 'All tests passed. All required attributes are defined.')
            print("-" * REPORT_WIDTH)
        else:
            print("-" * REPORT_WIDTH)
            # Print errors
            for e in self.errors:
                e.printFull(INDENT)
            print("-" * REPORT_WIDTH)
            # Print warnings
            for w in self.warnings:
                w.printFull(INDENT)
            print("-" * REPORT_WIDTH)
    
    def loadRequirements(self) -> dict:
        '''Loads requirements/checks from YAML'''
        import yaml
        with open(REQSPATH) as f:
            reqs = yaml.safe_load(f)
        if not isinstance(reqs, dict) or 'attributes' not in reqs:
            raise ConfigError('config must have "attributes" section')
        self.requirements = reqs
            
    def checkRequirements(self, attrs: dict = None):
        '''Checks attributes from input file against requirements defined in YAML'''
        if attrs:
            self.setAttrs(attrs=attrs)
        else:
            self.getAttrs()     # Get global attributes from input file
        self.loadRequirements() # Read requirements (checks) from YAML
        self.runChecks()        # Run checks
        self.printReport()      # Print results in terminal

    def runChecks(self, requirements: dict = None):
        '''Executes checks, adds errors and warnings to respective lists'''
        from checks import CHECK_FUNCS, CROSSCHECK_FUNCS
        from errors import MDError, MDWarning

        requirements = requirements if requirements else self.requirements
        # Helper func for checking if a specific test has passed
        def has_passed(ids):
            for check_id in ids:
                attr_name = check_id.split('/')[0]
                passed = next((c for c in self.checks_tracker[attr_name]['checks'] if c['id'] == check_id))['passed']
                if not passed:
                    return False
            return True
        
        for attr_name, attr_config in requirements['attributes'].items():
            value = self.attrs.get(attr_name)
            self.checks_tracker[attr_name] = {}
            self.checks_tracker[attr_name]['checks'] = []

            # Execute checks
            for check in attr_config.get('checks', []):
                check_type = check.get('type')
                conditions = check.get('conditions')
                args = check.get('args')

                if conditions:
                    if has_passed(conditions):
                        check_passed = CHECK_FUNCS[check_type](value, args) if args else CHECK_FUNCS[check_type](value)
                    else:
                        continue
                else:
                    check_passed = CHECK_FUNCS[check_type](value, args) if args else CHECK_FUNCS[check_type](value)
                
                check_track = check.copy()
                check_track['passed'] = check_passed
                self.checks_tracker[attr_name]['checks'].append(check_track)

                if not check_passed:
                    match check.get('severity'):
                        case 'error':
                            self.errors.append(MDError(attr=attr_name, message=check.get('message')))
                        case 'warning':
                            self.warnings.append(MDWarning(attr=attr_name, message=check.get('message')))

        # Execute cross-checks
        for check in requirements['cross_checks']:
            check_type = check.get('type')
            conditions = check.get('conditions')
            self.checks_tracker['cc'] = []
            attrs = check.get('involved_attributes')

            # Execute cross check if conditions are met
            if conditions:
                if has_passed(conditions):
                    values = [self.attrs[a] for a in attrs]
                    check_passed = CROSSCHECK_FUNCS[check_type](values)
                else:
                    continue
            else:
                values = [self.attrs[a] for a in attrs]
                check_passed = CROSSCHECK_FUNCS[check_type](values)
            
            check_track = check.copy()
            check_track['passed'] = check_passed
            self.checks_tracker['cc'].append(check_track)
            
            if not check_passed:
                match check.get('severity'):
                    case 'error':
                        self.errors.append(MDError(attr='cross-check', message=check.get('message')))
                    case 'warning':
                        self.warnings.append(MDWarning(attr='cross-check', message=check.get('message')))


def main(args):
    checker = MDChecker(input_file=args.input_file)
    checker.checkRequirements()