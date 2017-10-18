# -*- coding: utf-8 -*-
"""
Randomize a FASTQ file or a pair of FASTQ files
"""

import sys
import os
import argparse
import gzip
from mmap import mmap

import numpy as np
from numba import njit


@njit
def _count_fastq_entries(buf):
    j = 1
    n = 0
    for i, b in enumerate(buf):
        if  b == 10:
            n += 1
            if n%4 == 0:
                j += 1
    return j


@njit
def _build_index(buf, out):
    out[0]=0
    j = 1
    n = 0
    for i, b in enumerate(buf):
        if  b == 10:
            n += 1
            if n%4 == 0:
                out[j] = i+1
                j += 1


def fastq_index(fqname):
    # limitation: fastq file must not be compressed
    # limitation: fastq file must use exactly 4 lines per entry
    # limitation: fastq file must end with \n
    with open(fqname, 'r+b') as f:
        with mmap(f.fileno(), length=0) as m:
            bufsize = _count_fastq_entries(m)
            idx = np.zeros(bufsize, dtype=np.int64)
            _build_index(m, idx)
            if idx[-1] != len(m):
                raise RuntimeError("FASTQ file does not satisfy limitations")
    return idx


def write_permuted_fastq(fastq, idx, p, fout):
    with open(fastq, 'r+b') as f:
        with mmap(f.fileno(), length=0) as m:
            for i in p:
                start, end = idx[i], idx[i+1]
                fout.write(m[start:end])


def get_files(files):
    nfiles = len(files)
    paired = False
    in1 = in2 = None
    out1 = out2 = None
    if nfiles == 1:
        in1 = files[0]
        out1 = '-'
    elif nfiles == 2:
        in1, out1 = files
    elif nfiles == 4:
        paired = True
        in1, in2, out1, out2 = files
    else:
        raise ValueError("ERROR: invalid number of files: {}".format(nfiles))
    return paired, in1, in2, out1, out2


def abort_if_exists(fname):
    if os.path.exists(fname):
        raise FileExistsError(fname)


def get_argument_parser():
    p = argparse.ArgumentParser(description=
        'Randomize the order of reads in a FASTQ file, '
        'or jointly in a pair of FASTQ files for paired reads. '
        'Limitations: Input files CANNOT be compressed and MUST allow random access; '
        'input files must use exactly 4 lines per entry, no comments; '
        'the last entry must end with \\n.; '
        'lines must be separated by \\n (byte value 10).')
    p.add_argument('files', nargs='+', metavar='FASTQ',
        help="input and output files; give 1, 2 or 4 filenames: "
             "Given 'in.fq', read from it and write to stdout. "
             "Given 'in.fq out.fq', read from in.fq and write to out.fq. "
             "Given 'in1.fq in2.fq out1.fq out2.fq', work on read pairs "
             "and be careful with file order (both input files first!)"
             "If the output file name ends with '.gz' a gizzepd file is writte.")
    p.add_argument('--force', '-f', action='store_true',
        help='overwrite existing output file(s)')
    p.add_argument('--buffersize', '-b', metavar="BYTES",
        type=int, default=128*2**20,
        help='size of output buffer in bytes [128 MB]. Not used if writing gzipped files.')
    return p


def main():
    p = get_argument_parser()
    args = p.parse_args()
    paired, in1, in2, out1, out2 = get_files(args.files)
    if not paired:
        main_single(in1, out1, args.force, args.buffersize)
    else:
        main_paired(in1, in2, out1, out2, args.force, args.buffersize)


def main_single(in1, out1, force, buffersize):
    if not force and out1 != '-':
        abort_if_exists(out1)
    print("Randomizing '{}' to '{}': building index...".format(in1, out1), file=sys.stderr)
    idx = fastq_index(in1)
    n = len(idx) - 1
    print("Permuting {} entries...".format(n), file=sys.stderr)
    p = np.random.permutation(n).tolist()
    print("Writing output stream...", file=sys.stderr)

    if out1 == '-':
        write_permuted_fastq(in1, idx, p, sys.stdout.buffer)
    else:
        if out1.endswith(".gz"):
            with gzip.open(out1, 'wb') as fout:
                write_permuted_fastq(in1, idx, p, fout)
        else:
            with open(out1, 'wb', buffering=buffersize) as fout:
                write_permuted_fastq(in1, idx, p, fout)
    print("Done.", file=sys.stderr)


def main_paired(in1, in2, out1, out2, force, buffersize):
    if not force:
        # make sure that out1 and out2 don't exist
        abort_if_exists(out1)
        abort_if_exists(out2)
    print("Randomizing '{}', '{}' to '{}', {}: building index...".format(in1, in2, out1, out2), file=sys.stderr)
    idx1 = fastq_index(in1)
    n1 = len(idx1) - 1
    idx2 = fastq_index(in2)
    n2 = len(idx2) - 1
    if n1 != n2:
        raise ValueError("Files have different numbers of entries: {} vs. {}".format(n1, n2))
    n = n1
    print("Permuting {} entries...".format(n), file=sys.stderr)
    p = np.random.permutation(n).tolist()
    print("Writing {}...".format(out1), file=sys.stderr)
    if out1.endswith(".gz"):
        with gzip.open(out1, 'wb') as fout:
            write_permuted_fastq(in1, idx1, p, fout)
    else:
        with open(out1, 'wb', buffering=buffersize) as fout:
            write_permuted_fastq(in1, idx1, p, fout)
    print("Writing {}...".format(out2), file=sys.stderr)
    if out2.endswith(".gz"):
        with gzip.open(out2, 'wb') as fout:
            write_permuted_fastq(in2, idx2, p, fout)
    else:
        with open(out2, 'wb', buffering=buffersize) as fout:
            write_permuted_fastq(in2, idx2, p, fout)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
