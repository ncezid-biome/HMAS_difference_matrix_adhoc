#!/usr/bin/env python3

import argparse
import glob
from pathlib import Path
from collections import defaultdict
from Bio import SeqIO
import utilities
import hashlib


# -------------------------------
# Hashing logic (unchanged)
# -------------------------------

def hash_sequence(sequence: str) -> str:
    md5 = hashlib.md5(sequence.encode("utf-8"))
    max_bits_in_result = 56
    p = (1 << max_bits_in_result) - 1
    rest = int(md5.hexdigest(), 16)
    result = 0
    while rest != 0:
        result = result ^ (rest & p)
        rest = rest >> max_bits_in_result
    return str(result)


hash_cache = {}

def get_hash(seq):
    seq_str = str(seq)
    if seq_str not in hash_cache:
        hash_cache[seq_str] = hash_sequence(seq_str)
    return hash_cache[seq_str]


# -------------------------------
# Reverse complement cache (unchanged)
# -------------------------------

revcomp_cache = {}

def revcomp_cached(seq):
    seq_upper = seq.upper()
    if seq_upper not in revcomp_cache:
        revcomp_cache[seq_upper] = utilities.revcomp(seq_upper)
    return revcomp_cache[seq_upper]


# -------------------------------
# Sequence comparison (unchanged)
# -------------------------------

def check_diff_by_primer(seq1, seq2):
    seq1 = str(seq1).upper()
    seq2 = str(seq2).upper()

    if len(seq1) > 40:
        h1 = get_hash(seq1)
        h2 = get_hash(seq2)
        h2_rc = get_hash(revcomp_cached(seq2))
        return not (h1 == h2 or h1 == h2_rc)
        #return not (h1 == h2)
    else:
        return not (seq1 == seq2 or seq1 == revcomp_cached(seq2))


# -------------------------------
# NEW: Select most abundant sequence
# -------------------------------

def select_most_abundant(records):
    """
    Select the most abundant sequence from a list of records.
    If abundance ties, return the first among tied records.
    Abundance is parsed from 'size=NUMBER' in FASTA description.
    If not found, default abundance = 1.
    """
    if not records:
        return None

    max_count = -1
    selected_record = None

    for rec in records:
        abundance = 1  # default

        desc = rec.description
        if "size=" in desc:
            try:
                abundance = int(desc.split("size=")[1].split()[0])
            except Exception:
                abundance = 1

        if abundance > max_count:
            max_count = abundance
            selected_record = rec

    return selected_record


# -------------------------------
# Comparison logic (updated)
# -------------------------------

def compare(query_idx, target_idx, primer_list, numeric_flag, diff_only):
    diff_count = 0
    total_primer = 0

    for primer in primer_list:
        query_recs = query_idx.get(primer, [])
        target_recs = target_idx.get(primer, [])

        if not query_recs or not target_recs:
            continue  # skip if missing on either side

        # NEW behavior: select most abundant record
        query_rec = select_most_abundant(query_recs)
        target_rec = select_most_abundant(target_recs)

        if query_rec is None or target_rec is None:
            continue

        total_primer += 1

        if check_diff_by_primer(query_rec.seq, target_rec.seq):
            diff_count += 1

    if total_primer == 0:
        return "NA"

    if numeric_flag:
        return diff_count / total_primer
    elif diff_only:
        return diff_count
    else:
        return f"{diff_count}/{total_primer}"


# -------------------------------
# Primer indexing (unchanged)
# -------------------------------

def build_primer_index(fasta_file, primer_list):
    primer_idx = defaultdict(list)

    for record in SeqIO.parse(fasta_file, 'fasta'):
        for primer in primer_list:
            if primer in record.id:
                primer_idx[primer].append(record)
                break

    return primer_idx


# -------------------------------
# Main
# -------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True, help='Query fasta file')
    parser.add_argument('--all', required=True, help='Folder for all fasta files')
    parser.add_argument('--primers', required=True, help='Oligos file')
    parser.add_argument('--output', required=True, help='Output row file')
    parser.add_argument('--numeric', action='store_true')
    parser.add_argument('--diff_only', action='store_true')
    args = parser.parse_args()

    primers = utilities.Primers(args.primers)
    primer_list = primers.pnames

    query_name = Path(args.query).stem
    query_idx = build_primer_index(args.query, primer_list)

    all_fastas = sorted(glob.glob(f'{args.all}/**/*.fasta', recursive=True))
    all_indexes = [(Path(f).stem, build_primer_index(f, primer_list)) for f in all_fastas]

    row = [query_name]

    for sample_name, target_idx in all_indexes:
        result = compare(query_idx, target_idx, primer_list,
                         args.numeric, args.diff_only)
        row.append(str(result))

    with open(args.output, 'w') as f:
        f.write(','.join(row) + '\n')


if __name__ == '__main__':
    main()
