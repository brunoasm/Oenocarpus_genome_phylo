#!/usr/bin/env python3
"""
Generate statistics and summary paragraph for genome assemblies.
"""

import csv
import json
from collections import defaultdict

# Known diversity estimates (can be updated with better estimates)
DIVERSITY_ESTIMATES = {
    "Arecaceae": {
        "total_species": 2600,  # Approximate
        "total_genera": 181,
        "total_subfamilies": 5,
        "total_tribes_cocoseae": 15,  # Approximate for tribe Cocoseae
        "total_subtribes_cocoseae": 4,  # Approximate for tribe Cocoseae
    },
    "Curculionidae": {
        "total_species": 51000,  # Approximate (one of the largest animal families)
        "total_genera": 4600,  # Approximate
        "total_subfamilies": 8,  # Major subfamilies
    }
}

def is_high_quality(assembly):
    """
    Determine if an assembly is high quality.
    High quality = Chromosome level OR Scaffold N50 > 10 Mb

    Args:
        assembly: Dictionary with assembly information

    Returns:
        Boolean indicating if assembly is high quality
    """
    assembly_level = assembly.get("assembly_level", "").lower()

    # Check if chromosome level
    if "chromosome" in assembly_level or assembly_level == "complete genome":
        return True

    # Check scaffold N50
    scaffold_n50 = assembly.get("scaffold_n50")
    if scaffold_n50:
        try:
            n50_value = int(scaffold_n50)
            if n50_value > 10_000_000:  # 10 Mb
                return True
        except (ValueError, TypeError):
            pass

    return False

def analyze_arecaceae(input_file):
    """
    Analyze Arecaceae genome assemblies.

    Args:
        input_file: Path to enriched CSV file

    Returns:
        Dictionary with statistics
    """
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        assemblies = list(reader)

    # Filter high-quality assemblies
    hq_assemblies = [a for a in assemblies if is_high_quality(a)]

    # Count unique species
    all_species = set(a["species_name"] for a in assemblies if a["species_name"])
    hq_species = set(a["species_name"] for a in hq_assemblies if a["species_name"])

    # Count genera
    all_genera = set()
    hq_genera = set()
    for a in assemblies:
        if a["species_name"] and " " in a["species_name"]:
            genus = a["species_name"].split()[0]
            all_genera.add(genus)
            if is_high_quality(a):
                hq_genera.add(genus)

    # Count higher taxa
    subfamilies = set(a["subfamily"] for a in hq_assemblies if a.get("subfamily"))
    tribes = set(a["tribe"] for a in hq_assemblies if a.get("tribe"))
    subtribes = set(a["subtribe"] for a in hq_assemblies if a.get("subtribe"))

    # Filter for Cocoseae tribe
    cocoseae_assemblies = [a for a in hq_assemblies if a.get("tribe") == "Cocoseae"]
    cocoseae_subtribes = set(a["subtribe"] for a in cocoseae_assemblies if a.get("subtribe"))
    cocoseae_genera = set()
    for a in cocoseae_assemblies:
        if a["species_name"] and " " in a["species_name"]:
            genus = a["species_name"].split()[0]
            cocoseae_genera.add(genus)

    return {
        "total_assemblies": len(assemblies),
        "hq_assemblies": len(hq_assemblies),
        "all_species": len(all_species),
        "hq_species": len(hq_species),
        "all_genera": len(all_genera),
        "hq_genera": len(hq_genera),
        "subfamilies": len(subfamilies),
        "tribes": len(tribes),
        "subtribes": len(subtribes),
        "cocoseae_subtribes": len(cocoseae_subtribes),
        "cocoseae_genera": len(cocoseae_genera),
        "subfamilies_list": sorted(subfamilies),
        "tribes_list": sorted(tribes),
        "subtribes_list": sorted(subtribes),
        "cocoseae_subtribes_list": sorted(cocoseae_subtribes),
    }

