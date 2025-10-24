# NCBI Genome Assembly Comparisons

This analysis downloads and characterizes genome assembly metadata for Arecaceae (palms) and Curculionidae (weevils) from NCBI, enriches the data with taxonomic information from authoritative sources, and generates comparative statistics.

## Overview

This pipeline performs the following steps:

1. **Download NCBI metadata** - Retrieves all genome assemblies for Arecaceae and Curculionidae from NCBI
2. **Enrich with taxonomy** - Adds higher taxonomy (subfamily to subtribe) from:
   - iNaturalist for Arecaceae
   - Manual curation for Curculionidae (based on Handbook of Zoology classification)
3. **Generate statistics** - Calculates high-quality genome statistics and produces a natural language summary

## Requirements

### Software
- Python 3.7+
- Internet connection (for API access)

### Python Packages
```bash
pip install biopython requests
```

## Quick Start

Simply run the master script:

```bash
bash run_all.sh
```

This will execute all steps in sequence and generate all output files.

## Manual Execution

You can also run each step individually:

```bash
# Step 1: Download NCBI metadata
python3 01_download_ncbi_metadata.py

# Step 2: Enrich Arecaceae with iNaturalist taxonomy
python3 02_enrich_arecaceae_taxonomy.py

# Step 3: Manually curate Curculionidae taxonomy
# (Edit curculionidae_assemblies_enriched.csv with subfamily and tribe classifications
# based on Handbook of Zoology: Beutel et al. (2014) Coleoptera, Beetles,
# Volume 3, Morphology and Systematics (Phytophaga).
# Subfamily added for all Curculionidae; tribe added specifically for Curculioninae.)

# Step 4: Generate statistics and summary
python3 04_generate_statistics.py
```

## Output Files

### Raw NCBI Data
- `arecaceae_assemblies.csv` - All Arecaceae genome assemblies from NCBI
- `curculionidae_assemblies.csv` - All Curculionidae genome assemblies from NCBI

### Enriched Data
- `arecaceae_assemblies_enriched.csv` - Arecaceae assemblies with WFO taxonomy
- `curculionidae_assemblies_enriched.csv` - Curculionidae assemblies with COL taxonomy

### Higher Taxa Lists
- `arecaceae_higher_taxa.txt` - All subfamilies, tribes, and subtribes in palm genomes
- `curculionidae_higher_taxa.txt` - All subfamilies and genera in weevil genomes

### Summary Statistics
- `genome_statistics.json` - Structured statistics in JSON format
- `genome_statistics_summary.txt` - Natural language summary paragraph

## High-Quality Genome Criteria

Genomes are classified as "high-quality" if they meet either criterion:

1. **Assembly level**: Chromosome-level or complete genome
2. **Scaffold N50**: Greater than 10 Mb

## Taxonomy Sources

### Arecaceae (iNaturalist)
- **API**: https://api.inaturalist.org/v1
- **Method**: REST API taxon search
- **Ranks retrieved**: Family, subfamily, tribe, subtribe, genus
- **Special focus**: Subtribe representation within tribe Cocoseae
- **Note**: iNaturalist provides community-curated taxonomy with good coverage of palm higher taxonomy

### Curculionidae (Manual Curation)
- **Source**: Handbook of Zoology - Beutel, R. G., & Leschen, R. A. B. (2014). Coleoptera, Beetles, Volume 3: Morphology and Systematics (Phytophaga). De Gruyter. https://doi.org/10.1515/9783110274462
- **Method**: Manual assignment of subfamily and tribe classifications based on authoritative literature
- **Subfamilies recognized**: 12 subfamilies in Curculionidae
- **Tribes recognized**: 34 tribes in Curculioninae (plus genera of uncertain placement, Incertae Sedis)
- **Ranks used**: Family, subfamily, tribe (for Curculioninae), genus
- **Note**: Manual curation ensures taxonomic accuracy and consistency with the most authoritative systematic treatments. Tribal taxonomy was added for Curculioninae from the same source. For other subfamilies, tribal taxonomy is often unstable/unavailable, so analysis focuses on subfamily and genus.

## Diversity Estimates

The script uses the following diversity estimates for comparison:

### Arecaceae
- **Species**: ~2,600
- **Genera**: 181
- **Subfamilies**: 5
- **Source**: Published palm phylogenies and taxonomies

### Curculionidae
- **Species**: ~51,000
- **Genera**: ~4,600
- **Subfamilies**: 12 subfamilies (Handbook of Zoology classification)
- **Tribes in Curculioninae**: 34 tribes (Handbook of Zoology classification)
- **Source**: General estimates (one of the largest animal families); subfamily and tribe counts from Beutel et al. (2014)

These estimates can be updated in `04_generate_statistics.py` in the `DIVERSITY_ESTIMATES` dictionary.

## Customization

### Using Different Email for NCBI
Edit `01_download_ncbi_metadata.py` and change:
```python
Entrez.email = "your.email@example.com"
```

### Updating Diversity Estimates
Edit `04_generate_statistics.py` and modify the `DIVERSITY_ESTIMATES` dictionary with more current values.

### Adding Other Taxa
The scripts can be adapted for other taxonomic groups by:
1. Changing the taxon names in `01_download_ncbi_metadata.py`
2. Selecting appropriate taxonomy APIs for enrichment
3. Updating diversity estimates

## Runtime

- **Step 1** (NCBI download): 2-5 minutes
- **Step 2** (iNaturalist enrichment): 5-15 minutes (depends on number of species)
- **Step 3** (Manual curation): Variable (depends on taxonomic expertise)
- **Step 4** (Statistics): < 1 minute

**Total**: ~10-25 minutes (plus manual curation time)

## API Rate Limiting

The scripts include delays (0.5 seconds) between API calls to be respectful to the public APIs. If you encounter rate limiting errors, you can increase these delays in the enrichment scripts.

## Troubleshooting

### Biopython Errors
If you get NCBI Entrez errors, ensure:
1. You have a valid email in `01_download_ncbi_metadata.py`
2. Your internet connection is working
3. NCBI servers are accessible

### Taxonomy Not Found
Some species may not be found in iNaturalist:
- Recent species descriptions may not be in databases yet
- Synonyms may be used in NCBI but not recognized by taxonomy APIs
- Manual curation may be needed for these cases (as done for Curculionidae)

### Empty Results
If no results are returned:
- Check that the CSV files from previous steps exist
- Verify the taxon names are correct
- Check API endpoint availability

## Citation

If you use this analysis, please cite:

- **NCBI**: https://www.ncbi.nlm.nih.gov/
- **iNaturalist**: https://www.inaturalist.org/
- **Handbook of Zoology**: Beutel, R. G., & Leschen, R. A. B. (2014). Coleoptera, Beetles, Volume 3: Morphology and Systematics (Phytophaga). De Gruyter. https://doi.org/10.1515/9783110274462

## Authors

- Bruno de Medeiros (Field Museum)

## License

This analysis is part of the Oenocarpus/Anchylorhynchus genome paper project.
See the main repository LICENSE for details.
