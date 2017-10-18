#!/usr/bin/env python
"""Module to create .qmodel files from a set of FASTQ files."""
import glob
import numpy as np
import gzip
import os
import sys
import argparse
import gzip

from collections import Counter

import matplotlib
# matplotlib.use('PDF')
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
sns.set_style("ticks")


PLOT_MAX = 0

def setup_fig():
    plt.ion()
    f, (ax1, ax2) = plt.subplots(2)
    cbar_ax = f.add_axes([.91, .2, .02, .6])
    f.set_size_inches(12, 8)

    return f, (ax1, ax2), cbar_ax


def update_profile(args, data, read, progress, fig):
    global PLOT_MAX 
    f, (ax1, ax2), cbar_ax = fig
    if read == "p5":
        axes = ax1
        # if cbar_ax1 is None:
    else:
        axes = ax2
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=1.2)

    all_probs = []
    nr_positions = args.length # only consider valid read positions
    nr_quality_values = 104-33 # only consider valid PHRED scores in illumina format
    # initialize array to be plotted
    values = np.zeros(shape=(nr_quality_values, nr_positions), dtype=np.int)

    # get probabilities from files
    for pos, counter in enumerate(data):
        if pos >= nr_positions:
            continue
        else:
            for qvalue, count in counter.items():
                if 33 < qvalue < 104:
                    # convert ASCII to PHRED
                    values[qvalue-33][pos] = count
    # create mask to set zero values to white
    mask = (values == 0)

    if read == "p5":
        plot_max = max(np.max(values), PLOT_MAX)
        PLOT_MAX = plot_max
    else:
        plot_max = PLOT_MAX
    # plot the values
    heatmap = sns.heatmap(values, mask=mask, cmap="magma_r", xticklabels=10, yticklabels=10, ax=axes, cbar_ax=cbar_ax, vmin=0, vmax=plot_max)
    # make them readable
    axes.invert_yaxis()
    # make the graph pretty
    axes.set_title("Quality Value Distribution for {} from {} reads".format(read, progress))
    axes.set_xlabel("Read position")
    axes.set_ylabel("PHRED quality value")
    for item in heatmap.get_yticklabels():
        item.set_rotation(0)
    # plt.show()
    plt.pause(0.01)
    
    return f, (ax1, ax2), cbar_ax, plot_max


def plot_profiles(args, data, show):

    f, (ax1, ax2) = plt.subplots(2)
    cbar_ax = f.add_axes([.91, .2, .02, .6])
    f.set_size_inches(12, 8)
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=1.2)

    nr_positions = args.length # only consider valid read positions
    nr_quality_values = 104-33 # only consider valid PHRED scores in illumina format
    # initialize array to be plotted
    data_p5, data_p7 = data
    data_p5 = data_p5[:nr_quality_values+1,:]
    data_p7 = data_p7[:nr_quality_values+1,:]

    # create mask to set zero values to white
    mask_p5 = (data_p5 == 0)
    mask_p7 = (data_p7 == 0)
    heatmap_p5 = sns.heatmap(data_p5, mask=mask_p5, cmap="magma_r", xticklabels=10, yticklabels=10, ax=ax1, cbar_ax=cbar_ax)
    heatmap_p7 = sns.heatmap(data_p7, mask=mask_p7, cmap="magma_r", xticklabels=10, yticklabels=10, ax=ax2, cbar_ax=cbar_ax)
    ax1.invert_yaxis()
    ax2.invert_yaxis()
    # make the graph pretty
    ax1.set_title("Quality Value Distribution for p5 reads")
    ax2.set_title("Quality Value Distribution for p7 reads")
    ax1.set_xlabel("Read position")
    ax2.set_ylabel("PHRED quality value")
    ax1.set_xlabel("Read position")
    ax2.set_ylabel("PHRED quality value")
    for item in heatmap_p5.get_yticklabels():
        item.set_rotation(0)
    for item in heatmap_p7.get_yticklabels():
        item.set_rotation(0)
    if show:
        plt.show()
    else:
        plt.savefig(args.output + ".pdf")


def find_fastq_files(file_list):
    """Compile a list of all input files."""
    # flatten the command line parameters
    all_paths = []
    for paths in file_list:
        all_paths.extend(paths)
    # glob them, if possible
    all_files = []
    for path in all_paths:
        globbed = glob.glob(path)
        if not globbed:
            print("Could not locate file:", path, file=sys.stderr)
            sys.exit(1)
        all_files.extend(globbed)
    # return extended list of files
    return all_files


def count_quality_values(args, paths, fig, read):
    """Count quality values for all FASTQ files."""

    # initialize a counter for quality values for each position
    read_length = args.length
    all_counts = [Counter() for _ in range(read_length)]

    # count all quality values
    for path in paths:
        count_fastq_file(args, path, all_counts, fig, read)

    return all_counts


