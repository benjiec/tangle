tsv_files = [
  dict(filename="kegg_module_defs.csv", tablename="kegg_module_definitions", has_headers=True, delimiter=',',
       schema="module_id:STRING,step:INT64,step_option:INT64,step_option_component:INT64,sub_step:INT64,sub_step_option:INT64,sub_step_option_component:INT64,sub_sub_step:INT64,sub_sub_step_option:INT64,sub_sub_step_option_component:INT64,essential:INT64,ortholog_id:STRING"),
  dict(filename="kegg_modules.tsv", tablename="kegg_modules", has_headers=True, delimiter='\t',
       schema="module_id:STRING,module_name:STRING"),
  dict(filename="ko.tsv", tablename="kegg_orthologs", has_headers=True, delimiter='\t',
       schema="ortholog_id:STRING,ortholog_name:STRING"),
  dict(filename="pfam_go.tsv", tablename="pfam_go", has_headers=True, delimiter='\t',
       schema="pfam_accession:STRING,go_id:STRING,go_description:STRING"),
  dict(filename="Pfam-A.clans.tsv", tablename="pfam_domains", has_headers=False, delimiter='\t',
       schema="pfam_accession:STRING,clan_accession:STRING,clan_short_name:STRING,pfam_short_name:STRING,pfam_description:STRING"),
]

if __name__ == "__main__":
    import os
    import subprocess

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-name", required=True)
    args = ap.parse_args()

    gc_assets = os.environ.get('TANGLE_GCLOUD_ASSETS')
    gc_area = os.environ.get('TANGLE_GCLOUD_AREA')

    if gc_assets is None:
        raise Exception("Please set TANGLE_GCLOUD_ASSETS to point to where asset files are located")

    for entry in tsv_files:
        cmd = ["bq", "load",
               "--replace",
               "--source_format=CSV",
               f"--field_delimiter={entry['delimiter']}"]

        if entry["has_headers"]:
            cmd.append("--skip_leading_rows=1")

        cmd.extend([
            f"{args.dataset_name}.{entry['tablename']}",
            f"{gc_assets}/{entry['filename']}",
            entry['schema']
        ])

        print(" \\\n  ".join(cmd))
        subprocess.run(cmd)
