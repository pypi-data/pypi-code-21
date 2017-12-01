# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
import itertools

import cpinsim.constraint_io as io

class Proteinparser:
    """ Parse annotated interactions and constraints into a proteinwise
        representation that can be used for the simulation.

        Output format:
        > Proteinname
        (Interactor, Domain) \t  tab separated clauses

        one clause consists of semicolon separated positive and/or negative terms
        positive terms: (protein,domain)
        negative terms: -(protein, domain)

        Example:
        >SRC
        (ABL1,84-145)   -(*,84-145)
        (ERBB2,1)   (BCAR1,73);-(*,1)
    """

    def __init__(self):
        """ Initialize the datastructure for the transitions.

            Datastructure of transitions:
            The keys of the dictionary are the proteins. For each protein in the
            accessed list all interactions are stored. The list consists of a tuple
            (positive, negative). Proteins in positive have to be there for
            the interaction with the interactor to be possible (allosteric
            avctivation). Proteins in negative can't be there at the same time
            (competition or allosteric inhibition).
        """
        # Host - (Interactor,Domain) - Tuple of Constraints in form (positive, negative)
        self.transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(tuple)))


    def parse_interactions_without_constraints(self, files):
        """ Parse interactions between proteins without constraints. Files must
            have two columns for the two interacting proteins in each line.
        """
        for (p1, domain_p1, p2, domain_p2, _) in io.yield_interactions_without_constraints(files):
            self.add_transition(p1, p2, domain_p1, [], [])
            self.add_transition(p2, p1, domain_p2, [], [])


    def parse_competitions(self, files):
        """ Parse interactions with constraints of competing proteins.
            Files must have two columns, one with the host and one with
            comma-separated competitors.
        """
        for (host, domains_host, competitors, _) in io.yield_competitions(files):
            list_competitors = []
            i = 0 # counter for the domains at the host
            for competitor in competitors:
                domain_host, i = io.set_domain_at_host(domains_host, i)
                competitor, domain_competitor = io.split_interactor_and_domain(competitor)
                if (competitor, domain_host) not in list_competitors:
                    list_competitors.append((competitor, domain_host))
                self.add_transition(competitor, host, domain_competitor, [], [])
            for comp, dom in list_competitors:
                self.add_transition(host, comp, dom, [], list_competitors)


    def parse_allosteric_effects(self, files):
        """ Parse interactions with constraints of allosteric effects.
            Files must have four columns: host, interactors, activators, inhibitors.
        """
        for (host, domains_host, interactors, activators, inhibitors, _) in io.yield_allosteric_effects(files):
            list_activators = []
            list_inhibitors = []
            i = 0 # counter for the domains at the host
            for interactor in interactors:
                interactor, domain_interactor = io.split_interactor_and_domain(interactor)
                domain_host_interactor, i = io.set_domain_at_host(domains_host, i)
                self.add_transition(interactor, host, domain_interactor, [], [])

                for activator in activators:
                    if activator == "": # skip empty activators
                        continue
                    activator, domain_activator = io.split_interactor_and_domain(activator)
                    domain_host_activator, i = io.set_domain_at_host(domains_host, i)
                    list_activators.append((activator, domain_host_activator))
                    self.add_transition(activator, host, domain_activator, [], [])
                    self.add_transition(host, activator, domain_host_activator, [], [])

                for inhibitor in inhibitors:
                    if inhibitor == "":  # skip empty inhibitors
                        continue
                    inhibitor, domain_inhibitor = io.split_interactor_and_domain(inhibitor)
                    domain_host_inhibitor, i = io.set_domain_at_host(domains_host, i)
                    list_inhibitors.append((inhibitor, domain_host_inhibitor))
                    self.add_transition(inhibitor, host, domain_inhibitor, [], [])
                    self.add_transition(host, inhibitor, domain_host_inhibitor, [], [])

                i += 1
                self.add_transition(host, interactor, domain_host_interactor, list_activators, list_inhibitors)



    def add_transition(self, host, interactor, domain, positive, negative):
        """ Add a new transition if it is not already in the datastructure.
        """
        constraints = self.transitions[host][domain][interactor]
        if constraints != tuple():
            (p, n) = constraints
        else:
            p = set()
            n = set()
        p.update(positive)
        n.update(negative)
        self.transitions[host][domain][interactor] = (p, n)


    def merge_domains(self):
        """ Merge overlapping domains and modify self.transitions accordingly.
        """
        to_merge = defaultdict(set)
        for host in self.transitions:
            for d1, d2 in itertools.combinations(self.transitions[host].keys(), 2):
                if self.are_overlapping(d1, d2):
                    to_merge[host].add(d1)
                    to_merge[host].add(d2)
        for host in to_merge:
            d1 = to_merge[host].pop()
            for d2 in to_merge[host]:
                old1 = self.transitions[host][d1]
                del self.transitions[host][d1]
                old2 = self.transitions[host][d2]
                del self.transitions[host][d2]
                min1, *max1 = d1.split("-")
                min2, *max2 = d2.split("-")
                new_min, new_max = min(int(min1), int(min2)), max(int(max1[0]), int(max2[0]))
                new_dom = "{}-{}".format(new_min, new_max)
                for i in old1:
                    self.transitions[host][new_dom][i] = old1[i]
                for i in old2:
                    self.transitions[host][new_dom][i] = old2[i]
                d1 = new_dom


    def write_proteins_in_file(self, output):
        """ Write the proteins in the designated file at $output.
        """
        self.merge_domains()
        writer = csv.writer(open(output, 'w'), delimiter='\t', lineterminator='\n')
        for host in sorted(self.transitions):
            writer.writerow([">" + host])
            lines = []
            for domain_interactor in self.transitions[host]:
                for interactor in self.transitions[host][domain_interactor]:
                    #print(host, interactor, domain_interactor, self.transitions[host][(interactor, domain_interactor)])
                    positive, negative = self.transitions[host][domain_interactor][interactor]
                    temp = "-"+self.to_str("*", domain_interactor)
                    for protein, domain in negative:
                        if domain == domain_interactor: # competition at same domain already covered
                            continue
                        if self.are_overlapping(domain_interactor, domain): # competition with overlapping but not exact same domain
                            if temp.find(self.to_str("*", domain)) == -1:
                                temp += "-"+self.to_str("*", domain)
                            continue
                        temp += "-"+self.to_str(protein, domain) # allosteric inhibition
                    temp = temp.strip(";")
                    clauses = []
                    for actiavator, domain_activator in positive: # allosteric activation: interaction possible if activator present and all negative factors (temp) not present
                        clauses.append(self.to_str(actiavator, domain_activator)+temp)
                    if clauses == []: # no activators
                        clauses = [temp]
                    line = [self.to_str(interactor, domain_interactor).strip(";")]
                    line.extend(clauses)
                    if line not in lines:
                        lines.append(line)

            writer.writerows(sorted(lines))
            writer.writerow("")


    def to_str(self, protein, domain):
        """ Return string representation of protein and domain.
        """
        return "({},{});".format(protein, domain)


    def are_overlapping(self, domain_interactor, domain):
        """ Test if the domains are overlapping.
        """
        min1, *max1 = domain_interactor.split("-")
        if max1 == []: # domain_interactor is not an interval
            return False

        min2, *max2 = domain.split("-")
        if max2 == []:  # domain is not an interval
            return False

        cut0, cut1 = max(int(min1), int(min2)), min(int(max1[0]), int(max2[0]))
        if cut1 - cut0 > 0:
            return True
        return False

