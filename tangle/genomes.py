from .models import Table, Column

# Semantics: a list of genome accessions

GenomeAccessionList = Table("genome_accessions", [
    Column("genome_accession", required=True),
    Column("run_protein_detection", required=True, type=int, values=(0, 1)),
    Column("use_ncbi_proteins", required=True, type=int, values=(0, 1)),
])
