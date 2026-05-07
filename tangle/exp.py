from .models import Table, Column

TranscriptCountsTable = Table("transcript_counts", [
    Column("experiment_id", type=str, required=True),
    Column("cohort", required=True),
    Column("timepoint", type=str, required=True),
    Column("sample", type=str, required=True),
    Column("genome_accession", type=str),
    Column("sequence_id", type=str, required=True),
    Column("count", type=float, required=True),
    Column("raw_count", type=float),
    Column("tpm", type=float)
  ])

DESeq2Table = Table("deseq2_tall", [
    Column("experiment_id", type=str, required=True),
    Column("sequence_id", type=str, required=True),
    Column("analysis_type", type=str, required=True),
    Column("baseMean", type=float, required=True),
    Column("log2FoldChange", type=float, required=True),
    Column("lfcSE", type=float, required=True),
    Column("stat", type=float, required=True),
    Column("pvalue", type=float, required=True),
    Column("padj", type=float, required=True),
    Column("max_cv", type=float, required=True),
    Column("mean_base", type=float, required=True),
    Column("mean_testgroup", type=float, required=True)
  ])
