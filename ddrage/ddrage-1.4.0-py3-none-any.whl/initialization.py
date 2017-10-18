# -*- coding: utf-8 -*-
"""This module handles the creation of perfect loci from which genotypes
etc. will be derived.
"""
from .rad_locus import RADLocus
from .rad_reads import ProtoReadp7
from .generation import p5_seq_from_fragment, p7_seq_from_fragment

def init_conf(args, individuals, barcode_set, individuals_matrix, p7_bc):
    return {
        "nr of individuals": len(individuals),
        "nr of loci": args.nr_loci,
        "read length": args.read_length,
        "dbr sequence": args.dbr,
        "p7 barcode": p7_bc,
        "p5 recognition site": args.p5_rec_site,
        "p7 recogintion site": args.p7_rec_site,
        "p5 overhang": args.p5_overhang,
        "p7 overhang": args.p7_overhang,
        "prob. seq error": args.prob_seq_error,
        "individuals": str([i[1][2] for i in individuals]),
        "individual names": [str(i[1][2]) for i in individuals],
        "diversity parameter": args.diversity,
        'target coverage (d_s)':  args.cov,
        "used coverage model": args.coverage_model,
        "barcode set": barcode_set,
        "individuals matrix": individuals_matrix,
    }


def create_perfect_locus(locus_name, individuals, args, fragment_generator):
    # create fragment or read it from file and use it to create a locus
    if fragment_generator.from_file:
        fragment, fragment_name = fragment_generator.read_fragment_from_file()
        name = fragment_name.decode()
    else:
        if args.overlap:
            fragment_length = overlap_length(args, individuals)
        else:
            fragment_length = 2 * args.read_length
        fragment = fragment_generator.random_fragment(fragment_length)
        name = locus_name
    return RADLocus(individuals, name, args, fragment)


def create_perfect_hrl_locus(locus_name, args, individuals, fragment_generator):
    fragment = fragment_generator.random_fragment(args.read_length)
    name = locus_name
    # sort individuals to match 
    individuals = sorted(individuals, key=lambda x: x[1][2])
    return RADLocus(individuals, "HRL_{}".format(locus_name), args, fragment)


def overlap_length(args, individuals):
    min_p5_bc_len = None
    min_p5_spacer_len = None
    min_p7_spacer_len = None
    for (barcode_p5, barcode_p7), (spacer_p5, spacer_p7, individual_name, *_) in individuals:
        if min_p5_bc_len:
            min_p5_bc_len =  min(min_p5_bc_len, len(barcode_p5))
        else:
            min_p5_bc_len = len(barcode_p5)
        if min_p5_spacer_len:
            min_p5_spacer_len =  min(min_p5_spacer_len, len(spacer_p5))
        else:
            min_p5_spacer_len = len(spacer_p5)
        if min_p7_spacer_len:
            min_p7_spacer_len =  min(min_p7_spacer_len, len(spacer_p7))
        else:
            min_p7_spacer_len = len(spacer_p7)
    p5_adapter_length = min_p5_bc_len + min_p7_spacer_len + len(args.p5_overhang)
    p7_adaptor_length = min_p7_spacer_len + len(args.dbr) + len(args.p7_overhang)
    non_overlap_length = 2 * args.read_length - p5_adapter_length - p7_adaptor_length
    print("non overlap", non_overlap_length)
    length = int(non_overlap_length * (1 - (0.5*args.overlap)))
    return length if length >= args.read_length else args.read_length
