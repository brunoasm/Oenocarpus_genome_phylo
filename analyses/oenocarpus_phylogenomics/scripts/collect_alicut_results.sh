#!/bin/bash

# collect_alicut_results.sh
# Collect existing ALICUT results and regenerate summary with fixed length calculations
# This script processes already-completed Aliscore/ALICUT outputs

set -euo pipefail

OUTPUT_DIR="${1:-single_copy_orthologs/trimmed_aa}"
ALISCORE_OUTPUT_DIR="${2:-aliscore_output}"

echo "Collecting ALICUT results..."
echo "Output directory: ${OUTPUT_DIR}"
echo "Aliscore output directory: ${ALISCORE_OUTPUT_DIR}"
echo ""

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Initialize summary file
SUMMARY_FILE="${OUTPUT_DIR}/trimming_summary.txt"
echo -e "Locus\tOriginal_Length\tTrimmed_Length\tRemoved_Positions\tPercent_Removed\tRSS_Count" > "${SUMMARY_FILE}"

# Find all ALICUT output files
mapfile -t ALICUT_FILES < <(find "${ALISCORE_OUTPUT_DIR}" -name "ALICUT_*.fas" | sort)

echo "Found ${#ALICUT_FILES[@]} ALICUT output files"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for TRIMMED_FILE in "${ALICUT_FILES[@]}"; do
    # Extract locus name
    ALISCORE_DIR=$(dirname "${TRIMMED_FILE}")
    DIR_NAME=$(basename "${ALISCORE_DIR}")
    LOCUS=${DIR_NAME#aliscore_}

    # Find original alignment file in the aliscore directory
    ORIGINAL_FILE=$(find "${ALISCORE_DIR}" -maxdepth 1 -name "*.fas" ! -name "ALICUT_*" | head -n 1)

    if [ -z "${ORIGINAL_FILE}" ] || [ ! -f "${ORIGINAL_FILE}" ]; then
        echo "WARNING: Original file not found for ${LOCUS}" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Copy trimmed alignment to output directory
    cp "${TRIMMED_FILE}" "${OUTPUT_DIR}/${LOCUS}_trimmed.fas"

    # Calculate statistics with fixed multi-line FASTA handling
    ORIGINAL_LENGTH=$(awk '/^>/ {if (seq) exit; next} {seq = seq $0} END {print length(seq)}' "${ORIGINAL_FILE}")
    TRIMMED_LENGTH=$(awk '/^>/ {if (seq) exit; next} {seq = seq $0} END {print length(seq)}' "${TRIMMED_FILE}")

    REMOVED_LENGTH=$((ORIGINAL_LENGTH - TRIMMED_LENGTH))
    PERCENT_REMOVED=$(awk "BEGIN {if (${ORIGINAL_LENGTH} > 0) printf \"%.2f\", (${REMOVED_LENGTH}/${ORIGINAL_LENGTH})*100; else print \"0.00\"}")

    # Count RSS positions
    LIST_FILE=$(find "${ALISCORE_DIR}" -name "*_List_*.txt" | head -n 1)
    RSS_COUNT=$(wc -w < "${LIST_FILE}" 2>/dev/null || echo "0")

    # Append to summary
    echo -e "${LOCUS}\t${ORIGINAL_LENGTH}\t${TRIMMED_LENGTH}\t${REMOVED_LENGTH}\t${PERCENT_REMOVED}\t${RSS_COUNT}" >> "${SUMMARY_FILE}"

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

    if [ $((SUCCESS_COUNT % 100)) -eq 0 ]; then
        echo "Processed ${SUCCESS_COUNT}/${#ALICUT_FILES[@]}..."
    fi
done

echo ""
echo "=========================================="
echo "COLLECTION COMPLETE"
echo "=========================================="
echo ""
echo "Successfully processed: ${SUCCESS_COUNT}/${#ALICUT_FILES[@]} alignments"
echo "Failed: ${FAIL_COUNT}/${#ALICUT_FILES[@]} alignments"
echo ""
echo "Output directory: ${OUTPUT_DIR}"
echo "Trimmed alignments: ${OUTPUT_DIR}/*_trimmed.fas"
echo "Summary statistics: ${SUMMARY_FILE}"
echo ""

# Display summary statistics
if [ ${SUCCESS_COUNT} -gt 0 ]; then
    echo "Overall trimming statistics:"
    awk 'NR>1 {
        total_orig += $2;
        total_trim += $3;
        total_removed += $4;
        count++
    }
    END {
        if (count > 0) {
            avg_removed = (total_removed / total_orig) * 100;
            printf "  Total positions before: %d\n", total_orig;
            printf "  Total positions after:  %d\n", total_trim;
            printf "  Total removed:          %d (%.2f%%)\n", total_removed, avg_removed;
            printf "  Average per locus:      %.2f%% removed\n", avg_removed;
        }
    }' "${SUMMARY_FILE}"
fi

echo ""
echo "Done!"
