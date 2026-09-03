# MET Metadata Compliance Checker

Tool for checking global attributes of a netCDF file against METNO requirements.


See [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf) for the metadata requirements.

## Current functionality

- checks whether the global attributes of a provided file contain all attributes required by MET
- checks whether time attributes are formatted correctly
- contains script for scraping minimal requirements from [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf)

## Usage

To install all required libraries, run:
```
pip install -r met-md-checker/requirements.txt
```

To check whether a netCDF file complies with the MET requirements, run:
```
met-md-checker/mdcheck path/to/file.nc 
```

To scrape the minimal requirements, run: 

```
python met-md-checker/scrape_specs.py
```
The requirements will be saved at `met-md-checker/minimal_attrs.json`