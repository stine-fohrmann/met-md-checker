# MET Metadata Compliance Checker

Tool for checking global attributes of a netCDF file against METNO requirements.


See [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf) for the metadata requirements.

## Current functionality

- checks the global attributes of a provided file against the METNO requirements (see [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf)) and prints an overview report to the CLI
- checks whether the required attributes are given and formatted correctly
- requirements are defined in [mdreqs.yaml](mdreqs.yaml), including which checks should be performed for each mandatory attribute
- currently, only the required attributes are checked, not the optional ones

## Usage

To install all required libraries, run:
```
pip install -r met-md-checker/requirements.txt
```

To check whether a netCDF file complies with the MET requirements, run:
```
met-md-checker/mdcheck path/to/file.nc 
```