def analyze_curculionidae(input_file):
    """
    Analyze Curculionidae genome assemblies.

    Args:
        input_file: Path to enriched CSV file

    Returns:
        Dictionary with statistics
    """
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        assemblies = list(reader)

    # Filter high-quality assemblies
    hq_assemblies = [a for a in assemblies if is_high_quality(a)]

    # Count unique species
    all_species = set(a["species_name"] for a in assemblies if a["species_name"])
    hq_species = set(a["species_name"] for a in hq_assemblies if a["species_name"])

    # Count genera
    all_genera = set()
    hq_genera = set()
    for a in assemblies:
        if a["species_name"] and " " in a["species_name"]:
            genus = a["species_name"].split()[0]
            all_genera.add(genus)
            if is_high_quality(a):
                hq_genera.add(genus)

    # Count subfamilies
    subfamilies = set(a["subfamily_col"] for a in hq_assemblies if a.get("subfamily_col"))

    return {
        "total_assemblies": len(assemblies),
        "hq_assemblies": len(hq_assemblies),
        "all_species": len(all_species),
        "hq_species": len(hq_species),
        "all_genera": len(all_genera),
        "hq_genera": len(hq_genera),
        "subfamilies": len(subfamilies),
        "subfamilies_list": sorted(subfamilies),
    }

def generate_summary_paragraph(arec_stats, curc_stats):
    """
    Generate natural language summary paragraph.

    Args:
        arec_stats: Dictionary with Arecaceae statistics
        curc_stats: Dictionary with Curculionidae statistics

    Returns:
        String with summary paragraph
    """
    arec_div = DIVERSITY_ESTIMATES["Arecaceae"]
    curc_div = DIVERSITY_ESTIMATES["Curculionidae"]

    # Calculate percentages
    arec_species_pct = (arec_stats["hq_species"] / arec_div["total_species"]) * 100
    arec_genera_pct = (arec_stats["hq_genera"] / arec_div["total_genera"]) * 100
    arec_subfamily_pct = (arec_stats["subfamilies"] / arec_div["total_subfamilies"]) * 100
    arec_cocoseae_subtribe_pct = (arec_stats["cocoseae_subtribes"] / arec_div["total_subtribes_cocoseae"]) * 100

    curc_species_pct = (curc_stats["hq_species"] / curc_div["total_species"]) * 100
    curc_genera_pct = (curc_stats["hq_genera"] / curc_div["total_genera"]) * 100
    curc_subfamily_pct = (curc_stats["subfamilies"] / curc_div["total_subfamilies"]) * 100

    paragraph = f"""
GENOME ASSEMBLY STATISTICS FOR ARECACEAE AND CURCULIONIDAE

ARECACEAE (Palms)
-----------------
Of the {arec_stats['total_assemblies']} genome assemblies available for Arecaceae in NCBI,
{arec_stats['hq_assemblies']} ({(arec_stats['hq_assemblies']/arec_stats['total_assemblies']*100):.1f}%)
are high-quality (chromosome-level or scaffold N50 > 10 Mb). These high-quality assemblies
represent {arec_stats['hq_species']} species ({arec_species_pct:.2f}% of ~{arec_div['total_species']:,}
described palm species) from {arec_stats['hq_genera']} genera ({arec_genera_pct:.1f}% of
{arec_div['total_genera']} genera). At higher taxonomic levels, the assemblies span
{arec_stats['subfamilies']} of {arec_div['total_subfamilies']} subfamilies
({arec_subfamily_pct:.0f}%), {arec_stats['tribes']} tribes, and {arec_stats['subtribes']} subtribes.
Within the tribe Cocoseae specifically, high-quality genomes represent {arec_stats['cocoseae_subtribes']}
of {arec_div['total_subtribes_cocoseae']} subtribes ({arec_cocoseae_subtribe_pct:.0f}%) and
{arec_stats['cocoseae_genera']} genera. The represented subfamilies are: {', '.join(arec_stats['subfamilies_list'])}.

CURCULIONIDAE (Weevils)
-----------------------
For Curculionidae, {curc_stats['total_assemblies']} genome assemblies are available in NCBI,
with {curc_stats['hq_assemblies']} ({(curc_stats['hq_assemblies']/curc_stats['total_assemblies']*100):.1f}%)
meeting high-quality criteria. These assemblies represent {curc_stats['hq_species']} species
({curc_species_pct:.3f}% of ~{curc_div['total_species']:,} described weevil species) across
{curc_stats['hq_genera']} genera ({curc_genera_pct:.2f}% of ~{curc_div['total_genera']:,} genera).
At the subfamily level, {curc_stats['subfamilies']} of approximately {curc_div['total_subfamilies']}
major subfamilies ({curc_subfamily_pct:.0f}%) are represented by high-quality genome assemblies.
The represented subfamilies are: {', '.join(curc_stats['subfamilies_list']) if curc_stats['subfamilies_list'] else 'data pending taxonomic enrichment'}.

COMPARATIVE PERSPECTIVE
-----------------------
Both families show relatively limited genomic sampling, with high-quality genomes representing
less than 1% of described species diversity in both cases. However, Arecaceae shows substantially
better representation at higher taxonomic levels ({arec_subfamily_pct:.0f}% of subfamilies)
compared to Curculionidae ({curc_subfamily_pct:.0f}% of subfamilies), likely reflecting the
smaller size and greater phylogenetic tractability of the palm family. The addition of genomes
for Oenocarpus mapora (Arecaceae: Cocoseae) and Anchylorhynchus bicarinatus (Curculionidae)
represents valuable contributions to the genomic characterization of these diverse plant and
insect families.
"""

    return paragraph

