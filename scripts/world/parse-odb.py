import duckdb
from tangle import unique_batch
from tangle.orthodb import OrthoDBUniProtGroupTable
from scripts.defaults import Defaults

basedir = Defaults.tangle_dir() / "odb12v2"

group_fn = basedir / "odb12v2_OGs.tab.gz"
og2gn_fn = basedir / "odb12v2_OG2genes.tab.gz"
gnxrf_fn = basedir / "odb12v2_gene_xrefs.tab.uniprot.gz"

schema = dict(
  odbgp = (group_fn, ["odb_og_id", "ncbi_taxid", "og_name"]),
  og2gn = (og2gn_fn, ["odb_og_id", "odb_gene_id"]),
  gnxrf = (gnxrf_fn, ["odb_gene_id", "ext_id", "ext_db_name"]),
) 

schema_name = f"tmp_odb12v12_{unique_batch()}"

duckdb.execute(f"CREATE SCHEMA {schema_name}")

for tn, (fn, headers) in schema.items():
    create_str = f"CREATE TABLE {schema_name}.{tn} AS SELECT * FROM read_csv('{fn}', header=false, delim='\t', names={headers}, sample_size=1000)"
    duckdb.execute(create_str)

filter_str = f"CREATE TABLE {schema_name}.odbgp_filtered AS SELECT * FROM {schema_name}.odbgp WHERE odbgp.ncbi_taxid IN (2, 2157, 2759, 10239)"
duckdb.execute(filter_str)

db = duckdb.connect(':default:')

query = f"""
  SELECT gnxrf.ext_id AS 'uniprot_accession',
         odbgp_filtered.odb_og_id AS 'odb_group_id',
         odbgp_filtered.ncbi_taxid AS 'odb_group_level_ncbi_taxid',
         odbgp_filtered.og_name AS 'odb_group_name'
    FROM {schema_name}.og2gn
    JOIN {schema_name}.odbgp_filtered ON odbgp_filtered.odb_og_id = og2gn.odb_og_id
    JOIN {schema_name}.gnxrf ON og2gn.odb_gene_id = gnxrf.odb_gene_id AND gnxrf.ext_db_name = 'UniProt'
"""

rows = db.execute(query).fetchdf().to_dict('records')
OrthoDBUniProtGroupTable.write_tsv(str(Defaults.tangle_dir() / "odb_uniprot_groups.tsv"), rows)
