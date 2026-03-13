#!/usr/bin/env python3

import os
import shutil
import argparse


def copy_fasta_files(input_dir, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_dir):

        # Only process folders with 'PC' in the folder name
        if 'PC' in os.path.basename(root):

            for file in files:
                if file.endswith(".final.unique.fasta"):

                    src = os.path.join(root, file)
                    dst = os.path.join(output_dir, file)

                    print(f"Copying: {src} -> {dst}")
                    shutil.copy2(src, dst)


def main():

    parser = argparse.ArgumentParser(
        description="Recursively find folders containing 'PC' and copy *.final.unique.fasta files."
    )

    parser.add_argument(
        "-i", "--input_dir",
        required=True,
        help="Root directory to search"
    )

    parser.add_argument(
        "-o", "--output_dir",
        required=True,
        help="Directory to copy files to"
    )

    args = parser.parse_args()

    copy_fasta_files(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()