def save_json_summary(arec_stats, curc_stats, output_file):
    """
    Save statistics as JSON for programmatic access.

    Args:
        arec_stats: Arecaceae statistics
        curc_stats: Curculionidae statistics
        output_file: Output JSON file
    """
    summary = {
        "diversity_estimates": DIVERSITY_ESTIMATES,
        "arecaceae": arec_stats,
        "curculionidae": curc_stats,
    }

    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Saved JSON summary to {output_file}")

def main():
    """Main function."""
    print("="*70)
    print("GENERATING GENOME ASSEMBLY STATISTICS")
    print("="*70)

    # Analyze Arecaceae
    print("\nAnalyzing Arecaceae...")
    arec_stats = analyze_arecaceae("arecaceae_assemblies_enriched.csv")

    print(f"  Total assemblies: {arec_stats['total_assemblies']}")
    print(f"  High-quality assemblies: {arec_stats['hq_assemblies']}")
    print(f"  HQ species: {arec_stats['hq_species']}")
    print(f"  HQ genera: {arec_stats['hq_genera']}")
    print(f"  Subfamilies: {arec_stats['subfamilies']}")
    print(f"  Tribes: {arec_stats['tribes']}")
    print(f"  Subtribes: {arec_stats['subtribes']}")

    # Analyze Curculionidae
    print("\nAnalyzing Curculionidae...")
    curc_stats = analyze_curculionidae("curculionidae_assemblies_enriched.csv")

    print(f"  Total assemblies: {curc_stats['total_assemblies']}")
    print(f"  High-quality assemblies: {curc_stats['hq_assemblies']}")
    print(f"  HQ species: {curc_stats['hq_species']}")
    print(f"  HQ genera: {curc_stats['hq_genera']}")
    print(f"  Subfamilies: {curc_stats['subfamilies']}")

    # Generate summary paragraph
    print("\n" + "="*70)
    summary = generate_summary_paragraph(arec_stats, curc_stats)
    print(summary)

    # Save summary to file
    with open("genome_statistics_summary.txt", 'w') as f:
        f.write(summary)
    print("Saved summary to genome_statistics_summary.txt")

    # Save JSON summary
    save_json_summary(arec_stats, curc_stats, "genome_statistics.json")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
