#!/usr/bin/env python3

import argparse
import os
import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Reorder rows and columns of a symmetric difference matrix"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input CSV file (row and column labels required)"
    )
    parser.add_argument(
        "-p", "--priority",
        required=True,
        help="Text file containing sample ID prefixes (one per line)"
    )

    args = parser.parse_args()

    # -----------------------------
    # Read matrix
    # -----------------------------
    df = pd.read_csv(args.input, index_col=0)
    index_ids = list(df.index)

    # -----------------------------
    # Read priority prefixes file
    # -----------------------------
    with open(args.priority) as f:
        priority_prefixes = [
            line.strip()
            for line in f
            if line.strip()
        ]

    if not priority_prefixes:
        raise ValueError("Priority file is empty.")

    # -----------------------------
    # Find matches by prefix
    # -----------------------------
    matched = [
        idx for idx in index_ids
        if any(idx.startswith(p) for p in priority_prefixes)
    ]

    # Validate: each priority prefix must match at least one index
    missing = [
        p for p in priority_prefixes
        if not any(idx.startswith(p) for idx in index_ids)
    ]

    if missing:
        raise ValueError(
            f"Priority prefixes not found in matrix index: {missing}"
        )

    # Preserve original order within groups
    new_order = matched + [x for x in index_ids if x not in matched]

    # -----------------------------
    # Reorder rows and columns
    # -----------------------------
    df_reordered = df.loc[new_order, new_order]

    # -----------------------------
    # Build output filename
    # -----------------------------
    base, ext = os.path.splitext(args.input)
    output_file = f"{base}_reordered{ext}"

    # -----------------------------
    # Write output
    # -----------------------------
    df_reordered.to_csv(output_file)

    print(f"Reordered matrix written to: {output_file}")
    print(f"Moved {len(matched)} rows/columns to the top")


if __name__ == "__main__":
    main()
