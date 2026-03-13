#!/usr/bin/env python3

'''
python link_fastas_by_prefix.py \
  --search-root /path/to/source_folder \
  --dest-dir /path/to/link_folder \
  --prefix-file prefixes.txt
'''

import argparse
from pathlib import Path

# ---- CONFIG ----
# FASTA_EXTENSIONS = ("final.unique.fasta",)   # add ".fa" if needed
# ----------------


def load_prefixes(prefix_file):
    return [
        line.strip()
        for line in prefix_file.read_text().splitlines()
        if line.strip()
    ]


def main(search_root, dest_dir, prefix_file):
    search_root = Path(search_root).resolve()
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    prefixes = load_prefixes(prefix_file)

    # Find matching subdirectories
    matching_dirs = [
        d for d in search_root.iterdir()
        if d.is_dir() and any(d.name.startswith(p) for p in prefixes)
    ]

    if not matching_dirs:
        print("No matching directories found.")
        return

    print(f"Found {len(matching_dirs)} matching directories")

    linked = 0

    TARGET_SUFFIX = "final.unique.fasta"

    for d in matching_dirs:
        for fasta in d.rglob("*"):
            if fasta.name.endswith(TARGET_SUFFIX):
                link_name = dest_dir / fasta.name

                if link_name.exists():
                    print(f"Skipping existing: {link_name.name}")
                    continue

                link_name.symlink_to(fasta)
                linked += 1


    print(f"Created {linked} symlinks in {dest_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Symlink FASTA files from folders whose names start with given prefixes"
    )
    parser.add_argument(
        "--search-root",
        required=True,
        help="Root directory containing sample folders"
    )
    parser.add_argument(
        "--dest-dir",
        required=True,
        help="Destination directory for symlinks"
    )
    parser.add_argument(
        "--prefix-file",
        required=True,
        help="Text file containing folder name prefixes (one per line)"
    )

    args = parser.parse_args()

    main(args.search_root, args.dest_dir, Path(args.prefix_file))
