# -*- coding: utf-8 -*-
"""This module contains functions to add mutations to read objects.

Most functions here are factory-type functions that take one template read
and create new read objects as a result.
"""
import random
import copy
from functools import partial

from . import distributions
from .generation import random_seq
from .rad_reads import RADRead


def add_meta_info_to_all(it, info):
    """Add the info to all RADRead objects in the iterable."""
    for rad_read in it:
        rad_read.add_meta_info(info)


def plain_copies(template_read, coverage, meta_info="type:'common'"):
    """Create coverage copies of the read.

    Arguments:
        template_read (RADRead): Template read for the duplication.
        coverage (int): Total number of reads that will be returned.
        meta_info (str): Text to be added to the meta info list.
            Default: 'common'

    Returns:
        list: A list containing the created copies.

    Note:
        This does not modify the individual's information. I.e. all copies originate from
        the same individual.

    Note:
        The original read is not part of the returned list. All reads in there are
        actual deep copies.
    """
    # TODO: This is a runtime bottleneck. Using copy instead of deepcopy is faster, but breaks adding meta infos
    # The only problematic things are the meta infos, since they are a nested mutable object
    # When somethings else is changed (for example a seq error is added) new sequences are generated
    # So if this can be augmented to deep copy only the meta info, maxbe using a specialized version of
    # add meta info to all, this could receive a major speedup.
    copied_reads = [copy.deepcopy(template_read) for _ in range(coverage)]
    # copied_reads = [copy.copy(template_read) for _ in range(coverage)]
    add_meta_info_to_all(copied_reads, meta_info)
    return copied_reads


def shallow_plain_copies(template_read, coverage, meta_info="type:'common'"):
    """Create coverage copies of the read.

    Arguments:
        template_read (RADRead): Template read for the duplication.
        coverage (int): Total number of reads that will be returned.
        meta_info (str): Text to be added to the meta info list.
            Default: 'common'

    Returns:
        list: A list containing the created copies.

    Note:
        This does not modify the individual's information. I.e. all copies originate from
        the same individual.

    Note:
        The original read is not part of the returned list. All reads in there are
        copies. Containers like meta_info are deep copies, the rest (sequneces, etc.)
        are shallow copies (only the reference is copied.).
    """
    template_meta = template_read.meta_info
    copied_reads = [RADRead.shallow_copy(template_read) for _ in range(coverage)]
    for rad_read in copied_reads:
        rad_read.add_meta_info(meta_info)
    return copied_reads


def mutation_copies(rad_read, coverage, heterozygous, mutation_model):
    """Create copies of the read which contain homo- or heterozygous mutations.

    Arguments:
        rad_read (RADRead): Template read for the duplication.
        coverage (int): Total number (sum if heterozygous) of reads returned.
        heterozygous (bool): If given, heterozygous mutations are created. I.e. some copies retain the
            expected base, and the other parts gets a mutation. Note that this might differ for other individuals
            at the same locus.
        mutation_model (mutationModel): mutationModel of the reads locus.

    Returns:
        tuple(int or tuple, list, str): The number of created copies as int (for
            homozygous loci) or as tuple of (int, int) (for heterozygous loci)
            and a list containing the copies. Lastly the used allele is returned.

    Note:
        This does not modify the individual's information. I.e. all copies originate from
        the same individual.

    Note:
        The original read is not part of the returned list. All reads in there are
        actual deep copies.
    """
    if heterozygous:
        allele_1, allele_2 = mutation_model.get_random_genotype()
        template_read_1 = RADRead.mutated_copy(rad_read, allele_1)
        template_read_2 = RADRead.mutated_copy(rad_read, allele_2)

        # mutate only a part of the reads and duplicate each of them
        # distribute mutations to reads. Enforce at least one MUTATION on each read
        coverage_allele_1, coverage_allele_2 = distributions.heterozygous_mutation_distribution(coverage)

        # set coverage to 0 for dropout mutations
        if template_read_1 != "dropout NA":
            template_read_1.fix_lengths(mutation_model)
        else:
            coverage_allele_1 = 0
        if template_read_2 != "dropout NA":
            template_read_2.fix_lengths(mutation_model)
        else:
            coverage_allele_2 = 0
        
        # create plain and mutated copies
        reads_allele_1 = [RADRead.shallow_copy(template_read_1) for _ in range(coverage_allele_1)]
        add_meta_info_to_all(reads_allele_1, "genotype:'het. Allele {}'".format(allele_1.name))
        reads_allele_2 = [RADRead.shallow_copy(template_read_2) for _ in range(coverage_allele_2)]
        add_meta_info_to_all(reads_allele_2, "genotype:'het. Allele {}'".format(allele_2.name))
        return (coverage_allele_1, coverage_allele_2), (reads_allele_1, reads_allele_2), (allele_1, allele_2)
    else:
        # only return mutated copies. Other individuals from the same locus will differ form this
        allele = mutation_model.get_random_allele() # this is assured to not be the common allele
        mutated_template_read = RADRead.mutated_copy(rad_read, allele)
        if mutated_template_read != "dropout NA":
            mutated_template_read.fix_lengths(mutation_model)
        else:
            coverage = 0
        mutated_reads = [RADRead.shallow_copy(mutated_template_read) for _ in range(coverage)]
        add_meta_info_to_all(mutated_reads, "genotype:'hom. Allele {}'".format(allele.name))
        return coverage, mutated_reads, allele


