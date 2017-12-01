# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
import itertools

import cpinsim.constraint_io as io

domain_counter = 0 # counter for artificial domains
negative_counter = -1 # temporary negative counter to distinguish competitions/allosterics
boundary = -1 # boundary between competitions and allosterics

# host -> interactor -> set of domains
# str -> str -> set
map_interactions_to_domains = defaultdict(lambda: defaultdict(set))

# host -> domain_host -> set of (interactor, domain_interactor)
# str -> str -> set(tuple)
map_domains_to_interactors = defaultdict(lambda: defaultdict(set))

# host -> interactor -> (domain_host_interactor, domain_interactor)-> id_count
# str -> str -> tuple -> int
allosteric_interactors = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# host -> activator/inhibitor -> id_count -> (domain_host_activator/inhibitor, domain_activator/inhibitor)
# str -> str -> int -> tuple
allosteric_activators = defaultdict(lambda: defaultdict(lambda: defaultdict(tuple)))
allosteric_inhibitors = defaultdict(lambda: defaultdict(lambda: defaultdict(tuple)))


def is_real(domain):
    """ Return if the domain is real (not None, not artificial)
    """
    return domain is not None and type(domain) != int


def is_artificial(domain):
    """ Return if the domain is artificial.
    """
    return domain is not None and type(domain) == int and domain > 0


#---------- Reading the files  ----------#

def add_interaction(p1, domain_p1, p2, domain_p2):
    """ Add the interaction in both directions to map_domains_to_interactors if
        not already present, remove interactions with None if already domains known.
    """
    if domain_p1 is not None or \
      (p2, domain_p2) not in [(i, d) for dom in map_domains_to_interactors[p1] for i, d in map_domains_to_interactors[p1][dom]]:
        map_domains_to_interactors[p1][domain_p1].add((p2, domain_p2))
    if domain_p1 is not None and (p2, domain_p2) in map_domains_to_interactors[p1][None]:
        map_domains_to_interactors[p1][None].remove((p2, domain_p2))
        map_domains_to_interactors[p2][domain_p2].remove((p1, None))

    if domain_p2 is not None or \
      (p1, domain_p1) not in [(i, d) for dom in map_domains_to_interactors[p2] for i, d in map_domains_to_interactors[p2][dom]]:
        map_domains_to_interactors[p2][domain_p2].add((p1, domain_p1))
    if domain_p2 is not None and (p1, domain_p1) in map_domains_to_interactors[p2][None]:
        map_domains_to_interactors[p2][None].remove((p1, domain_p1))
        map_domains_to_interactors[p1][domain_p1].remove((p2, None))


def appoint_negative_domains(domain_1, domain_2):
    """ If input domains are None give two different negative domains.
    """
    global negative_counter
    if domain_1 is None:
        domain_1 = negative_counter
        negative_counter -= 1
    if domain_2 is None:
        domain_2 = negative_counter
        negative_counter -= 1
    return (domain_1, domain_2)


def read_interactions_without_constraints(files):
    """ Read interactions between proteins without constraints.
        Files must have two columns for the two interacting proteins in each line.
    """
    for (p1, domain_p1, p2, domain_p2, _) in io.yield_interactions_without_constraints(files):
        add_interaction(p1, domain_p1, p2, domain_p2)


def read_competitions(files):
    """ Read interactions with constraints of competing proteins.
        Files must have two columns, one with the host and one with
        comma-separated competitors.
    """
    global negative_counter, boundary
    for (host, domains_host, competitors, _) in io.yield_competitions(files):
        inc_counter = False
        i = 0
        for competitor in competitors:
            domain_host, i = io.set_domain_at_host(domains_host, i)
            competitor, domain_competitor = io.split_interactor_and_domain(competitor)
            if domain_host is None:
                domain_host = negative_counter
                inc_counter = True
            add_interaction(host, domain_host, competitor, domain_competitor)

        if inc_counter:
            negative_counter -= 1
    boundary = negative_counter


