#!/bin/bash

# This script converts directory containing Thermo .raw files to .mzML format using ThermoRawFileParser.
# https://github.com/CompOmics/ThermoRawFileParser

# REQUIRED EXTERNAL ENVIRONMENT VARIABLES:
# $RAW_DIR: Directory containing .raw files to convert.
# $OUTPUT_MZML_DIR: Directory where the converted .mzML files will be saved.

# $RAW_DIR contains the directory with .raw files, convert them to .mzML (-f=1)
mono /usr/local/thermo/ThermoRawFileParser.exe -d="${RAW_DIR}" -o="${OUTPUT_MZML_DIR}" -f=1

# If you want to delete the original .raw files after conversion, uncomment the following lines:
# rm "./ALL_MZML/*.raw"
# rm "./ALL_MZML/*.RAW"