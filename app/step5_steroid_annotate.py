"""
This script annotates steroid derivatives in feature tables.
It calculates the masses of steroid derivatives based on a base mass and a group mass,
and then annotates features in provided TSV files based on these calculated masses.
It outputs annotated feature tables in TSV format.

ENVIRONMENT VARIABLES:
# OUTPUT_DIR: Directory where the annotated feature tables will be saved.
# STEROID_CSV: Path to the steroids CSV file

"""

import pandas as pd
import argparse
import os
from mass2chem.formula import calculate_formula_mass

def calculate_derivative_masses(steroid_csv, group_mass, group_name):
    steroids_df = pd.read_csv(steroid_csv)
    derivatives = []

    for _, row in steroids_df.iterrows():
        formula = row['formula']
        base_mass = calculate_formula_mass(formula)
        for groups_added in range(0, 4):  # Updated to include 0 groups
            total_mass = base_mass + groups_added * group_mass
            derivative = {
                'steroid': row['steroid'],
                'groups_added': groups_added,
                'group_name': group_name,
                'derivative_mass': total_mass
            }
            derivatives.append(derivative)

    return pd.DataFrame(derivatives)


def annotate_features(feature_tsv, derivatives_df, ppm_tolerance=10):
    features_df = pd.read_csv(feature_tsv, sep='\t')

    mzml_cols_standards = [x for x in features_df.columns if "Standard" in x]
    print(mzml_cols_standards)
    annotations = []
    annotation_df = []
    for _, feature in features_df.iterrows():
        mz = feature['mz']
        matches = []

        for _, derivative in derivatives_df.iterrows():
            expected_mass = derivative['derivative_mass'] + 1.00727647 
            tolerance = expected_mass * ppm_tolerance / 1e6
            
            if abs(mz - expected_mass) <= tolerance:
                if all(feature[file] > 0 for file in mzml_cols_standards):
                    match = f"{derivative['steroid']}+{derivative['groups_added']}{derivative['group_name']}"
                    matches.append(match)
                    print(match)
        annotation_df.append({'mz': feature['mz'], 'id_number': feature['id_number'], 'annotation': ';'.join(matches)})
    return pd.DataFrame(annotation_df)


if __name__ == '__main__':
    # Parse file/folder paths from environment variables
    steroid_csv = os.getenv('STEROID_CSV')
    output_dir = os.getenv('OUTPUT_DIR')

    # Calculate derivative masses for DnCl and DnHz
    derivatives_df_dncl = calculate_derivative_masses(steroid_csv, 233.05105, "DnCl")
    derivatives_df_dnhz = calculate_derivative_masses(steroid_csv, 247.07793, "DnHz")

    feature_tables = []

    # Find feature_tables.tsv files in the specified directories, save their paths
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file == "feature_table.tsv":
                feature_tables.append(os.path.join(root, file))

    # Annotate features in the provided feature tables (cell pellet and supernatant)
    # Outputs stored in the same directory as the input feature tables, called "annotation_table.tsv"
    for feature_table in feature_tables:
        feature_table_dirname = os.path.dirname(feature_table)
        if "DnCl_Pellet" in feature_table:
            annotated_df = annotate_features(feature_table, derivatives_df_dncl)
            annotated_df.to_csv(os.path.join(feature_table_dirname, "annotation_table.tsv"), sep='\t', index=False)
        elif "DnHz_Pellet" in feature_table:
            annotated_df = annotate_features(feature_table, derivatives_df_dnhz)
            annotated_df.to_csv(os.path.join(feature_table_dirname, "annotation_table.tsv"), sep='\t', index=False)
        elif "DnCl_Supernatant" in feature_table:
            annotated_df = annotate_features(feature_table, derivatives_df_dncl)
            annotated_df.to_csv(os.path.join(feature_table_dirname, "annotation_table.tsv"), sep='\t', index=False)
        elif "DnHz_Supernatant" in feature_table:
            annotated_df = annotate_features(feature_table, derivatives_df_dnhz)
            annotated_df.to_csv(os.path.join(feature_table_dirname, "annotation_table.tsv"), sep='\t', index=False)
        else:
            print(f"Skipping {feature_table} as it does not match expected naming conventions for DnCl or DnHz.")
