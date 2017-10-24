# Python 2 and 3 compatibility
from __future__ import print_function

import copy
from collections import defaultdict
import numpy as np

import yaml
from yaml import CSafeLoader as Loader


def temporal_correlation(data):
    """
    This function expects "data" to be a dictionary, with obsids as key values (integer typed),
    and the associated values as a cthulhu Obsid object. Returns a list [rho, error],
    where rho is a dictionary with keys of seconds of lags with associated correlation values,
    and errors similarly keyed with seconds of lag and error associated with the correlation.
    """
    obsids = data.keys()
    timestamps = []
    for o in data:
        timestamps.append(data[o].metadata["timestamps"])
    timestamps = sorted([i for l in timestamps for i in l])

    with open("bias.yaml", 'r') as f:
        source_biases = yaml.load(f, Loader=Loader)
    
    # Record common to every obsid.
    sources = []
    for s in data[obsids[0]].sources:
        flag = True
        for o in obsids:
            if s not in data[o].sources:
                flag = False
                break
        if flag:
            sources.append(s)
    print("number of sources in common to all obsids: %s" % len(sources))

    # Screen sources for NaNs.
    for i, s in enumerate(sources):
        for o in obsids:
            if sources[i] == 0:
                break
            for j, t in enumerate(data[o].metadata["timestamps"]):
                l_shift = data[o].sources[s]["l_shifts"][j]
                m_shift = data[o].sources[s]["m_shifts"][j]
                if not np.isfinite(l_shift) or not np.isfinite(m_shift):
                    sources[i] = 0
                    break
    sources_copy = copy.copy(sources)
    deleted = 0
    for i, s in enumerate(sources_copy):
        if s == 0:
            del(sources[i-deleted])
            deleted += 1
    print("number of sources without NaNs: %s" % len(sources))

    # Loop through every obsid, then every source and get its (l,m) values.
    # offsets = defaultdict(lambda: [])
    l_offsets = defaultdict(lambda: [])
    m_offsets = defaultdict(lambda: [])
    for s in sources:
        for o in obsids:
            for i, t in enumerate(data[o].metadata["timestamps"]):
                # l_shift = data[o].sources[s]["l_shifts"][i]
                # m_shift = data[o].sources[s]["m_shifts"][i]
                # offsets[t].append(np.sqrt(l_shift**2 + m_shift**2))
                l_shift = data[o].sources[s]["l_shifts"][i] - source_biases[s][0]
                m_shift = data[o].sources[s]["m_shifts"][i] - source_biases[s][1]
                l_offsets[t].append(l_shift)
                m_offsets[t].append(m_shift)

    # Find the separations in time, and the timestamps that contribute to them.
    partners = defaultdict(lambda: [])
    for i, o in enumerate(timestamps):
        for o2 in timestamps[i+1:]:
            partners[abs(o - o2)].append([o, o2])

    # Multiply the products to obtain rho.
    rho, errors = {}, {}
    rho[0] = 1
    errors[0] = 0
    for t in sorted(partners.keys()):
        for p in partners[t]:
            o1, o2 = p[0], p[1]

            # mean1 = np.mean(offsets[o1])
            # std1 = np.std(offsets[o1])
            # product1 = (offsets[o1] - mean1)

            # mean2 = np.mean(offsets[o2])
            # std2 = np.std(offsets[o2])
            # product2 = (offsets[o2] - mean2)

            try:
                mean1 = np.mean(l_offsets[o1])
                std1 = np.std(l_offsets[o1])
                product1 = (l_offsets[o1] - mean1)

                mean2 = np.mean(l_offsets[o2])
                std2 = np.std(l_offsets[o2])
                product2 = (l_offsets[o2] - mean2)

                try:
                    rho[t].append( np.mean(product1 * product2) / (std1*std2) )
                except KeyError:
                    rho[t] = [np.mean(product1 * product2) / (std1*std2)]

                errors[t] = np.sqrt(2)*np.mean(rho[t])/np.sqrt(len(rho[t]))
                rho[t] = np.mean(rho[t])

            except:
                pass

    for t in rho:
        rho[t] = float(rho[t])
        errors[t] = float(errors[t])

    return rho, errors
