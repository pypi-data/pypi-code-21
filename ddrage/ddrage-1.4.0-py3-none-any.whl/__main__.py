# -*- coding: utf-8 -*-
"""RAGE - ddRAD generator is a python program to simulate ddRADseq data.

Rage creates a set of FASTQ files that can be analyzed and a ground truth file
in which all simulated effects are logged.

The simulated reads contain the most commonly encountered deviations in ddRAD data:
    - both heterozygouos and homozygous mutations consisting of SNPs, indels and null alleles
    - missing information for single individuals
    - singleton reads (for example by contamination during library preparation)
    - reads from highly repetitive loci (lumberjack stacks)
    - variable coverage
    - PCR copies
    - reads affected by incomplete digestion
    - sequencing errors

All simulated effects contained in a read are logged in the FASTQ name line.
Additionally a ground truth file is written next to the created FASTQ files.

The FASTQ files are written in order of read creation and need to be shuffled.
Files written in creation order will provide an easier view on the
available data when looking at the file. Beware that this might create
abnormally easy instances for the further analysis process.
"""
import argparse
import sys
import gc
import os
# from memory_profiler import profile

from .initialization import create_perfect_locus, init_conf
from .postprocessors import SingletonGenerator
from .postprocessors import HighlyRepetitiveLocusGenerator as HRLGenerator
from .distributions import validate_probability_parameters, initialize_coverage_generators
from .generation import initialize_quality_model, FragmentGenerator, count_fragments
from . import barcodes
from . import output


def all_seqs_to_bytes(args):
    """Convert all sequences (overhangs, recognition sites) to bytes."""
    def to_bytes(seq):
        if isinstance(seq, bytes):
            return seq
        else:
            return seq.encode()
    args.dbr = to_bytes(args.dbr)
    args.p5_overhang = to_bytes(args.p5_overhang)
    args.p7_overhang = to_bytes(args.p7_overhang)
    args.p5_rec_site = to_bytes(args.p5_rec_site)
    args.p7_rec_site = to_bytes(args.p7_rec_site)


def validate_sequence_parameters(args, individuals):
    """Assert that the sequence parameters are valid.

    Arguments:
        args (argparse.Namespace): User parameters.
        individuals (iterable of tuples): Individuals list returned by barcodes module.

    Raises:
        ValueError if the p5 overhang is not a suffix of the p5 recognition site.
        ValueError if the p7 overhang is not a suffix of the p7 recognition site.
        ValueError if the sum of the p5 auxilliary sequences is smaller than the 
             read length. I.e. no read length is left to fill with genomic sequence.
        ValueError if the sum of the p7 auxilliary sequences is smaller than the 
             read length. I.e. no read length is left to fill with genomic sequence.
    """
    all_seqs_to_bytes(args)
    # check rec sites and overhangs are subsets of each other
    if not args.p5_rec_site.endswith(args.p5_overhang):
        raise ValueError("P5 overhang '{}' is not a suffix of the recignition site '{}'.".format(args.p5_overhang.decode(), args.p5_rec_site.decode()))
    if not args.p7_rec_site.endswith(args.p7_overhang):
        raise ValueError("P7 overhang '{}' is not a suffix of the recignition site '{}'.".format(args.p7_overhang.decode(), args.p7_rec_site.decode()))
    # get barcode lengths and spacer lengths
    barcodes, other = zip(*individuals)
    p5_bcs, _ = zip(*barcodes)
    p5_spacers, p7_spacers, *_ = zip(*other)
    longest_p5_bc = max((len(bc) for bc in p5_bcs))
    longest_p5_spacer = max((len(spacer) for spacer in p5_spacers))
    longest_p7_spacer = max((len(spacer) for spacer in p7_spacers))

    p5_aux_length = longest_p5_bc + longest_p5_spacer + len(args.p5_overhang)
    if args.read_length <= p5_aux_length + 1:
        raise ValueError("Read length is smaller than sum of p5 auxiliary sequences ({}).".format(p5_aux_length))

    p7_aux_length = longest_p7_spacer + len(args.dbr) + len(args.p7_overhang)
    if args.read_length <= p7_aux_length + 1:
        raise ValueError("Read length is smaller than sum of p7 auxiliary sequences ({}).".format(p7_aux_length))

    if args.overlap > 1.0:
        raise ValueError("The maximal read overlap is 1.0.")


