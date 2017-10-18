# -*- coding: utf-8 -*-
"""This module contains classes and a mutation model.

These are used to create a tree structure of mutations
using a phylogenetic process.
"""
import random
import copy
import sys
import itertools

from . import rad_locus
from . import distributions
from .generation import random_seq

# This is queried to make sure, that SNPs really change the
# perceived base. For example a C -> C SNP can not be reasonably detected.
not_this = dict({
    "A": ("C", "G", "T"),
    "C": ("A", "G", "T"),
    "G": ("A", "C", "T"),
    "T": ("A", "C", "G"),
    b"A": (b"C", b"G", b"T"),
    b"C": (b"A", b"G", b"T"),
    b"G": (b"A", b"C", b"T"),
    b"T": (b"A", b"C", b"G"),
    65: (67, 71, 84),
    67: (65, 71, 84),
    71: (65, 67, 84),
    84: (65, 67, 71),
})


class MutPosError(Exception):
    """Error signifying, that no mutation positions are remaining in the read."""
    pass


class Mutation:
    """Base class for all mutation types.

    Every types implements a __repr__ method that is used for annotating fastq
    files.

    SNPs:     p5@33(54):A>T
    Insert:   p7@20:+ACG
    Deletion: p5@42:-6
    p7NA:     p7:NA
    """
    def __repr__(self):
        return self.annotation_entry()

    def _str_mate(const, mate):
        if mate in ("p5", 0):
            return "p5"
        elif mate in ("p7", 1):
            return "p7"
        else:
            raise ValueError("Invalid mate information: {}".format(mate))


class SNPMutation(Mutation):
    """Represents a single SNP mutation.

    Arguments:
        mate (int): 0 for "p5" or 1 for "p7"
        pos (int): position relative to the common sequence
        base_from (bytes): Old base
        base_to (bytes): New base
    """
    def __init__(self, mate, pos, base_from, base_to):
        self.mate = mate
        self.pos = pos
        self.base_from = base_from
        self.base_to = base_to

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return [(self.mate, self.pos)]

    def annotation_entry(self, offset=False):
        """Example: p5@33(54):A>T
        
        The positions denote genomic sequence pos (first) and read pos (second)
        """
        if offset:
            return "{}@{}({}):{}>{}".format(
                self._str_mate(self.mate),
                self.pos + offset,
                self.pos,
                chr(self.base_from),
                chr(self.base_to),
                )
        else:
            return "{}@{}:{}>{}".format(
                self._str_mate(self.mate),
                self.pos,
                chr(self.base_from),
                chr(self.base_to),
                )


class InsertMutation(Mutation):
    """Represents a single insert mutation:
    
    Arguments:
        mate (int): 0 for "p5" or 1 for "p7"
        pos (int): position relative to the common sequence
        seq (bytes): inserted sequence
    """
    def __init__(self, mate, pos, seq):
        self.mate = mate
        self.pos = pos
        self.seq = seq

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return []

    def annotation_entry(self, offset=False):
        """Example: p7@20(43):+ACG"""
        if offset:
             return "{}@{}({}):+{}".format(
                 self._str_mate(self.mate),
                 self.pos + offset,
                 self.pos,
                 self.seq.decode(),
                 )
        else:
             return "{}@{}:+{}".format(
                 self._str_mate(self.mate),
                 self.pos,
                 self.seq.decode(),
                 )


