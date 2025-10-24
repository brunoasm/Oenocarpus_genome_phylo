# Methods Paragraph for Publication

## Phylogenomic Analysis of Palm Genomes

[Copy and customize the text below for your manuscript]

---

### Ortholog Identification and Quality Control

We identified single-copy orthologs from 13 palm genome assemblies (12 downloaded from NCBI plus our newly sequenced *Oenocarpus mapora* genome) using compleasm v0.2.6 (Huang & Li, 2023) with the liliopsida_odb10 BUSCO lineage dataset (v10, 4,896 BUSCOs). Genomes with completeness scores below [THRESHOLD]% were excluded from downstream analyses. From the retained high-quality genomes, we extracted [NUMBER] single-copy orthologs present in all species.

### Multiple Sequence Alignment and Trimming

Each orthologous gene set was aligned using MAFFT v7.520 (Katoh & Standley, 2013) with the L-INS-i algorithm (--localpair --maxiterate 1000) for accurate alignment of conserved protein sequences. Aligned sequences were then trimmed to remove ambiguously aligned regions using Aliscore v2.2 and ALICUT v2.31 (Kück et al., 2010). Aliscore identified randomly similar sequence (RSS) sections using Monte Carlo resampling with default parameters (window size = 4, treating gaps as ambiguous characters with -N option), and ALICUT removed these positions from the alignments. After trimming, alignments containing fewer than [MIN_LENGTH] informative positions were excluded, resulting in [FINAL_NUMBER] high-quality gene alignments.

### Phylogenetic Inference

#### Concatenated Analysis

Trimmed alignments were concatenated into a supermatrix using FASconCAT-G v1.05 (Kück & Longo, 2014), yielding a final alignment of [TOTAL_LENGTH] amino acid positions across [NUMBER] partitions. We performed partitioned maximum likelihood (ML) phylogenetic inference using IQ-TREE v2.3.6 (Minh et al., 2020). The best-fit partitioning scheme and substitution models were selected using ModelFinder (Kalyaanamoorthy et al., 2017) with the TESTMERGEONLY option and LG+G model set. Partitions were merged if they shared the same evolutionary model to reduce model complexity. Branch support was assessed using 1,000 ultrafast bootstrap replicates (Hoang et al., 2018) with the -bnni option to reduce potential overestimation of branch support.

#### Coalescent-Based Species Tree

To account for incomplete lineage sorting, we also inferred a species tree using the multispecies coalescent model. Individual gene trees were estimated for each of the [NUMBER] alignments using IQ-TREE v2.3.6 with automatic model selection and 1,000 ultrafast bootstrap replicates. The resulting gene trees were summarized into a species tree using ASTRAL-III v5.7.8 (Zhang et al., 2018), which estimates the species tree topology that agrees with the largest number of quartet trees induced by the gene trees. Branch support was quantified using local posterior probabilities.

### Software and Reproducibility

All analyses were conducted using a unified conda environment (conda v24.7.1) to ensure reproducibility. Downloaded genome assemblies were retrieved using NCBI Datasets CLI. Analysis scripts and detailed workflow documentation are available at [GITHUB_URL or supplementary materials].

---

## Complete Reference List

Capella-Gutiérrez, S., Silla-Martínez, J. M., & Gabaldón, T. (2009). trimAl: a tool for automated alignment trimming in large-scale phylogenetic analyses. *Bioinformatics*, 25(15), 1972-1973. https://doi.org/10.1093/bioinformatics/btp348

Criscuolo, A., & Gribaldo, S. (2010). BMGE (Block Mapping and Gathering with Entropy): a new software for selection of phylogenetic informative regions from multiple sequence alignments. *BMC Evolutionary Biology*, 10(1), 210. https://doi.org/10.1186/1471-2148-10-210

Hoang, D. T., Chernomor, O., von Haeseler, A., Minh, B. Q., & Vinh, L. S. (2018). UFBoot2: improving the ultrafast bootstrap approximation. *Molecular Biology and Evolution*, 35(2), 518-522. https://doi.org/10.1093/molbev/msx281

Huang, N., & Li, H. (2023). compleasm: a faster and more accurate reimplementation of BUSCO. *Bioinformatics*, 39(10), btad595. https://doi.org/10.1093/bioinformatics/btad595

Kalyaanamoorthy, S., Minh, B. Q., Wong, T. K., von Haeseler, A., & Jermiin, L. S. (2017). ModelFinder: fast model selection for accurate phylogenetic estimates. *Nature Methods*, 14(6), 587-589. https://doi.org/10.1038/nmeth.4285

Katoh, K., & Standley, D. M. (2013). MAFFT multiple sequence alignment software version 7: improvements in performance and usability. *Molecular Biology and Evolution*, 30(4), 772-780. https://doi.org/10.1093/molbev/mst010

Kück, P., & Longo, G. C. (2014). FASconCAT-G: extensive functions for multiple sequence alignment preparations concerning phylogenetic studies. *Frontiers in Zoology*, 11(1), 81. https://doi.org/10.1186/s12983-014-0081-x

Kück, P., Meusemann, K., Dambach, J., Thormann, B., von Reumont, B. M., Wägele, J. W., & Misof, B. (2010). Parametric and non-parametric masking of randomness in sequence alignments can be improved and leads to better resolved trees. *Frontiers in Zoology*, 7(1), 10. https://doi.org/10.1186/1742-9994-7-10

