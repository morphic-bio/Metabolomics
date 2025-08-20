"""
Main script including metadata to combined sequence data based on JSON input.

# ENVIRONMENT VARIABLES:
# ${COMBINED_SEQUENCE_DIR} - Directory containing combined_sequences.csv from step1.
# ${SEARCH_DICT} - JSON file defining how to assign or adjust sample metadata (like sample type) based on substrings.

Run via `python3.11 step2_add_pcpfm_metadata.py`
"""

import os
import pandas as pd
import json

def add_metadata(df, search_list):
    """Updates 'Sample Type' column based on presence of substrings in other columns.

    Parameters:
        df (DataFrame): DataFrame to update.
        search_dict (dict): Dictionary containing fields to look for and their substrings.

    Returns:
        updated DataFrame with modified "Sample Type" field.
    """
    for substring in search_list:
        if len(substring) == 2:
            field, match_ss = substring
            new_type = match_ss
            pass
        elif len(substring) == 3:
            field, match_ss, new_type = substring
        df.loc[df[field].str.contains(match_ss), "Sample Type"] = f"{new_type}"
    return df

def main():
   """Updates 'Sample Type' column of combined CSV data based on provided substrings."""
   # input_file = "combined_sequences.csv"
   input_file = os.getenv("COMBINED_SEQUENCE_DIR") + "/combined_sequences.csv"
   combined = pd.read_csv(input_file)

   # json_file_path = "./config/search_dict.json"
   json_file_path = os.getenv('SEARCH_DICT')
   # Load dictionary from JSON file
   with open(json_file_path, 'r') as f:
       search_dict = json.load(f)

   combined = add_metadata(combined, search_dict)
   updated_file = os.getenv("COMBINED_SEQUENCE_DIR") + "/combined_sequences_modified.csv"  # Modify this if you need to write to a different file
   combined.to_csv(updated_file, index=False)

if __name__ == '__main__':
   main()