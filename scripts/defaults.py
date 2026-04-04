import os
from pathlib import Path


class Defaults(object):

    @staticmethod
    def world_dir():
        world = os.environ.get('TANGLE_WORLD')
        assert world is not None
        return Path(world)

    @staticmethod
    def ncbi_download_dir():
        return Defaults.world_dir() / "ncbi"

    @staticmethod
    def ncbi_downloaded_data_dir():
        return Defaults.ncbi_downloaded_data_dir() / "ncbi_dataset/data"

    @staticmethod
    def ncbi_genome_dir(genome_accession):
        return Defaults.ncbi_downloaded_data_dir() / genome_accession

    @staticmethod
    def ncbi_genome_protein_faa(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "protein.faa"

    @staticmethod
    def ncbi_genome_gff(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "genomic.gff"

    @staticmethod
    def ncbi_genome_fna(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "genomic.fna"

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
