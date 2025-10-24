#!/bin/bash
# Master script to run the complete NCBI genome comparison analysis
# This script downloads genome metadata, enriches with taxonomy, and generates statistics

set -e  # Exit on error

echo "======================================================================"
echo "NCBI Genome Assembly Comparison Analysis"
echo "For Arecaceae and Curculionidae"
echo "======================================================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

# Check for required Python packages
echo "Checking for required Python packages..."
python3 -c "import Bio" 2>/dev/null || { echo "Error: Biopython not installed. Run: pip install biopython"; exit 1; }
python3 -c "import requests" 2>/dev/null || { echo "Error: requests not installed. Run: pip install requests"; exit 1; }

echo "All dependencies found!"
echo ""

# Step 1: Download NCBI metadata
echo "======================================================================"
echo "STEP 1: Downloading NCBI genome metadata"
echo "======================================================================"
python3 01_download_ncbi_metadata.py
echo ""

# Check if files were created
if [ ! -f "arecaceae_assemblies.csv" ] || [ ! -f "curculionidae_assemblies.csv" ]; then
    echo "Error: NCBI download failed"
    exit 1
fi

# Step 2: Enrich Arecaceae with WFO taxonomy
echo "======================================================================"
echo "STEP 2: Enriching Arecaceae data with WFO Plant List taxonomy"
echo "======================================================================"
python3 02_enrich_arecaceae_taxonomy.py
echo ""

# Step 3: Enrich Curculionidae with COL taxonomy
echo "======================================================================"
echo "STEP 3: Enriching Curculionidae data with Catalogue of Life taxonomy"
echo "======================================================================"
python3 03_enrich_curculionidae_taxonomy.py
echo ""

# Step 4: Generate statistics and summary
echo "======================================================================"
echo "STEP 4: Generating statistics and summary"
echo "======================================================================"
python3 04_generate_statistics.py
echo ""

echo "======================================================================"
echo "ANALYSIS COMPLETE!"
echo "======================================================================"
echo ""
echo "Output files:"
echo "  - arecaceae_assemblies.csv           : Raw NCBI data for palms"
echo "  - arecaceae_assemblies_enriched.csv  : Enriched with WFO taxonomy"
echo "  - arecaceae_higher_taxa.txt          : List of higher taxa in palms"
echo "  - curculionidae_assemblies.csv       : Raw NCBI data for weevils"
echo "  - curculionidae_assemblies_enriched.csv : Enriched with COL taxonomy"
echo "  - curculionidae_higher_taxa.txt      : List of higher taxa in weevils"
echo "  - genome_statistics.json             : Statistics in JSON format"
echo "  - genome_statistics_summary.txt      : Natural language summary"
echo ""
echo "To view the summary:"
echo "  cat genome_statistics_summary.txt"
echo ""
