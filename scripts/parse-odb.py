import duckdb
from tangle import unique_batch
from tangle.orthodb import OrthoDBUniProtGroupTable
from scripts.defaults import Defaults

basedir = Defaults.tangle_dir() / "odb12v2"

group_fn = basedir / "odb12v2_OGs.tab.gz"
og2gn_fn = basedir / "odb12v2_OG2genes.tab.gz"
gnxrf_fn = basedir / "odb12v2_gene_xrefs.tab.gz"

schema = dict(
  group = (group_fn, ["odb_og_id", "ncbi_taxid", "og_name"]),
  og2gn = (og2gn_fn, ["odb_og_id", "odb_gene_id"]),
  gnxrf = (gnxrf_fn, ["odb_gene_id", "ext_id", "ext_db_name"]),
) 

schema_name = f"tmp_odb12v12_{unique_batch()}"

duckdb.execute(f"CREATE SCHEMA {schema_name}")

for tn, (fn, headers) in schema.items():
    create_str = f"CREATE TABLE {schema_name}.{tn} AS SELECT * FROM read_csv('{fn}', header=false, delim='\t', names={headers}, sample_size=1000)"
    print(create_str)

    # XXX DEBUG
    create_str += " LIMIT 1000";

    duckdb.execute(create_str)

db = duckdb.connect(':default:')

query = """
  SELECT gnxrf.ext_id AS 'uniprot_accession',
         group.odb_og_id AS 'odb_group_id',
         group.ncbi_taxid AS 'odb_group_level_ncbi_taxid',
         group.og_name AS 'odb_group_name'
    FROM group
    JOIN og2gn ON group.odb_og_id = og2gn.odb_og_id
    JOIN gnxrf ON og2gn.odb_gene_id = gnxrf.odb_gene_id
   WHERE group.ncbi_taxid IN (2, 2157, 2759, 10239)
         gnxrf.ext_db_name = 'UniProt'
"""

rows = db.execute(query).fetchdf().to_dict('records')
OrthoDBUniProtGroupTable.write_tsv(Defaults.tangle_dir() / "odb_uniprot_groups.tsv", rows)