def main():
    """Handle main flow of read generation.

    This includes:
        * Picking barcode pairs (i.e. individuals)
        * create initial set of perfect loci; i.e. a read for all
          (loci x individuals) grouped in RADLocus objects
        * Add deviations / modifications to all loci
        * Write reads to file
    """
    argument_parser = get_argument_parser()
    args = argument_parser.parse_args()

    if args.get_barcodes:
        print("Copying barcode files.")
        output.copy_barcode_files(args)
        sys.exit(0)

    if isinstance(args.loci, int) or args.loci.isdecimal():
        args.nr_loci = int(args.loci)
        if args.nr_loci <= 0:
            print("The `-l, --loci` parameter must either be a positive integer or a path to a FASTA file.", file=sys.stderr)
            sys.exit(1)
    elif not os.path.exists(args.loci):
        print("The `-l, --loci` parameter must either be an integer or a path to a FASTA file.", file=sys.stderr)
        sys.exit(1)
    else:
        args.nr_loci = count_fragments(args.loci)

    print("Simulating reads from {} individuals at {} loci with a coverage of {}.".format(args.nr_individuals, args.nr_loci, args.cov))

    if args.verbosity >= 1:
        print("Initialization")
    ############################################################################
    # Initialization Phase
    ############################################################################
    if args.verbosity >= 1:
        print("Picking individuals.")
    barcode_set = barcodes.select_barcode_set(args.barcode_set)

    # pick a number of individuals with the same p7 barcode
    # and prepare them for processing
    individuals, p7_bc, individuals_matrix = barcodes.pick_individuals(args.nr_individuals, multiple_p7=args.multiple_p7_bcs)
    individuals = sorted(individuals, key=lambda x: x[1][2])
    validate_sequence_parameters(args, individuals)

    # Prepare generators for coverage values
    initialize_coverage_generators(args)
    # initialize the quality generator
    initialize_quality_model(path=args.quality_model, read_length=args.read_length)
    
    # initialize fragment generator
    fragment_generator = FragmentGenerator(args)
    
    # if an event profile was given, i.e. a list of probabilities for
    # locus event types, make sure it sums up to one and is a dict
    validate_probability_parameters(args)
    
    if args.verbosity >= 1:
        print("Initializing loci.")

    # create perfect read pairs and use them to initialize empty locus objects
    # loci, conf = create_perfect_loci(individuals, args)
    # save statistics information for later use
    # also safe config information for output files
    # conf['target coverage (d_s)'] = args.cov
    # conf['used coverage model'] = args.coverage_model
    # conf['barcode set'] = barcode_set
    # conf['individuals matrix'] = individuals_matrix
    conf = init_conf(args, individuals, barcode_set, individuals_matrix, p7_bc)
    stats = output.init_stats(individuals)
    
    # create filepaths, namelines, assemble fastq entry objects
    # these have to be generators to enable stream processing
    paths = output.generate_file_name(p7_bc, args.output_path_prefix, name=args.name, zipped=args.zip_output, single_end=args.single_end)

    # write ground truth files 
    if args.verbosity >= 1:
        print("Initializing ground truth file.")
    output.write_ground_truth(individuals, paths, args)
    first_gt_output = True

    ############################################################################
    # Simulation Phase
    ############################################################################
    # pick event types, create reads, write them to file
    ticksize = 20 if args.nr_loci >= 20 else 1
    if args.verbosity >= 1:
        print("Simulating loci:")

    for i in range(args.nr_loci):
        # show progress
        if args.verbosity >= 1 and i % (args.nr_loci // ticksize) == 0:
            print(" {:>7}/{:>7}".format(i, args.nr_loci))
        try:
            locus = create_perfect_locus(i, individuals, args, fragment_generator)
        except StopIteration:
            # exhausted the fragment generator sooner than expected due to undersized fragments
            # notify user and adjust the nr of loci to avoid length differences down the line.
            print("Could only create loci for {} of the {} fragments. Fragments shorter than the read length {} were skipped.".format(i, args.nr_loci, args.read_length), file=sys.stderr)
            args.nr_loci = i
            break
        # add modifications to the reads (SNPs, Indels, null alleles, dropout, ...)
        # pick the event type and create read coverage
        locus.simulate_individual_events(args)

        # create fastq entries and write them to file
        final_reads_fastq = locus.fastq_entries()
        output.append_to_fastq_files(final_reads_fastq, path_p5=paths.p5, path_p7=paths.p7, zipped=args.zip_output)

        # update statistics information that will be used for the output files
        stats.nr_total_valid_reads += len(locus)
        stats.nr_valid_pcr_copies += locus.nr_pcr_copies

        # remove the most memory-filling parts of the locus object,
        # i.e. the generated reads, to save memory, but keep
        # the locus object and all of its derived values for later use
        output.update_stats(stats, locus)
        if locus.total_valid_coverage == 0:
            stats.dropout_loci += 1
        first_gt_output = output.append_locus_to_gt(locus, paths, first_gt_output)
        del(locus)  # force deletion of the locus object
        # gc.collect()

    ############################################################################
    # Postprocessing Phase
    ############################################################################
    # generate obscuring reads (singletons, HRL reads)
    # specify a blocksize for writing obscuring reads to file
    # this prevents lots of small writing accesses to the disc
    blocksize = 10000
    # create list of singleton reads that do not belong to any locus.
    # they come with a finalized dbr etc. and PCR copies,
    # but only a coverage of one.
    if args.verbosity >= 1:
        print("Simulating singletons.")
    singleton_gen = SingletonGenerator(individuals, args)
    for singletons in singleton_gen.read_blocks(blocksize):
        fastq_singletons = [read.fastq_entry() for read in singletons]
        output.append_to_fastq_files(fastq_singletons, path_p5=paths.p5, path_p7=paths.p7, zipped=args.zip_output)
        gc.collect()
    stats.singletons = singleton_gen.nr_singletons
    stats.singleton_pcr_copies = singleton_gen.nr_pcr_copies
    stats.total_singleton_reads = stats.singletons + stats.singleton_pcr_copies
    del(singleton_gen)

    # create a list of HRL reads that form giant loci
    hrl_gen = HRLGenerator(individuals, fragment_generator, args)
    if args.verbosity >= 1:
        print("Simulating HRLs.")
    for hrl_reads in hrl_gen.read_blocks(blocksize):
        fastq_hrl_reads = [read.fastq_entry() for read in hrl_reads]
        output.append_to_fastq_files(fastq_hrl_reads, path_p5=paths.p5, path_p7=paths.p7, zipped=args.zip_output)
        gc.collect()
    output.append_hrls_to_ground_truth(hrl_gen, paths)
    stats.nr_hrl_loci = hrl_gen.nr_hrl_loci
    stats.hrl_reads = hrl_gen.nr_hrl_reads
    stats.hrl_pcr_copies = hrl_gen.nr_pcr_copies
    stats.total_hrl_reads = stats.hrl_reads + stats.hrl_pcr_copies
    stats.nr_total_reads = stats.nr_total_valid_reads + stats.total_singleton_reads + stats.total_hrl_reads
    del(hrl_gen)

    # assemble some statistic values for the statistics file
    if args.verbosity >= 1:
        print("Gathering data for statistics.")


    # write annotation and statistics files
    if args.verbosity >= 1:
        print("Writing logs and statistics.")
    output.assemble_statistic_data(stats, conf, args)
    output.write_annotation_file(stats, conf, args, paths.annotation)
    output.write_barcode_file(individuals, paths.barcodes)
    output.write_user_output(stats, conf, args, paths)
    output.assemble_overview_data(stats, conf, args, paths)


def get_argument_parser():
    """ Create an argument parser."""
    description_text = "RAGE -- the ddRAD generator -- simulates ddRADseq datasets, comprising reads (FASTQ files) and ground truth (YAML file)."

    parser = argparse.ArgumentParser(
        description=description_text)

    # naming and paths
    names_group = parser.add_argument_group("Naming Parameters")
    names_group.add_argument(
        "--name",
        help="Name for the data set that will be used in the file name. If none is given, the name 'RAGEdataset' will be used.",
        action="store",
        dest="name",
        default=None,
        )

    names_group.add_argument(
        "-o", "--output",
        help="Prefix of the output path. At this point a folder will be created that contains all output files created by ddRAGE.",
        action="store",
        dest="output_path_prefix",
        default="",
        )

    # Main dataset parameters
    dataset_group = parser.add_argument_group("Dataset Parameters")
    dataset_group.add_argument(
        "-n", "--nr-individuals",
        help="Number of individuals in the result. Default: 3",
        action="store",
        dest="nr_individuals",
        type=int,
        default=3,
        )

    dataset_group.add_argument(
        "-l", "--loci",
        help="Number of loci for which reads will be created or path to a FASTA file with predefined fragments. Default: 3",
        action="store",
        dest="loci",
        default=3,
        )

    dataset_group.add_argument(
        "-r", "--read-length",
        help="Total sequence length of the reads (including overhang, barcodes, etc.). The officially supported and well tested range is 50-500bp but longer or shorter reads are also possible. Default: 100",
        action="store",
        dest="read_length",
        type=int,
        default=100,
        )

    dataset_group.add_argument(
        "-c", "--coverage",
        help="Expected coverage that will be created by normal duplication and mutations. The exact coverage value is determined using a probabilistic process. Default: 30",
        action="store",
        dest="cov",
        type=int,
        default=30,
        )

    dataset_group.add_argument(
        "--hrl-number",
        help="Number of Highly Repetitive Loci (HRLs) that will be added, given as fraction of total locus size. Example: ``-l 100 --hrl-number 0.1`` for 10 HRLs. Default: 0.05",
        action="store",
        dest="hrl_number",
        type=float,
        default=0.05,
        )

    dataset_group.add_argument(
        "--diversity",
        help="Parameter for the number of genotypes created per locus. This will be used as parameter for a Poisson distribution. Default: 1.0, increase for more alleles/ genotypes per locus.",
        action="store",
        dest="diversity",
        type=float,
        default=1.0,
        )

    dataset_group.add_argument(
        "--gc-content",
        help="GC content of the generated sequences. Default: 0.5",
        action="store",
        dest="gc_content",
        type=float,
        default=0.5,
        )

    dataset_group.add_argument(
        "-q", "--quality-model",
        help="Path to a quality model file (.qmodel.npz). A qmodel file contains a probability vector for each read position. For details, please refer to the documentation.",
        action="store",
        dest="quality_model",
        default="L100-Q70-A",
        )

    dataset_group.add_argument(
        "--single-end", "--se",
        help="Write a single-end dataset. Only writes a p5 FASTQ file. Default: False",
        action="store_true",
        dest="single_end",
        default=False,
        )
    
    dataset_group.add_argument(
        "--overlap", "--ol",
        help="Overlap factor (between 0 and 1.0) of randomly generated reads. Default 0",
        action="store",
        dest="overlap",
        type=float,
        default=0,
        )

    dataset_group.add_argument(
        "--multiple-p7-barcodes", "--combine-p7-bcs",
        help="Combine individuals with multiple p7 barcodes in one output file. Default: False",
        action="store_true",
        dest="multiple_p7_bcs",
        default=False,
        )
    
    # coverage model parameters
    cov_group = parser.add_argument_group("Coverage Model Parameters")
    cov_group.add_argument(
        "--coverage-model",
        help="Model to choose coverage values. Can be either 'poisson' or 'betabinomial'. The Betabinomial model is the default as it can be easily adapted to different coverage profiles using the --BBD-alpha and --BBD-beta parameters.",
        action="store",
        dest="coverage_model",
        default="betabinomial",
        )

    cov_group.add_argument(
        "--BBD-alpha",
        help="Alpha parameter of the Beta-binomial distribution. Higher values increase the left tailing of the coverage distribution, if the BBD model is used. Default: 6",
        action="store",
        dest="bbd_alpha",
        type=float,
        default=6,
        )

    cov_group.add_argument(
        "--BBD-beta",
        help="Beta parameter of the Beta-binomial distribution. Higher values increase the right tailing of the coverage distribution, if the BBD model is used. Default: 2",
        action="store",
        dest="bbd_beta",
        type=float,
        default=2,
        )

    cov_group.add_argument(
        "--max-pcr-copies",
        help="Maximum number of PCR copies that can be created for each finalized (potentially mutated and multiplied) read. Default: 3",
        action="store",
        dest="max_pcr_copy_nr",
        type=int,
        default=3,
        )

    cov_group.add_argument(
        "--hrl-max-cov", "--hrl-max-coverage",
        help="Maximum coverage for Highly Repetitive Loci (HRLs) (per individual). The minimum coverage is determined as mean + 2 standard deviations of the main coverage generating function. Default: 1000",
        action="store",
        dest="hrl_max_cov",
        default=1000,
        )

    # Sequence Infos
    seqs_group = parser.add_argument_group("Read Sequences")
    seqs_group.add_argument(
        "-d", "--dbr",
        help="Sequence of the degenerate base region (DBR) in IUPAC ambiguity code. Default: 'NNNNNNMMGGACG'. To not include a DBR sequence use --dbr ''",
        action="store",
        type=str,
        dest="dbr",
        default="NNNNNNMMGGACG",
        )

    seqs_group.add_argument(
        "--p5-overhang",
        help="Sequence of the p5 overhang. Default: 'TGCAT'",
        action="store",
        type=str,
        dest="p5_overhang",
        default="TGCAT",
        )

    seqs_group.add_argument(
        "--p7-overhang",
        help="Sequence of the p7 overhang. Default: 'TAC'",
        action="store",
        type=str,
        dest="p7_overhang",
        default="TAC",
        )

    seqs_group.add_argument(
        "--p5-rec-site",
        help="Sequence of the p5 recognition site. Default: 'ATGCAT'",
        action="store",
        type=str,
        dest="p5_rec_site",
        default="ATGCAT",
        )

    seqs_group.add_argument(
        "--p7-rec-site",
        help="Sequence of the p7 recognition site. Default: 'GTCA'",
        action="store",
        type=str,
        dest="p7_rec_site",
        default="GTAC",
        )

    seqs_group.add_argument(
        "-b", "--barcodes",
        help="Path to barcodes file or predefined barcode set like 'barcodes', 'small', 'full' or 'full'. Default: 'barcodes', a generic population. Take a look at the rage/barcode_handler/barcodes folder for more information.",
        action="store",
        type=str,
        dest="barcode_set",
        default="full",
        )

    # probabilities
    probs_group = parser.add_argument_group("Simulation Probabilities")
    probs_group.add_argument(
        "--event-probabilities",
        help="Probability profile for the distribution of event types (common, dropout, mutation; in this order).\
              Example: ``python ddrage.py --event-probabilities 0.9 0.05 0.05`` -> common 90%%, dropout 5%%, mutation 5%% (Default).\
              Each entry can be given as a float or a string of python code (see example above) which is helpful for small probability values.",
        action="store",
        dest="event_prob_profile",
        metavar=("PROB_COMMON", "PROB_DROPOUT", "PROB_MUTATION"),
        nargs=3,
        default=None,
        )

    probs_group.add_argument(
        "--mutation-type-probabilities",
        help="Probability profile for the distribution of mutation types (snp, insertion, deletion, p5 na alternative, p7 na alternative, p5 na dropout, p7 na dropout; in this order).\
              Example: ``python ddrage.py --mutation-type-probabilities 0.8999 0.05 0.05 '0.0001*0.001' '0.0001*0.05' '0.0001*0.899' '0.0001*0.05'``\
              -> snp 89.99%%, insertion 5%%, deletion 5%%, p5 na alternative 0.00001%% , p7 na alternative 0.0005%%, p5 na dropout 0.00899%%, p7 na dropout 0.0005%% (Default).\
              Each entry can be given as a float or a string of python code (see example above) which is helpful for small probability values.",
        action="store",
        dest="mutation_type_prob_profile",
        metavar=("PROB_SNP", "PROB_INSERTION", "PROB_DELETION", "PROB_P5_NA_ALTERNATIVE", "PROB_P7_NA_ALTERNATIVE", "PROB_P5_NA_DROPOUT", "PROB_P7_NA_DROPOUT"),
        nargs=7,
        default=None,
        )

    probs_group.add_argument(
        "--prob-heterozygous",
        help="Probability of mutations being heterozygous. Default: 0.5",
        action="store",
        dest="prob_heterozygocity",
        type=float,
        default=0.5,
        )

    probs_group.add_argument(
        "--prob-incomplete-digestion",
        help="Probability of incomplete digestion for an individual at a locus. Default: 0.1",
        action="store",
        dest="prob_incomplete_digestion",
        type=float,
        default=0.1,
        )

    probs_group.add_argument(
        "--rate-incomplete-digestion",
        help="Expected fraction of reads that are being lost in the event of Incomplete Digestion. Default: 0.2",
        action="store",
        dest="rate_incomplete_digestion",
        type=float,
        default=0.2,
        )

    probs_group.add_argument(
        "--prob-pcr-copy",
        help="Probability that a (potentially mutated and multiplied) read will receive pcr copies. This influences the simulated pcr copy rate. Default: 0.2",
        action="store",
        dest="prob_pcr_copy",
        type=float,
        default=0.2,
        )

    probs_group.add_argument(
        "--hrl-pcr-copies",
        help="Probability of PCR copies for HRL reads in relation to normal reads. Default: 0.9, i.e. the probability for a PCR copy of a HRL read is prob_pcr_copy * hrl_pcr copies = 0.2 * 0.9 = 0.18",
        action="store",
        dest="hrl_pcr_copies",
        type=float,
        default=0.9,
        )

    probs_group.add_argument(
        "--singleton-pcr-copies",
        help="Probability of PCR copies for singleton reads in relation to normal reads. Default: 1/3, i.e. the probability for a PCR copy of a singleton read is prob_pcr_copy * singleton_pcr_copies = 0.2 * (1/3) = 0.0666...",
        action="store",
        dest="singleton_pcr_copies",
        type=float,
        default=(1/3),
        )

    probs_group.add_argument(
        "-e", "--prob-seq-error",
        help="Probability of sequencing substitution errors. Default: 0.01",
        action="store",
        dest="prob_seq_error",
        type=float,
        default=0.01,
        )

    # debug and output
    parser.add_argument(
        "-v", "--verbose",
        help="Increase verbosity of output.\n-v: Show progress of simulation.\n-vv: Print used parameters after simulation.\n-vvv: Show details for each simulated locus.",
        action="count",
        dest="verbosity",
        default=0,
        )

    parser.add_argument(
        "-z", "--zip",
        help="Write output as gzipped fastq.",
        action="store_true",
        dest="zip_output",
        default=False,
        )

    parser.add_argument(
        "--get-barcodes",
        help="Write copies of the default barcode files into the current folder. ",
        action="store_true",
        dest="get_barcodes",
        default=False,
        )

    parser.add_argument(
        "--DEBUG",
        help="Set debug-friendly values for the data set, i.e. all mutation events and mutation types are equally probable.",
        action="store_true",
        dest="debug_run",
        default=False,
        )

    return parser



if __name__ == "__main__":
    main()
