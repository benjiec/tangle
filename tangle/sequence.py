from . import open_file_to_read, open_file_to_write
from Bio.Seq import Seq
from typing import Optional


def read_fasta_as_dict(path, preserve_full_accession=False):
    sequences_by_accession = {}
    current_acc = None
    current_seq_parts = []

    with open_file_to_read(path) as f:
        for raw_line in f:
            if not raw_line:
                continue
            line = raw_line.rstrip("\n")
            if not line:
                continue
            if line.startswith(">"):
                # Flush previous
                if current_acc is not None:
                    sequences_by_accession[current_acc] = "".join(current_seq_parts)
                header_content = line[1:].strip()
                if preserve_full_accession:
                    accession = header_content
                else:
                    # accession is the first whitespace-delimited token
                    accession = header_content.split(None, 1)[0]
                current_acc = accession
                current_seq_parts = []
            else:
                current_seq_parts.append(line.strip())
        # Flush final
        if current_acc is not None:
            sequences_by_accession[current_acc] = "".join(current_seq_parts)

    return sequences_by_accession


def write_fasta_from_dict(fasta_dict, path, append = False):
    mode = "wt"
    if append is True:
        mode = "at"

    with open_file_to_write(path, mode) as f:
        for k,v in fasta_dict.items():
            f.write(f">{k}\n{v}\n")


def extract_subsequence(full_sequence: Optional[str], start_1_based: int, end_1_based: int) -> Optional[str]:
    if full_sequence is None:
        return None
    if start_1_based <= 0 or end_1_based <= 0:
        return None
    # coordinates are 1-based inclusive; order can be reversed depending on alignment direction
    left = min(start_1_based, end_1_based)
    right = max(start_1_based, end_1_based)
    if left > len(full_sequence):
        return None
    # slice is exclusive of end; adjust for 1-based inclusive
    return full_sequence[left - 1 : min(right, len(full_sequence))]


def extract_subsequence_strand_sensitive(full_sequence: Optional[str], start_1_based: int, end_1_based: int) -> Optional[str]:
    subs = extract_subsequence(full_sequence, start_1_based, end_1_based)
    if start_1_based > end_1_based:
        return str(Seq(subs).reverse_complement())
    return subs


def compute_three_frame_translations(full_seq, start, end):
    target_sequence = extract_subsequence_strand_sensitive(full_seq, start, end)
    if target_sequence is None:
        print("Cannot extract sequence using", len(full_seq), start, end)

    translations = []
    for frame in range(3):
        trim_right = (len(target_sequence)-frame)%3
        if trim_right > 0:
          frame_sequence = target_sequence[frame:-trim_right]
        else:
          frame_sequence = target_sequence[frame:]
        assert len(frame_sequence) % 3 == 0
        aa = Seq(frame_sequence).translate(to_stop=False) # Translate entire sequence, including stops

        if end > start:  # fwd strand
            translations.append((start+frame, end-trim_right, str(aa)))
        else:  # rev strand
            translations.append((start-frame, end+trim_right, str(aa)))

    return translations
