# MET Metadata Compliance Checker

Tool for checking global attributes of a netCDF file against METNO requirements.


See [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf) for the metadata requirements.

## Functionality

- checks the global attributes of a provided file against the METNO requirements (see [https://adc.met.no/submit-data-as-netcdf-cf](https://adc.met.no/submit-data-as-netcdf-cf)) and prints an overview report to the CLI
- checks whether the required attributes are given and formatted correctly
- requirements are defined in [configs/mdreqs.yaml](configs/mdreqs.yaml), including which checks should be performed for each mandatory attribute
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

## File structure

```
met-md-checker/
├── requirements.txt            # Required libraries
├── README.md
│
├── mdcheck                     # Executable
├── mdcheck.py                  # Checker class
├── configs/                    # Config templates
│   └── mdreqs.yaml             # METNO requirements
│
├── checks.py                   # Checking functions
├── errors.py                   # MDError, MDWarning
├── helpers.py                  # Smaller helper functions
├── gcmd_tools.py               # Classes for handling GCMD keywords
└── data/                       # Reference data
    ├── licenses.json           # SPDX licenses
    └── sciencekeywords.csv     # GCMD science keywords
```

## Additional resources

- SPDX licenses:
    -  https://spdx.org/licenses/
    - `licenses.json`: https://github.com/spdx/license-list-data/blob/main/json/licenses.json
- GCMD Keyword Viewer: https://gkv-keyword.earthdatacloud.nasa.gov/