Minh, B. Q., Schmidt, H. A., Chernomor, O., Schrempf, D., Woodhams, M. D., von Haeseler, A., & Lanfear, R. (2020). IQ-TREE 2: new models and efficient methods for phylogenetic inference in the genomic era. *Molecular Biology and Evolution*, 37(5), 1530-1534. https://doi.org/10.1093/molbev/msaa015

Steenwyk, J. L., Buida III, T. J., Li, Y., Shen, X. X., & Rokas, A. (2020). ClipKIT: a multiple sequence alignment trimming software for accurate phylogenomic inference. *PLOS Biology*, 18(12), e3001007. https://doi.org/10.1371/journal.pbio.3001007

Zhang, C., Rabiee, M., Sayyari, E., & Mirarab, S. (2018). ASTRAL-III: polynomial time species tree reconstruction from partially resolved gene trees. *BMC Bioinformatics*, 19(6), 153. https://doi.org/10.1186/s12859-018-2129-y

---

## Instructions for Use

### 1. Replace placeholders in brackets with your actual values:

- `[THRESHOLD]` - Completeness threshold used (e.g., 85, 90, 95)
- `[NUMBER]` - Number of single-copy orthologs initially extracted
- `[MIN_LENGTH]` - Minimum alignment length after trimming
- `[FINAL_NUMBER]` - Final number of gene alignments used
- `[TOTAL_LENGTH]` - Total alignment length of supermatrix
- `[GITHUB_URL]` - URL to your analysis scripts or data repository

### 2. Get actual values after running the pipeline:

```bash
# Activate environment
conda activate phylo

# Get version numbers
conda list | grep -E "compleasm|mafft|iqtree"

# Count orthologs
ls single_copy_orthologs/unaligned_aa/*.fas | wc -l

# Count final trimmed alignments
ls single_copy_orthologs/trimmed_aa/*.fas | wc -l

# Get supermatrix length (from IQ-TREE log)
grep "Input data:" concatenated_ML_tree.log

# Get number of partitions
wc -l single_copy_orthologs/trimmed_aa/partition_def.txt
```

### 3. Adjust detail level based on your target journal:

- **Short version** (word limit journals): Combine paragraphs, remove some technical details
- **Detailed version** (bioinformatics journals): Keep all parameters and add more details
- **Supplementary methods**: Move some technical details to supplement if needed

### 4. Optional modifications:

- If you excluded the coalescent analysis section, remove the "Coalescent-Based Species Tree" paragraph
- If you used different quality thresholds, update the "Quality Control" section
- Add information about outgroup selection if relevant
- Mention any additional filtering steps you performed

### 5. Add to your manuscript:

This text goes in your **Materials and Methods** section under a heading like "Phylogenomic Analysis" or "Phylogenetic Reconstruction"

All references should be added to your bibliography. They are formatted here in a standard citation style and include DOIs for easy verification.

---

## Example Customized Version

Here's an example with placeholders filled in:

> We identified single-copy orthologs from 13 palm genome assemblies using compleasm v0.2.6 with the liliopsida_odb10 BUSCO lineage dataset. Genomes with completeness scores below 85% were excluded. From 12 high-quality genomes, we extracted 3,245 single-copy orthologs present in all species. Each gene set was aligned using MAFFT v7.520 L-INS-i algorithm and trimmed using Aliscore v2.2 and ALICUT v2.31 to remove randomly similar sequences. After excluding alignments shorter than 50 amino acids, 2,187 high-quality gene alignments remained. These were concatenated using FASconCAT-G v1.05 into a supermatrix of 486,293 amino acid positions across 2,187 partitions. Partitioned ML phylogenetic inference was performed using IQ-TREE v2.3.6 with ModelFinder for model selection (TESTMERGEONLY, LG+G) and 1,000 ultrafast bootstrap replicates with -bnni. Individual gene trees were inferred using IQ-TREE and summarized into a coalescent species tree using ASTRAL-III v5.7.8.

---

## Tips for Writing

1. **Be concise but complete**: Include all essential parameters while avoiding excessive detail
2. **Version numbers matter**: Always include software versions for reproducibility
3. **Cite appropriately**: Every software tool mentioned should have a citation
4. **Justify choices**: If asked by reviewers, be prepared to explain why you chose:
   - liliopsida_odb10 lineage (most specific for palms)
   - Aliscore/ALICUT (standard in phylogenomics, handles alignment ambiguity)
   - Both concatenated and coalescent methods (complementary approaches)

5. **Transparency**: If you excluded genomes or genes, state the criteria clearly

---

## Additional Information to Consider Including

Depending on your study, you might also want to add:

- **Outgroup selection**: "We included *Oryza sativa* (rice) as an outgroup..."
- **Root placement**: "Trees were rooted using *Oryza sativa*..."
- **Divergence time estimation**: If you performed molecular dating
- **Tree visualization**: "Trees were visualized using FigTree v1.4.4..."
- **Data deposition**: "Raw sequencing reads were deposited in NCBI SRA under accession..."
- **Code availability**: "Analysis scripts are available at github.com/..."

---

**This methods paragraph was auto-generated by the Claude phylo_from_buscos skill for your palm phylogenomics project.**

**Workflow details:**
- Computing environment: Local Linux machine
- BUSCO lineage: liliopsida_odb10 (monocots, 4,896 BUSCOs)
- Alignment trimming: Aliscore/ALICUT
- Phylogenetic methods: Both concatenated (IQ-TREE) and coalescent (ASTRAL)
