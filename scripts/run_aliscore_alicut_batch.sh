#!/bin/bash

# run_aliscore_alicut_batch.sh
# Batch processing script for Aliscore + ALICUT alignment trimming
# Processes all alignments in a directory through both tools sequentially or in parallel
#
# Usage:
#   bash run_aliscore_alicut_batch.sh [alignment_dir] [options]
#
# This script:
#   1. Runs Aliscore on all alignments to identify RSS
#   2. Runs ALICUT on each Aliscore output to remove RSS
#   3. Collects trimmed alignments in output directory
#
# Requirements:
#   - run_aliscore.sh and run_alicut.sh in same directory or PATH
#   - Aliscore.02.2.pl and ALICUT_V2.31.pl available
#   - GNU parallel (optional, for parallel processing)

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to display usage
usage() {
    cat <<EOF
Usage: $0 [alignment_dir] [options]

Batch process multiple alignments through Aliscore and ALICUT.

Arguments:
  alignment_dir   Directory containing aligned FASTA files (*.fas)

Options:
  -o DIR         Output directory for trimmed alignments (default: aliscore_alicut_trimmed)
  -j INT         Number of parallel jobs (default: 1, serial processing)
  -w INT         Aliscore window size (default: 4)
  -r INT         Aliscore random pairs (default: 4*N)
  -N             Aliscore: treat gaps as ambiguous (recommended for AA)
  --remain-stems ALICUT: remain RNA stem positions
  --remove-codon ALICUT: remove entire codons (for back-translation)
  --remove-3rd   ALICUT: remove only 3rd codon positions
  -h             Display this help message

Examples:
  # Basic usage for amino acid alignments
  bash run_aliscore_alicut_batch.sh aligned_aa/ -N

  # Parallel processing with 20 cores
  bash run_aliscore_alicut_batch.sh aligned_aa/ -N -j 20

  # Custom window size
  bash run_aliscore_alicut_batch.sh aligned_aa/ -w 6 -N

  # With RNA structure preservation
  bash run_aliscore_alicut_batch.sh aligned_rrna/ --remain-stems

Output:
  - aliscore_output/aliscore_[locus]/  : Individual Aliscore results per locus
  - aliscore_alicut_trimmed/           : Final trimmed alignments
  - trimming_summary.txt               : Statistics for all loci

EOF
    exit 0
}

# Default parameters
ALIGNMENT_DIR=""
OUTPUT_DIR="aliscore_alicut_trimmed"
ALISCORE_OPTS=""
ALICUT_OPTS="-s"  # Silent mode by default
JOBS=1

if [ $# -eq 0 ]; then
    usage
fi

ALIGNMENT_DIR="$1"
shift

# Validate alignment directory
if [ ! -d "${ALIGNMENT_DIR}" ]; then
    echo "ERROR: Alignment directory not found: ${ALIGNMENT_DIR}"
    exit 1
fi

# Parse options
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -j|--jobs)
            JOBS="$2"
            shift 2
            ;;
        -w)
            ALISCORE_OPTS="${ALISCORE_OPTS} -w $2"
            shift 2
            ;;
        -r)
            ALISCORE_OPTS="${ALISCORE_OPTS} -r $2"
            shift 2
            ;;
        -N)
            ALISCORE_OPTS="${ALISCORE_OPTS} -N"
            shift
            ;;
        --remain-stems)
            ALICUT_OPTS="${ALICUT_OPTS} -r"
            shift
            ;;
        --remove-codon)
            ALICUT_OPTS="${ALICUT_OPTS} -c"
            shift
            ;;
        --remove-3rd)
            ALICUT_OPTS="${ALICUT_OPTS} -3"
            shift
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

# Check for wrapper scripts
RUN_ALISCORE="${SCRIPT_DIR}/run_aliscore.sh"
RUN_ALICUT="${SCRIPT_DIR}/run_alicut.sh"

if [ ! -f "${RUN_ALISCORE}" ]; then
    echo "ERROR: run_aliscore.sh not found: ${RUN_ALISCORE}"
    exit 1
fi

if [ ! -f "${RUN_ALICUT}" ]; then
    echo "ERROR: run_alicut.sh not found: ${RUN_ALICUT}"
    exit 1
fi

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Find all FASTA files
mapfile -t ALIGNMENTS < <(find "${ALIGNMENT_DIR}" -maxdepth 1 \( -name "*.fas" -o -name "*.fasta" \))

