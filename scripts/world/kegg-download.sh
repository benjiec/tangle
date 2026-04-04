if [ ! -f "$TANGLE_WORLD/tangle/ko.tsv" ]; then
    echo "Fetching KO list"
    curl https://rest.kegg.jp/list/ko -o /tmp/ko.txt.$$
    echo "Ortholog ID\tOrtholog Name" | cat - /tmp/ko.txt.$$ > $TANGLE_WORLD/tangle/ko.tsv
    rm -f /tmp/ko.txt.$$
fi

if [ ! -f "$TANGLE_WORLD/tangle/kegg_modules.tsv" ]; then
    echo "Fetching KEGG module list"
    curl https://rest.kegg.jp/list/module -o /tmp/kegg_modules.txt.$$
    echo "Module ID\tModule Name" | cat - /tmp/kegg_modules.txt.$$ > $TANGLE_WORLD/tangle/kegg_modules.tsv
    rm -f /tmp/kegg_modules.txt.$$
fi

if [ ! -f "$TANGLE_WORLD/tangle/kegg_module_defs.csv" ]; then
    echo "Downloading KEGG module definitions"
    python3 scripts/world/kegg-download-module-defs.py
fi
