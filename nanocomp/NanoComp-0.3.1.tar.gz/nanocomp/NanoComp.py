from sys import exit as sysexit
import nanoget
from os import path
from argparse import ArgumentParser
from nanoplot import utils
import nanoplotter
import pandas as pd
import numpy as np
import logging
from .version import __version__


def main():
    '''
    Organization function
    -setups logging
    -gets inputdata
    -calls plotting function
    '''
    args = get_args()
    try:
        utils.make_output_dir(args.outdir)
        utils.init_logs(args, tool="NanoComp")
        args.format = nanoplotter.check_valid_format(args.format)
        sources = [args.fastq, args.bam, args.summary]
        sourcename = ["fastq", "bam", "summary"]
        datadf = nanoget.get_input(
            source=[n for n, s in zip(sourcename, sources) if s][0],
            files=[f for f in [args.fastq, args.bam, args.summary] if f][0],
            threads=args.threads,
            readtype=args.readtype,
            names=args.names,
            combine="track")
        make_plots(datadf, path.join(args.outdir, args.prefix), args)
        logging.info("Succesfully processed all input.")
    except Exception as e:
        logging.error(e, exc_info=True)
        raise


def get_args():
    parser = ArgumentParser(description="Compares Oxford Nanopore Sequencing datasets.")
    parser.add_argument("-v", "--version",
                        help="Print version and exit.",
                        action="version",
                        version='NanoComp {}'.format(__version__))
    parser.add_argument("-t", "--threads",
                        help="Set the allowed number of threads to be used by the script",
                        default=4,
                        type=int)
    parser.add_argument("--readtype",
                        help="Which read type to extract information about from summary. \
                             Options are 1D, 2D, 1D2",
                        default="1D",
                        choices=['1D', '2D', '1D2'])
    parser.add_argument("-o", "--outdir",
                        help="Specify directory in which output has to be created.",
                        default=".")
    parser.add_argument("-p", "--prefix",
                        help="Specify an optional prefix to be used for the output files.",
                        default="",
                        type=str)
    parser.add_argument("-f", "--format",
                        help="Specify the output format of the plots.",
                        default="png",
                        type=str,
                        choices=['eps', 'jpeg', 'jpg', 'pdf', 'pgf', 'png', 'ps',
                                 'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff'])
    parser.add_argument("-n", "--names",
                        help="Specify the names to be used for the datasets",
                        nargs="*")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--fastq",
                        help="Data is in default fastq format.",
                        nargs='*')
    target.add_argument("--summary",
                        help="Data is a summary file generated by albacore.",
                        nargs='*')
    target.add_argument("--bam",
                        help="Data as a sorted bam file.",
                        nargs='*')
    args = parser.parse_args()
    if args.names:
        if not len(args.names) == [len(i) for i in [args.fastq, args.summary, args.bam] if i][0]:
            sysexit("ERROR: Number of names (-n) should be same as number of files specified!")
    return args


def make_plots(df, path, args):
    df["log length"] = np.log10(df["lengths"])
    nanoplotter.violin_plot(
        df=df,
        y="lengths",
        figformat=args.format,
        path=path)
    nanoplotter.violin_plot(
        df=df,
        y="log length",
        figformat=args.format,
        path=path,
        log=True)
    nanoplotter.violin_plot(
        df=df,
        y="quals",
        figformat=args.format,
        path=path)
    if args.bam:
        nanoplotter.violin_plot(
            df=df,
            y="percentIdentity",
            figformat=args.format,
            path=path)


if __name__ == '__main__':
    main()
