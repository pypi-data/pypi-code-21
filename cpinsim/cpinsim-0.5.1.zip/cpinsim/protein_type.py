# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
from bitarray import bitarray


def read_proteins(filename):
    """ Read the text representation of the proteins into the following data
        structure: Each protein has a index (PxD->N) and an array to determine
        the possible interactions. In the array for each interactor (PxD) there
        are clauses representing the constraints. Each clause consists of two
        bitarrays (positive and negative).
    """
    proteins = dict()
    name = ""
    # read the information for one protein, then build the corresponding array
    reader = csv.reader(open(filename, newline=''), delimiter='\t')
    for line in reader:
        # skip empty lines
        if line == "\n" or len(line) == 0:
            continue
        # beginning of new protein in file
        if line[0][0] == ">":
            if name != "": # do not build array yet if first protein
                index = build_index(interactors)
                protein_array = build_array(index, interactions)
                proteins[name] = ProteinType(name, index, protein_array)

            name = line[0][1:]
            # new protein has new interactors and new interactions
            interactors = set()
            interactions = defaultdict(list)
            continue
        # parse transitions into dictionary
        else:
            interactor, *constraints = line
            interactor = tuple(interactor.replace("(", "").replace(")", "").split(","))
            interactors.add(interactor)
            for clause in constraints:
                terms = clause.split(";")
                split_terms = [tuple(term.replace("(", "").replace(")", "").split(",")) for term in terms]
                interactions[interactor].append(split_terms)

    # for last protein in file:
    index = build_index(interactors)
    protein_array = build_array(index, interactions)
    proteins[name] = ProteinType(name, index, protein_array)

    return proteins


def build_index(interactors):
    """ Build the index (P x D) -> N for all interactors of the current protein.
    """
    index = dict() # P x D -> N
    sorted_interactors = sorted(list(interactors))
    for p, d in sorted_interactors:
        index[(p, d)] = sorted_interactors.index((p, d))
    return index


def build_array(index, interactions):
    """ Build the array for the current protein. In the first dimension there
        is an entry for each interactor. In the second dimension there are the
        constraints represented as clauses consisting of two bitarrays.
    """
    return [[build_bitarray(index, clause) for clause in interactions[interactor]] for interactor in sorted(index, key=index.__getitem__)]


def build_bitarray(index, clause):
    """ Construct the two bitarrays positive and negative for a given clause.
        The positive array has a 1 for each protein that has to be bound already
        for an interaction to be possible, while in the negative array the bits
        are set for competitions and inhibitions.
    """
    positive = bitarray(len(index))
    positive.setall(False)
    negative = bitarray(len(index))
    negative.setall(False)

    for protein, domain in clause:
        # set bits in negative-array
        if protein[0] == "-":
            # special case for occupied domains
            if protein[1] == "*":
                for p, d in index:
                    if d == domain:
                        negative[index[(p, d)]] = True
            else:
                negative[index[(protein[1:], domain)]] = True # [1:] to cut of the "-"

        # set bits in positive-array
        else:
            positive[index[(protein, domain)]] = True
    #print(clause, positive, negative)
    return (positive, negative)


class ProteinType:
    """ A class for the different protein types. Each protein type consists of
        a name, an index for the possible combinations of proteins and domains
        and the array describing the constraints for interactions.
    """

    def __init__(self, name, index, interactions):
        """ Initialize a protein with its name, index and possible interactions.
        """
        self.name = name
        self.index = index
        self.interactions = interactions

        self.domains = set()
        self.map_interactor_domains = defaultdict(set)
        for p, d in self.index:
            self.map_interactor_domains[p].add(d)
            if not self.are_domains_overlapping(self.domains, d):
                self.domains.add(d)


    def are_domains_overlapping(self, domains, new_domain):
        """ Test if at least one domain in the set domains is overlapping with the new_domain.
        """
        min2, *max2 = new_domain.split("-")
        if max2 == []:  # new_domain is not an interval
            return False

        for d in domains:
            min1, *max1 = d.split("-")
            if max1 == []: # d is not an interval
                continue

            cut0, cut1 = max(int(min1), int(min2)), min(int(max1[0]), int(max2[0]))
            if cut1 - cut0 > 0:
                return True
        return False


