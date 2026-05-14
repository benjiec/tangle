import gzip
import argparse
from Bio import SwissProt
from tangle.uniprot import UniPGoTable, UniPTable

parser = argparse.ArgumentParser()
parser.add_argument("input_gz_file")
args = parser.parse_args()

sp_rows = []
go_rows = []

with gzip.open(args.input_gz_file, "rt") as handle:
    for record in SwissProt.parse(handle):

        gene_name = ""
        if record.description.startswith("RecName: Full="):
            gene_name = record.description.split(";")[0][len("RecName: Full="):]
        elif record.gene_name:
            for name_rec in record.gene_name:
                if "Name" in name_rec:
                    gene_name = name_rec["Name"]
                    break

        go_terms = []
        for cr in record.cross_references:
            if cr[0] == "GO":
                go_terms.append((cr[1], cr[2][2:]))

        function = ""
        for comment in record.comments:
            if comment.startswith("FUNCTION:"):
                function = comment.replace("FUNCTION: ", "")
                break

        for acc in record.accessions:
            sp_rows.append(dict(uniprot_accession=acc, name=gene_name, function=function))
            for go_term, go_desc in go_terms:
                go_rows.append(dict(uniprot_accession=acc, go_id=go_term, go_description=go_desc))

UniPTable.write_tsv("uniprot.tsv.gz", sp_rows)
UniPGoTable.write_tsv("uniprot_go.tsv.gz", go_rows)
