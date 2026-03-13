#!/usr/bin/env python3

# import argparse
# import glob
# from pathlib import Path
# from collections import defaultdict
# from Bio import SeqIO
# import utilities
# import hashlib

# # -------------------------------
# # Hashing logic (unchanged)
# # -------------------------------

# def hash_sequence(sequence: str) -> str:
#     md5 = hashlib.md5(sequence.encode("utf-8"))
#     max_bits_in_result = 56
#     p = (1 << max_bits_in_result) - 1
#     rest = int(md5.hexdigest(), 16)
#     result = 0
#     while rest != 0:
#         result = result ^ (rest & p)
#         rest = rest >> max_bits_in_result
#     return str(result)

# hash_cache = {}

# def get_hash(seq):
#     seq_str = str(seq)
#     if seq_str not in hash_cache:
#         hash_cache[seq_str] = hash_sequence(seq_str)
#     return hash_cache[seq_str]

# # -------------------------------
# # Reverse complement cache (unchanged)
# # -------------------------------

# revcomp_cache = {}

# def revcomp_cached(seq):
#     seq_upper = seq.upper()
#     if seq_upper not in revcomp_cache:
#         revcomp_cache[seq_upper] = utilities.revcomp(seq_upper)
#     return revcomp_cache[seq_upper]

# # -------------------------------
# # Sequence comparison (unchanged)
# # -------------------------------

# def check_diff_by_primer(seq1, seq2):
#     seq1 = str(seq1).upper()
#     seq2 = str(seq2).upper()

#     if len(seq1) > 40:
#         h1 = get_hash(seq1)
#         h2 = get_hash(seq2)
#         h2_rc = get_hash(revcomp_cached(seq2))
#         return not (h1 == h2 or h1 == h2_rc)
#     else:
#         return not (seq1 == seq2 or seq1 == revcomp_cached(seq2))

# # -------------------------------
# # Select most abundant (kept for reference)
# # -------------------------------

# def select_most_abundant(records):
#     if not records:
#         return None

#     max_count = -1
#     selected_record = None

#     for rec in records:
#         abundance = 1
#         desc = rec.description
#         if "size=" in desc:
#             try:
#                 abundance = int(desc.split("size=")[1].split()[0])
#             except Exception:
#                 abundance = 1

#         if abundance > max_count:
#             max_count = abundance
#             selected_record = rec

#     return selected_record

# # -------------------------------
# # Comparison logic (updated)
# # -------------------------------

# # def compare(query_idx, target_idx, primer_list, numeric_flag, diff_only):
# #     diff_count = 0
# #     total_primer = 0
# #     matched_primers = 0
# #     total_unique_match_occurrences = 0

# #     for primer in primer_list:
# #         query_recs = query_idx.get(primer, [])
# #         target_recs = target_idx.get(primer, [])

# #         if not query_recs or not target_recs:
# #             continue

# #         total_primer += 1

# #         # Get most abundant sequences (reference match)
# #         query_main = select_most_abundant(query_recs)
# #         target_main = select_most_abundant(target_recs)

# #         main_matches = False
# #         if query_main and target_main:
# #             main_matches = not check_diff_by_primer(query_main.seq, target_main.seq)

# #         # Build hash sets for all sequences (including reverse complement)
# #         query_hashes = set()
# #         for rec in query_recs:
# #             seq = str(rec.seq).upper()
# #             query_hashes.add(get_hash(seq))
# #             query_hashes.add(get_hash(revcomp_cached(seq)))

# #         target_hashes = set()
# #         for rec in target_recs:
# #             seq = str(rec.seq).upper()
# #             target_hashes.add(get_hash(seq))
# #             target_hashes.add(get_hash(revcomp_cached(seq)))

# #         # Unique matching sequences
# #         matches = query_hashes.intersection(target_hashes)
# #         unique_match_count = len(matches)

# #         # Determine diff vs match
# #         if main_matches:
# #             # Most abundant sequence matched — diff_count does not increase
# #             # Count only additional matches from other sequences
# #             if unique_match_count > 1:
# #                 # At least one other sequence contributed
# #                 matched_primers += 1
# #                 total_unique_match_occurrences += (unique_match_count - 1)
# #         else:
# #             if unique_match_count > 0:
# #                 # No main match but other sequences matched
# #                 matched_primers += 1
# #                 total_unique_match_occurrences += unique_match_count
# #             else:
# #                 # No matches at all
# #                 diff_count += 1

# #     if total_primer == 0:
# #         return "NA"

