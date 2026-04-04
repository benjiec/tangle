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
        return Defaults.world_dir() / "ncbi-downloads/ncbi_dataset/data"

    @staticmethod
    def ncbi_genome_dir(genome_accession):
        return Defaults.ncbi_download_dir() / genome_accession

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
    def area_dir():
        area = os.environ.get('TANGLE_AREA')
        assert area is not None
        return Path(area)
