if [ ! -d "$TANGLE_WORLD/tangle/odb12v2/" ]; then
  mkdir $TANGLE_WORLD/tangle/odb12v2
  # curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_genes.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_genes.tab.gz
  # curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_levels.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_levels.tab.gz
  # curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_OG_xrefs.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_OG_xrefs.tab.gz
  curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_OG2genes.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_OG2genes.tab.gz
  curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_OGs.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_OGs.tab.gz
  curl https://data.orthodb.org/odb12v2/download/odb_data_dump/odb12v2_gene_xrefs.tab.gz -o $TANGLE_WORLD/tangle/odb12v2/odb12v2_gene_xrefs.tab.gz

  zgrep "UniProt" $TANGLE_WORLD/tangle/odb12v2/odb12v2_gene_xrefs.tab.gz > $TANGLE_WORLD/tangle/odb12v2/odb12v2_gene_xrefs.tab.uniprot
  gzip $TANGLE_WORLD/tangle/odb12v2/odb12v2_gene_xrefs.tab.uniprot
fi
