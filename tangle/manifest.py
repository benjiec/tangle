from .models import Table, Column

ManifestTable = Table("manifest", [
    Column("sequence_accession", required=True),
    Column("sequence_database", required=True),
    Column("sequence_type", values=("contig", "transcript", "gene", "exon", "cds", "protein"), required=True),
    Column("sequence_source"),
  ])
