#!/usr/bin/env python3
"""
Enrich Arecaceae genome data with WFO Plant List taxonomy (subtribe to subfamily).
"""

import csv
import json
import time
import requests
from collections import defaultdict
import sys

# WFO GraphQL API endpoint
WFO_API = "https://list.worldfloraonline.org/gql.php"

def query_wfo_taxonomy(genus, species):
    """
    Query WFO Plant List for taxonomy information.

    Args:
        genus: Genus name
        species: Species epithet

    Returns:
        Dictionary with taxonomy information or None
    """
    # GraphQL query to get taxonomy
    query = """
    query($scientificName: String!) {
        taxonNameMatch(scientificName: $scientificName) {
            name {
                fullNameStringPlain
                rank
            }
            acceptedName {
                fullNameStringPlain
                id
            }
            acceptedPlacement {
                family {
                    fullNameStringPlain
                }
                subfamily {
                    fullNameStringPlain
                }
                tribe {
                    fullNameStringPlain
                }
                subtribe {
                    fullNameStringPlain
                }
                genus {
                    fullNameStringPlain
                }
            }
        }
    }
    """

    scientific_name = f"{genus} {species}".strip()

    try:
        response = requests.post(
            WFO_API,
            json={
                "query": query,
                "variables": {"scientificName": scientific_name}
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"  Warning: WFO API returned status {response.status_code} for {scientific_name}")
            return None

        data = response.json()

        if "errors" in data:
            print(f"  Warning: WFO API errors for {scientific_name}: {data['errors']}")
            return None

        # Extract taxonomy from response
        if "data" in data and data["data"].get("taxonNameMatch"):
            match = data["data"]["taxonNameMatch"]

            # Get accepted name if different from query
            accepted_name = scientific_name
            if match.get("acceptedName"):
                accepted_name = match["acceptedName"].get("fullNameStringPlain", scientific_name)

            placement = match.get("acceptedPlacement", {})

            return {
                "accepted_name": accepted_name,
                "family": placement.get("family", {}).get("fullNameStringPlain", "") if placement.get("family") else "",
                "subfamily": placement.get("subfamily", {}).get("fullNameStringPlain", "") if placement.get("subfamily") else "",
                "tribe": placement.get("tribe", {}).get("fullNameStringPlain", "") if placement.get("tribe") else "",
                "subtribe": placement.get("subtribe", {}).get("fullNameStringPlain", "") if placement.get("subtribe") else "",
                "genus_wfo": placement.get("genus", {}).get("fullNameStringPlain", "") if placement.get("genus") else "",
            }

        return None

    except requests.exceptions.Timeout:
        print(f"  Warning: Timeout querying WFO for {scientific_name}")
        return None
    except Exception as e:
        print(f"  Warning: Error querying WFO for {scientific_name}: {e}")
        return None

def enrich_arecaceae_data(input_file, output_file):
    """
    Read Arecaceae assemblies and enrich with WFO taxonomy.

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
                "family": "",
                "subfamily": "",
                "tribe": "",
                "subtribe": "",
                "genus_wfo": "",
            })
            enriched.append(assembly)
            failed.append(species_name)
            continue

        # Parse genus and species
        parts = species_name.split()
        genus = parts[0]
        species = parts[1] if len(parts) > 1 else ""

        # Query WFO
        taxonomy = query_wfo_taxonomy(genus, species)

        if taxonomy:
            print(f"  Found: {taxonomy['accepted_name']}")
            if taxonomy['subfamily']:
                print(f"    Subfamily: {taxonomy['subfamily']}")
            if taxonomy['tribe']:
                print(f"    Tribe: {taxonomy['tribe']}")
            if taxonomy['subtribe']:
                print(f"    Subtribe: {taxonomy['subtribe']}")

            assembly.update(taxonomy)
        else:
            print(f"  Not found in WFO")
            assembly.update({
                "accepted_name": "",
                "family": "",
                "subfamily": "",
                "tribe": "",
                "subtribe": "",
                "genus_wfo": "",
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
    Extract all unique higher taxa (subfamily to subtribe) from enriched data.

    Args:
        enriched_data: List of enriched assembly records
        output_file: Output file for higher taxa list
    """
    taxa_sets = {
        "subfamily": set(),
        "tribe": set(),
        "subtribe": set(),
    }

    for record in enriched_data:
        for rank in taxa_sets.keys():
            taxon = record.get(rank, "").strip()
            if taxon:
                taxa_sets[rank].add(taxon)

    # Save to file
    with open(output_file, 'w') as f:
        f.write("# Higher Taxa in Arecaceae (from WFO Plant List)\n")
        f.write("# Format: rank | taxon name\n\n")

        for rank in ["subfamily", "tribe", "subtribe"]:
            taxa = sorted(taxa_sets[rank])
            f.write(f"\n## {rank.upper()}\n")
            f.write(f"# Total: {len(taxa)}\n\n")
            for taxon in taxa:
                f.write(f"{rank}\t{taxon}\n")

    print(f"\nSaved higher taxa list to {output_file}")

    # Print summary
    print("\nHigher taxa summary:")
    for rank in ["subfamily", "tribe", "subtribe"]:
        print(f"  {rank}: {len(taxa_sets[rank])} unique taxa")

def main():
    """Main function."""
    input_file = "arecaceae_assemblies.csv"
    output_file = "arecaceae_assemblies_enriched.csv"
    taxa_file = "arecaceae_higher_taxa.txt"

    print("="*60)
    print("Enriching Arecaceae genome data with WFO taxonomy")
    print("="*60)

    # Enrich data
    enriched = enrich_arecaceae_data(input_file, output_file)

    # Extract higher taxa
    extract_all_taxa(enriched, taxa_file)

    print("\n" + "="*60)
    print("Enrichment complete!")
    print("="*60)

if __name__ == "__main__":
    main()
