#!/usr/bin/env python

import os
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import prosite_parser as prop


def blast_plot(blast_output, output_dir, show=False):
    """ Plot blast output for each of the queries provided in input file """
    df = pd.read_csv(blast_output, delimiter='\t')
    df = df.sort_values(['qseqid', 'qcovs', 'pident', 'evalue'], ascending=[1, 0, 0, 0]).reset_index(drop=True)
    # Use identity percentage to set color accordingly
    df['pident greater than'] = round(df.pident / 10) * 10
    for query in pd.unique(df.qseqid):
        data = df[df.qseqid == query]
        # with plt.style.context('dark_background'):
        sns.set(context='paper', font_scale=.9, font='times')
        sns.set_style('white')
        # plt.rc('ytick', labelsize=2)
        fig, ax = plt.subplots(figsize=(8,8), clear=True)
        # Plot totality of query (100% coverage)
        sns.barplot(data=data, x='qseqlen', y='sseqid' , color="lightgrey")
        # Plot coverage 
        sns.barplot(data=data, x="qend", y="sseqid", hue='pident greater than', palette=sns.light_palette('green'), dodge=False) #dodge avoids hue shrinkage of width
        # Plot N-terminal if uncovered
        sns.barplot(data=data, x="qstart", y="sseqid", color='lightgrey')
        ax.set(xlabel='Blast overlap', ylabel='subject Accession Number', title=str(query)+' blast output plot')
        ax.legend(title='pident lower or equal to', loc='lower left', bbox_to_anchor=(1, 0))
        fig.tight_layout()
        # Save figure in appropiate directory
        graph_dir = output_dir.rstrip('/')+'/'+query+'/'
        if not os.path.isdir(graph_dir): os.mkdir(graph_dir)
        fig.savefig(graph_dir+'blast.png')
        if show:
            plt.show()
        plt.close(fig)
    

def domain_plot(blast_output, output_dir, show=False):
    """ Plot ProSite protein domains of blast hits from input file """
    df = pd.read_csv(blast_output, delimiter='\t') # .set_index['sseqid']
    idx=0 #Index to extract subject sequences
    for qid in pd.unique(df.qseqid):
        data = df[df.qseqid == qid]
        query_dir = output_dir.rstrip('/')+'/'+qid+'/domains/'
        os.makedirs(query_dir, exist_ok=True)
        doms = pd.read_csv(query_dir+'_domains.tsv', delimiter='\t') # Get previously extracted domains
        for sseqid in data.sseqid:
            subject = data[data.sseqid == sseqid]
            seq_len = len(subject.sseq[idx])
            domains = doms[doms.id == sseqid].name.to_numpy()
            midpoints = doms[doms.id == sseqid].midpoint.to_numpy()
            # Create different levels for domain name tags
            levels = np.tile(np.arange(-9, 9 , 2), int(np.ceil(len(midpoints)/9)))[:len(midpoints)]
            fig, ax = plt.subplots(figsize=(15, 7), constrained_layout=True)
            ax.set(title="ProSite domains of "+sseqid)
            plt.axhline(y=0, color='black', linestyle='-')
            # Represent domains as lines (and hollow dots) on the sequence. Stem plot
            markerline, dummy_stemline, dummy_baseline = ax.stem(midpoints, levels, linefmt="C3-", basefmt="k-", use_line_collection=True)
            plt.setp(markerline, mec="k", mfc="w", zorder=3)
            # Shift the markers to the baseline by replacing the y-data by zeros
            markerline.set_ydata(np.zeros(len(midpoints)))
            # Annotate lines
            vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
            for d, l, r, va in zip(midpoints, levels, domains, vert):
                ax.annotate(r, xy=(d, l), xytext=(3, np.sign(l)*3), textcoords="offset points", va=va, ha="right", **{'fontsize':6, 'rotation':'vertical'}) # xytext=(-3, np.sign(l)*3), textcoords="offset points"
            # remove y axis
            ax.get_yaxis().set_visible(False)
            # for spine in ["left", "top", "right"]
            #     ax.spines[spine].set_visible(False)
            plt.xticks(list(range(0,seq_len, 50)))
            plt.ylim(-15, 13)
            ax.margins(y=0.1)
            fig.savefig("{}{}_domains.png".format(query_dir, sseqid))
            plt.close(fig)
            idx += 1



# # https://matplotlib.org/3.1.1/users/event_handling.html#mouse-enter-and-leave
