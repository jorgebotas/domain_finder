#!/usr/bin/env python

import os
import sys

from subprocess import call, PIPE, Popen
import pandas as pd

import file_handler as fh

def multiple_alignment(multifasta, query=None,
                       output_filename="alignment.fasta", log='/dev/null'):
    """ Perform multiple alignment using MUSCLE.
        To include query sequence, provide tuple (id, seq) """
    # If query_fasta provided, include in multiple alignment input
    if query:
        with open(multifasta, 'a+') as multifasta_file:
            multifasta_file.write('>'+query[0]+'\n')
            multifasta_file.write(query[1]+'\n')
    call(
        ['muscle', '-in', multifasta, '-out', output_filename,
         '-verbose', '-loga', log], stderr=open(log, 'a+')
        )
    return


def compute_alignments(blast_output, output_dir):
    """ Compute multiple alignment(s) \
        for each of the queries in blast_output.tsv """
    df = pd.read_csv(blast_output, delimiter='\t')
    for qid in pd.unique(df.qseqid):
        data = df[df.qseqid == qid].reset_index(drop=True)
        query_dir = output_dir.rstrip('/')+'/'+qid+'/'
        # Create FASTA file containing hits for each query
        fh.tsv2fasta(tsv_file=blast_output, output_dir=output_dir,
                     separate_dirs=True)
        multiple_alignment(
                           multifasta=query_dir+'unaligned.fasta',
                           query=(qid, data.qseq[0]),
                           output_filename=query_dir+'alignment.fasta'
                          )
    return


def compute_NJtree(alignment, output_filename="NJ.phy", log='/dev/null'):
    """ Compute Neighbor-Joining tree using MUSCLE """
    call(
         ['muscle', '-maketree', '-in', alignment, '-out', output_filename,
         '-quiet', '-loga', log, '-cluster', 'neighborjoining'],
         stderr=open(log, 'a+')
        )
    return


def compute_trees(blast_output, output_dir, output_filename="NJ.phy",
                  log='/dev/null'):
    """ Compute Neighbor-Joining tree for each query in blast_output.tsv """
    df = pd.read_csv(blast_output, delimiter='\t')
    for idx in range(len(df.qseqid)):
        qid = df.qseqid[idx]
        query_dir = output_dir.rstrip('/')+'/'+qid+'/'
        compute_NJtree(alignment=query_dir+'alignment.fasta',
                       output_filename=query_dir+output_filename, log=log)
    return
