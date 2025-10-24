#!/usr/bin/env python3
"""
Download genome assembly metadata from NCBI for Curculionidae and Arecaceae.
Alternative version using requests directly.
"""

import time
import json
import csv
import os
import sys
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

# Configuration
EMAIL = "bdemedeiros@fieldmuseum.org"
TOOL = "GenomeComparisonScript"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Get API key from environment variable or command line
API_KEY = os.environ.get("NCBI_API_KEY")
if len(sys.argv) > 1:
    API_KEY = sys.argv[1]

if API_KEY:
    print(f"Using NCBI API key: {API_KEY[:10]}...")

def search_assemblies(taxon_name, retmax=10000):
    """
    Search for genome assemblies for a given taxon.

    Args:
        taxon_name: Scientific name of taxon
        retmax: Maximum number of results to return

    Returns:
        List of assembly IDs
    """
    print(f"Searching for {taxon_name} assemblies...")
    search_term = f"{taxon_name}[Organism] AND latest[filter]"

    params = {
        "db": "assembly",
        "term": search_term,
        "retmax": retmax,
        "email": EMAIL,
        "tool": TOOL,
    }

    if API_KEY:
        params["api_key"] = API_KEY

    try:
        url = f"{NCBI_BASE}/esearch.fcgi"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)
        id_list = [id_elem.text for id_elem in root.findall(".//Id")]

        print(f"Found {len(id_list)} assemblies for {taxon_name}")
        return id_list
    except Exception as e:
        print(f"Error searching for {taxon_name}: {e}")
        return []

def fetch_assembly_details(id_list, batch_size=100):
    """
    Fetch detailed information for assembly IDs.

    Args:
        id_list: List of assembly IDs
        batch_size: Number of IDs to fetch per request

    Returns:
        List of assembly records
    """
    all_records = []

    for i in range(0, len(id_list), batch_size):
        batch = id_list[i:i + batch_size]
        print(f"Fetching details for assemblies {i+1}-{min(i+batch_size, len(id_list))}...")

        params = {
            "db": "assembly",
            "id": ",".join(batch),
            "email": EMAIL,
            "tool": TOOL,
        }

        if API_KEY:
            params["api_key"] = API_KEY

        try:
            url = f"{NCBI_BASE}/esummary.fcgi"
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Extract DocumentSummary elements
            for doc_sum in root.findall(".//DocumentSummary"):
                record = {}
                for child in doc_sum:
                    if child.tag == "Meta":
                        # Keep Meta as string for later parsing
                        record["Meta"] = ET.tostring(child, encoding='unicode')
                    elif child.tag == "Biosample":
                        # Handle nested Biosample
                        record["BioSampleAccn"] = child.get("accession", "")
                    else:
                        record[child.tag] = child.text or ""

                all_records.append(record)

            # Be nice to NCBI servers
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching batch {i}: {e}")
            continue

    return all_records

def parse_assembly_record(record):
    """
    Parse an assembly record and extract relevant information.

    Args:
        record: Assembly record from NCBI

    Returns:
        Dictionary with parsed information
    """
    try:
        # Extract organism name
        organism = record.get("Organism", "")

        # Extract species name (binomial)
        species_name = record.get("SpeciesName", "")
        if not species_name and organism:
            # Try to extract binomial from organism name
            parts = organism.split()
            if len(parts) >= 2:
                species_name = f"{parts[0]} {parts[1]}"

        # Extract assembly stats from Meta XML
        meta_xml = record.get("Meta", "")
        scaffold_n50 = None
        contig_n50 = None

        if meta_xml:
            try:
                meta_root = ET.fromstring(f"<root>{meta_xml}</root>")
                for stat in meta_root.findall(".//Stat"):
                    category = stat.get("category")
                    if category == "scaffold_n50":
                        scaffold_n50 = int(stat.text) if stat.text else None
                    elif category == "contig_n50":
                        contig_n50 = int(stat.text) if stat.text else None
            except:
                pass

        return {
            "accession": record.get("AssemblyAccession", ""),
            "organism": organism,
            "species_name": species_name,
            "strain": record.get("Biosample", ""),
            "assembly_name": record.get("AssemblyName", ""),
            "assembly_level": record.get("AssemblyStatus", ""),
            "scaffold_n50": scaffold_n50,
            "contig_n50": contig_n50,
            "submission_date": record.get("SubmissionDate", ""),
            "sequencing_tech": record.get("Coverage", ""),
            "biosample": record.get("BioSampleAccn", ""),
            "taxid": record.get("Taxid", ""),
        }
    except Exception as e:
        print(f"Error parsing record: {e}")
        return None

def save_to_csv(records, filename):
    """
    Save parsed records to CSV file.

    Args:
        records: List of parsed records
        filename: Output filename
    """
    if not records:
        print(f"No records to save to {filename}")
        return

    fieldnames = records[0].keys()

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {filename}")

def main():
    """Main function to download and process genome metadata."""

    taxa = {
        "Curculionidae": "curculionidae_assemblies.csv",
        "Arecaceae": "arecaceae_assemblies.csv"
    }

    for taxon, output_file in taxa.items():
        print(f"\n{'='*60}")
        print(f"Processing {taxon}")
        print(f"{'='*60}\n")

        # Search for assemblies
        id_list = search_assemblies(taxon)

        if not id_list:
            print(f"No assemblies found for {taxon}")
            continue

        # Fetch assembly details
        records = fetch_assembly_details(id_list)

        # Parse records
        parsed_records = []
        for record in records:
            parsed = parse_assembly_record(record)
            if parsed:
                parsed_records.append(parsed)

        # Save to CSV
        save_to_csv(parsed_records, output_file)

        # Print summary
        print(f"\nSummary for {taxon}:")
        print(f"  Total assemblies: {len(parsed_records)}")

        # Count by assembly level
        level_counts = defaultdict(int)
        for rec in parsed_records:
            level_counts[rec["assembly_level"]] += 1

        print(f"  By assembly level:")
        for level, count in sorted(level_counts.items()):
            print(f"    {level}: {count}")

        # Count unique species
        unique_species = len(set(rec["species_name"] for rec in parsed_records if rec["species_name"]))
        print(f"  Unique species: {unique_species}")

    print(f"\n{'='*60}")
    print("Download complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
