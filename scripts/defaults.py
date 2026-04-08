import os
from pathlib import Path
from tangle.defaults import PathDefaultsBase, validate_path_exists


class Defaults(PathDefaultsBase):

    @staticmethod
    def world_dir():
        world = os.environ.get('TANGLE_WORLD')
        assert world is not None
        return Path(world)

    @staticmethod
    def tangle_dir():
        return Defaults.world_dir() / "tangle"

    @staticmethod
    def ncbi_download_dir():
        return Defaults.world_dir() / "ncbi"

    @staticmethod
    def ncbi_downloaded_data_dir():
        return Defaults.ncbi_download_dir() / "ncbi_dataset/data"

    @staticmethod
    def ncbi_genome_dir(genome_accession):
        return Defaults.ncbi_downloaded_data_dir() / genome_accession

    @validate_path_exists
    @staticmethod
    def ncbi_genome_proteins_path(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "protein.faa"

    @validate_path_exists
    @staticmethod
    def ncbi_genome_proteins(genome_accession):
        return Defaults.ncbi_genome_proteins_path(genome_accession)

    @staticmethod
    def ncbi_genome_gff_path(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "genomic.gff"

    @validate_path_exists
    @staticmethod
    def ncbi_genome_gff(genome_accession):
        return Defaults.ncbi_genome_gff_path(genome_accession)

    @staticmethod
    def ncbi_genome_fna_path(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "genomic.fna"

    @validate_path_exists
    @staticmethod
    def ncbi_genome_fna(genome_accession):
        return Defaults.ncbi_genome_fna_path(genome_accession)

    @staticmethod
    def kegg_module_list_tsv():
        return Defaults.tangle_dir() / "kegg_modules.tsv"

    @staticmethod
    def kegg_module_def_csv():
        return Defaults.tangle_dir() / "kegg_module_defs.csv"

    @staticmethod
    def areas_dir():
        return Defaults.world_dir() / "areas"

    @staticmethod
    def area_dir():
        area = os.environ.get('TANGLE_AREA')
        assert area is not None
        return Defaults.areas_dir() / area

    @staticmethod
    def area_metadata_dir():
        return Defaults.area_dir() / "metadata"

    @staticmethod
    def area_genomes():
        return Defaults.area_dir() / "genomes.csv"

    @staticmethod
    def area_genome_taxon_tsv():
        return Defaults.area_metadata_dir() / "genomes.tsv"

    @staticmethod
    def area_genomics_dir():
        return Defaults.area_dir() / "genomics"

    @staticmethod
    def area_sequence_manifest_tsv():
        return Defaults.area_genomics_dir() / "sequences.tsv"

    @staticmethod
    def area_detected_proteins_tsv_path(genome_accession):
        return (Defaults.area_genomics_dir() / genome_accession) / "proteins.tsv"

    @staticmethod
    def area_detected_proteins_path(genome_accession):
        return (Defaults.area_genomics_dir() / genome_accession) / "proteins.faa"

    @validate_path_exists
    @staticmethod
    def area_detected_proteins(genome_accession):
        return Defaults.area_detected_proteins_path(genome_accession)

    @staticmethod
    def area_protein_pfam_tsv():
        return Defaults.area_genomics_dir() / "protein_pfam.tsv"

    @staticmethod
    def area_protein_ko_assigned_tsv():
        return Defaults.area_genomics_dir() / "protein_ko_assigned.tsv"


if __name__ == "__main__":
    Defaults.main(Defaults)