def read_allosteric_effects(files):
    """ Read interactions with constraints of allosteric effects.
        Files must have four columns: host, interactors, activators, inhibitors.
    """
    id_count = 0
    for (host, domains_host, interactors, activators, inhibitors, _) in io.yield_allosteric_effects(files):
        i = 0
        for interactor in interactors:
            interactor, domain_interactor = io.split_interactor_and_domain(interactor)
            domain_host_interactor, i = io.set_domain_at_host(domains_host, i)

            (domain_host_interactor, domain_interactor) = appoint_negative_domains(domain_host_interactor, domain_interactor)
            add_interaction(host, domain_host_interactor, interactor, domain_interactor)
            allosteric_interactors[host][interactor][(domain_host_interactor, domain_interactor)] = id_count

            for activator in activators:
                if activator == "": # skip empty activators
                    continue
                activator, domain_activator = io.split_interactor_and_domain(activator)
                domain_host_activator, i = io.set_domain_at_host(domains_host, i)

                (domain_host_activator, domain_activator) = appoint_negative_domains(domain_host_activator, domain_activator)
                add_interaction(host, domain_host_activator, activator, domain_activator)
                allosteric_activators[host][activator][id_count] = (domain_host_activator, domain_activator)

            for inhibitor in inhibitors:
                if inhibitor == "":  # skip empty inhibitors
                    continue
                inhibitor, domain_inhibitor = io.split_interactor_and_domain(inhibitor)
                domain_host_inhibitor, i = io.set_domain_at_host(domains_host, i)

                (domain_host_inhibitor, domain_inhibitor) = appoint_negative_domains(domain_host_inhibitor, domain_inhibitor)
                add_interaction(host, domain_host_inhibitor, inhibitor, domain_inhibitor)
                allosteric_inhibitors[host][inhibitor][id_count] = (domain_host_inhibitor, domain_inhibitor)

            i += 1
            id_count += 1


#---------- Normalize the existing domains, inference of domains and distribution of artificial domains  ----------#


def propagate_changes_to_allosterics(host, domain_host, new_dom, interactor, domain_interactor, swapped=False):
    """ Propagate a new domain for allosteric effects and remove the old one in
        in all data structures.
    """
    if host in allosteric_interactors and interactor in allosteric_interactors[host] and \
      (domain_host, domain_interactor) in allosteric_interactors[host][interactor]:

        id_count = allosteric_interactors[host][interactor][(domain_host, domain_interactor)]
        del allosteric_interactors[host][interactor][(domain_host, domain_interactor)]
        if not swapped:
            allosteric_interactors[host][interactor][(new_dom, domain_interactor)] = id_count
        else:
            allosteric_interactors[host][interactor][(domain_host, new_dom)] = id_count

    for data in (allosteric_activators, allosteric_inhibitors):
        if host in data and interactor in data[host]:
            for id_count in data[host][interactor]:
                if (domain_host, domain_interactor) == data[host][interactor][id_count]:
                    del data[host][interactor][id_count]
                    if not swapped:
                        data[host][interactor][id_count] = (new_dom, domain_interactor)
                    else:
                        data[host][interactor][id_count] = (domain_host, new_dom)


def normalize():
    """ Merge overlapping domains and propagate the information throughout the
        whole network.
    """
    proteins = list(map_domains_to_interactors.keys())
    for host in proteins:
        update_needed = True
        while update_needed:
            update_needed = False
            domains = [d for d in map_domains_to_interactors[host] if d is not None and type(d) != int]
            if len(domains) > 1:
                for d1, d2 in itertools.combinations(domains, 2):
                    new_dom = get_merged_domain(d1, d2)
                    if new_dom is not None:
                        update_needed = True
                        old1 = map_domains_to_interactors[host][d1]
                        del map_domains_to_interactors[host][d1]
                        map_domains_to_interactors[host][new_dom].update(old1)

                        old2 = map_domains_to_interactors[host][d2]
                        del map_domains_to_interactors[host][d2]
                        map_domains_to_interactors[host][new_dom].update(old2)

                        for interactor, domain_interactor in old1:
                            if (host, d1) in map_domains_to_interactors[interactor][domain_interactor]:
                                map_domains_to_interactors[interactor][domain_interactor].remove((host, d1))
                                map_domains_to_interactors[interactor][domain_interactor].add((host, new_dom))
                            propagate_changes_to_allosterics(host, d1, new_dom, interactor, domain_interactor)

                        for interactor, domain_interactor in old2:
                            if (host, d2) in map_domains_to_interactors[interactor][domain_interactor]:
                                map_domains_to_interactors[interactor][domain_interactor].remove((host, d2))
                                map_domains_to_interactors[interactor][domain_interactor].add((host, new_dom))
                            propagate_changes_to_allosterics(host, d2, new_dom, interactor, domain_interactor)
                        break


