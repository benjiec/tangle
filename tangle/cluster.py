from .models import Table, Column

ClusterTable = Table("cluster", [
    Column("batch", required=True),
    Column("clustering_description", required=True),
    Column("cluster_name", required=True),
    Column("cluster_type", required=True),
    Column("parameters"),
    Column("member_database", required=True),
    Column("member_accession", required=True)
  ])
