from .models import Table, Column

DetectedTable = Table("detected", [
    Column("detection_type", values=("sequence", "structure"), required=True),
    Column("detection_method", required=True, values=("hmm", "prost-t5-foldseek")),
    Column("batch", required=True),
    Column("query_accession", required=True),
    Column("query_database", required=True),
    Column("query_type", values=("transcript", "cds", "protein")),
    Column("target_accession", required=True),
    Column("target_database", required=True),
    Column("target_type", values=("transcript", "cds", "protein", "feature")),
    Column("query_start", type=int, required=True),
    Column("query_end", type=int, required=True),
    Column("target_start", type=int),
    Column("target_end", type=int),
    Column("evalue", type=float),
    Column("bitscore", type=float),
    Column("bitscore_threshold", type=float),
    Column("custom_metric_name"),
    Column("custom_metric_value", type=float),
  ])