def count_fastq_file(args, path, all_counts, fig, read):
    """Count quality values in one fastq file and add the results to all_counts in place."""
    print("  Tallying {}".format(path), flush=True)
    read_length = args.length
    with gzip.open(path, "rb") if path.endswith(".gz") else open(path, "rb") as fastq_file:
        for i, values in enumerate(fastq_file):
            if i % 4 == 3:
                # found a quality line
                for pos, val in enumerate(values.strip(b"\n")):
                    if pos < read_length:
                        all_counts[pos][val] += 1
            if ((i+1) % (4 * 10000)) == 0:
                print("\rAnalyzed {:>10} reads".format((i+1) // 4), end="")
                if args.visualize:
                    update_profile(args, all_counts, read, ((i+1) // 4), fig)
    print("\n")


def compute_relative_abundance(args, all_counts):
    """Compute relative abundances from absolute counts."""
    relative_counts = None

    for pos, pos_tally in enumerate(all_counts):
        total = sum(pos_tally.values())
        probs = np.array([pos_tally[x] / total if pos_tally[x] else 0 for x in range(args.length)], dtype=np.double)
        if relative_counts is not None:
            relative_counts = np.vstack((relative_counts, probs))
        else:
            relative_counts = probs

    return relative_counts


def compile_qmodel(args, relative_p5_counts, relative_p7_counts):
    """Interpret probs files, absolute QV counts per position."""

    nr_positions = args.length # only consider valid read positions
    nr_quality_values = 104-33 # only consider valid PHRED scores in illumina format
    # initialize array to be plotted
    values_p5 = np.zeros(shape=(nr_quality_values, nr_positions), dtype=np.double)
    values_p7 = np.zeros(shape=(nr_quality_values, nr_positions), dtype=np.double)

    # transfer probabilities to numpy array
    for pos, probs in enumerate(relative_p5_counts):
        if pos >= nr_positions:
            continue
        else:
            for qvalue, prob in enumerate(probs):
                if 33 <= qvalue < 104:
                    # convert ASCII to PHRED
                    values_p5[qvalue-33][pos] = prob
    for pos, probs in enumerate(relative_p7_counts):
        if pos >= nr_positions:
            continue
        else:
            for qvalue, prob in enumerate(probs):
                if 33 <= qvalue < 104:
                    # convert ASCII to PHRED
                    values_p7[qvalue-33][pos] = prob

    return values_p5, values_p7


def write_qmodel(args, relative_p5_counts, relative_p7_counts):
    values_p5, values_p7 = compile_qmodel(args, relative_p5_counts, relative_p7_counts)
    print("Writing output to", args.output+".npz")
    np.savez(args.output, p5=values_p5, p7=values_p7)


def get_argument_parser():
    description_text = ("This tool compiles a position-wise distribution of quality values from one or more "
                        "FASTQ files. It creates a .qmodel file which can be passed to ddRAGE using the -q parameter."
    )
    parser = argparse.ArgumentParser(
        description=description_text)

    parser.add_argument(
        "-1", "-f", "--p5",
        help="Path to a forward read file.",
        action="append",
        dest="p5_files",
        nargs="+",
        metavar="FASTQ_PATH",
    )

    parser.add_argument(
        "-2", "-r", "--p7",
        help="Path to a forward read file.",
        action="append",
        dest="p7_files",
        nargs="+",
        metavar="FASTQ_PATH",
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file name/path. Default: custom.qmodel",
        action="store",
        dest="output",
        default="custom.qmodel",
    )

    parser.add_argument(
        "-v", "--visualize",
        help=("Visualize the accumulating profile. And create a pdf version of the  plot. Only works for read file with more than 10000 reads."),
        action="store_true",
        dest="visualize",
        default=False,
    )

    parser.add_argument(
        "-p", "--plot",
        help=("Plot the quality distributions as pdf. (Like visualize, but without the progress updates. Only plots the final distributions.)"),
        action="store_true",
        dest="plot",
        default=False,
    )

    parser.add_argument(
        "-s", "--show",
        help=("Read and plot a .qmodel.npz file."),
        action="store",
        dest="show",
        default=None,
    )

    parser.add_argument(
        "-l", "--length",
        help=("Maximum read length. All values after this position will "
              "be truncated and not become part of the model. "
              "Default: 100"
        ),
        action="store",
        dest="length",
        type=int,
        default=100,
    )

    return parser


def main():
    argparser = get_argument_parser()
    args = argparser.parse_args()
    if args.show is not None:
        print("Showing learned data")
        qmodel = np.load(args.show)
        plot_profiles(args, (qmodel["p5"], qmodel["p7"]), show=True)
        sys.exit(0)
    
    if args.visualize:
        fig = setup_fig()
    else:
        fig = None
    print("Learning quality model:")
    all_p5_files = find_fastq_files(args.p5_files)
    all_p7_files = find_fastq_files(args.p7_files)
    all_p5_counts = count_quality_values(args, all_p5_files, fig, read="p5")
    all_p7_counts = count_quality_values(args, all_p7_files, fig, read="p7")
    p5_relative_abundances = compute_relative_abundance(args, all_p5_counts)
    p7_relative_abundances = compute_relative_abundance(args, all_p7_counts)
    write_qmodel(args, p5_relative_abundances, p7_relative_abundances)
    if args.visualize:
        print("Writing plot of profile to:", args.output + ".pdf")
        plt.savefig(args.output + ".pdf")
    
    if args.plot:
        print("Plotting learned data to" + args.output+".pdf")
        model = compile_qmodel(args, p5_relative_abundances, p7_relative_abundances)
        plot_profiles(args, model, show=False)


if __name__ == '__main__':
    main()
