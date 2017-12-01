# -*- coding: utf-8 -*-

import random
import json
import datetime
import gzip
import pickle
from collections import defaultdict
from math import floor
import heapq

from cpinsim.abstract_simulation import AbstractSimulation
from cpinsim.protein import Protein


class InfiniteSimulation(AbstractSimulation):
    """ Simulation of interactions between proteins without regard to protein
        positions (infinte radius interaction radius). Interactions can happen
        between all possible interactors if no constraints are violated.
    """

    def __init__(self, proteins, concentrations, num_copies,
                 perturbed_proteins, output_log, output_graph):
        """ Generate a list and sample a start assignment of $proteins. Either
            each protein has $num_copies copies or each protein is draw according
            to it concentration.
        """
        AbstractSimulation.__init__(self, output_log)
        print(datetime.datetime.now(), "begin of __init__", sep='\t', file=self.output_log)

        self.proteins = proteins
        self.num_copies = num_copies

        self.protein_instances = []
        self.map_protein_positions = defaultdict(list)

        if output_graph is not None:
            if output_graph[-2:] == "gz":
                self.output_graph_path = gzip.open(output_graph, 'wb', compresslevel=4)
            else:
                self.output_graph_path = gzip.open(output_graph+".gz", 'wb', compresslevel=4)
        else:
            self.output_graph_path = None

        if concentrations is not None:
            max_protein_instances, concentrations = concentrations
            max_protein_instances = int(max_protein_instances)
        parsed_concentrations = self.parse_concentrations(concentrations)
        protein_copies = dict()

        if num_copies is not None:
            for protein in proteins:
                protein_copies[protein] = num_copies

        if parsed_concentrations is not None:
            sum_proteins = 0
            remainder_list = []
            for protein, con in parsed_concentrations:
                exact_number = con * max_protein_instances
                rounded_number = floor(exact_number)
                remainder = exact_number - rounded_number
                remainder_list.append((protein, remainder))
                sum_proteins += rounded_number
                protein_copies[protein] = rounded_number
            lacking = max_protein_instances - sum_proteins
            for protein, remainder in heapq.nlargest(lacking, remainder_list, key=lambda x: x[1]):
                protein_copies[protein] += 1

        self.perturbed_proteins = perturbed_proteins
        if self.perturbed_proteins != None:
            for name, factor in self.perturbed_proteins:
                factor = float(factor)
                protein_copies[name] = int(protein_copies[name]*factor)

        count = 0
        for name in proteins.keys():
            p = proteins[name]
            for i in range(protein_copies[name]):
                self.protein_instances.append(Protein(name, p))
                self.map_protein_positions[name].append(count)
                self.map_positions_protein[count] = name
                self.num_protein_instances += 1
                count += 1

        self.positions = list(range(self.num_protein_instances))
        for pos in self.positions:
            self.interactions.add_node(pos, name=self.get_protein(pos).name)

        self.number_of_singletons = self.num_protein_instances
        print(datetime.datetime.now(), "end of __init__", sep='\t', file=self.output_log)


    def get_protein(self, pos):
        """ Return the protein at the given postion.
        """
        return self.protein_instances[pos]


    def sample_interactor(self, protein, pos):
        """ Sample a protein for association with $protein.
        """
        possible_interactors = list(protein.get_possible_interactors())
        random.shuffle(possible_interactors, random.random)
        for interactor in possible_interactors: # Go to each possbile interactor in random order
            interactor_postitions = self.map_protein_positions[interactor]
            if len(interactor_postitions) == 0:
                continue
            # Test up to 50 posititions until you find a possible interaction
            for i in range(50): #TODO: Determine sensible threshold
                index = random.choice(interactor_postitions)
                if index != pos and not (self.interactions.has_edge(pos, index) or self.interactions.has_edge(index, pos)):
                    return (self.get_protein(index), index)
        return (None, None)


    def simulate_network(self, steps, association_probability, dissociation_probability):
        """ Simulate the Simulation with $steps.
        """
        # header in JSON format
        print(json.dumps({"num_protein_instances": self.num_protein_instances, "number of copies": self.num_copies, "steps": steps, "dissociation_probability": dissociation_probability, "association_probability": association_probability}, sort_keys=True), file=self.output_log)
        print(datetime.datetime.now(), "initial start of simulation", sep='\t', file=self.output_log)
        #self.writer("\n")

        for t in range(1, steps+1):
            if self.simulate_interaction_step(association_probability, dissociation_probability, t):
                print(datetime.datetime.now(), "####", "convergence test triggered after step", t, sep='\t', file=self.output_log)
                break

        # After meeting convergence criterion repeat same number of steps
        for i in range(t):
            self.simulate_interaction_step(association_probability, dissociation_probability, t+i+1)

        # Save graph datastructure via pickling
        if self.output_graph_path:
            output_graphstring = pickle.dumps(self.interactions)
            self.output_graph_path.write(output_graphstring)

