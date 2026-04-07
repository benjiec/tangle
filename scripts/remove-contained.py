# remove duplicated entries based on sequence

import ahocorasick

def filter_contained_sequences(data_dict):
    # deduplicate exact strings first to reduce trie size
    unique_to_keys = {}
    for k, v in data_dict.items():
        if v not in unique_to_keys:
            unique_to_keys[v] = k

    sorted_items = sorted(
      unique_to_keys.items(),
      key=lambda x: len(x[0]), reverse=True
    )

    # build the automaton with all unique sequences
    automaton = ahocorasick.Automaton()
    for seq, key in sorted_items:
        automaton.add_word(seq, (key, seq))
    automaton.make_automaton()
    print("done making automaton")

    # XXX build concept of locus, from rows, acc:locus
    # XXX build contained_locus check

    to_remove = set()
    for seq, key in sorted_items:
        if key in to_remove:
            continue

        # search 'seq' against the automaton to find any internal patterns
        for end_index, (found_contained_key, found_contained_seq) in automaton.iter(seq):
            # if the found pattern is not the string itself, it's a contained sequence
            if found_contained_key != key:

                # XXX and contained_in_locus

                to_remove.add(found_contained_key)

    # 4. Return dictionary excluding the contained keys
    return {k: v for k, v in data_dict.items() if k in unique_to_keys.values() and k not in to_remove}


if __name__ == "__main__":
    import argparse
    from tangle.sequence import read_fasta_as_dict, write_fasta_from_dict
    from tangle.models import CSVSource
    from tangle.detected import DetectedTable

    ap = argparse.ArgumentParser()
    ap.add_argument("tsv_fn")
    ap.add_argument("fasta_fn")
    ap.add_argument("filtered_tsv_fn")
    ap.add_argument("filtered_fasta_fn")

    args = ap.parse_args()

    source = CSVSource(DetectedTable, args.tsv_fn)
    rows = source.values()
    protein_sequences = read_fasta_as_dict(args.fasta_fn)

    filtered = filter_contained_sequences(protein_sequences)
    print("filtered from", len(protein_sequences), "to", len(filtered))

    write_fasta_from_dict(filtered, args.filtered_fasta_fn)
    filtered_rows = [row for row in rows if row["target_accession"] in filtered]
    DetectedTable.write_tsv(args.filtered_tsv_fn, filtered_rows)
