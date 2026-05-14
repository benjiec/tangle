from .models import Table, Column

UniPTable = Table("uniprot", [
    Column("uniprot_accession", required=True),
    Column("name", required=True),
    Column("function", required=False),
  ])

UniPGoTable = Table("uniprot_go", [
    Column("uniprot_accession", required=True),
    Column("go_id", required=True),
    Column("go_description", required=True),
  ])
