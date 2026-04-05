from .models import Table, Column

PfamGoTable = Table("pfam_go", [
    Column("pfam_accession", required=True),
    Column("go_id", required=True),
    Column("go_description", required=True),
  ])