if [ ${#ALIGNMENTS[@]} -eq 0 ]; then
    echo "ERROR: No FASTA files found in ${ALIGNMENT_DIR}"
    exit 1
fi

echo "Found ${#ALIGNMENTS[@]} alignments to process"
echo "Aliscore options: ${ALISCORE_OPTS}"
echo "ALICUT options: ${ALICUT_OPTS}"
echo "Parallel jobs: ${JOBS}"
echo ""

# Initialize summary file
SUMMARY_FILE="${OUTPUT_DIR}/trimming_summary.txt"
echo -e "Locus\tOriginal_Length\tTrimmed_Length\tRemoved_Positions\tPercent_Removed\tRSS_Count" > "${SUMMARY_FILE}"

# Function to process a single alignment
process_alignment() {
    local ALIGNMENT="$1"
    local ALISCORE_OPTS="$2"
    local ALICUT_OPTS="$3"
    local OUTPUT_DIR="$4"
    local RUN_ALISCORE="$5"
    local RUN_ALICUT="$6"
    local SUMMARY_FILE="$7"

    local LOCUS=$(basename "${ALIGNMENT}" .fas)
    LOCUS=$(basename "${LOCUS}" .fasta)

    # Step 1: Run Aliscore
    if ! bash "${RUN_ALISCORE}" "${ALIGNMENT}" ${ALISCORE_OPTS} > /dev/null 2>&1; then
        echo "ERROR: Aliscore failed for ${LOCUS}" >&2
        return 1
    fi

    # Step 2: Run ALICUT
    local ALISCORE_DIR="aliscore_output/aliscore_${LOCUS}"

    if [ ! -d "${ALISCORE_DIR}" ]; then
        echo "ERROR: Aliscore output directory not found: ${ALISCORE_DIR}" >&2
        return 1
    fi

    if ! bash "${RUN_ALICUT}" "${ALISCORE_DIR}" ${ALICUT_OPTS} > /dev/null 2>&1; then
        echo "ERROR: ALICUT failed for ${LOCUS}" >&2
        return 1
    fi

    # Copy trimmed alignment to output directory
    local TRIMMED_FILE=$(find "${ALISCORE_DIR}" -name "ALICUT_*.fas" -o -name "ALICUT_*.fasta" | head -n 1)

    if [ -z "${TRIMMED_FILE}" ] || [ ! -f "${TRIMMED_FILE}" ]; then
        echo "WARNING: Trimmed file not found for ${LOCUS}" >&2
        return 1
    fi

    cp "${TRIMMED_FILE}" "${OUTPUT_DIR}/${LOCUS}_trimmed.fas"

    # Calculate statistics - FIX: properly handle multi-line FASTA
    # Get the first sequence from the alignment (concatenate all lines for first sequence)
    local ORIGINAL_LENGTH=$(awk '/^>/ {if (seq) exit; next} {seq = seq $0} END {print length(seq)}' "${ALISCORE_DIR}/$(basename ${ALIGNMENT})")
    local TRIMMED_LENGTH=$(awk '/^>/ {if (seq) exit; next} {seq = seq $0} END {print length(seq)}' "${TRIMMED_FILE}")

    local REMOVED_LENGTH=$((ORIGINAL_LENGTH - TRIMMED_LENGTH))
    local PERCENT_REMOVED=$(awk "BEGIN {if (${ORIGINAL_LENGTH} > 0) printf \"%.2f\", (${REMOVED_LENGTH}/${ORIGINAL_LENGTH})*100; else print \"0.00\"}")

    # Count RSS positions
    local LIST_FILE=$(find "${ALISCORE_DIR}" -name "*_List_*.txt" | head -n 1)
    local RSS_COUNT=$(wc -w < "${LIST_FILE}" 2>/dev/null || echo "0")

    # Append to summary (with locking for parallel writes)
    (
        flock 200
        echo -e "${LOCUS}\t${ORIGINAL_LENGTH}\t${TRIMMED_LENGTH}\t${REMOVED_LENGTH}\t${PERCENT_REMOVED}\t${RSS_COUNT}"
    ) 200>>"${SUMMARY_FILE}.lock" >> "${SUMMARY_FILE}"

    echo "Completed: ${LOCUS} (${ORIGINAL_LENGTH} -> ${TRIMMED_LENGTH} bp, ${PERCENT_REMOVED}% removed)"
    return 0
}

# Export function and variables for parallel execution
export -f process_alignment
export ALISCORE_OPTS ALICUT_OPTS OUTPUT_DIR RUN_ALISCORE RUN_ALICUT SUMMARY_FILE

# Process alignments
if [ ${JOBS} -eq 1 ]; then
    # Serial processing
    SUCCESS_COUNT=0
    FAIL_COUNT=0

    for ALIGNMENT in "${ALIGNMENTS[@]}"; do
        LOCUS=$(basename "${ALIGNMENT}" .fas)
        LOCUS=$(basename "${LOCUS}" .fasta)

        echo "=========================================="
        echo "Processing: ${LOCUS}"
        echo "=========================================="

        if process_alignment "${ALIGNMENT}" "${ALISCORE_OPTS}" "${ALICUT_OPTS}" "${OUTPUT_DIR}" "${RUN_ALISCORE}" "${RUN_ALICUT}" "${SUMMARY_FILE}"; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
        echo ""
    done
else
    # Parallel processing
    echo "Processing alignments in parallel with ${JOBS} jobs..."
    echo ""

    # Check for GNU parallel
    if command -v parallel &> /dev/null; then
        printf "%s\n" "${ALIGNMENTS[@]}" | parallel -j "${JOBS}" --bar process_alignment {} "${ALISCORE_OPTS}" "${ALICUT_OPTS}" "${OUTPUT_DIR}" "${RUN_ALISCORE}" "${RUN_ALICUT}" "${SUMMARY_FILE}"
    else
        # Fallback to xargs if parallel is not available
        echo "GNU parallel not found, using xargs instead (progress reporting limited)"
        printf "%s\n" "${ALIGNMENTS[@]}" | xargs -P "${JOBS}" -I {} bash -c 'process_alignment "$@"' _ {} "${ALISCORE_OPTS}" "${ALICUT_OPTS}" "${OUTPUT_DIR}" "${RUN_ALISCORE}" "${RUN_ALICUT}" "${SUMMARY_FILE}"
    fi

    # Count results
    SUCCESS_COUNT=$(($(wc -l < "${SUMMARY_FILE}") - 1))  # -1 for header
    FAIL_COUNT=$((${#ALIGNMENTS[@]} - SUCCESS_COUNT))
fi

# Cleanup lock file
rm -f "${SUMMARY_FILE}.lock"

# Final report
echo ""
echo "=========================================="
echo "BATCH PROCESSING COMPLETE"
echo "=========================================="
echo ""
echo "Successfully processed: ${SUCCESS_COUNT}/${#ALIGNMENTS[@]} alignments"
echo "Failed: ${FAIL_COUNT}/${#ALIGNMENTS[@]} alignments"
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
