# -*- coding: utf-8 -*-

import random
import sys
import datetime
import csv

import itertools
from scipy.stats import poisson
import networkx as nx


class AbstractSimulation:
    """ Functions for the simulation of interactions between proteins that are
        needed independently from the consideration of protein positions.
    """

    def __init__(self, output_log):
        """ Initialization of the abstract Simulation.
        """

        if output_log is not None:
            if output_log[-2:] == "gz":
                self.output_log = gzip.open(output_log, "wt", compresslevel=4)
            else:
                self.output_log = open(output_log, "wt")
        else:
            self.output_log = sys.stdout

        self.free = str("--")

        # nodes = proteinpositions with proteinname as label,
        # edges = interactions, have the used domains as attribute
        self.interactions = nx.Graph()
        self.positions = []

        self.map_positions_protein = dict()
        self.num_protein_instances = 0
        self.protein_instances = 0
        self.number_of_edges = 0
        self.number_of_singletons = 0

        # number of edges and complexes from last 10 steps, for recognizing convergence
        self.edgecount_ass = []
        self.edgecount_dis = []
        self.mean_edge_ass = 0
        self.mean_edge_dis = 0

        self.convergence_edge = None


    def parse_concentrations(self, concentrations):
        """ Parse the concentrations of the csv-file and and normalize them.
        """
        if concentrations is None:
            return concentrations
        parsed_concentrations = []
        sum_concentrations = 0
        reader = csv.reader(open(concentrations, newline=''), delimiter='\t')
        for name, value in reader:
            sum_concentrations += float(value)
            parsed_concentrations.append((name, float(value)))
        for i, (name, con) in enumerate(parsed_concentrations):
            parsed_concentrations[i] = (name, con/sum_concentrations)
        return parsed_concentrations


    def get_sampled_indices(self, number, probability):
        """ Return the sampled indices according to poisson distribution.
        """
        number_to_sample = min(number, poisson.rvs(probability * number))
        return random.sample(range(0, number), number_to_sample)


    def associate(self, index):
        """ Attempt an association for protein at index of positions.
        """
        pos_1 = self.positions[index]

        p1 = self.get_protein(pos_1)
        if p1.number_of_free_domains == 0: # continue if protein has already interactions on all domains
            return

        (p2, pos_2) = self.sample_interactor(p1, pos_1)
        if p2 is None:
            return

        domains1 = list(p1.get_domains_to_interactor(p2.name))
        random.shuffle(domains1)
        domains2 = list(p2.get_domains_to_interactor(p1.name))
        random.shuffle(domains2)
        for d1, d2 in itertools.product(domains1, domains2):
            if p1.is_association_possible(p2.name, d1) and p2.is_association_possible(p1.name, d2):
                p1.associate(p2.name, d1)
                p2.associate(p1.name, d2)

                if self.interactions[pos_1] == {}: # node was a singleton before
                    self.number_of_singletons -= 1
                if self.interactions[pos_2] == {}:
                    self.number_of_singletons -= 1

                self.interactions.add_edge(pos_1, pos_2, domains=(d1, d2))
                self.number_of_edges += 1

                break


    def dissociate(self, index, edges):
        """ Dissociate the two proteins indicated through edge index and remove
            the corresponding edge.
        """
        pos_1, pos_2, dom = edges[index]

        p1 = self.get_protein(pos_1)
        p2 = self.get_protein(pos_2)

        d1, d2 = dom["domains"] #self.interactions[pos_1][pos_2]["domains"]
        if  not p1.is_interacting(p2.name, d1) or not p2.is_interacting(p1.name, d2):
            d2, d1 = dom["domains"] #self.interactions[pos_1][pos_2]["domains"]
            if  not p1.is_interacting(p2.name, d1) or not p2.is_interacting(p1.name, d2):
                print("error - dissociation not possible", file=sys.stderr)
                print(pos_1, pos_2, p1.name, d1, p2.name, d2, file=sys.stderr)
                print(p1.state, p2.state, file=sys.stderr)
                return

        p1.dissociate(p2.name, d1)
        p2.dissociate(p1.name, d2)
        self.interactions.remove_edge(pos_1, pos_2)
        self.number_of_edges -= 1
        if self.interactions[pos_1] == {}: # node has become a singleton
            self.number_of_singletons += 1
        if self.interactions[pos_2] == {}:
            self.number_of_singletons += 1


    def simulate_interaction_step(self, association_probability, dissociation_probability, step):
        """ Simulate one step: First all proteins try with $association_probability
            to interact with an other protein in a random order. After that each
            interaction is tested for dissociation with $dissociation_probability.
        """
        # association
        print(datetime.datetime.now(), "begin of association step", step, sep='\t', file=self.output_log)

        indices_to_associate = self.get_sampled_indices(self.num_protein_instances, association_probability)
        for index in indices_to_associate:
            self.associate(index)

        print(datetime.datetime.now(), step, "a", self.number_of_edges, "edges", self.number_of_singletons, "singletons", sep='\t', file=self.output_log, flush=True)

        self.edgecount_ass.append(self.number_of_edges)
        print(datetime.datetime.now(), "begin of dissociation step", step, sep='\t', file=self.output_log)

        # dissociation
        indices_to_remove = self.get_sampled_indices(self.number_of_edges, dissociation_probability)
        edges = self.interactions.edges(data=True)
        for index in indices_to_remove:
            self.dissociate(index, edges)

        print(datetime.datetime.now(), step, "d", self.number_of_edges, "edges", self.number_of_singletons, "singletons", sep='\t', file=self.output_log, flush=True)

        self.edgecount_dis.append(self.number_of_edges)

        if self.test_convergence(self.edgecount_ass, self.edgecount_dis):
            if self.convergence_edge is None:
                self.convergence_edge = step
                return True


    def test_convergence(self, edgecount_ass, edgecount_dis):
        """ Test the convergence criterion.
        """
        # Compare the last 10 steps, so the arrays should have 10 items
        if len(edgecount_ass) < 10:
            return False

        new_mean_edge_ass = 0.1*sum(edgecount_ass[-10:])
        result_ass = new_mean_edge_ass < self.mean_edge_ass
        self.mean_edge_ass = new_mean_edge_ass
        #edgecount_ass.pop(0)

        new_mean_edge_dis = 0.1*sum(edgecount_dis[-10:])
        result_dis = new_mean_edge_dis < self.mean_edge_dis
        self.mean_edge_dis = new_mean_edge_dis
        #edgecount_dis.pop(0)

        return result_ass and result_dis


#---------- methods that have to be implemented in the concrete simulations ----------

    def get_protein(self, pos):
        """ Return the protein at position $pos.
        """
        raise NotImplementedError

    def sample_interactor(self, protein, pos):
        """ Sample an interactor for $protein at position $pos.
        """
        raise NotImplementedError

    def simulate_network(self, steps, association_probability, dissociation_probability):
        """ Simulate the network with given parameters.
        """
        raise NotImplementedError
