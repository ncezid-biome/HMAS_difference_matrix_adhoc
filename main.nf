#!/usr/bin/env nextflow

params.input        = null
params.primers      = null
params.outdir       = null

// Boolean flags
params.any_amplicon  = false
params.most_amplicon = false
params.diff_only     = false

/*
This workflow generates the pairwise difference matrix
from FASTA files and primer list.

Usage example:

nextflow run main.nf \
    --input /path/to/fasta \
    --primers primers.txt \
    --outdir diff_matrix_most \
    --most_amplicon true \
    --diff_only true
*/

// --------------------------------------------------
// Validation
// --------------------------------------------------

if (!params.input || !params.primers || !params.outdir) {
    error "ERROR: --input, --primers, and --outdir are required."
}

if (params.any_amplicon == params.most_amplicon) {
    error "ERROR: Specify exactly ONE of --any_amplicon or --most_amplicon."
}

// --------------------------------------------------
// Dynamic output filename
// --------------------------------------------------

def outdir_name = new File(params.outdir).getName()
params.output_csv = "pairwise_diff_matrix-${outdir_name}.csv"

// --------------------------------------------------
// Choose script dynamically
// --------------------------------------------------

def compare_script = params.any_amplicon ?
        "pairwise_compare_any.py" :
        "pairwise_compare_most.py"

// Optional diff_only flag
def diff_flag = params.diff_only ? "--diff_only" : ""

// --------------------------------------------------
// Channels
// --------------------------------------------------

Channel
    .fromPath("${params.input}/*.fasta")
    .set { individual_fasta }

// --------------------------------------------------
// Processes
// --------------------------------------------------

process runPairwiseRow {

    tag "${query.simpleName}"
    publishDir "${params.outdir}", mode: 'copy'

    input:
        path(query)

    output:
        path("${query.simpleName}.txt")

    script:
    """
    ${compare_script} \
        --query ${query} \
        --all ${params.input} \
        --primers ${params.primers} \
        --output ${query.simpleName}.txt \
        ${diff_flag}
    """
}


process mergeRows {

    tag "merge"
    publishDir "${params.outdir}", mode: 'copy'

    input:
        path row_files

    output:
        path "${params.output_csv}"

    script:
    """
    merge_rows.py \
        -i ${row_files} \
        -o ${params.output_csv}
    """
}

// --------------------------------------------------
// Workflow
// --------------------------------------------------

workflow {
    runPairwiseRow(individual_fasta)
    mergeRows(runPairwiseRow.out.collect())
}
