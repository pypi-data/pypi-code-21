# -*- coding: utf-8 -*-
"""This module is an interface for the barcodes module.

It manages different barcode data sets.
"""
import random
from . import barcode_handler
from .barcode_handler.barcode_file_parser import DeBarcoder
import os
import sys

# TODO: parse content of barcodes folder and populate this tuple automatically
BARCODE_SETS = ("barcodes", "small", "full", "big", "huge")

# define default barcode paths
path_barcodes = "rage/barcode_handler/barcodes/barcodes.txt"
barcodes_folder = "rage/barcode_handler/barcodes/"

if os.path.exists(path_barcodes):
    bcs_barcodes = DeBarcoder(path_barcodes, dtype=str) # set to str for compatibility
else:
    bcs_barcodes = None

# set default value
try:
    barcodes = bcs_barcodes
    bc_dict = bcs_barcodes.bc_pairs
except AttributeError:
    # make sure the modules works from a different path in 
    # order for sphinx to work properly
    barcodes = None
    bc_dict = dict()


def select_barcode_set(name):
    """Select the barcode set to be used for the analysis.

    Arguments:
        name (str): Name of the set to be selected or path to barcodes file.
    
    Returns:
        str: The name of the selected set. The set itself is set as a global
        varible in the barcodes module.
    """
    global bc_dict
    global barcodes
    if name in BARCODE_SETS:
        predefined_sets_path = os.path.join(os.path.dirname(barcode_handler.__file__), "barcodes")
        bcs_name = os.path.join(predefined_sets_path, "{}.txt".format(name))
        custom_bcs = DeBarcoder(os.path.join(predefined_sets_path, bcs_name), dtype=str)
        barcodes = custom_bcs
        bc_dict = custom_bcs.bc_pairs
    elif os.path.exists(name):
        custom_bcs = DeBarcoder(name, dtype=str)
        barcodes = custom_bcs
        bc_dict = custom_bcs.bc_pairs
    else:
        raise ValueError("Barcode set {} not found.".format(name))


def _all_seqs_to_bytes(individual):
    """Convert all str sequences in the individual to bytes for compatibily."""
    (p5_bc, p7_bc), (p5_spacer, p7_spacer, individual, *other) = individual
    bc_pair = (bytes(p5_bc, 'ascii'), bytes(p7_bc, 'ascii'))
    individual_info = (bytes(p5_spacer, 'ascii'), bytes(p7_spacer, 'ascii'), individual, *other)
    return bc_pair, individual_info


def pick_individuals(nr, multiple_p7, as_bytes=True):
    """Pick a given number of individuals with matching p7 barcodes.

    Arguments:
        nr (int): Number of individuals desired.
        as_bytes (bool): Return sequences as bytes. Default: True

    Returns:
        tuple: A tuple containing a list of individuals (for the structure of an
        individual see Note), the common p7 barcode they all share, and the
        matrix of all individuals in the data set.

    Note:
        An individual consists of a a nested tuple of the structure::

            ((p5 barcode, p7 barcode), (p5 spacer, p7 spacer, individual name, ...))

        Where ... can be any list of additional items.
    """
    if not multiple_p7:
        # randomly (uniform) choose an inital individual
        first_individual = random.choice(list(bc_dict.items()))
        (p5_bc, p7_bc), (p5_spacer, p7_spacer, individual, *_) = first_individual
        # assemble all individuals with matching p7 barcode which are not the initial individual
        candidates = [(key, value) for key, value in bc_dict.items() if (key[1] == p7_bc and key[0] != p5_bc)]
        # choose nr-1 additional individuals
        if len(candidates) >= nr-1:
            all_individuals = [first_individual] + random.sample(candidates, nr-1)
        else:
            raise ValueError("Can not create more than {} individuals with this p7 barcode. Tried to create {}. Use   -b huge   to use the huge barcode set or create an own barcodes file.".format(len(candidates)+1, nr))
        if as_bytes:
            return [_all_seqs_to_bytes(individual) for individual in all_individuals], p7_bc, barcodes.get_individual_matrix()
        else:
            return all_individuals, p7_bc, barcodes.get_individual_matrix()
    else:
        try:
            all_individuals = random.sample(list(bc_dict.items()), nr)
        except ValueError:
            raise ValueError("Can not create more than {} individuals from this file. Tried to create {}. Use   -b huge   to use the huge barcode set or create an own barcodes file.".format(len(bc_dict.items()), nr))
        if as_bytes:
            return [_all_seqs_to_bytes(individual) for individual in all_individuals], list(set([p7_bc for (_, p7_bc), _ in all_individuals])), barcodes.get_individual_matrix()
        else:
            return all_individuals, p7_bc, barcodes.get_individual_matrix()


def get_bc_files():
    paths = []
    for name in BARCODE_SETS:
        predefined_sets_path = os.path.join(os.path.dirname(barcode_handler.__file__), "barcodes")
        bcs_name = os.path.join(predefined_sets_path, "{}.txt".format(name))
        paths.append(os.path.join(predefined_sets_path, bcs_name))
    return paths
