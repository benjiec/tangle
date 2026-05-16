from .models import Table, Column

OrthoDBUniProtGroupTable = Table("odb_uniprot_groups", [
    Column("uniprot_accession", required=True),
    Column("odb_group_id", required=True),
    Column("odb_group_level_ncbi_taxid", required=True),
    Column("odb_group_name", required=True),
  ])
