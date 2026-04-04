import os
import csv
import time
import requests
import argparse
import xml.etree.ElementTree as ET
from scripts.defaults import Defaults
from tangle import open_file_to_read


def _parse_taxonomy_lineage(root):

    domain = kingdom = phylum = order = class_ = family = genus = species = ''

    for taxon in root.findall('.//LineageEx/Taxon'):
        rank = taxon.findtext('Rank')
        name = taxon.findtext('ScientificName')
        if rank == 'domain':
            domain = name
        elif rank == 'kingdom':
            kingdom = name
        elif rank == 'phylum':
            phylum = name
        elif rank == 'clade':
            if domain and not kingdom and not phylum and not class_:
                kingdom = name
            elif kingdom and not phylum and not class_:
                phylum = name
        elif rank == 'class':
            class_ = name
        elif rank == 'order':
            order = name
        elif rank == 'family':
            family = name
        elif rank == 'genus':
            genus = name
        elif rank == 'species':
            species = name

    # If the current node is species, use its name
    for node in root.findall('.//Taxon'):
        rank = node.findtext('Rank')
        name = node.findtext('ScientificName')
        if rank == 'species':
            species = name

    return {
        'Domain': domain,
        'Kingdom': kingdom,
        'Phylum': phylum,
        'Class': class_,
        'Order': order,
        'Family': family,
        'Genus': genus,
        'Species': species,
    }


def parse_taxonomy_tsv(taxonomy_tsv):
    """
    Yield each row of a taxonomy TSV/CSV as a dict, robust to column order and delimiter.
    """
    with open(taxonomy_tsv, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            yield row


def fetch_and_append_taxonomy(genome_acc: str, taxonomy_tsv: str):
    """
    Fetch genome and taxonomy info and append to taxonomy_tsv.
    """

    genome_fieldnames = ['Genome Accession', 'Genome Name', 'TaxID', 'Organism']
    lineage_fieldnames = ['Domain', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # Lookup UID for accession
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=assembly&term={genome_acc}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    uid_list = r.json()['esearchresult']['idlist']
    if not uid_list:
        print(f"Warning: No UID found for accession {genome_acc}. Skipping taxonomy.", flush=True)
        return
    uid = uid_list[0]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=assembly&id={uid}&retmode=json"
    r = requests.get(url)
    r.raise_for_status()
    doc = r.json()['result'][uid]
    species = doc.get('speciesname', '')
    taxid = doc.get('taxid', '')
    genome_name = doc.get('assemblyname', '')
    organism = doc.get('organism', '')

    # Fetch taxonomy info from NCBI taxonomy using taxid
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={taxid}&retmode=xml"
    r = requests.get(url)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    lineage = _parse_taxonomy_lineage(root)
    new_row = {
        'Genome Accession': genome_acc,
        'Genome Name': genome_name,
        'TaxID': taxid,
        'Organism': organism
    }
    new_row.update(lineage)

    fieldnames = new_row.keys()
    if set(fieldnames) != set(genome_fieldnames+lineage_fieldnames):
        print(f"{genome_acc}: fieldnames do not match")
        return

    # If file does not exist or is empty, create it with header
    if not os.path.exists(taxonomy_tsv):
        print("Creating TSV")
        with open(taxonomy_tsv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()

    # Read all rows, filter out any with matching accession or taxid
    rows = []
    for row in parse_taxonomy_tsv(taxonomy_tsv):
        if row.get('Genome Accession', '') != genome_acc:
            rows.append(row)
    rows.append(new_row)

    # Write all rows back using DictWriter
    with open(taxonomy_tsv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("accessions_fn")
    args = parser.parse_args()

    with open_file_to_read(args.accessions_fn) as f:
        lines = f.readlines()
        for line in lines:
            accession = line.strip()
            assert len(accession.split()) == 1
            print(accession)
            fetch_and_append_taxonomy(accession, Defaults.area_genome_taxon_tsv())
            time.sleep(1)
