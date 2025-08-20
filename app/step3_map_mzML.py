"""
This script maps .raw file names to their corresponding .mzML file paths.
It reads a CSV file containing the .raw file names, searches for the corresponding .mzML files in a specified directory, and writes the results to a new CSV file.

ENVIRONMENT VARIABLES:
${COMBINED_SEQUENCE_DIR} - Directory containing the sequence CSV files to be combined. Output CSV file will also be saved here.
${MZML_DIR} - Directory containing the .mzML files to be mapped. Subdirectories are also searched for the .mzML files.
Run via `python3.11 step3_map_mzML.py`
"""

import pandas as pd
import os
from os import path

def find_mzml_file(filename, base_dir):
    """
    This function searches for the mzML file in a directory corresponding to a given filename.

    Parameters:
        filename (str): The name of the .raw-file which the sought .mzML-file corresponds to.
        base_dir (str): Path to the directory where the .mzML files are located.

    Returns:
        str: The path to the found .mzML file or an error message if it could not be discovered.
    """
    # Generate mzML filename from raw filename
    mzml_filename = f"{filename}.mzML"

    # Search for the file in base_dir and all its subdirectories
    for root, dirs, files in os.walk(base_dir):
        if mzml_filename in files:
            print(f"Found {mzml_filename} in {root}")
            fullpath = path.join(root, mzml_filename)
            return fullpath
        # else:
        #     print(f"{mzml_filename} not found in {base_dir} or its subdirectories")
            # raise Exception(f"{mzml_filename} not found in {base_dir} or its subdirectories")

def main():
    """
    The main function of the script which drives the entire program flow.
    """
    # Inputs and definitions
    # csv_file = 'combined_sequences.csv'  # CSV file containing the filenames for search
    csv_file = os.getenv('COMBINED_SEQUENCE_DIR') + '/combined_sequences_modified.csv'  # Path to the CSV file with .raw filenames
    # mzml_dir = '../ALL_MZML/'  # Directory where to find the .mzML files
    mzml_dir = os.getenv('MZML_DIR')  # Directory containing the .mzML files
    # output_csv = 'pcpfm_sequence.csv'  # Output CSV file with matched filename and mzML paths
    output_csv = os.getenv('COMBINED_SEQUENCE_DIR') + '/pcpfm_sequence.csv'  # Output CSV file stored in the same directory as the input CSV

    # Load data from CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Find the matching .mzML for each .raw-filename in the DataFrame
    df['mzml_path'] = [find_mzml_file(name, mzml_dir) for name in df['File Name']]

    # Separate rows with missing mzML paths
    missing_mzml = df[df['mzml_path'].isnull()]

    # Remove rows with missing mzML paths from the original DataFrame
    df = df.dropna(subset=['mzml_path'])

    # Write DataFrame with added column to a new CSV file
    df.to_csv(output_csv, index=False)

    # Write Dataframe with missing mzML paths to a separate CSV file
    if not missing_mzml.empty:
        missing_csv = os.getenv('COMBINED_SEQUENCE_DIR') + '/missing_mzml.csv'
        missing_mzml.to_csv(missing_csv, index=False)
        print(f"Missing mzML files saved to {missing_csv}")
    else:
        print("No missing mzML files found.")

# This call statement ensures the main function only runs if the script is executed directly (not imported as module)
if __name__ == '__main__':
    main()