def get_merged_domain(domain_interactor, domain):
    """ Test if the domains are overlapping and return the merged domain. If the
        domains are not overlapping or not an interval return None.
    """
    if domain_interactor is None or domain is None or type(domain_interactor) == int or type(domain) == int:
        return None
    min1, *max1 = domain_interactor.split("-")
    if max1 == []: # domain_interactor is not an interval
        return None

    min2, *max2 = domain.split("-")
    if max2 == []:  # domain is not an interval
        return None

    cut0, cut1 = max(int(min1), int(min2)), min(int(max1[0]), int(max2[0]))
    if cut1 - cut0 > 0:
        new_min, new_max = min(int(min1), int(min2)), max(int(max1[0]), int(max2[0]))
        new_dom = "{}-{}".format(new_min, new_max)
        return new_dom
    return None


def remove_redundant_nones():
    """ Remove Nones where domains are known and domains without interactors after
        merging.
    """
    proteins = sorted(list(map_domains_to_interactors.keys()))
    to_remove = set()
    to_delete = set()
    for host in proteins:
        for domain_host in map_domains_to_interactors[host]:
            if len(map_domains_to_interactors[host][domain_host]) == 0:
                to_delete.add((host, domain_host))
            for interactor, domain_interactor in map_domains_to_interactors[host][domain_host]:
                if  not(type(domain_host) == int and domain_host < 0) and domain_interactor is None and [i for i, d in map_domains_to_interactors[host][domain_host]].count(interactor) > 1:
                    to_remove.add((host, domain_host, interactor, domain_interactor))
                elif not(type(domain_host) == int and domain_host < 0) and domain_interactor is None and \
                   [i for dom in map_domains_to_interactors[host] for i, d in map_domains_to_interactors[host][dom]].count(interactor) > 1:
                    to_remove.add((host, domain_host, interactor, domain_interactor))
                else:
                    map_interactions_to_domains[host][interactor].add(domain_host)
                    map_interactions_to_domains[interactor][host].add(domain_interactor)

    for host, domain_host, interactor, domain_interactor in to_remove:
        map_domains_to_interactors[host][domain_host].remove((interactor, domain_interactor))
        if len(map_domains_to_interactors[host][domain_host]) == 0:
            to_delete.add((host, domain_host))
    for host, domain_host in to_delete:
        del map_domains_to_interactors[host][domain_host]


def domain_inference_competition_host():
    """ Try to infer unknown domains for host of competitions.
    """
    proteins = list(map_domains_to_interactors.keys())
    for host in proteins:
        update_needed = True
        while update_needed:
            update_needed = False
            to_change = set()
            domains = [d for d in map_domains_to_interactors[host] if type(d) == int and d < 0 and d >= boundary]
            for domain_host in domains:
                for interactor, domain_interactor in map_domains_to_interactors[host][domain_host]:
                    if is_real(domain_interactor):
                        candidates = [(p, d) for p, d in map_domains_to_interactors[interactor][domain_interactor] if d != domain_host]
                        for p, d in candidates:
                            if host == p:
                                update_needed = True
                                to_change.add((host, domain_host, d, interactor, domain_interactor))
                if update_needed:
                    break
            if update_needed:
                for (host, domain_host, new_dom, interactor, domain_interactor) in to_change:
                    #print((host, domain_host, new_dom, interactor, domain_interactor))
                    map_domains_to_interactors[host][new_dom].add((interactor, domain_interactor))
                    map_domains_to_interactors[interactor][domain_interactor].add((host, new_dom))
                    if (host, domain_host) in map_domains_to_interactors[interactor][domain_interactor]:
                        map_domains_to_interactors[interactor][domain_interactor].remove((host,domain_host))
                    if host == interactor and (host, None) in map_domains_to_interactors[host][new_dom]:
                        map_domains_to_interactors[host][new_dom].remove((host, None))
                        map_domains_to_interactors[host][new_dom].add((host, new_dom))
                    if domain_host in map_domains_to_interactors[host]:
                        del map_domains_to_interactors[host][domain_host]
                    propagate_changes_to_allosterics(host, domain_host, new_dom, interactor, domain_interactor)
                    propagate_changes_to_allosterics(interactor, domain_interactor, new_dom, host, domain_host, swapped=True)