class DeletionMutation(Mutation):
    """Represents a single deletion mutation:
    
    Arguments:
        mate (int): 0 for "p5" or 1 for "p7"
        pos (int): position relative to the common sequence
        length (int): Length of deleted sequence
    """
    def __init__(self, mate, pos, length):
        self.mate = mate
        self.pos = pos
        self.length = length
        # the del seq has to be set by the read and can not be know
        # at instantiation time. set this after applying the mutation
        self.del_seq = None

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        # All deleted positions in the common string
        # since deletions are reaslized as
        # seq[:pos] + seq[pos + len:]
        # the affected position are pos, pos+1, ..., pos+(len-1)
        return [(self.mate, pos) for pos in range(self.pos, self.pos + self.length)]

    def annotation_entry(self, offset=False):
        """Example: p5@42(65):-6"""
        # if the mutaion has been applied and the 
        # deleted sequence is know use it.
        # Use the length of the deletion otherwise
        if self.del_seq is None:
            del_seq = self.length
        else:
            del_seq = self.del_seq.decode()

        if offset:
            return "{}@{}({}):-{}".format(
                self._str_mate(self.mate),
                self.pos + offset,
                self.pos,
                del_seq,
                )
        else:
            return "{}@{}:-{}".format(
                self._str_mate(self.mate),
                self.pos,
                del_seq,
                )


class P7NAAlternative(Mutation):
    """Represents the presence of a p7 NA."""
    def __init__(self, seq):
        self.seq = seq
        self.mate = 1
        self.pos = -1 # dummy value for sorting

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return "all p7"

    def annotation_entry(self, offset=0):
        return "p7:NA_alternative"


class P5NAAlternative(Mutation):
    """Represents the presence of a p7 NA."""
    def __init__(self, seq):
        self.seq = seq
        self.mate = 0
        self.pos = -1 # dummy value for sorting

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return "all p5"

    def annotation_entry(self, offset=0):
        return "p5:NA_alternative"


class P7NADropout(Mutation):
    """Represents the presence of a p7 NA."""
    def __init__(self):
        self.seq = None
        self.mate = 1
        self.pos = -1 # dummy value for sorting

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return "all"

    def annotation_entry(self, offset=0):
        return "p7:NA_dropout"

class P5NADropout(Mutation):
    """Represents the presence of a p7 NA."""
    def __init__(self):
        self.seq = None
        self.mate = 0
        self.pos = -1 # dummy value for sorting

    def affected_positions(self):
        """The positions of the wildtype seq that are affected by this Mutation."""
        return "all"

    def annotation_entry(self, offset=0):
        return "p5:NA_dropout"
    

# SNPs should be applied first
# after this, inserts and deletions
# finally p7 NAs, since they change the whole sequence
MUTATION_PRIORITY = {
    SNPMutation: 0,
    InsertMutation: 1,
    DeletionMutation: 1,
    P7NAAlternative: 3,
    P5NAAlternative: 4,
    P7NADropout: 5,
    P5NADropout: 6,
    }

def mut_application_order(key):
    return (MUTATION_PRIORITY[type(key)], key.mate, key.pos)

def mut_position(key):
    return (key.mate, key.pos)


