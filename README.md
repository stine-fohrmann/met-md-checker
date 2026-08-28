# ADC Metadata Compliance Checker

Tool for checking global attributes of a netCDF file against METNO requirements.


See [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf) for the metadata requirements.

## Current functionality

- checks whether the global attributes of a provided file contain all attributes required by MET
- contains script for scraping minimal requirements from [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf)

## Usage

To check whether a netCDF file complies with the MET requirements, run:
```
adc-checker/adccheck [path-to-file] 
```

To scrape the minimal requirements, run: 

```
python adc-checker/scrape_specs.py
```
The requirements will be saved at `adc-checker/minimal_attrs.json`