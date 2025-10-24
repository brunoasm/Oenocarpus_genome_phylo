# Oenocarpus Genome Phylogenomics

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Automated phylogenomic analysis pipeline for palm genomes using BUSCO single-copy orthologs. This pipeline was developed to place the newly sequenced *Oenocarpus mapora* genome in a phylogenetic context with other palm species.

## Overview

This repository contains scripts and documentation for inferring phylogenies from genome assemblies using:
- **Ortholog identification:** compleasm (BUSCO methodology)
- **Multiple sequence alignment:** MAFFT L-INS-i
- **Alignment trimming:** Aliscore/ALICUT
- **Phylogenetic inference:** IQ-TREE (concatenated) + ASTRAL (coalescent)

### Dataset
- 13 genome assemblies (12 palms + 1 rice outgroup)
- BUSCO lineage: liliopsida_odb10 (monocots, 4,896 BUSCOs)
- Target genome: *Oenocarpus mapora* (newly sequenced)

## Quick Start

### Prerequisites
- Linux or macOS
- Conda/Miniconda
- 20+ CPU cores (recommended)
- 100+ GB RAM (recommended)
- ~60 GB disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/brunoasm/Oenocarpus_genome_phylo.git
cd Oenocarpus_genome_phylo

# Set up the conda environment and download tools
bash setup_phylo_env.sh

# Activate the environment
conda activate phylo
```

### Running the Pipeline

Execute the numbered scripts in order:

```bash
# 1. Download genomes from NCBI
bash 01_download_genomes.sh

# 2. Identify single-copy orthologs (may take hours)
bash 02_run_compleasm.sh

# 3. Generate quality control report
bash 03_generate_qc_report.sh

# 4. Extract orthologs
bash 04_extract_orthologs.sh

# 5. Align sequences (may take hours)
bash 05_run_mafft.sh

# 6. Trim alignments (may take hours)
bash 06_run_aliscore_alicut.sh

# 7. Concatenate alignments
bash 07_concatenate.sh

# 8a. Find best partitioning scheme (may take many hours)
bash 08a_iqtree_partition_search.sh

# 8b. Infer maximum likelihood tree (may take hours to days)
bash 08b_iqtree_concat_tree.sh