class Allele:
    """This class models a single allele in a Mutation Model.

    A allele consists of a rad read, a list of mutations in
    pos -> base_from, base_to format and a parent allele.
    The parent allele is None for the wilt type allele.

    The combination of two alleles defines a genotype.
    """

    def __init__(self, read, p5_na_seq, p7_na_seq, single_end, mutations=None, name=None, *,
                 parent=None, has_p5_mutation=False, has_p7_mutation=False,
                 p5_length_variability=3
                 ):
        """Create a new allele.

        Arguments:
            read (RadRead): The template read.
            p5_na_seq (bytes): The sequence used for p5 null alleles at this locus.
            p7_na_seq (bytes): The sequence used for p7 null alleles at this locus.
            single_end (bool): Flag to restrict mutating positions to the p5 read.
            mutations (list): A list of Mutation objects.
            name: An arbitrary identifier for the allele. The default are incrementing
                integers, handled by MutationModel.

        Keyword Arguments:
            parent (Allele): The allele from which this one is derived.
            has_p5_mutation (bool): Does this allele affect the p5 read? (Default: False)
            has_p7_mutation (bool): Does this allele affect the p7 read? (Default: False)
            p5_length_variability (int): Length of the unmutating tail of the p5 sequence that
                will be enforced in order to prevent mutations that are later cut off due to
                length adjustment because of different insert length of different individuals.
                (Extremely reduced) Example: insert 1: '', insert 2: 'CAT', seq: "GATTACA"
                seq 1: -GATTACA |, seq 2: CAT-GATT |ACA, where the ACA of seq 2 will be truncated
                to fit the length of seq 1.
                Default: 3 (Maximal possible length difference between inserts -> max length of the
                truncated sequence).
        """
        self.read = read
        self.p5_na_seq = p5_na_seq
        self.p7_na_seq = p7_na_seq
        self.parent = parent
        self.p5_length_variability = p5_length_variability
        self.has_p5_mutation = has_p5_mutation
        self.has_p7_mutation = has_p7_mutation
        self.name = name
        self.single_end = single_end
        if mutations:
            self.mutations = mutations
        else:
            self.mutations = []

    @classmethod
    def copy(cls, allele, name=None):
        """Create a new allele as a copy (and child) of an existing one.

        Arguments:
            allele(Allele): The template allele that will be copied.
                All of its attributes will be copied using copy.deepcopy,
                and the parent of the new Allele will be set to this Allele.
            name: An arbitrary identifier for the allel. The default are incrementing
                integers, handled by MutationModel.

        Returns:
            Allele: A new Allele object, inheriting all mutations from the
            passed allele.
        """
        # copy unchanged attributes
        read = copy.deepcopy(allele.read)
        p5_na_seq = copy.deepcopy(allele.p5_na_seq)
        p7_na_seq = copy.deepcopy(allele.p7_na_seq)
        mutations = copy.deepcopy(allele.mutations)
        return cls(
            read,
            p5_na_seq,
            p7_na_seq,
            allele.single_end,
            mutations,
            name=name,
            parent=allele,
            has_p5_mutation=allele.has_p5_mutation,
            has_p7_mutation=allele.has_p7_mutation,
        )

    def get_mutated_positions(self):
        """Compute affected sequence positions from list of mutation
        
        Arguments:
            mutations (iterable of Mutation subclasses): The mutations already applied.

        Returns:
            set(tuple): mate, position tuples describing all positions already
            affected by mutations.
        """
        all_mut_pos = []
        for mutation in self.mutations:
            affected_pos = mutation.affected_positions()
            if affected_pos == "all p7":
                # handle p7 null alleles
                _, p7_seq = self.read.seqs()
                all_mut_pos.extend([(1, pos) for pos, _ in enumerate(p7_seq)])
            elif affected_pos == "all p5":
                # handle not implemented p5 null alleles
                p5_seq, _ = self.read.seqs()
                all_mut_pos.extend([(0, pos) for pos, _ in enumerate(p5_seq)])
            elif affected_pos == "all":
                # handle not implemented p5 null alleles
                p5_seq, p7_seq = self.read.seqs()
                all_mut_pos.extend([(0, pos) for pos, _ in enumerate(p5_seq)])
                all_mut_pos.extend([(1, pos) for pos, _ in enumerate(p7_seq)])
            else:
                # add all affected positions toi a set
                all_mut_pos.extend(affected_pos)
        return set(all_mut_pos)

    def still_unmutated_positions(self, min_del_length=0):
        """Assemble a list of positions still eligible for mutations.

        Arguments:
            min_del_length (int): Minimal length of deletion mutations
                considered. This is to assure that no snps are removed.

        Returns:
            tuple: All positions viable for mutations.
        """
        # create collection of positions that can still mutate
        p5_seq, p7_seq = self.read.seqs()
        # place no mutations in the tail of the p5 sequence, because they might
        # be truncated in a later step in order to fit the size restrictions
        # of the reads.
        p5_positions = set(zip(itertools.repeat(0), range(len(p5_seq) - self.p5_length_variability)))
        # This is not nessecary for p7 reads
        p7_positions = set(zip(itertools.repeat(1), range(len(p7_seq))))
        if self.single_end:
            # use only p5_positions here for single end mode
            all_positions = p5_positions
        else:
            all_positions = p5_positions | p7_positions # unite both sets to use both reads
        already_mutated_positions = self.get_mutated_positions()
        all_unmutated_positions = tuple(all_positions - already_mutated_positions)
        # check if the following positions are in the set
        # to determine, if a deletion with min_del_length does fit
        # in this position
        unmutated_positions = []
        for (mut_strand, mut_pos) in all_unmutated_positions:
            min_length_satisfied = True
            for i in range(1,min_del_length):
                if (mut_strand, mut_pos + i) not in all_unmutated_positions:
                    # the position is already mutated and a deletion
                    # at mut_pos would obfuscate that
                    # hence, mut_pos is not a valid mutation position
                    min_length_satisfied = False
            if min_length_satisfied:
                unmutated_positions.append((mut_strand, mut_pos))

        if not unmutated_positions:
            error_message = "Ran out of positions to mutate. Please choose a longer read length or a lower diversity."
            raise MutPosError(error_message)
        else:
            return unmutated_positions

    def _mutation_entry(self, mutation):
        """Create a str representation of a single entry of self.mutated_positions"""
        return mutation.annotation_entry()

    def __str__(self):
        """Return one line output of the Allele with seq and all mutations."""
        return self.__repr__()

    def __repr__(self):
        """Create a line containing the sequences and append position and type of all mutations."""
        mutations = [self._mutation_entry(mutation) for mutation in sorted(self.mutations, key=mut_position)]
        mutations_str = ";  ".join(mutations)
        try:
            p5seq, p7seq = self.read.seqs()
        except AttributeError:
            p5seq, p7seq = b"-", b"-"
        if self.name is not None:
            return "{}: {} {} Mutations: {}".format(self.name, p5seq.decode(), p7seq.decode(), mutations_str)
        else:
            return "{} {} Mutations: {}".format(p5seq.decode(), p7seq.decode(), mutations_str)

    def log_format(self):
        """Return entry for logfile."""
        sorted_mutations = sorted(self.mutations, key=mut_position)
        if sorted_mutations:
            name = "allele {} with ".format(self.name)
            entries = []
            for mutation in sorted_mutations:
                entries.append(self._mutation_entry(mutation))
            return name + "; ".join(entries)
        else:
            return "the common allele"

    def add_snp(self):
        """Add a SNP to this Allele.

        The SNP will be at a previously unmutated position and will definitely
        be a different base than before.
        """
        possible_mutation_positions = self.still_unmutated_positions()
        # pick mutating position and new base
        mate, pos = random.choice(possible_mutation_positions)
        base = self.read[(mate, pos)]
        mutated_base = random.choice(not_this[base])

        self.mutations.append(SNPMutation(mate, pos, base, mutated_base))
        if mate == 0:
            self.has_p5_mutation = True
        else:
            self.has_p7_mutation = True

    def add_insert(self):
        """Add an insert to this Allele.

        The insert will be at a previously unmutated position.
        """
        insert_length = distributions.indel_length_generator.get_insert_length()
        insert_seq = random_seq(insert_length)
        possible_mutation_positions = self.still_unmutated_positions()

        # pick mutating position
        mate, pos = random.choice(possible_mutation_positions)
        self.mutations.append(InsertMutation(mate, pos, insert_seq))
        if mate == 0:
            self.has_p5_mutation = True
        else:
            self.has_p7_mutation = True

    def add_deletion(self):
        """Add a deletion to this Allele.

        The deletion will not remove other mutations.
        """
        deletion_length = distributions.indel_length_generator.get_deletion_length()
        possible_mutation_positions = self.still_unmutated_positions(min_del_length=deletion_length)

        # pick mutating position
        mate, pos = random.choice(possible_mutation_positions)
        self.mutations.append(DeletionMutation(mate, pos, deletion_length))
        if mate == 0:
            self.has_p5_mutation = True
        else:
            self.has_p7_mutation = True

    def add_p5_na_mut(self):
        """Add a Null Allele mutation to this allele.

        After this, no further mutations are added to the NA mate,
        but mutations already in there will just be overwritten.
        Those mutations can still be discovered in other alleles.
        """
        seq = self.p5_na_seq
        self.mutations.append(P5NAAlternative(seq))
        self.has_p5_mutation = True

    def add_p5_na_dropout(self):
        """Add a Null Allele mutation to this allele.

        After this, no further mutations are added to the NA mate,
        but mutations already in there will just be overwritten.
        Those mutations can still be discovered in other alleles.
        """
        self.mutations.append(P5NADropout())
        self.has_p5_mutation = True

    def add_p7_na_mut(self):
        """Add a Null Allele mutation to this allele.

        After this, no further mutations are added to the NA mate,
        but mutations already in there will just be overwritten.
        Those mutations can still be discovered in other alleles.
        """
        seq = self.p7_na_seq
        self.mutations.append(P7NAAlternative(seq))
        self.has_p7_mutation = True

    def add_p7_na_dropout(self):
        """Add a Null Allele mutation to this allele.

        After this, no further mutations are added to the NA mate,
        but mutations already in there will just be overwritten.
        Those mutations can still be discovered in other alleles.
        """
        self.mutations.append(P7NADropout())
        self.has_p7_mutation = True
    


            
    def fastq_header_annotations(self, p5_prefix_length, p7_prefix_length):
        """Return lists containing meta infos for p5 and p7 mutations.

        Arguments:
            p5_prefix_length (int): Length of the p5 prefix to correctly report positions
                of mutations in the read from positions of mutations in the sequence.
            p7_prefix_length (int): Length of the p7 prefix to correctly report positions
                of mutations in the read from positions of mutations in the sequence.

        Returns:
            tuple(list, list): One list for p5 and p7 read, each containing the str encoded
            information that should be added to the FASTQ header as strings.
        """
        only_p5_mutations = [mut for mut in sorted(self.mutations, key=mut_position) if mut.mate == 0]
        only_p7_mutations = [mut for mut in sorted(self.mutations, key=mut_position) if mut.mate == 1]
        # add up offsets from indels
        p5_mutations_offsets = []
        p7_mutations_offsets = []
        p5_offset = 0
        p7_offset = 0
        for mutation in only_p5_mutations:
            p5_mutations_offsets.append((mutation, p5_offset))
            if type(mutation) == InsertMutation:
                p5_offset += len(mutation.seq)
            elif type(mutation) == DeletionMutation:
                p5_offset += mutation.length
        for mutation in only_p7_mutations:
            p7_mutations_offsets.append((mutation, p7_offset))
            if type(mutation) == InsertMutation:
                p7_offset += len(mutation.seq)
            elif type(mutation) == DeletionMutation:
                p7_offset += mutation.length
        # assemble annotations, incorporating the indel offsets
        p5_annotations = [mut.annotation_entry(p5_prefix_length + offset) for (mut, offset) in p5_mutations_offsets]
        p7_annotations = [mut.annotation_entry(p7_prefix_length + offset) for (mut, offset) in p7_mutations_offsets]
        return (p5_annotations, p7_annotations)

    def has_na_mut(self):
        """Return True if the allele has an NA mutation.
        """
        for mutation in self.mutations:
            if type(mutation) in (P5NAAlternative, P7NAAlternative):
                return True
        return False

    def has_dropout(self):
        """Return True if the allele has an NA dropout mutation.
        """
        for mutation in self.mutations:
            if type(mutation) in (P5NADropout, P7NADropout):
                return True
        return False

    def has_p5_na(self):
        """Return the type of p5 NA mutation. The other kind is prohibited."""
        for mutation in self.mutations:
            if type(mutation) == P5NADropout:
                return "p5 na dropout"
            elif type(mutation) == P5NAAlternative:
                return "p5 na alternative"
        return False

    def has_p7_na(self):
        """Return the type of p5 NA mutation. The other kind is prohibited."""
        for mutation in self.mutations:
            if type(mutation) == P7NADropout:
                return "p7 na dropout"
            elif type(mutation) == P7NAAlternative:
                return "p7 na alternative"
        return False
        
    def prohibited_mutations(self):
        """Get mutations prohibited by this read.
        This is to make sure no NA type is added two times.
        """
        prohibited_mutations = []
        present_p5_na = self.has_p5_na()
        if present_p5_na:
            prohibited_mutations.append(present_p5_na)
        present_p7_na = self.has_p7_na
        if present_p7_na:
            prohibited_mutations.append(present_p7_na)
        return prohibited_mutations

    def has_na(self):
        for mutation in self.mutations:
            if type(mutation) in (P5NADropout, P5NAAlternative, P7NADropout, P7NAAlternative):
                return True
        return False