def domain_inference_competitors():
    """ Try to infer unknown domains for competitors.
    """
    proteins = list(map_domains_to_interactors.keys())
    something_changed = True
    while something_changed:
        something_changed = False
        for host in proteins:
            domains = [d for d in map_domains_to_interactors[host] if is_real(d) and len(map_domains_to_interactors[host][d]) > 1]
            update_needed = True
            while update_needed:
                update_needed = False
                inferred_domains = set()
                for domain_host in domains:
                    for ((interactor1, domain_interactor1), (interactor2, domain_interactor2)) in itertools.combinations(map_domains_to_interactors[host][domain_host], 2):
                        if domain_interactor1 is None and domain_interactor2 is not None:
                            query, ref, ref_domain = interactor1, interactor2, domain_interactor2
                        elif domain_interactor1 is not None and domain_interactor2 is None:
                            query, ref, ref_domain = interactor2, interactor1, domain_interactor1
                        else:
                            continue
                        for second_host in proteins:
                            domains = [d for d in map_domains_to_interactors[second_host] if is_real(d) and len(map_domains_to_interactors[second_host][d]) > 1]
                            for dom in domains:
                                if second_host == host and dom == domain_host:
                                    continue
                                if (ref, ref_domain) in map_domains_to_interactors[second_host][dom]:
                                    candidates = [(p, d) for p, d in map_domains_to_interactors[second_host][dom] if p == query and d is not None]
                                    if len(candidates) != 0:
                                        inferred_domains.update(set(candidates))
                                        update_needed = True
                                        something_changed = True
                    if update_needed:
                        break
                if update_needed:
                    #print(host, domain_host, inferred_domains)
                    for protein, new_dom in inferred_domains:
                        map_domains_to_interactors[protein][new_dom].add((host, domain_host))
                        map_domains_to_interactors[host][domain_host].add((protein, new_dom))
                        if (protein, None) in map_domains_to_interactors[host][domain_host]:
                            map_domains_to_interactors[host][domain_host].remove((protein, None))
                        if (host, domain_host) in map_domains_to_interactors[protein][None]:
                            map_domains_to_interactors[protein][None].remove((host, domain_host))
                        if protein == host and (protein, None) in map_domains_to_interactors[protein][new_dom]:
                            map_domains_to_interactors[protein][new_dom].remove((protein, None))
                            map_domains_to_interactors[protein][new_dom].add((protein, new_dom))
                        propagate_changes_to_allosterics(protein, None, new_dom, host, domain_host)
                        propagate_changes_to_allosterics(host, domain_host, new_dom, protein, None, swapped=True)


def apply_artificial_domains():
    """ Choose domains for all negative placeholder domains and Nones. If one real
        domain is known use this domain, otherwise choose a unique artificial domain.
        Competitions with unknown domain at the host get the same domain.
    """
    global domain_counter, boundary
    proteins = sorted(list(map_domains_to_interactors.keys()))
    for host in proteins:
        update_needed = True
        while update_needed:
            update_needed = False
            changed = set()
            inc_counter = False
            for domain_host in map_domains_to_interactors[host]:
                if not (type(domain_host) == int and domain_host < 0) and domain_host is not None:
                    continue
                for interactor, domain_interactor in map_domains_to_interactors[host][domain_host]:
                    mapped_domains = map_interactions_to_domains[host][interactor]
                    if None in mapped_domains:
                        mapped_domains.remove(None)
                    if type(domain_host) == int and domain_host < 0 and domain_host >= boundary: # unknown domain at host of competition
                        new_dom = domain_counter
                        map_interactions_to_domains[host][interactor].add(new_dom)
                        inc_counter = True
                    elif len(mapped_domains) > 1 or len(mapped_domains) == 0: # no or multiple domains are known
                        new_dom = domain_counter
                        domain_counter += 1
                        map_interactions_to_domains[host][interactor].add(new_dom)
                    else: # len(mapped_domains) == 1, exactly one domain is known
                        new_dom = mapped_domains.pop()
                        if type(new_dom) == int:
                            new_dom = domain_counter
                            domain_counter += 1
                            map_interactions_to_domains[host][interactor].add(new_dom)
                    changed.add((interactor, domain_interactor, host, domain_host, new_dom))
                    update_needed = True
                break
            if update_needed:
                if inc_counter:
                    domain_counter += 1
                for (interactor, domain_interactor, host, domain_host, new_dom) in changed:
                    map_domains_to_interactors[host][new_dom].add((interactor, domain_interactor))
                    if (host, domain_host) in map_domains_to_interactors[interactor][domain_interactor]:
                        map_domains_to_interactors[interactor][domain_interactor].remove((host, domain_host))
                        map_domains_to_interactors[interactor][domain_interactor].add((host, new_dom))
                    if domain_host in map_domains_to_interactors[host]:
                        del map_domains_to_interactors[host][domain_host]
                    if host == interactor and (host, None) in map_domains_to_interactors[host][new_dom]:
                        map_domains_to_interactors[host][new_dom].remove((host, None))
                        map_domains_to_interactors[host][new_dom].add((host, new_dom))

                    propagate_changes_to_allosterics(host, domain_host, new_dom, interactor, domain_interactor)
                    propagate_changes_to_allosterics(interactor, domain_interactor, new_dom, host, domain_host, swapped=True)


 #---------- Output the annotated interactions and constraints  ----------#

