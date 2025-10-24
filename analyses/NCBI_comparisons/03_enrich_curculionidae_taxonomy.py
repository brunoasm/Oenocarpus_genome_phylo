#!/usr/bin/env python3
"""
Enrich Curculionidae genome data with Catalogue of Life taxonomy.
"""

import csv
import json
import time
import requests
from collections import defaultdict
import sys

# Catalogue of Life API endpoint
COL_API = "https://api.catalogueoflife.org"

def query_col_taxonomy(genus, species):
    """
    Query Catalogue of Life for taxonomy information.

    Args:
        genus: Genus name
        species: Species epithet

    Returns:
        Dictionary with taxonomy information or None
    """
    scientific_name = f"{genus} {species}".strip()

    # First, search for the name
    try:
        search_url = f"{COL_API}/dataset/3/nameusage/search"
        params = {
            "q": scientific_name,
            "type": "EXACT",
            "rank": "species"
        }

        response = requests.get(search_url, params=params, timeout=30)

        if response.status_code != 200:
            print(f"  Warning: COL API returned status {response.status_code} for {scientific_name}")
            return None

        data = response.json()

        if not data.get("result"):
            # Try fuzzy search if exact fails
            params["type"] = "WHOLE_WORDS"
            response = requests.get(search_url, params=params, timeout=30)
            data = response.json()

        if not data.get("result"):
            print(f"  Not found in Catalogue of Life")
            return None

        # Get the first result
        result = data["result"][0]

        # Get full taxonomy from usage ID
        usage_id = result.get("id")
        if usage_id:
            detail_url = f"{COL_API}/dataset/3/nameusage/{usage_id}"
            detail_response = requests.get(detail_url, timeout=30)

            if detail_response.status_code == 200:
                detail_data = detail_response.json()

                # Extract classification
                classification = detail_data.get("classification", [])

                # Build taxonomy dictionary
                taxonomy_dict = {}
                for taxon in classification:
                    rank = taxon.get("rank", "").lower()
                    name = taxon.get("name", "")
                    if rank and name:
                        taxonomy_dict[rank] = name

                accepted_name = detail_data.get("name", {}).get("scientificName", scientific_name)

                return {
                    "accepted_name": accepted_name,
                    "family_col": taxonomy_dict.get("family", ""),
                    "subfamily_col": taxonomy_dict.get("subfamily", ""),
                    "tribe_col": taxonomy_dict.get("tribe", ""),
                    "genus_col": taxonomy_dict.get("genus", ""),
                    "status": detail_data.get("status", ""),
                }

        return None

    except requests.exceptions.Timeout:
        print(f"  Warning: Timeout querying COL for {scientific_name}")
        return None
    except Exception as e:
        print(f"  Warning: Error querying COL for {scientific_name}: {e}")
        return None

def enrich_curculionidae_data(input_file, output_file):
    """
    Read Curculionidae assemblies and enrich with COL taxonomy.

    Args:
        input_file: Input CSV file with assembly data
        output_file: Output CSV file with enriched data
    """
    # Read input data
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        assemblies = list(reader)

    print(f"Read {len(assemblies)} assemblies from {input_file}")

    # Enrich with taxonomy
    enriched = []
    failed = []

    for i, assembly in enumerate(assemblies, 1):
        species_name = assembly.get("species_name", "")
        print(f"\n[{i}/{len(assemblies)}] Processing {species_name}...")

        if not species_name or " " not in species_name:
            print(f"  Skipping: invalid species name")
            assembly.update({
                "accepted_name": "",
                "family_col": "",
                "subfamily_col": "",
                "tribe_col": "",
                "genus_col": "",
                "status": "",
            })
            enriched.append(assembly)
            failed.append(species_name)
            continue

        # Parse genus and species
        parts = species_name.split()
        genus = parts[0]
        species = parts[1] if len(parts) > 1 else ""

        # Query COL
        taxonomy = query_col_taxonomy(genus, species)

        if taxonomy:
            print(f"  Found: {taxonomy['accepted_name']}")
            if taxonomy['subfamily_col']:
                print(f"    Subfamily: {taxonomy['subfamily_col']}")
            if taxonomy['genus_col']:
                print(f"    Genus: {taxonomy['genus_col']}")

            assembly.update(taxonomy)
        else:
            print(f"  Not found in COL")
            assembly.update({
                "accepted_name": "",
                "family_col": "",
                "subfamily_col": "",
                "tribe_col": "",
                "genus_col": "",
                "status": "",
            })
            failed.append(species_name)

        enriched.append(assembly)

        # Be nice to the API
        time.sleep(0.5)

    # Save enriched data
    if enriched:
        fieldnames = enriched[0].keys()
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enriched)

        print(f"\nSaved {len(enriched)} enriched records to {output_file}")

    # Report failures
    if failed:
        print(f"\nFailed to find taxonomy for {len(failed)} species:")
        for name in failed:
            print(f"  - {name}")

    return enriched

def extract_all_taxa(enriched_data, output_file):
    """
    Extract all unique higher taxa (subfamily and genus) from enriched data.

    Args:
        enriched_data: List of enriched assembly records
        output_file: Output file for higher taxa list
    """
    taxa_sets = {
        "subfamily": set(),
        "genus": set(),
    }

    for record in enriched_data:
        subfamily = record.get("subfamily_col", "").strip()
        if subfamily:
            taxa_sets["subfamily"].add(subfamily)

        genus = record.get("genus_col", "").strip()
        if genus:
            taxa_sets["genus"].add(genus)

    # Save to file
    with open(output_file, 'w') as f:
        f.write("# Higher Taxa in Curculionidae (from Catalogue of Life)\n")
        f.write("# Format: rank | taxon name\n\n")

        for rank in ["subfamily", "genus"]:
            taxa = sorted(taxa_sets[rank])
            f.write(f"\n## {rank.upper()}\n")
            f.write(f"# Total: {len(taxa)}\n\n")
            for taxon in taxa:
                f.write(f"{rank}\t{taxon}\n")

    print(f"\nSaved higher taxa list to {output_file}")

    # Print summary
    print("\nHigher taxa summary:")
    for rank in ["subfamily", "genus"]:
        print(f"  {rank}: {len(taxa_sets[rank])} unique taxa")

def main():
    """Main function."""
    input_file = "curculionidae_assemblies.csv"
    output_file = "curculionidae_assemblies_enriched.csv"
    taxa_file = "curculionidae_higher_taxa.txt"

    print("="*60)
    print("Enriching Curculionidae genome data with COL taxonomy")
    print("="*60)

    # Enrich data
    enriched = enrich_curculionidae_data(input_file, output_file)

    # Extract higher taxa
    extract_all_taxa(enriched, taxa_file)

    print("\n" + "="*60)
    print("Enrichment complete!")
    print("="*60)

if __name__ == "__main__":
    main()