# #     if numeric_flag:
# #         return diff_count / total_primer
# #     elif diff_only:
# #         return diff_count
# #     else:
# #         return f"{diff_count}/{total_primer}|{matched_primers}/{total_unique_match_occurrences}"



# def compare(query_idx, target_idx, primer_list, numeric_flag, diff_only):
#     diff_count = 0
#     total_primer = 0
#     matched_primers = 0
#     total_unique_match_occurrences = 0

#     for primer in primer_list:
#         query_recs = query_idx.get(primer, [])
#         target_recs = target_idx.get(primer, [])

#         if not query_recs or not target_recs:
#             continue

#         total_primer += 1

#         # Most abundant sequence
#         query_main = select_most_abundant(query_recs)
#         target_main = select_most_abundant(target_recs)

#         main_hashes = set()
#         if query_main and target_main:
#             main_hashes.add(get_hash(str(query_main.seq).upper()))
#             main_hashes.add(get_hash(revcomp_cached(str(query_main.seq).upper())))
#             main_matches = not check_diff_by_primer(query_main.seq, target_main.seq)
#         else:
#             main_matches = False

#         # All sequences (query + target)
#         query_hashes = set(get_hash(str(rec.seq).upper()) for rec in query_recs)
#         query_hashes.update(get_hash(revcomp_cached(str(rec.seq).upper())) for rec in query_recs)

#         target_hashes = set(get_hash(str(rec.seq).upper()) for rec in target_recs)
#         target_hashes.update(get_hash(revcomp_cached(str(rec.seq).upper())) for rec in target_recs)

#         # All unique matching sequences
#         matches = query_hashes.intersection(target_hashes)

#         # Only count bonus matches (exclude main sequence)
#         bonus_matches = matches - main_hashes if main_matches else matches

#         if main_matches:
#             # main matched, count bonus only
#             if bonus_matches:
#                 matched_primers += 1
#                 total_unique_match_occurrences += len(bonus_matches)
#         else:
#             # main did not match
#             if matches:
#                 matched_primers += 1
#                 total_unique_match_occurrences += len(matches)
#             else:
#                 diff_count += 1

#     if total_primer == 0:
#         return "NA"

#     if numeric_flag:
#         return diff_count / total_primer
#     elif diff_only:
#         return diff_count
#     else:
#         return f"{diff_count}/{total_primer}|{matched_primers}/{total_unique_match_occurrences}"




# # -------------------------------
# # Primer indexing (unchanged)
# # -------------------------------

# def build_primer_index(fasta_file, primer_list):
#     primer_idx = defaultdict(list)
#     for record in SeqIO.parse(fasta_file, 'fasta'):
#         for primer in primer_list:
#             if primer in record.id:
#                 primer_idx[primer].append(record)
#                 break
#     return primer_idx

# # -------------------------------
# # Main
# # -------------------------------

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--query', required=True, help='Query fasta file')
#     parser.add_argument('--all', required=True, help='Folder for all fasta files')
#     parser.add_argument('--primers', required=True, help='Oligos file')
#     parser.add_argument('--output', required=True, help='Output row file')
#     parser.add_argument('--numeric', action='store_true')
#     parser.add_argument('--diff_only', action='store_true')
#     args = parser.parse_args()

#     primers = utilities.Primers(args.primers)
#     primer_list = primers.pnames

#     query_name = Path(args.query).stem
#     query_idx = build_primer_index(args.query, primer_list)

#     all_fastas = sorted(glob.glob(f'{args.all}/**/*.fasta', recursive=True))
#     all_indexes = [(Path(f).stem, build_primer_index(f, primer_list)) for f in all_fastas]

#     row = [query_name]

#     for sample_name, target_idx in all_indexes:
#         result = compare(query_idx, target_idx, primer_list,
#                          args.numeric, args.diff_only)
#         row.append(str(result))

#     with open(args.output, 'w') as f:
#         f.write(','.join(row) + '\n')

# if __name__ == '__main__':
#     main()










import argparse
import glob
from pathlib import Path
from collections import defaultdict
from Bio import SeqIO
import utilities
import hashlib

# -------------------------------
# Hashing (unchanged folding)
# -------------------------------

def hash_sequence(sequence: str) -> str:
    md5 = hashlib.md5(sequence.encode("utf-8"))
    max_bits_in_result = 56
    p = (1 << max_bits_in_result) - 1
    rest = int(md5.hexdigest(), 16)
    result = 0
    while rest != 0:
        result ^= (rest & p)
        rest >>= max_bits_in_result
    return str(result)