# Optional: Coalescent species tree
bash 08c_iqtree_gene_trees.sh
bash 08d_astral_species_tree.sh
```

## Pipeline Steps

| Step | Description | Runtime | Output |
|------|-------------|---------|--------|
| 0 | Setup environment | 5-15 min | conda env, tools |
| 1 | Download genomes | 10-30 min | `genomes/*.fasta` |
| 2 | Ortholog identification | 4-16 h | `*_compleasm/` dirs |
| 3 | Quality control | <1 min | `qc_report.csv` |
| 4 | Extract orthologs | 1-5 min | `single_copy_orthologs/unaligned_aa/*.fas` |
| 5 | Multiple alignment | 1-4 h | `single_copy_orthologs/aligned_aa/*.fas` |
| 6 | Trim alignments | 1-4 h | `single_copy_orthologs/trimmed_aa/*.fas` |
| 7 | Concatenate | 1-5 min | `FcC_smatrix.fas` |
| 8a | Partition search | 2-24 h | `partition_search.best_scheme.nex` |
| 8b | ML tree inference | 4-72 h | `concatenated_ML_tree.treefile` |
| 8c | Gene trees (optional) | 1-8 h | `all_gene_trees.tre` |
| 8d | ASTRAL tree (optional) | 1-10 min | `astral_species_tree.tre` |

**Total estimated time:** 2-7 days

## Output Files

### Primary Results
- `concatenated_ML_tree.treefile` - Maximum likelihood phylogeny (concatenated analysis)
- `astral_species_tree.tre` - Coalescent species tree (optional)
- `qc_report.csv` - Genome quality statistics

### Intermediate Files
- `FcC_smatrix.fas` - Concatenated supermatrix
- `partition_def.txt` - Partition definitions for IQ-TREE
- `all_gene_trees.tre` - Individual gene trees

See `METHODS_PARAGRAPH.md` for ready-to-use methods text with citations.

## Directory Structure

```
.
├── setup_phylo_env.sh          # Environment setup
├── 01_download_genomes.sh      # Download NCBI genomes
├── 02_run_compleasm.sh         # Ortholog identification
├── 03_generate_qc_report.sh    # Quality control
├── 04_extract_orthologs.sh     # Extract orthologs
├── 05_run_mafft.sh             # Multiple alignment
├── 06_run_aliscore_alicut.sh   # Alignment trimming
├── 07_concatenate.sh           # Concatenation
├── 08a_iqtree_partition_search.sh  # Partition search
├── 08b_iqtree_concat_tree.sh   # ML tree inference
├── 08c_iqtree_gene_trees.sh    # Gene trees (optional)
├── 08d_astral_species_tree.sh  # ASTRAL tree (optional)
└── sources/
    └── genomes_to_download.txt # NCBI accessions
```

## System Requirements

- **Minimum:** 8 cores, 32 GB RAM, 50 GB disk
- **Recommended:** 20 cores, 100 GB RAM, 100 GB disk
- **OS:** Linux (tested on Ubuntu 20.04+) or macOS

## Software Dependencies

All dependencies are automatically installed via `setup_phylo_env.sh`:
- compleasm
- MAFFT
- IQ-TREE
- GNU Parallel
- Aliscore/ALICUT (Perl scripts)
- FASconCAT-G (Perl script)
- ASTRAL (Java)
- Python 3.9+ (with BioPython)

## Customization

### Using Your Own Genomes
1. Add genome assemblies to `sources/` directory
2. Update `sources/genomes_to_download.txt` with NCBI accessions
3. Modify `genome_list.txt` to include your local genomes

### Adjusting Parameters
- **Parallel jobs:** Edit `-j` flags in scripts (reduce if limited RAM)
- **BUSCO lineage:** Change `liliopsida_odb10` to your target lineage
- **Alignment method:** Replace MAFFT with MUSCLE/PRANK in `05_run_mafft.sh`
- **Trimming:** Use trimAl or ClipKit instead of Aliscore/ALICUT

## Troubleshooting

### Memory Issues
- Reduce parallel jobs: Change `-j 20` to `-j 10` in scripts
- Add memory limit to IQ-TREE: Add `-mem 80G` flag

### Low Completeness Scores
- Check genome quality (fragmentation, contamination)
- Verify correct BUSCO lineage
- Consider excluding genomes with <85% completeness

### Process Monitoring
```bash
# Check running processes
ps aux | grep -E "compleasm|mafft|iqtree"

# Monitor IQ-TREE progress
tail -f concatenated_ML_tree.log
```

## Citation

If you use this pipeline, please cite:

- **compleasm:** Huang N, Li H (2023). compleasm: a faster and more accurate reimplementation of BUSCO. Bioinformatics 39:btad595
- **MAFFT:** Katoh K, Standley DM (2013). MAFFT multiple sequence alignment software version 7. Mol Biol Evol 30:772-780
- **Aliscore/ALICUT:** Kück P, Meusemann K, Dambach J, et al. (2010). Parametric and non-parametric masking of randomness in sequence alignments. Front Zool 7:10
- **IQ-TREE:** Minh BQ, Schmidt HA, Chernomor O, et al. (2020). IQ-TREE 2: New models and efficient methods for phylogenetic inference. Mol Biol Evol 37:1530-1534
- **ASTRAL:** Zhang C, Rabiee M, Sayyari E, Mirarab S (2018). ASTRAL-III: polynomial time species tree reconstruction from partially resolved gene trees. BMC Bioinformatics 19:153

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- Bruno de Medeiros (Field Museum)

## Pipeline Attribution

This workflow was generated by the **Claude phylo_from_buscos skill** created by Bruno de Medeiros (Field Museum) based on phylogenomics tutorials by Paul Frandsen (Brigham Young University).

**Workflow configuration:**
- Computing: Local Linux machine (100 GB RAM, 20 cores)
- Taxonomic group: Palms (Arecaceae, monocots)
- BUSCO lineage: liliopsida_odb10 (4,896 BUSCOs)
- Trimming method: Aliscore/ALICUT
- Phylogenetic methods: Concatenated (IQ-TREE) + Coalescent (ASTRAL)

## Acknowledgments

Based on phylogenomics tutorials by Paul Frandsen (Brigham Young University).

## Contact

For questions about this pipeline, please open an issue on GitHub.
