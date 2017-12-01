# -*- coding: utf-8 -*-

import csv
from sys import stderr

""" Provide some functions for reading/writing/manipulating the csv files of
    constraints.
"""


def split_interactor_and_domain(interactor):
    """ Split interactor and it domains. Return interactor and one domain,
        a list of domains or None if there was no domain.
    """
    interactor, *domain_interactor = interactor.split("[")
    interactor = interactor.strip().upper()
    # exactly one domain
    if domain_interactor != [] and len(domain_interactor) == 1:
        domain_interactor = domain_interactor[0].replace("]", "")
    # more than one domain
    elif domain_interactor != []:
        domain_interactor = [domain_interactor[i].replace("]", "") for i in range(len(domain_interactor))]
    # no domain
    else:
        domain_interactor = None
    return interactor, domain_interactor


def set_domain_at_host(domains_host, i):
    """ Choose the right domain out of domains_host. If i < len(domains_host)
        then it is the i-th element otherwise it is the last element in the list.
    """
    if type(domains_host) == list:
        j = i if i < len(domains_host) else len(domains_host)-1
        domain_host_interactor = domains_host[j]
        i += 1
    else:
        domain_host_interactor = domains_host
    return domain_host_interactor, i


def yield_interactions_without_constraints(files):
    """ Yield proteins and domains from interactions between proteins without
        constraints. Files must have two columns for the two interacting
        proteins in each line.
    """
    for filename in files:
        with open(filename, newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            try:
                next(reader) # skip header
            except:
                print("File", filename, "was empty!", file=stderr)
                continue # case of empty file
            for line in reader:
                p1, p2 = line
                p1, domain_p1 = split_interactor_and_domain(p1)
                p2, domain_p2 = split_interactor_and_domain(p2)
                yield (p1, domain_p1, p2, domain_p2, line)


def yield_competitions(files):
    """ Yield host and competitors with domains from interactions with
        constraints of competing proteins. Files must have two columns, one with
        the host and one with comma-separated competitors.
    """
    for filename in files:
        with open(filename, newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            try:
                next(reader) # skip header
            except:
                print("File", filename, "was empty!", file=stderr)
                continue # case of empty file
            for line in reader:
                host, competitors, *temp = line # *temp because there can be additional columns with irrelevant information
                competitors = competitors.split(",")
                host, domains_host = split_interactor_and_domain(host)
                yield (host, domains_host, competitors, line)


def yield_allosteric_effects(files):
    """ Yield host and interactors, activators, inhibitors from interactions with
        constraints of allosteric effects. Files must have four columns: host,
        interactors, activators, inhibitors.
    """
    for filename in files:
        with open(filename, newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            try:
                next(reader) # skip header
            except:
                print("File", filename, "was empty!", file=stderr)
                continue # case of empty file
            for line in reader:
                host, interactors, activators, inhibitors, *temp = line # *temp because there can be additional columns with irrelevant information
                host, domains_host = split_interactor_and_domain(host)
                interactors = interactors.split(",")
                activators = activators.split(",")
                inhibitors = inhibitors.split(",")
                yield (host, domains_host, interactors, activators, inhibitors, line)

