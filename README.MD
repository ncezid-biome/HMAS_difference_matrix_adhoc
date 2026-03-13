

# Amplicon Difference Matrix Pipeline

This repository contains a **Nextflow pipeline** for generating a **pairwise amplicon difference matrix** from HMAS sequencing samples.

It is designed for **stool HMAS samples or isolate HMAS samples** used in outbreak analysis.

Unlike in-silico amplicon comparisons, real HMAS samples often contain **multiple amplicon variants for the same primer group**, which requires special comparison strategies implemented in this pipeline.

---

# Requirements

* Nextflow
* Python 3

Python scripts used by the pipeline:

```
pairwise_compare_any.py
pairwise_compare_most.py
merge_rows.py
```

---

# Input

### 1. Sample FASTA files

A directory containing sample FASTA files:

```
sample1.fasta
sample2.fasta
sample3.fasta
```

⚠️ **All FASTA files must be directly inside the input directory.**
Subdirectories are not supported.

---

### 2. Primer file

A primer list used to identify amplicon groups.

---

# Usage

Example:

```
nextflow run main.nf \
    --input fasta_samples \
    --primers primers.txt \
    --outdir diff_matrix \
    --most_amplicon true
```

---

# Parameters

| Parameter         | Description                                    |
| ----------------- | ---------------------------------------------- |
| `--input`         | Directory containing FASTA files               |
| `--primers`       | Primer list file                               |
| `--outdir`        | Output directory                               |
| `--any_amplicon`  | Compare samples using any matching amplicon    |
| `--most_amplicon` | Compare samples using the most common amplicon |
| `--diff_only`     | Output only differences                        |

⚠️ Exactly **one** of the following must be specified:

```
--any_amplicon
--most_amplicon
```

---

# Output

The pipeline produces a pairwise difference matrix:

```
pairwise_diff_matrix-<outdir>.csv
```

Each cell represents the **number of primer groups with different amplicons between two samples**.

---


# Usage

Example command:

```bash
nextflow run main.nf \
  --primers /2461_legacy_3columns_primers \
  --input $PWD/fasta_SH/ \
  --outdir diff_matrix_any \
  --any_amplicon true \
  --diff_only true
````

