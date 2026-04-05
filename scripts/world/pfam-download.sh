if [ ! -f "$TANGLE_WORLD/tangle/Pfam-A.clans.tsv" ]; then
    echo "Fetching Pfam-A.clans"
    curl https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz -o $TANGLE_WORLD/tangle/Pfam-A.clans.tsv.gz
    gunzip $TANGLE_WORLD/tangle/Pfam-A.clans.tsv.gz
fi

if [ ! -f "$TANGLE_WORLD/tangle/pfam_go.tsv" ]; then
    echo "Downloading Pfam to GO mapping table"
    curl https://current.geneontology.org/ontology/external2go/pfam2go -o /tmp/pfam_go.txt.$$
    python3 scripts/world/parse-pfam-go.py /tmp/pfam_go.txt.$$ $TANGLE_WORLD/tangle/pfam_go.tsv
fi
