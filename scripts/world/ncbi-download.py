import os
import sys
import csv
import glob
import shutil
import subprocess
import zipfile
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import time
from scripts.defaults import Defaults


BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/accession"

FILE_TYPE_PATTERNS = {
    "GENOME_FASTA": "genomic.fna",
    "PROT_FASTA": "protein.faa",
    "GENOME_GFF": "genomic.gff"
}


def rename_genomic_file(target_dir: str, new_name: str = "genomic.fna"):
    base_path = Path(target_dir)

    if not base_path.is_dir():
        raise NotADirectoryError(f"Target path is invalid: {target_dir}")

    # Use a generator to avoid loading entire directory into memory
    fna_files = base_path.glob("*.fna")
    
    try:
        target_file = next(fna_files)
    except StopIteration:
        print(f"No *.fna files found in {target_dir}")
        return

    # Construct new path and execute rename
    destination = target_file.with_name(new_name)
    
    if destination.exists():
        print(f"Collision detected: {destination} already exists. Aborting.")
        return

    target_file.rename(destination)


def download_and_extract_by_accession(accession: str, cache_dir: str) -> str:
    """
    Downloads and extracts all file types for a given accession to a cache directory.
    
    This function implements the same directory structure as scripts/ncbi-download.sh:
    cache_dir/
    └── ncbi_dataset/
        └── data/
            ├── dataset_catalog.json
            ├── assembly_data_report.jsonl
            └── {accession}/
                ├── genomic.fna (GENOME_FASTA)
                ├── genomic.gff (GENOME_GFF)
                └── protein.faa (PROT_FASTA)
    
    Args:
        accession: The NCBI genome accession (e.g., 'GCA_000507305.1')
        cache_dir: The cache directory that follows the ncbi-downloads structure
        
    Returns:
        Path to the extracted accession directory in the cache
        
    Raises:
        Exception: If download or extraction fails
    """
    # Create cache directory structure
    cache_data_dir = os.path.join(cache_dir, "ncbi_dataset", "data")
    accession_cache_dir = os.path.join(cache_data_dir, accession)
    
    # Check if files already exist in cache
    if os.path.exists(accession_cache_dir):
        # Only check if GENOME_FASTA pattern exists - this is the main file we need
        genome_pattern = FILE_TYPE_PATTERNS["GENOME_FASTA"]
        genome_files = glob.glob(os.path.join(accession_cache_dir, genome_pattern))
        if genome_files:
            return accession_cache_dir

    # Download all file types by concatenating the keys from the mapping
    annotation_types = ",".join(FILE_TYPE_PATTERNS.keys())
    url = f"{BASE_URL}/{accession}/download?include_annotation_type={annotation_types}"
    
    # Create temporary directories
    os.makedirs(cache_dir, exist_ok=True)
    temp_zip = os.path.join(cache_dir, f"{accession}.zip")
    temp_extract_dir = os.path.join(cache_dir, accession)

    try:
        # Download the zip file
        print(f"Downloading {accession} from NCBI...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(temp_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        print(f"Extracting {accession}...")
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        
        # Create the cache directory structure
        os.makedirs(cache_data_dir, exist_ok=True)
        
        # Move the accession directory to the flattened location
        if os.path.exists(accession_cache_dir):
            shutil.rmtree(accession_cache_dir)

        # Find the nested accession directory
        nested_accession_dir = os.path.join(temp_extract_dir, "ncbi_dataset", "data", accession)
        if os.path.exists(nested_accession_dir):
            shutil.move(nested_accession_dir, accession_cache_dir)
        else:
            raise FileNotFoundError(f"Expected directory structure not found for {accession}")
       
        # Move the *.fna file to genomic.fna
        rename_genomic_file(accession_cache_dir)
 
        # Copy metadata files if they exist
        metadata_files = ["assembly_data_report.jsonl", "dataset_catalog.json"]
        for metadata_file in metadata_files:
            src_path = os.path.join(temp_extract_dir, "ncbi_dataset", "data", metadata_file)
            dst_path = os.path.join(cache_data_dir, metadata_file)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
        
        print(f"Successfully cached {accession}")
        return accession_cache_dir
        
    except Exception as e:
        # Clean up on failure
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
        if os.path.exists(accession_cache_dir):
            shutil.rmtree(accession_cache_dir, ignore_errors=True)
        raise e
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir, ignore_errors=True)