def write_annotated_files(output_i, output_c, output_a):
    """ Write the annotated constraints into the three output files.
    """
    lines_i, lines_a, lines_c = [], [], []
    for host in allosteric_interactors:
        for interactor in allosteric_interactors[host]:
            for (domain_host, domain_interactor) in allosteric_interactors[host][interactor]:
                id_count = allosteric_interactors[host][interactor][(domain_host, domain_interactor)]
                host_string = "{}[{}]".format(host, domain_host)
                interactor_string = "{}[{}]".format(interactor, domain_interactor)
                activators_string, inhibitors_string = [], []
                for activator in allosteric_activators[host]:
                    if id_count in allosteric_activators[host][activator]:
                        (domain_host_activator, domain_activator) = allosteric_activators[host][activator][id_count]
                        activators_string.append("{}[{}]".format(activator, domain_activator))
                        host_string += "[{}]".format(domain_host_activator)
                for inhibitor in allosteric_inhibitors[host]:
                    if id_count in allosteric_inhibitors[host][inhibitor]:
                        (domain_host_inhibitor, domain_inhibitor) = allosteric_inhibitors[host][inhibitor][id_count]
                        inhibitors_string.append("{}[{}]".format(inhibitor, domain_inhibitor))
                        host_string += "[{}]".format(domain_host_inhibitor)
                line = [host_string, interactor_string, ",".join(activators_string), ",".join(inhibitors_string)]
                if line not in lines_a:
                    lines_a.append(line)

    for host in sorted(map_domains_to_interactors):
        for domain_host in map_domains_to_interactors[host]:
            host_string = "{}[{}]".format(host, domain_host)
            interactors = map_domains_to_interactors[host][domain_host]
            if len(interactors) == 0:
                continue
            if len(interactors) == 1:
                interactor, domain_interactor = interactors.pop()
                interactors_string = "{}[{}]".format(interactor, domain_interactor)
                line = sorted([host_string, interactors_string])
                if line not in lines_i:
                    lines_i.append(line)
            else:
                temp = []
                for interactor, domain_interactor in interactors:
                    temp.append("{}[{}]".format(interactor, domain_interactor))
                interactors_string = ",".join(sorted(temp))
                line = [host_string, interactors_string]
                if line not in lines_c:
                    lines_c.append(line)

    writer = csv.writer(open(output_i, 'w'), delimiter='\t', lineterminator='\n')
    writer.writerow(["Interactor_A", "Interactor_B"])
    writer.writerows(sorted(lines_i))

    writer = csv.writer(open(output_a, 'w'), delimiter='\t', lineterminator='\n')
    writer.writerow(["Host", "Interactor", "Activator", "Inhibitor"])
    writer.writerows(sorted(lines_a))

    writer = csv.writer(open(output_c, 'w'), delimiter='\t', lineterminator='\n')
    writer.writerow(["Host", "Competitors"])
    writer.writerows(sorted(lines_c))