hash_cache = {}

def get_hash(seq):
    if seq not in hash_cache:
        hash_cache[seq] = hash_sequence(seq)
    return hash_cache[seq]

# -------------------------------
# Reverse complement cache
# -------------------------------

revcomp_cache = {}

def revcomp_cached(seq):
    if seq not in revcomp_cache:
        revcomp_cache[seq] = utilities.revcomp(seq)
    return revcomp_cache[seq]

# -------------------------------
# Canonical representation
# -------------------------------

def canonical_seq(seq):
    seq = seq.upper()
    rc = revcomp_cached(seq)
    return min(seq, rc)

# -------------------------------
# Select most abundant
# -------------------------------

def select_most_abundant(records):
    max_count = -1
    selected = None

    for rec in records:
        abundance = 1
        desc = rec.description
        if "size=" in desc:
            try:
                abundance = int(desc.split("size=")[1].split()[0])
            except Exception:
                abundance = 1

        if abundance > max_count:
            max_count = abundance
            selected = rec

    return selected

# -------------------------------
# Comparison logic
# -------------------------------

def compare(query_idx, target_idx, primer_list, numeric_flag, diff_only, sample_name, debug_primer=None):

    diff_count = 0
    total_primer = 0

    rescued_primers = 0
    rescued_occ = 0

    extra_primers = 0
    extra_occ = 0

    for primer in primer_list:

        if debug_primer and primer != debug_primer:
            continue

        query_recs = query_idx.get(primer, [])
        target_recs = target_idx.get(primer, [])

        if not query_recs or not target_recs:
            continue

        total_primer += 1

        # ---- Most abundant sequences
        q_main = select_most_abundant(query_recs)
        t_main = select_most_abundant(target_recs)

        main_match = False
        if q_main and t_main:
            q_can = canonical_seq(str(q_main.seq))
            t_can = canonical_seq(str(t_main.seq))
            main_match = (q_can == t_can)

        # ---- Build canonical hash sets (ALL sequences)
        q_hashes = set()
        for rec in query_recs:
            can = canonical_seq(str(rec.seq))
            q_hashes.add(get_hash(can))

        t_hashes = set()
        for rec in target_recs:
            can = canonical_seq(str(rec.seq))
            t_hashes.add(get_hash(can))

        matches = q_hashes.intersection(t_hashes)

        # Remove dominant sequence from bonus calculation if matched
        if main_match:
            main_hash = get_hash(canonical_seq(str(q_main.seq)))
            bonus_hashes = matches - {main_hash}
        else:
            bonus_hashes = matches

        # ---- Classification
        if not matches:
            diff_count += 1

        elif not main_match and matches:
            rescued_primers += 1
            rescued_occ += len(bonus_hashes)

        elif main_match and bonus_hashes:
            extra_primers += 1
            extra_occ += len(bonus_hashes)

        # ---- Debug printing
        if debug_primer:
            print(f"\nPrimer: {primer}")
            print(f"Sample: {sample_name}")
            print(f"Main match: {main_match}")
            print(f"Total matches: {len(matches)}")
            print(f"Bonus matches: {len(bonus_hashes)}")

    if total_primer == 0:
        return "NA"

    if numeric_flag:
        return diff_count / total_primer
    elif diff_only:
        return diff_count
    else:
        return f"{diff_count}/{total_primer}|{rescued_primers}/{rescued_occ}|{extra_primers}/{extra_occ}"

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
    parser.add_argument('--query', required=True)
    parser.add_argument('--all', required=True)
    parser.add_argument('--primers', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--numeric', action='store_true')
    parser.add_argument('--diff_only', action='store_true')
    parser.add_argument('--debug_primer', help="Optional: inspect one primer only")
    args = parser.parse_args()

    primers = utilities.Primers(args.primers)
    primer_list = primers.pnames

    query_name = Path(args.query).stem
    query_idx = build_primer_index(args.query, primer_list)

    all_fastas = sorted(glob.glob(f'{args.all}/**/*.fasta', recursive=True))
    all_indexes = [(Path(f).stem, build_primer_index(f, primer_list)) for f in all_fastas]

    row = [query_name]

    for sample_name, target_idx in all_indexes:
        result = compare(
            query_idx,
            target_idx,
            primer_list,
            args.numeric,
            args.diff_only,
            sample_name,
            args.debug_primer
        )
        row.append(str(result))

    with open(args.output, 'w') as f:
        f.write(','.join(row) + '\n')

if __name__ == '__main__':
    main()
