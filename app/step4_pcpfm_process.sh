#!/bin/bash
# This script processes metabolomics data using pcpfm.

# REQUIRED EXTERNAL ENVIRONMENT VARIABLES:
# $COMBINED_SEQUENCE_DIR: Directory containing the combined sequence & pcpfm sequence CSV files (pcpfm_sequence.csv only required).
# $OUTPUT_PREFIX: Prefix for the output files.
# $PCPFM_OUTPUT_DIR: Directory where the output files will be saved.
# $FILTERS_DIR: Directory containing the filter JSON files for pcpfm processing.

CSV="${COMBINED_SEQUENCE_DIR}/pcpfm_sequence.csv"
OUTPUT="${OUTPUT_PREFIX}_"
BASE="${PCPFM_OUTPUT_DIR}/"
FILTERS="${FILTERS_DIR}/"

# OPTIONAL EXTERNAL ENVIRONMENT VARIABLES:
# $MS2_HILICNEGSUPERNATANT_DIR: Directory containing MS2 files for HILIC negative supernatant.
# $MS2_HILICPOSSUPERNATANT_DIR: Directory containing MS2 files for HILIC positive supernatant.
# $MS2_RPNegSUPERNATANT_DIR: Directory containing MS2 files for RP negative supernatant.
# $MS2_RPPosSUPERNATANT_DIR: Directory containing MS2 files for RP positive supernatant.

# Check if the required arguments are provided
if [ -z "$CSV" ] || [ -z "$OUTPUT" ]; then
    echo "Usage: $0 <INPUT_CSV> <OUTPUT_PREFIX>" >&2
    exit 1
fi

run() {
    MODE=$1
    FILTER=$2
    EXPERIMENT="$BASE$OUTPUT$MODE"

    printf "Processing mode: %s\n" "$MODE"
    printf "Starting pcpmf assemble with filter (create output directory): %s\n" "$FILTER"
    python3.11 -m pcpfm assemble -o $BASE -j $OUTPUT$MODE -s $CSV --filter=$FILTER --path_field='mzml_path' --name_field='File Name'

    printf "Assembling complete. Output saved to: %s\n" "$EXPERIMENT"
    printf "Running pcpfm asari on experiment (process mzML to feature tables): %s\n" "$EXPERIMENT"
    if [[ $MODE =~ (DnHz|dnhz|DnCl|dncl) ]]; then
        #echo "skip"
        # python3.11 -m pcpfm assemble -o $BASE -j $OUTPUT$MODE -s $CSV --filter=$FILTER --path_field mzml_path --name_field "File Name"
        python3.11 -m pcpfm asari -i $EXPERIMENT --extra_asari "--min_peak_height 500000 --min_intensity_threshold 500000"
        python3.11 -m pcpfm build_empCpds -i $EXPERIMENT -tm preferred -em preferred --add_singletons=True
        python3.11 -m pcpfm generate_output -i $EXPERIMENT -em preferred -tm preferred 
    else
        # echo "skip"
        # python3.11 -m pcpfm assemble -o $BASE -j $OUTPUT$MODE -s $CSV --filter=$FILTER --path_field mzml_path --name_field "File Name"
        python3.11 -m pcpfm asari -i $EXPERIMENT
        python3.11 -m pcpfm build_empCpds -i $EXPERIMENT -tm preferred -em preferred --add_singletons=True

        # If  all MS2 directories are set (combination of {hilicneg, hilicpos, rpneg, rppos} and {supernatant, cellpellet}), use them to map MS2 data.
        if [[ -n "$MS2_HILICNEGSUPERNATANT_DIR" && -n "$MS2_HILICPOSSUPERNATANT_DIR" && -n "$MS2_RPNegSUPERNATANT_DIR" && -n "$MS2_RPPosSUPERNATANT_DIR"  && -n "$MS2_HILICNEGCELLPELLET_DIR" && -n "$MS2_HILICPOSCELLPELLET_DIR" && -n "$MS2_RPNegCELLPELLET_DIR" && -n "$MS2_RPPosCELLPELLET_DIR" ]]; then
            printf "Mapping MS2 data for experiment: %s\n" "$EXPERIMENT"
            if [[ $MODE =~ .*hilicneg.* && $MODE =~ .*Supernatant.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_HILICNEGSUPERNATANT_DIR
            fi
            if [[ $MODE =~ .*hilicpos.* && $MODE =~ .*Supernatant.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_HILICPOSSUPERNATANT_DIR
            fi
            if [[ $MODE =~ .*rpneg.* && $MODE =~ .*Supernatant.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_RPNegSUPERNATANT_DIR
            fi
            if [[ $MODE =~ .*rppos.* && $MODE =~ .*Supernatant.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_RPPosSUPERNATANT_DIR
            fi

            if [[ $MODE =~ .*hilicneg.* && $MODE =~ .*Cellpellet.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_HILICNEGCELLPELLET_DIR
            fi
            if [[ $MODE =~ .*hilicpos.* && $MODE =~ .*Cellpellet.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_HILICPOSCELLPELLET_DIR
            fi
            if [[ $MODE =~ .*rpneg.* && $MODE =~ .*Cellpellet.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_RPNegCELLPELLET_DIR
            fi
            if [[ $MODE =~ .*rppos.* && $MODE =~ .*Cellpellet.* ]]; then
               python3.11 -m pcpfm map_ms2 -i $EXPERIMENT -em preferred -nm preferred_map -tm preferred_w_MS2 --ms2_dir $MS2_RPPosCELLPELLET_DIR
            fi
         else
            printf "No MS2 directories set for mapping. Skipping MS2 mapping for experiment: %s\n" "$EXPERIMENT"
            printf "Four MS2 directories are required (hilicneg, hilicpos, rpneg, rppos)\n"
        fi

        # Annotate the feature table with level 4 (HMDB_LMSD) and level 2 (MoNA) annotations.
        python3.11 -m pcpfm l4_annotate -i $EXPERIMENT -em preferred_map -nm HMDB_LMSD_annotated_preferred
        python3.11 -m pcpfm l2_annotate -i $EXPERIMENT -em HMDB_LMSD_annotated_preferred -nm HMDB_LMSD_MoNA_annotated_preferred
        python3.11 -m pcpfm generate_output -i $EXPERIMENT -em HMDB_LMSD_MoNA_annotated_preferred -tm preferred 
    fi
}

for file in $FILTERS*.json; do
    MODE=$(basename "$file" .json)
    run "$MODE" "$file"
done