def id_copies(template_read, coverage, rec_sites):
    """Create copies of the read containing a null allele with incomplete digestion.

    Arguments:
        template_read (RADRead): Template read for the duplication.
        coverage (int): Number of reads that will be created.
        rec_sites (tuple): Restriction sites of the p5 and p7 enzyme.

    Returns:
        list: The modified reads are returned as a list of RADRead objects.

    Note:
        This does not modify the individual's information. I.e. all copies originate from
        the same individual.
    """
    rec_site = random.choice(rec_sites)
    p5_id_prob = 0.01
    mate = "p5" if random.random() < p5_id_prob else "p7"
    if mate == "p5":
        p5_null_allele_seq = random_seq(len(template_read.protoread_p5.sequence))
        meta_info = "type:'ID_p5'"
    else:
        p7_null_allele_seq = random_seq(len(template_read.protoread_p7.sequence))
        meta_info = "type:'ID_p7'"

    id_reads = [RADRead.shallow_copy(template_read) for _ in range(coverage)]
    for id_read in id_reads:
        id_read.add_meta_info(meta_info)
        if mate == "p5":
            id_read.protoread_p5.sequence = p5_null_allele_seq
        else:
            id_read.protoread_p7.sequence = p7_null_allele_seq
    return id_reads


def pcr_copies(rad_read, max_cov, min_cov=1):
    """Create between min_cov and max_cov copies of the read_pair.

    Arguments:
        rad_read (RADRead): The template rad read.
        max_cov (int): Maximal nr of pcr copies generated.
        min_cov (int): Minimal nr of pcr copies generated. Default: 1

    Returns:
        tuple(int, list): The number of created copies as int and a list containing the
            actual copies. The original read is not contained.

    Note:
        This does not modify The individual's information. I.e. all copies originate from
        the same individual.
    """
    copy_nr = random.randint(min_cov, max_cov)
    pcr_copies = [copy.deepcopy(rad_read) for _ in range(copy_nr)]
    add_meta_info_to_all(pcr_copies, "type:'PCR copy'")
    return copy_nr, pcr_copies


def shallow_pcr_copies(rad_read, max_cov, min_cov=1):
    """Create between min_cov and max_cov copies of the read_pair.

    Arguments:
        rad_read (RADRead): The template rad read.
        max_cov (int): Maximal nr of pcr copies generated.
        min_cov (int): Minimal nr of pcr copies generated. Default: 1

    Returns:
        tuple(int, list): The number of created copies as int and a list containing the
            actual copies. The original read is not contained.

    Note:
        This does not modify the individual's information. I.e. all copies originate from
        the same individual.
    """
    template_meta = rad_read.meta_info
    copy_nr = random.randint(min_cov, max_cov)
    pcr_copies = [RADRead.shallow_copy(rad_read) for _ in range(copy_nr)]
    for pcr_copy in pcr_copies:
        pcr_copy.add_meta_info("type:'PCR copy'")
    return copy_nr, pcr_copies


def get_id_template(rad_read, allele, mutation_model):
    """Costruct a template read for ID read simulation with a given allele.

    This is used to construct ID reads even when no coverage was assigned.
    """
    mutated_template_read = RADRead.mutated_copy(rad_read, allele)
    mutated_template_read.fix_lengths(mutation_model)
    add_meta_info_to_all([mutated_template_read], "genotype:'hom. Allele {}'".format(allele.name))
    return mutated_template_read
