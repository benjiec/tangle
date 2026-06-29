import os
import inspect
import argparse
import functools
from pathlib import Path
from tangle import open_file_to_read


class PathDefaultsBase(object):

    @staticmethod
    def main(cls):

        methods = {}
        for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue
            sig = inspect.signature(func)
            if len(sig.parameters) <= 1:
                methods[name] = func

        parser = argparse.ArgumentParser(description="Get default paths")
        parser.add_argument("-m", "--method", action="append", choices=methods.keys(), help="Method to execute")
        parser.add_argument("values", nargs='*', help="Zero or more values to pass to the method, each triggers one method call")
        parser.add_argument("-f", "--file", help="consider arguments as files that contain input values", action="store_true", default=False)

        args = parser.parse_args()

        if args.file:
            input_values = []
            for fn in args.values:
                with open_file_to_read(fn) as f:
                    for line in f:
                        input_values.append(line.strip())
        else:
            input_values = args.values

        for method in args.method:
            target_func = methods[method]
            if len(input_values) == 0:
                p = target_func()
                if p: print(p)
            for val in input_values:
                p = target_func(val)
                if p: print(p)


def validate_path_exists(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            return
        if Path(result).exists():
            return result
        return
    return wrapper


def maybe_gzipped(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            if Path(result).exists():
                return result
            if Path(str(result)+".gz").exists():
                return str(result)+".gz"
        return result
    return wrapper


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

    @maybe_gzipped
    @staticmethod
    def ncbi_genome_proteins_path(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "protein.faa"

    @validate_path_exists
    @staticmethod
    def ncbi_genome_proteins(genome_accession):
        return Defaults.ncbi_genome_proteins_path(genome_accession)

    @maybe_gzipped
    @staticmethod
    def ncbi_genome_gff_path(genome_accession):
        return Defaults.ncbi_genome_dir(genome_accession) / "genomic.gff"

    @validate_path_exists
    @staticmethod
    def ncbi_genome_gff(genome_accession):
        return Defaults.ncbi_genome_gff_path(genome_accession)

    @maybe_gzipped
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
    def area_experiments_dir():
        return Defaults.area_dir() / "experiments"

    @staticmethod
    def area_experiment(exp_id):
        return Defaults.area_experiments_dir() / exp_id

    @staticmethod
    def area_genome_taxon_tsv():
        return Defaults.area_metadata_dir() / "genomes.tsv"

    @staticmethod
    def area_genomics_dir():
        return Defaults.area_dir() / "genomics"

    @maybe_gzipped
    @staticmethod
    def area_sequence_manifest_tsv():
        return Defaults.area_genomics_dir() / "sequences.tsv"

    @maybe_gzipped
    @staticmethod
    def area_detected_proteins_tsv_path(genome_accession):
        return (Defaults.area_genomics_dir() / genome_accession) / "proteins.tsv"

    @maybe_gzipped
    @staticmethod
    def area_detected_proteins_path(genome_accession):
        return (Defaults.area_genomics_dir() / genome_accession) / "proteins.faa"

    @validate_path_exists
    @staticmethod
    def area_detected_proteins(genome_accession):
        return Defaults.area_detected_proteins_path(genome_accession)

    @maybe_gzipped
    @staticmethod
    def area_protein_pfam_tsv():
        return Defaults.area_genomics_dir() / "protein_pfam.tsv"

    @maybe_gzipped
    @staticmethod
    def area_protein_ko_assigned_tsv():
        return Defaults.area_genomics_dir() / "protein_ko_assigned.tsv"