class MutationModel:
    """Model of mutations with treelike dependencies."""

    def __init__(self, read, p5_na_seq, p7_na_seq, p5_spacer_spare_seq, p7_spacer_spare_seq,
                 spare_sequence_p5, spare_sequence_p7, p5_longest_adaptor,
                 p7_longest_adaptor, p5_adaptor_length_var, p7_adaptor_length_var,
                 nr_alleles, mutation_type_probabilities, single_end):
        """Create structure from sample sequence with a fixed nr of different alleles.

        Arguments:
            read (RADRead): A mate pair read in respect to which mutations will be generated.
            p5_na_seq (bytes): Null Allele sequence for the locus, i.e. the sequence after 
                the next common restriction site. This is used by all individuals at the locus
                as sequence for NA and ID events.
            p7_na_seq (bytes): Null Allele sequence for the locus, i.e. the sequence after 
                the next common restriction site. This is used by all individuals at the locus
                as sequence for NA and ID events.
            p5_spacer_spare_seq (bytes): Sequence bases that are pushed from the read by p5 spacer
                length variability. These will be used to fill up reads that are shortened
                by deletions.
            p7_spacer_spare_seq (bytes): Seqeunce bases that are pushed from the read by p7 spacer
                length variability. These will be used to fill up reads that are shortened
                by deletions.
            spare_sequence_p5 (bytes): Common sequence after the end of the p5 read. If additional bases 
                are required due to deletion mutations, all individuals take them from this
                sequence to be consistent.
            spare_sequence_p7 (bytes): Common sequence after the end of the p7 read. If additional bases 
                are required due to deletion mutations, all individuals take them from this
                sequence to be consistent.
            nr_alleles (int): Number of alleles that will be created.
            mutation_type_probabilities (dict): Dictionary mapping mutation type events
                (snp, insert, deletion na) to probabilities (which sum up to 1).
            single_end (bool): Flag to restrict mutations to the p5 read.
        """
        self.single_end = single_end
        self.p5_na_type = None
        self.p7_na_type = None
        if isinstance(read, rad_locus.RADRead):
            g = Allele(read, p5_na_seq, p7_na_seq, single_end=self.single_end, name=0)
        else:
            raise ValueError("A RADRead object has to be provided as reference!")
        self.mutation_type_probabilities = mutation_type_probabilities
        self._next_name = 1
        self.common = g
        self.alleles = [g]
        self.add_alleles(nr_alleles)
        self.has_p5_mutation_allele = False
        self.spare_sequence_p5 = spare_sequence_p5
        self.spare_sequence_p5_spacer = p5_spacer_spare_seq
        self.spare_sequence_p7 = spare_sequence_p7
        self.spare_sequence_p7_spacer = p7_spacer_spare_seq
        self.p5_longest_adaptor = p5_longest_adaptor
        self.p7_longest_adaptor = p7_longest_adaptor
        self.p5_adaptor_length_var = p5_adaptor_length_var
        self.p7_adaptor_length_var = p7_adaptor_length_var

    def prohibited_mutations(self):
        """Return mutation types prohibited by the model.

        This is to prevent two different types of na mutation to arise
        at one, i.e. p5 NA dropout and p5 NA mutation, since these
        can not occur at the same locus.
        """
        prohibited_mutations = []
        if self.p5_na_type == "p5 na dropout":
            prohibited_mutations.append("p5 na alternative")
        elif self.p5_na_type == "p5 na alternative":
            prohibited_mutations.append("p5 na dropout")
        if self.p7_na_type == "p7 na dropout":
            prohibited_mutations.append("p7 na alternative")
        elif self.p7_na_type == "p7 na alternative":
            prohibited_mutations.append("p7 na dropout")
        return prohibited_mutations

    def add_alleles(self, nr_alleles):
        """Add new alleles with to the model.

        Arguments:
            nr_alleles (int): Number of additional alleles that will be added.
        """
        for _ in range(nr_alleles):
            # find a parent allele that can still be mutated
            # at least the root allele should always be available
            keep_searching = True
            tries = 0
            while keep_searching:
                
                parent_allele = random.choice(self.alleles)
                if parent_allele.has_dropout():
                    tries += 1
                    if tries >= 1000:
                        error_message = "Ran out of positions to mutate. Please choose a longer read length or a lower diversity."
                        raise MutPosError(error_message)
                try:
                    # if unmutated positions can be found
                    # terminate the search
                    parent_allele.still_unmutated_positions()
                    keep_searching = False
                except MutPosError as mpe:
                    # no unmutated positions left in the parent.
                    # keep searching
                    tries += 1
                    # after too many tries escalate the problem
                    if tries >= 1000:
                        raise mpe
                    continue
            
            new_allele = Allele.copy(parent_allele, name=self._next_name)
            self._next_name += 1

            # Can be prohibited by locus (example: one p5 dropout -> no more p5 mutation)
            # Can be prohibited by parent (example: p5 na alternative already present -> no more p5 na alternative)
            prohibited_mutations = new_allele.prohibited_mutations() + self.prohibited_mutations()
            # pick mutation type
            if prohibited_mutations:
                mutation_type = distributions.distributed_mutation_type(self.mutation_type_probabilities)
            else:
                mutation_type = distributions.distributed_mutation_type(self.mutation_type_probabilities, prohibited=prohibited_mutations)


            # Check here:
            # has a p5 na been added? -> no other p5 na
            # has a p7 na been added? -> no ther p7 na
            #### solved:  has a dropout been added? -> can no longer be parent
            #### solved:  no valid parents remaining? -> warn the user (extremely unlikely, since the root
            # allele is always present; can only happen if only NAs are allowed and have already been added.)
            # however in that case, duplicate alleles could arise.
            # That would not be bad, since multiple mutations can erode the enzyme binding site
            # which can be simulated by 'identical' alleles.

            # TODO: check for self.na_type
            
            
            # validate mutation type, especially prevent adding double null alleles
            if mutation_type == "p7 na alternative" and parent_allele.has_na_mut():
                if self.mutation_type_probabilities["p7 na alternative"] == 1.0:
                    # Only null alleles can be chosen and a na is already present
                    # in the allele. No new mutation and allele are added
                    return
                elif self.mutation_type_probabilities["p7 na alternative"] > 0.99:
                    # almost only nas can be chosen.
                    # print a warning for the user and continue searching for
                    # a different mutation type
                    error_message = """Warning: A null allele has already been added to the model.

                    Since null alleles are extremely likely in the current model (P(p7 na alternative) = {})
                    finding valid mutation types might be slow.
                    """.format(self.mutation_type_probabilities["p7 na alternative"])
                    print(error_message, file=sys.stderr)
                # search for a different mutation type until it is no longer 'na'
                while mutation_type == "p7 na alternative":
                    mutation_type = distributions.distributed_mutation_type(self.mutation_type_probabilities)
            elif mutation_type == "na" and self.single_end:
                # p7 NAs can not be added to single end reads.
                # reroll, until a non-na mutation is chosen.
                while mutation_type == "na":
                    mutation_type = distributions.distributed_mutation_type(self.mutation_type_probabilities)

            try:
                if mutation_type == "snp":
                    new_allele.add_snp()
                elif mutation_type == "insert":
                    new_allele.add_insert()
                elif mutation_type == "deletion":
                    new_allele.add_deletion()
                elif mutation_type == "p5 na alternative":
                    new_allele.add_p5_na_mut()
                    self.p5_na_type = mutation_type
                elif mutation_type == "p7 na alternative":
                    new_allele.add_p7_na_mut()
                    self.p7_na_type = mutation_type
                elif mutation_type == "p5 na dropout":
                    new_allele.add_p5_na_dropout()
                    self.p5_na_type = mutation_type
                elif mutation_type == "p7 na dropout":
                    new_allele.add_p7_na_dropout()
                    self.p7_na_type = mutation_type
                else:
                    raise ValueError("Invalid mutation type {}".format(mutation_type))
            except MutPosError:
                raise 
            self.alleles.append(new_allele)

    def get_random_genotype(self):
        """Pick a random genotype, i.e. a combination of two alleles.
        
        Returns:
            tuple: Two alleles.
        """
        return random.sample(self.alleles, 2)

    def get_random_allele(self, *, exclude_common=True):
        """Return a random allele from the model.

        Keyword Argumnets:
            exclude_common (bool): Exclude the unmutated wilt type allele.
                Default: True

        Returns:
            Allele: A allele from the model.
        """
        if exclude_common:
            non_common_alleles = [g for g in self.alleles if g != self.common]
            return random.choice(non_common_alleles)
        else:
            return random.choice(self.alleles)

    def get_random_allele_p5(self, *,  exclude_common=True):
        """Return a random allele from the model, if possible with at least one p5 mutation.

        Note:
            If no allele with p5 mutation is present in this model a allele with 
            p7 mutations will be returned as fallback.

        Keyword Argumnets:
            exclude_common (bool): Exclude the unmutated common allele.
                Default: True

        Returns:
            Allele: A allele from the model.
        """
        if exclude_common:
            p5_mutating_alleles = [g for g in self.alleles if (g != self.common) and g.has_p5_mutation]
        else:
            p5_mutating_alleles = [g for g in self.alleles if g.has_p5_mutation]
        # If no allele has a p5 mutation, fall back to other alleles.
        if p5_mutating_alleles:
            return random.choice(p5_mutating_alleles)
        else:
            return self.get_random_allele()

    def __str__(self):
        """Get readble string representation showing all alleles as a list."""
        out = ["Alleles:"]
        out.extend([str(g) for g in self.alleles])
        return "\n".join(out)


# Special cases, kept as constats for easier assignment and comparison.
DROPOUT = Allele(read=None, p5_na_seq=None, p7_na_seq=None, single_end=None, mutations=None, name="Dropout")
NONE = Allele(read=None, p5_na_seq=None, p7_na_seq=None, single_end=None, mutations=None, name="None")


def classify_type(allele_1, allele_2):
    """Find out which type is encoded in the alleles.

    Arguments:
        allele_1 (Allele): The first allele of the genotype.
        allele_1 (Allele): The second allele of the genotype.

    Returns:
        string: Type of the allele combination. Can be 'valid with errors',
        'clear NA', 'skewed', 'dropout', 'valid'
    """
    if allele_1 == DROPOUT and allele_2 == DROPOUT:
        return "dropout"
    # the only remaining option is a valid locus
    else:
        return "valid"

