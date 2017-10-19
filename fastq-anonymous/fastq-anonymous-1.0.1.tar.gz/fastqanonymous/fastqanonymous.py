from Bio import SeqIO, Seq
from argparse import ArgumentParser
from .version import __version__
import sys
from random import choice as rchoice


def main():
    args = get_args()
    anonymize(args.mask)


def get_args():
    parser = ArgumentParser(description="Change the sequence of a fastq file \
                                        to enable sharing of confidential information, \
                                        for troubleshooting of tools.")
    parser.add_argument("-v", "--version",
                        help="Print version and exit.",
                        action="version",
                        version='fastq-anonymous {}'.format(__version__))
    parser.add_argument("-m", "--mask",
                        help="Mask all nucleotides using N",
                        action="store_true")
    return parser.parse_args()


def anonymize(masking):
    i = 0
    for rec in SeqIO.parse(sys.stdin, "fastq"):
        rec.id, rec.description, i = make_id(i)
        if masking:
            rec.seq = Seq.Seq(len(rec) * 'N')
        else:
            rec.seq = Seq.Seq(''.join([rchoice(['A', 'C', 'T', 'G']) for i in range(len(rec))]))
        print(rec.format("fastq"))


def make_id(index):
    return "dummy" + str(index), "", index + 1
