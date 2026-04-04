import argparse
from scripts.defaults import Defaults
from tangle.genomes import GenomeAccessionList
from tangle.models import CSVSource


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--detect", action="store_true", default=False)
    parser.add_argument("-n", "--ncbi", action="store_true", default=False)
    args = parser.parse_args()

    area_genomes_fn = Defaults.area_genomes()
    source = CSVSource(GenomeAccessionList, area_genomes_fn)

    filters = []
    if args.detect:
        filters.append("run_protein_detection == 1")
    if args.ncbi:
        filters.append("use_ncbi_proteins == 1")

    accessions = source.values(column_filters=filters, just="genome_accession")
    print("\n".join(accessions))
