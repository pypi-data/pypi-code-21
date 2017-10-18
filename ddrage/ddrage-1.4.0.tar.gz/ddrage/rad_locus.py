# -*- coding: utf-8 -*-
"""This module contains the RADLocus class which is ddRAGE's pivotal data structure.

RADLocus relies heavily on the RADRead and ProtoRead classes from the
rad_reads module.
"""
import random
import string
import copy
import numpy as np
from functools import partial
from collections import Counter
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

from . import read_mutation_handling as rmh
from . import mutation_model
from . import distributions
from .generation import random_seq, p5_seq_from_fragment, p7_seq_from_fragment
from .distributions import ztpd as zero_truncated_poisson_distribution
from .rad_reads import RADRead, ProtoReadp5, ProtoReadp7
from .mutation_model import mut_position


POSSIBLE_TYPES = ("common", "mutation", "dropout")


class RADLocus:
    """Structure to contain several RAD reads from the same locus.

    Contains facilities to manage reads, compute statistics and derived values
    for the locus, such as allele frequency etc.
    Also provides methods to create lines for the TSV output.
    """
    
    def __init__(self, individuals, locus_name, args, fragment):
        """Create a new locus from a set of individuals and a p7 protoread.

        Create one read per locus, per individual as a starting point.
        Deviations, mutations and copies will be added later with the
        `simulate_individual_events` method.

        Arguments:
            individuals (iterable): A list containing the barcoding information
                for all individuals in the sample. For the structure of entries
                see the note below.
            protoread_p7 (ProtoReadP7): An unfinished read that will be the
                base for the p7 side of the locus.
            locus_name (str/int): Id of the locus. Should be unique.
            args (Argparse.Namespace): Containing the following parameters:
                rec_site_p5 (bytes): The recognition site of the used p5 enzyme.
                read_length (int): Total read length, including all auxiliary sequences.
    
                prob_seq_error (float): Probability for a sequencing error (base
                    change).
                diversity (float): Genetic diversity at this locus. Given as the lambda
                    parameter for the zero-truncated poisson distribution that regulates
                    the number of alleles per MutationModel. Default: 1.0
                gc_content (float): GC content of the simulated sequence.

        Note:
            The structure of an individual entry is as follows:
            ::

                (p5_barcode, p7_barcode), (p5_spacer, p7_spacer, individual_name, *meta_info) = individual
        """
        self.individuals = individuals
        self.locus_name = str(locus_name)
        self.prob_seq_error = args.prob_seq_error
        self.gc_content = args.gc_content
        self.single_end = args.single_end

        # this value will be overwritten in the get_allele_frequency method
        self.total_valid_coverage = 0
        # Variables to save the simulated effetcs for a locus
        self.assigned_types = {}
        self.assigned_alleles = {}
        self.allele_frequency = None
        self.coverage_frequency = None
        self.count_id = 0

        # use given fragment
        sequence_p5 = p5_seq_from_fragment(2 * args.read_length, fragment)
        sequence_p7 = p7_seq_from_fragment(2 * args.read_length, fragment)
        self.reads = []

        # copies are used here to prevent side effects down the line when adding mutations
        # especially to avoid adding the mutations to the same p7 read over and over again.
        for (barcode_p5, barcode_p7), (spacer_p5, spacer_p7, individual_name, *_) in individuals:
            # assemble meta information about this proto read pair
            meta_info = [
                "read_from:'{}'".format(individual_name),
                "at_locus:'{}'".format(locus_name),
                "p5_bc:'{}'".format(barcode_p5.decode()),
                "p7_bc:'{}'".format(barcode_p7.decode()),
                "rID:'{}'".format("".join([random.choice(string.ascii_lowercase) for _ in range(5)]))
                ]
            # calculate the prefix length and truncate the raw read sequence to match total read length
            prefix_length_p5 = ProtoReadp5.p5_prefix_length(barcode_p5, spacer_p5, args.p5_overhang)
            sequence_p5_truncated = sequence_p5[:args.read_length - prefix_length_p5]
            p7_read = ProtoReadp7(
                barcode_p7,
                spacer_p7,
                args.dbr,
                args.p7_overhang,
                args.p7_rec_site,
                args.gc_content,
                args.read_length,
                sequence_p7,
                )
            p5_read = ProtoReadp5(
                barcode_p5,
                spacer_p5,
                args.p5_overhang,
                args.p5_rec_site,
                args.read_length,
                args.gc_content,
                sequence=sequence_p5_truncated,
            )
            rad_read = RADRead.from_protoreads(
                p5_read, p7_read, individual_name, meta_info, self.single_end
            )
            self.reads.append(rad_read)

        self.initial_reads = [copy.deepcopy(read) for read in self.reads]

        # compute the variability in lengths due to differently sized spacer sequences
        # this is needed to correctly elongate reads which are shortened by deletions
        # 
        # for p7 reads: overhangs and DBR are fixed, but spacer and barcodes can vary
        all_spacer_lengths = [(len(spacer_p5), len(spacer_p7)) for _, (spacer_p5, spacer_p7, *_) in individuals]
        min_p5_spacer_length = min([p5_spacer_length for (p5_spacer_length, _) in all_spacer_lengths])
        max_p5_spacer_length = max([p5_spacer_length for (p5_spacer_length, _) in all_spacer_lengths])
        min_p7_spacer_length = min([p7_spacer_length for (_, p7_spacer_length) in all_spacer_lengths])
        max_p7_spacer_length = max([p7_spacer_length for (_, p7_spacer_length) in all_spacer_lengths])

        all_bc_lengths = [len(p5_bc) for (p5_bc, _), _ in individuals]
        min_p5_bc_length = min(all_bc_lengths)
        max_p5_bc_length = max(all_bc_lengths)

        p5_length_variability = (max_p5_spacer_length + max_p5_bc_length) - (min_p5_spacer_length + min_p5_bc_length)
        p7_length_variability = (max_p7_spacer_length) - (min_p7_spacer_length)  # Different lengths of index barcodes do not vary the read size.
        p5_longest_adaptor = max_p5_spacer_length + max_p5_bc_length
        p7_longest_adaptor = max_p7_spacer_length

        # keep bases that are truncated due to variable adapter lengths
        # example:
        # r1: (aux)A(seq)TT
        # r2: (aux)ACG(seq)
        # due to the shorter spacer (        self.spare_sequence_p5_spacer = p5_spacer_spare_seqA) in r1 two additional bases are present in the
        # genomic sequence. If deletions shorten the read, these need to be added,
        # before the common spare sequence can be used.
        p5_shortest_read_end = args.read_length - (max_p5_bc_length + max_p5_spacer_length + len(args.p5_overhang))
        p5_longest_read_end = args.read_length - (min_p5_bc_length + min_p5_spacer_length + len(args.p5_overhang))
        p7_shortest_read_end = args.read_length - (max_p7_spacer_length + len(args.dbr) + len(args.p7_overhang))
        p7_longest_read_end = args.read_length - (min_p7_spacer_length + len(args.dbr) + len(args.p7_overhang))
        # extract the bases that can be 'pushed out' of the read by
        # spacer length variability
        self.p5_spacer_spare_seq = sequence_p5[p5_shortest_read_end:p5_longest_read_end]
        self.p7_spacer_spare_seq = sequence_p7[p7_shortest_read_end:p7_longest_read_end]

        # compute spare sequence from which to take bases after if deletions have reduced the total read length
        # longest_possible_deletion = distributions.indel_length_generator.longest_possible_deletion()
        self.spare_sequence_p5 = sequence_p5[p5_longest_read_end:]
        self.spare_sequence_p7 = sequence_p7[p7_longest_read_end:]

        self.p5_null_allele_seq = random_seq(args.read_length, p=self.gc_content, excluded_motif=args.p5_rec_site)
        self.p7_null_allele_seq = random_seq(args.read_length, p=self.gc_content, excluded_motif=args.p7_rec_site)
        # pick a number of mutated alleles using a ztpd and the diversity parameter
        nr_alleles = zero_truncated_poisson_distribution(l=args.diversity)

        self.mutation_model = mutation_model.MutationModel(
            self.initial_reads[0],
            self.p5_null_allele_seq,
            self.p7_null_allele_seq,
            self.p5_spacer_spare_seq,
            self.p7_spacer_spare_seq,
            self.spare_sequence_p5,
            self.spare_sequence_p7,
            p5_longest_adaptor,
            p7_longest_adaptor,
            p5_length_variability,
            p7_length_variability,
            nr_alleles,
            args.mutation_type_prob_profile,
            self.single_end,
            )

        self.mutations_added = False
        # This denotes if the locus was used to create HRL reads in postprocessing
        self.is_hrl = False
        # this denotes whether the locus has been reduced in size after writing the reads
        self.burned = False

    def burn(self):
        """Remove everything from the locus that takes up space.

        Keep only stuff that is usable for statistics and logging.

        Removes:

            - self.reads
            - self.initial_reads

        Keeps:

            - self.nr_reads (keeps the last value before deleting. No longer updates after this)
            - self.p5_consensus_seq, self.p7_consensus_seq (Computed before deleting)
        """
        self.nr_reads = len(self)
        self.p5_consensus_seq, self.p7_consensus_seq = self.consensus_sequences()
        del self.reads
        del self.initial_reads
        self.burned = True

    def __len__(self):
        """Return the number of reads in the locus as length."""
        if not self.burned:
            return len(self.reads)
        else:
            return self.nr_reads

    def get_individual_names(self):
        """Return a list of all individual names at this locus."""
        return [name for  _, (_, _, name, *_) in self.individuals]

    def consensus_sequences(self):
        """Get the p5 and p7 consensus sequence of the Locus.

        Note:
            Sequences size varies due to spacer length.
            The consensus sequences are the shortest clean sequence at
            this locus. The legth of the p7 sequences does not change,
            as the spacers are always the same assuming the same p7
            barcode for all individuals.
            The length of p5 sequences can vary by ``max([len(spacer) for spacer in spacers])``
            which is the length of the longest spacer.

        Returns:
            tuple(bytes,bytes): The p5 and p7 consensus sequences of the locus.
        """
        if not self.burned:
            # p7 read has no spacer length variability, hence any sequence can be used
            _, p7_consensus_seq = self.initial_reads[0].seqs()
            # find the longest p5 sequence
            all_p5_seqs = [read.seqs()[0] for read in self.initial_reads]
            p5_consensus_seq = max(all_p5_seqs, key=len)
            return p5_consensus_seq, p7_consensus_seq
        else:
            # If the locus already has been burned, rely on precomputed sequence
            return self.p5_consensus_seq, self.p7_consensus_seq


    def get_individual_coverage(self):
        """Compute coverage per individual."""
        coverages = []
        for _, ((cov_1, cov_2), (allele_1, allele_2)) in self.assigned_alleles.items():
            if mutation_model.classify_type(allele_1, allele_2) != "dropout":
                coverages.append(cov_1 + cov_2)
        return coverages

    def get_allele_frequency(self):
        """Return the allele- and coverage freqeuncies at this locus.

        Returns:
            tuple(dict, dict): The first containing the allele 
            frequencies, mapping allele names to nr of observed
            individuals (count), total number of alleles and the ratio
            of count to total (allele frequency).
            The second dict maps name to coverage, total_coverage and
            the ration of coverage/total_coverage.
        
            If no alleles have been assigned, i.e. due to chance all
            individuals have been assigned 'dropout' type for this locus,
            just two empty dicts will be returned.
        """
        if self.allele_frequency is not None and self.coverage_frequency is not None:
            # make sure these are computed only once.
            # after these have been computed they should not change again
            return self.allele_frequency, self.coverage_frequency
        else:
            allele_counts = Counter()
            allele_coverage_counts = Counter()
            allele_frequency = {}
            coverage_frequency = {}
            individual_allele_coverage = {}
            # count all allele occurences
            for name, ((cov_1, cov_2), (allele_1, allele_2)) in self.assigned_alleles.items():

                if allele_1 == mutation_model.NONE:
                    allele_1 = allele_2
                if allele_2 == mutation_model.NONE:
                    allele_2 = allele_1
                    
                # classify which behaviour is shown by the selected genotype
                if allele_1 != mutation_model.DROPOUT and allele_2 != mutation_model.DROPOUT:
                    # both alleles are valid
                    # increase the allele tally and coverage tally for the two alleles
                    allele_counts[allele_1.name] += 1
                    allele_counts[allele_2.name] += 1
                    allele_coverage_counts[allele_1.name] += cov_1
                    allele_coverage_counts[allele_2.name] += cov_2
                    individual_allele_coverage[(name, allele_1)] = cov_1
                    # make sure the first allele information is not overwritten
                    # for homozygous alleles
                    if allele_1 == allele_2:
                        individual_allele_coverage[(name, allele_2)] += cov_2
                    else:
                        individual_allele_coverage[(name, allele_2)] = cov_2
                elif (allele_1 == mutation_model.DROPOUT and allele_2 == mutation_model.DROPOUT):
                    continue
                else:
                    raise ValueError("Invalid allele combination {}, {}".format(allele_1, allele_2))

            # compute total number of reads at locus (no PCR copies)
            total_coverage = sum(allele_coverage_counts.values())
            total_alleles = self.get_total_alleles()
            # no alleles have been assigned
            # return a valid response and call it a day
            if total_alleles == 0:
                self.allele_frequency = dict()
                self.coverage_frequency = dict()
                return dict(), dict()
            # compute frequencies and assemble output dictionary
            for allele, count in allele_counts.items():
                allele_frequency[allele] = (count, total_alleles, count/total_alleles)
            for allele, coverage in allele_coverage_counts.items():
                if total_coverage:
                    coverage_frequency[allele] = (coverage, total_coverage, coverage/total_coverage)  # TODO: check what happens for total coverage == 0
                else:
                    coverage_frequency[allele] = (0, 0, 0)
            # save the total coverage to be easily accessible later
            self.total_valid_coverage = total_coverage
            self.allele_frequency = allele_frequency
            self.coverage_frequency = coverage_frequency
            self.individual_allele_coverage = individual_allele_coverage
            return allele_frequency, coverage_frequency

    def get_total_alleles(self):
        """Return total number of alleles at this locus.

        Count all allele pairs, that can be reasonably interpreted.
        This means, that a Null Allele will be counted as valid,
        if it still contains a portion of unaffected reads.
        Please take a look at the documentation of NA-types for
        more information.

        Returns:
            int: Number of valid allele pairs.
        """
        valid_alleles = 0
        for _, (_, (allele_1, allele_2)) in self.assigned_alleles.items():
            if mutation_model.classify_type(allele_1, allele_2) not in ("dropout", ):
                valid_alleles += 2
        return valid_alleles

    def get_hrl_coverage(self):
        """Return coverage for HRL loci. This should not be used by other code."""
        if self.is_hrl:
            coverages = [(name, cov) for name, ((cov, _), _) in self.assigned_alleles.items()]
            return coverages
        else:
            return 0

    def get_number_of_mutations_per_ind(self):
        """Count the number of mutations assigned to each individual with a mutation event.

        Note:
            This counts unique mutations per individual.
            For an individual with `allele_1: p5@15:A>T` and 
            `allele_2: p5@15:A>T; p5@32:-TCGAGG` only two mutations
            are counted, because the first mutation occurs in both alleles.

        Returns:
            Counter: Tallied up number of mutations by individual.
        """
        nr_mutations_per_ind = Counter()
        for name, ((cov_1, cov_2), (allele_1, allele_2)) in self.assigned_alleles.items():
            unique_mutations = set(allele_1.mutations) | set(allele_2.mutations)
            nr_mutations_per_ind[name] += len(unique_mutations)
        return nr_mutations_per_ind

    def get_all_mutations(self):
        """Get a set of all mutations at this locus.

        Returns:
            set(Mutation): Set of all mutations affecteing this locus.
        """
        all_mutations = set()
        for name, ((cov_1, cov_2), (allele_1, allele_2)) in self.assigned_alleles.items():
            # update mutated position set
            # remember that | is the union operator for sets 
            all_mutations |= set(allele_1.mutations)
            all_mutations |= set(allele_2.mutations)
        return all_mutations

    def get_null_allele_counts(self):
        """Count the number of Null Allele events at this locus.

        Returns:
            Counter: mapping individual name to nr of null alleles
            for that individual at this locus.
        """
        null_allele_mutation_tally = Counter()
        null_allele_id_tally = Counter()
        # compare each allele against the placeholder constants that are set 
        # for mutation type and incomplete digetsion type null alleles.
        for name, (_, (allele_1, allele_2)) in self.assigned_alleles.items():
            null_allele_mutation_tally[name] += 1 if allele_1.has_na() else 0
            null_allele_mutation_tally[name] += 1 if allele_2.has_na() else 0
        return null_allele_mutation_tally

    def _add_common_reads(self, template_read, coverage):
        """Add plain copies to the locus.

        Arguments:
            template_read (RADRead): The template read that will be used for the created reads.
            coverage (int): Target coverage for the reads. This will be modified using a
                coverage distribution.
        """
        # zero coverage values can occur, if an ID completely depletes the modified reads
        # if coverage:


        # get reads from the factory function in mutations
        modified_reads = rmh.shallow_plain_copies(template_read, coverage)
        self._id_templates = (template_read, )
        # add generated reads to read pool at the locus
        self.modified_reads_at_locus.extend(modified_reads)

        # add event information to locus
        self.assigned_alleles[template_read.individual_name] = ((coverage, 0), (self.mutation_model.common, mutation_model.NONE))

    def _add_mutation_reads(self, template_read, coverage, args):
        """Add a mutation for this read at this locus.

        A random genotype is chosen for heterozygous mutations.

        Arguments:
            template_read (RADRead): Base for the mutations.
            coverage (int): Total coverage at this locus. For heterozygous,
                this is the sum of both alleles.
            args (argparse.Namespace): see above
        """
        # determine if the mutation will be heterozygous
        heterozygous = random.random() < args.prob_heterozygocity
        if heterozygous:
            # add mutations to an individuals reads
            # two alleles per individual, one of which can be the common allele
            self.assigned_types[template_read.individual_name] = "mutation heterozygous"
            if not self.mutation_model:
                self._compute_mutation_model()
            # call the factory function to generate copies
            mutated_copies = rmh.mutation_copies(template_read, coverage, True, self.mutation_model)
            (cov_allele_1, cov_allele_2), (reads_allele_1, reads_allele_2), (allele_1, allele_2) = mutated_copies
            # save template reads for ID generation
            # the branching is necessary to prevent index errors,
            # as it is not guaranteed that both alleles will
            # have coverage and hence reads

            if cov_allele_1:
                allele_1_id_template = reads_allele_1[0]
            elif allele_1.has_dropout():
                allele_1_id_template = None
            else:
                allele_1_id_template = rmh.get_id_template(template_read, allele_1, self.mutation_model)

            if cov_allele_2:
                allele_2_id_template = reads_allele_2[0]
            elif allele_2.has_dropout():
                allele_2_id_template = None
            else:
                allele_2_id_template = rmh.get_id_template(template_read, allele_2, self.mutation_model)

            if allele_1_id_template and allele_2_id_template:
                self._id_templates = (allele_1_id_template, allele_2_id_template)
            elif allele_1_id_template:
                self._id_templates = (allele_1_id_template, )
            elif allele_2_id_template:
                self._id_templates = (allele_2_id_template, )
            else:
                self._id_templates = []
                
            self.modified_reads_at_locus.extend(reads_allele_1)
            self.modified_reads_at_locus.extend(reads_allele_2)
            self.mutations_added = True
            self.assigned_alleles[template_read.individual_name] = ((cov_allele_1, cov_allele_2), (allele_1, allele_2))
        else:
            # add mutations to an individuals reads
            # only ONE allele per individual
            # this is guaranteed to not be the wilt type allele
            self.assigned_types[template_read.individual_name] = "mutation homozygous"
            if not self.mutation_model:
                self._compute_mutation_model()
            # call the factory function to generate copies
            coverage, modified_reads, allele = rmh.mutation_copies(template_read, coverage, False, self.mutation_model)
            if allele.has_dropout():
                self._id_templates = []
            else:
                self._id_templates = (modified_reads[0], )
            self.modified_reads_at_locus.extend(modified_reads)
            self.mutations_added = True
            self.assigned_alleles[template_read.individual_name] = ((0, coverage), (mutation_model.NONE, allele))

    def _add_dropout(self, template_read):
        """Remove template read for this individual and add no replacement.
        
        Note:
            This models missing information for this individual at this locus.
            The responsible factors for this can be manifold and will not be
            modeled. Exception: Null alleles, which are handled elsewhere.

        Arguments:
            template_read (RADRead): Read that will not be added. Used for
                documentation purposes only.
        
        """
        # add nothing and thereby remove initial version of the read.
        # there is no information from this individual at this locus.
        modified_reads = []
        self.modified_reads_at_locus.extend(modified_reads)
        self.assigned_alleles[template_read.individual_name] = ((0, 0), (mutation_model.DROPOUT, mutation_model.DROPOUT))

    def _add_id_reads(self, id_coverage):
        """Add incompletely digested reads to the locus.

        Arguments:
            id_coverage (int): Number of ID reads to be added.
        """
        rec_sites = (self._id_templates[0].protoread_p5.rec_site, self._id_templates[0].protoread_p7.rec_site)
        if len(self._id_templates) == 2:
            id_coverage_allele_1, id_coverage_allele_2 = distributions.heterozygous_mutation_distribution(id_coverage)
            id_reads_allele_1 = rmh.id_copies(self._id_templates[0], id_coverage_allele_1, rec_sites)
            id_reads_allele_2 = rmh.id_copies(self._id_templates[1], id_coverage_allele_2, rec_sites)
            id_reads = id_reads_allele_1 + id_reads_allele_2
        else:
            id_reads = rmh.id_copies(self._id_templates[0], id_coverage, rec_sites)
        self.modified_reads_at_locus.extend(id_reads)

    def simulate_individual_events(self, args):
        """Choose event types, create and add reads to locus, satisfying the types.

        Arguments:
            args (argparse namespace): Arguments object from argparse.

        Raises:
            ValueError: if an invalid locus type is chosen.
        """
        if args.verbosity >= 3:
            print("locus {}:\n".format(self.locus_name))

        template_reads = self.reads
        self.modified_reads_at_locus = []

        # Pick a number of indiviudal event types
        # matching the number of individuals at the locus.
        # The distribution of the types depends on the event probabilities
        # provided by the user. In a debug run all events are equally probable
        # while the default values reflect a realistic distribution.
        nr_events = len(template_reads)
        individual_event_types = distributions.distributed_events(
            nr_events, args.event_prob_profile)

        # Iterate through all existing (perfect) reads
        # and apply the selected types by dispatching calls
        # to the respective add_* method
        for template_read, individual_event_type in zip(template_reads, individual_event_types):
            if args.verbosity >= 3:
                print("{:>25}: {:>20}".format(template_read.individual_name, individual_event_type))

            # determine coverage
            coverage = distributions.normal_coverage_generator.get()
            id_coverage = None
            
            if random.random() < args.prob_incomplete_digestion:
                # Check if this individual at this locus has incomplete digestion
                # and reserve some coverage for that 
                coverage, id_coverage = distributions.incomplete_digestion_coverage(coverage, args.rate_incomplete_digestion)

            if individual_event_type == "common":
                self.assigned_types[template_read.individual_name] = individual_event_type
                self._add_common_reads(template_read, coverage)
            elif individual_event_type == "mutation":
                # assigned_type and count are added in _add_mutation_reads
                # as they depend on the zygosity, which is determined there
                self._add_mutation_reads(template_read, coverage, args)
            elif individual_event_type == "dropout":
                self.assigned_types[template_read.individual_name] = individual_event_type
                self._add_dropout(template_read)
            else:
                raise ValueError("Spectacular crash due to invalid locus type {}. This should never happen though!".format(individual_event_type))

            if (id_coverage is not None) and (individual_event_type != "dropout") and len(self._id_templates) >= 1:
                self.count_id += id_coverage
                self._add_id_reads(id_coverage)


        # Replace IUPAC characters with specific bases
        for read in self.modified_reads_at_locus:
            read.finalize_dbr()

        # Add PCR copies
        all_reads_at_locus = []
        self.nr_pcr_copies = 0
        for read in self.modified_reads_at_locus:
            if random.random() < args.prob_pcr_copy:
                # add original read
                all_reads_at_locus.append(read)
                # create and add PCR copies
                # pcr_copy_nr, copies = rmh.pcr_copies(read, args.max_pcr_copy_nr)
                pcr_copy_nr, copies = rmh.shallow_pcr_copies(read, args.max_pcr_copy_nr)
                all_reads_at_locus.extend(copies)
                self.nr_pcr_copies += pcr_copy_nr
            else:
                all_reads_at_locus.append(read)
        del self.modified_reads_at_locus # these are no longer needed
        # Drop perfect (initial) reads and only keep modified read set
        # The modified set also contains 'perfect' reads
        # Note that there is still a copy of the original reads for future
        # reference in the initial_reads attribute.
        self.reads = all_reads_at_locus
        # Add sequencing error
        self.add_sequencing_errors()

    def add_highly_repetitive_reads(self, args):
        """Add reads from a HRL to this locus. This affects all individuals
        and overrides all other locus types, etc.

        This locus will never be finished like a valid locus, but the 
        modified reads will be extracted directly from the HRL generator.
        
        Arguments:
            args (argparse namespace): Arguments object from argparse.

        Note:
            This should only be used by the HRL read generator from the
            postprocessor module in order to create HRL loci.

            The generated HRL reads are never added to the Locus.reads attribute
            in order to prevent mixups.
        """
        # mark that this locus is a HRL
        self.is_hrl = True
        template_reads = self.reads
        self.modified_reads_at_locus = []
        if args.verbosity >= 3:
            print("HRL {}\n".format(self.locus_name))
        for template_read in template_reads:
            hrl_coverage = distributions.hrl_coverage_generator.get()
            modified_reads = rmh.shallow_plain_copies(template_read, hrl_coverage, meta_info="type:'HRL copy'")
            self.modified_reads_at_locus.extend(modified_reads)
            self.assigned_alleles[template_read.individual_name] = ((hrl_coverage, 0), (self.mutation_model.common, self.mutation_model.common))
            if args.verbosity >= 3:
                print("HRL {}\n  Coverage: {}".format(self.locus_name, hrl_coverage))

    def add_sequencing_errors(self):
        """Add sequencing errors to both mates of all reads."""
        p_error = self.prob_seq_error
        for read in self.reads:
            read.add_seq_errors(p_error)

    def fastq_entries(self):
        """Create a list of FASTQ-entries from the locus.

        Returns:
            list: Containing `(p5_seq, p5_name, p5_qvs), (p7_seq, p7_name, p7_qvs)`
            for each read in the locus. 
        """
        return [read.fastq_entry() for read in self.reads]

    def yaml_entry(self):
        """Create a YAML entry for this locus.

        Notes:
            Each entry contains:
              - total locus coverage
              - p5 sequence
              - p7 sequence
              - allele frequencies for all alleles (dict: allele name -> freq)
              - allele coverage for all alleles (dict: allele name -> coverage)
              - individual info for individual x (dict: ind name ->):
                - allele name -> {cov: int, mutations: [list of str encoded mutations]}

        Returns:
            dict: Containing information about the locus and the alleles
            expressed by the individuals (see above).
        """
        # assemble locus data, allele frequency, total coverage etc.
        record = dict()
        p5_seq, p7_seq = self.consensus_sequences()
        record["p5 seq"] = p5_seq.decode()
        # record["p5 var length spare"] = self.p5_spacer_spare_seq.decode()
        # record["p5 spare"] = self.spare_sequence_p5.decode()
        if not self.single_end:
            record["p7 seq"] = p7_seq.decode()
            # record["p7 var length spare"] = self.p7_spacer_spare_seq.decode()
            # record["p7 spare"] = self.spare_sequence_p7.decode()
        allele_frequencies, coverage_frequencies = self.get_allele_frequency()
        # this needs to come after the call to get allele frequency
        # since the total valid coverage is computed there
        record["coverage"] = int(self.total_valid_coverage)
        # assemble mapping of allele names to frequencies and coverage
        record["allele frequencies"] = {allele_name: freq[2] for allele_name, freq in allele_frequencies.items()}
        record["allele coverages"] = {allele_name: int(freq[0]) for allele_name, freq in coverage_frequencies.items()}
        record["id reads"] = self.count_id

        # assemble individual information
        # including genotypes, individual coverages etc.
        record["individuals"] = dict()
        for ind_name, ((cov1, cov2), (allele1, allele2)) in self.assigned_alleles.items():
            record["individuals"][ind_name] = dict()
            if (cov1 > 0) or (cov1 == 0 and allele1.has_dropout()):
                a1 = {
                    "cov":int(cov1),
                    "mutations":[m.annotation_entry() for m in sorted(allele1.mutations, key=mut_position)],
                }
                record["individuals"][ind_name][allele1.name] = a1
            if (cov2 > 0) or (cov2 == 0 and allele2.has_dropout()):
                a2 = {
                    "cov":int(cov2),
                    "mutations":[m.annotation_entry() for m in sorted(allele2.mutations, key=mut_position)],
                }
                record["individuals"][ind_name][allele2.name] = a2
        return record
