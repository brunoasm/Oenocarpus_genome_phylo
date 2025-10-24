#!/usr/bin/env python3
"""
Enrich Curculionidae genome data with Wikidata taxonomy (subfamily and genus).
"""

import csv
import json
import time
import requests
from collections import defaultdict
import sys

# Wikidata API endpoint
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

# Set proper User-Agent as required by Wikidata
HEADERS = {
    "User-Agent": "GenomeResearchBot/1.0 (bdemedeiros@fieldmuseum.org) Python/requests"
}

def search_wikidata_taxon(scientific_name):
    """
    Search for a taxon in Wikidata.

    Args:
        scientific_name: Scientific name to search for

    Returns:
        Wikidata entity ID or None
    """
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "type": "item",
        "search": scientific_name
    }

    try:
        response = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=30)
        data = response.json()

        if data.get("search"):
            # Return the first result that looks like a species/insect
            for result in data["search"]:
                description = result.get("description", "").lower()
                if any(keyword in description for keyword in ["species", "insect", "beetle", "weevil"]):
                    return result["id"]
            # If no species found, return first result
            if data["search"]:
                return data["search"][0]["id"]

        return None

    except Exception as e:
        print(f"  Warning: Error searching Wikidata: {e}")
        return None

def get_entity_info(entity_id):
    """
    Get label, rank, and parent taxon for a Wikidata entity.

    Args:
        entity_id: Wikidata entity ID (e.g., Q13187)

    Returns:
        Tuple of (label, rank_id, parent_id)
    """
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": entity_id,
        "props": "labels|claims"
    }

    try:
        response = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=30)
        data = response.json()

        if "entities" in data and entity_id in data["entities"]:
            entity = data["entities"][entity_id]

            # Get label
            label = entity.get("labels", {}).get("en", {}).get("value", "")

            # Get taxonomic rank (P105)
            claims = entity.get("claims", {})
            rank_id = None
            if "P105" in claims:
                rank_id = claims["P105"][0]["mainsnak"]["datavalue"]["value"]["id"]

            # Get parent taxon (P171)
            parent_id = None
            if "P171" in claims:
                parent_id = claims["P171"][0]["mainsnak"]["datavalue"]["value"]["id"]

            return label, rank_id, parent_id

        return None, None, None

    except Exception as e:
        print(f"  Warning: Error getting entity info: {e}")
        return None, None, None

def get_taxon_lineage(entity_id, max_depth=20):
    """
    Get the full taxonomic lineage from species to family.

    Args:
        entity_id: Starting Wikidata entity ID
        max_depth: Maximum number of levels to traverse

    Returns:
        List of dicts with taxonomy information
    """
    lineage = []
    current_id = entity_id

    for i in range(max_depth):
        label, rank_id, parent_id = get_entity_info(current_id)

        if not label:
            break

        # Get rank name
        rank_name = ""
        if rank_id:
            rank_label, _, _ = get_entity_info(rank_id)
            rank_name = rank_label if rank_label else ""

        lineage.append({
            "id": current_id,
            "name": label,
            "rank": rank_name
        })

        # Stop at family level
        if rank_name == "family":
            break

        if not parent_id:
            break

        current_id = parent_id
        time.sleep(0.2)  # Be respectful to the API

    return lineage

def extract_taxonomy_from_lineage(lineage):
    """
    Extract relevant taxonomic ranks from lineage.

    Args:
        lineage: List of taxonomic levels

    Returns:
        Dict with family, subfamily, and genus
    """
    taxonomy = {
        "family": "",
        "subfamily": "",
        "genus": "",
    }

    for taxon in lineage:
        rank = taxon["rank"].lower()
        name = taxon["name"]

        if rank == "family":
            taxonomy["family"] = name
        elif rank == "subfamily":
            taxonomy["subfamily"] = name
        elif rank == "genus":
            taxonomy["genus"] = name

    return taxonomy

def query_wikidata_taxonomy(genus, species):
    """
    Query Wikidata for taxonomy information.

    Args:
        genus: Genus name
        species: Species epithet

    Returns:
        Dictionary with taxonomy information or None
    """
    scientific_name = f"{genus} {species}".strip()

    # Search for the taxon
    entity_id = search_wikidata_taxon(scientific_name)

    if not entity_id:
        return None

    # Get lineage
    lineage = get_taxon_lineage(entity_id)

    if not lineage:
        return None

    # Extract accepted name (first in lineage should be the species)
    accepted_name = lineage[0]["name"] if lineage else scientific_name

    # Extract taxonomy
    taxonomy = extract_taxonomy_from_lineage(lineage)
    taxonomy["accepted_name"] = accepted_name
    taxonomy["wikidata_id"] = entity_id

    return taxonomy

def enrich_curculionidae_data(input_file, output_file):
    """
    Read Curculionidae assemblies and enrich with Wikidata taxonomy.

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
                "genus_wikidata": "",
                "wikidata_id": "",
            })
            enriched.append(assembly)
            failed.append(species_name)
            continue

        # Parse genus and species
        parts = species_name.split()
        genus = parts[0]
        species = parts[1] if len(parts) > 1 else ""

        # Query Wikidata
        taxonomy = query_wikidata_taxonomy(genus, species)

        if taxonomy:
            print(f"  Found: {taxonomy['accepted_name']} ({taxonomy['wikidata_id']})")
            if taxonomy['subfamily']:
                print(f"    Subfamily: {taxonomy['subfamily']}")
            if taxonomy['genus']:
                print(f"    Genus: {taxonomy['genus']}")

            # Add genus_wikidata for consistency
            taxonomy["genus_wikidata"] = taxonomy.get("genus", "")

            assembly.update(taxonomy)
        else:
            print(f"  Not found in Wikidata")
            assembly.update({
                "accepted_name": "",
                "family": "",
                "subfamily": "",
                "genus_wikidata": "",
                "wikidata_id": "",
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
        subfamily = record.get("subfamily", "").strip()
        if subfamily:
            taxa_sets["subfamily"].add(subfamily)

        genus = record.get("genus_wikidata", "").strip()
        if genus:
            taxa_sets["genus"].add(genus)

    # Save to file
    with open(output_file, 'w') as f:
        f.write("# Higher Taxa in Curculionidae (from Wikidata)\n")
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
    print("Enriching Curculionidae genome data with Wikidata taxonomy")
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
