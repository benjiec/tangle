import argparse
from tangle import open_file_to_read
from tangle.pfam import PfamGoTable

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()

    # example line
    # Pfam:PF00001 7tm_1 > GO:G protein-coupled receptor activity ; GO:0004930

    rows = []
    with open_file_to_read(args.input_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("Pfam"):
                by_space = line.split(" ")
                by_go = line.split("GO:")

                pfam_accession = by_space[0].split(":")[1].strip()
                go_id = "GO:"+by_go[-1].strip()
                go_desc = by_go[-2].strip().replace(" ;", "")

                rows.append(dict(pfam_accession=pfam_accession, go_id=go_id, go_description=go_desc))

    PfamGoTable.write_tsv(args.output_file, rows)