def print_status(message: str, level: str = "INFO"):
    """Print a timestamped status message with color coding."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Color codes for different levels
    colors = {
        "INFO": "\033[0;34m",    # Blue
        "SUCCESS": "\033[0;32m", # Green
        "WARNING": "\033[1;33m", # Yellow
        "ERROR": "\033[0;31m",   # Red
        "NC": "\033[0m"          # No Color
    }
    
    color = colors.get(level, colors["INFO"])
    print(f"{color}[{timestamp}] {message}{colors['NC']}")


def process_accession(accession: str, output_dir: str, delay: float = 1.0):
    """
    Process a single accession by downloading and extracting all file types.
    
    Args:
        accession: The NCBI genome accession
        output_dir: The output directory for downloads
        delay: Delay between requests in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print_status(f"Processing: {accession}", "INFO")
        
        # Use the coral/ncbi/download.py module
        cache_dir = download_and_extract_by_accession(accession, output_dir)
        
        if cache_dir and os.path.exists(cache_dir):
            print_status(f"Successfully processed: {accession}", "SUCCESS")
            return True
        else:
            print_status(f"Failed to process: {accession}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Error processing {accession}: {str(e)}", "ERROR")
        return False
    finally:
        # Apply delay if specified
        if delay > 0:
            time.sleep(delay)


def process_accession_file(accession_file: str, output_dir: str, delay: float = 1.0):
    """
    Process multiple accessions from a file.
    
    Args:
        accession_file: Path to file containing accessions
        output_dir: The output directory for downloads
        delay: Delay between requests in seconds
        
    Returns:
        tuple: (success_count, failed_count, total_count)
    """
    success_count = 0
    failed_count = 0
    total_count = 0
    
    try:
        with open(accession_file, 'r') as f:
            accessions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        total_count = len(accessions)
        print_status(f"Starting download of {total_count} genome(s)", "INFO")
        print_status(f"Output directory: {output_dir}", "INFO")
        print_status(f"Annotation types: {', '.join(FILE_TYPE_PATTERNS.keys())}", "INFO")
        print_status(f"Delay between requests: {delay}s", "INFO")
        
        for i, accession in enumerate(accessions, 1):
            print_status(f"[{i}/{total_count}] Processing: {accession}", "INFO")
            
            if process_accession(accession, output_dir, delay):
                success_count += 1
            else:
                failed_count += 1
                
    except FileNotFoundError:
        print_status(f"Error: Accession file '{accession_file}' not found", "ERROR")
        return 0, 0, 0
    except Exception as e:
        print_status(f"Error reading accession file: {str(e)}", "ERROR")
        return 0, 0, 0
    
    return success_count, failed_count, total_count


def process_single_accession(accession: str, output_dir: str, delay: float = 1.0):
    """
    Process a single accession.
    
    Args:
        accession: The NCBI genome accession
        output_dir: The output directory for downloads
        delay: Delay between requests in seconds
        
    Returns:
        tuple: (success_count, failed_count, total_count)
    """
    print_status(f"Starting download of 1 genome", "INFO")
    print_status(f"Output directory: {output_dir}", "INFO")
    print_status(f"Annotation types: {', '.join(FILE_TYPE_PATTERNS.keys())}", "INFO")
    print_status(f"Delay between requests: {delay}s", "INFO")
    
    success_count = 0
    failed_count = 0
    
    if process_accession(accession, output_dir, delay):
        success_count = 1
    else:
        failed_count = 1
    
    return success_count, failed_count, 1


def main():
    """Main function to handle command line arguments and execute downloads."""
    parser = argparse.ArgumentParser(
        description="Download NCBI genome datasets using the coral/ncbi/download.py module",
        add_help=False  # We'll handle help manually to match the bash script
    )
    
    parser.add_argument("-o", "--output", default=Defaults.ncbi_download_dir(),
                       help="Output directory (default: ncbi-downloads)")
    parser.add_argument("-d", "--delay", type=float, default=1.0,
                       help="Delay between requests in seconds (default: 1)")
    parser.add_argument("accession")

    # Parse known args first to check for help
    args = parser.parse_args()

    accession_arg = args.accession
    output_dir = args.output
    delay = args.delay
    
    # Create output directory
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print_status(f"Error: Could not create output directory '{output_dir}': {e}", "ERROR")
        sys.exit(1)
    
    # Process accessions
    if os.path.isfile(accession_arg):
        # Process as accession file
        success_count, failed_count, total_count = process_accession_file(
            accession_arg, output_dir, delay
        )
    else:
        # Process as single accession
        success_count, failed_count, total_count = process_single_accession(
            accession_arg, output_dir, delay
        )
    
    # Print summary
    print()
    print_status("=== DOWNLOAD SUMMARY ===", "INFO")
    print_status(f"Successful downloads: {success_count}", "SUCCESS")
    print_status(f"Failed downloads: {failed_count}", "ERROR")
    print_status(f"Total processed: {total_count}", "INFO")
    
    # List what was downloaded
    if success_count > 0:
        print()
        print_status(f"Files extracted to: {output_dir}/ncbi_dataset/data", "INFO")
        print_status("Each genome is in its own subdirectory:", "INFO")
        
        data_dir = os.path.join(output_dir, "ncbi_dataset", "data")
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    print(f"  {item}")
    
    # Exit with appropriate code
    if failed_count == 0:
        print_status("All downloads completed successfully!", "SUCCESS")
        sys.exit(0)
    else:
        print_status("Some downloads failed. Check the log above for details.", "WARNING")
        sys.exit(1)


if __name__ == "__main__":
    main()
