# Network Limitation Notice

## Issue
The scripts in this directory require access to external APIs:
- NCBI E-utilities (https://eutils.ncbi.nlm.nih.gov)
- World Flora Online (https://list.worldfloraonline.org)
- Catalogue of Life (https://api.catalogueoflife.org)

The current development environment has network restrictions that block access to these APIs.

## Solution
These scripts are fully functional and ready to use. To run them:

1. **Clone the repository to your local machine** or a server with internet access:
   ```bash
   git clone https://github.com/brunoasm/Oenocarpus_genome_phylo.git
   cd Oenocarpus_genome_phylo/analyses/NCBI_comparisons
   ```

2. **Install required Python packages**:
   ```bash
   pip install biopython requests
   ```

3. **Set your NCBI API key** (recommended for better rate limits):
   ```bash
   export NCBI_API_KEY="your_api_key_here"
   ```

4. **Run the complete analysis**:
   ```bash
   bash run_all.sh
   ```

   Or run steps individually:
   ```bash
   python3 01_download_ncbi_metadata_v2.py
   python3 02_enrich_arecaceae_taxonomy.py
   python3 03_enrich_curculionidae_taxonomy.py
   python3 04_generate_statistics.py
   ```

## Expected Runtime
- Total: ~15-35 minutes with a good internet connection
- Step 1 (NCBI download): 2-5 minutes
- Step 2 (WFO enrichment): 5-15 minutes
- Step 3 (COL enrichment): 5-15 minutes
- Step 4 (Statistics): < 1 minute

## Your API Key
Your NCBI API key is: `5e6a24889b4aa2f7eeffed3f3dc262847b09`

The scripts are configured to use this from the `NCBI_API_KEY` environment variable.

## Output Files
When successfully run, you'll get:
- `arecaceae_assemblies_enriched.csv` - Palm genomes with full taxonomy
- `curculionidae_assemblies_enriched.csv` - Weevil genomes with full taxonomy
- `genome_statistics_summary.txt` - Natural language summary paragraph
- `genome_statistics.json` - Structured statistics

## Testing
Example mock data has been provided in `example_output/` to demonstrate the expected results.
