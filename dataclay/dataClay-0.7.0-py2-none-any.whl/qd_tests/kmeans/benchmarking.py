from collections import defaultdict
import numpy as np


def cluster_points_proposal(fragment, mu):
    dic = defaultdict(list)

    augm_points = np.tile(fragment, len(mu)).reshape([len(fragment)] + list(mu.shape))
    augm_norm = np.linalg.norm(augm_points - mu, axis=2)
    min_args = augm_norm.argmin(axis=1)

    for x_idx, mu_idx in enumerate(min_args):
        dic[mu_idx].append(x_idx)

    return dic


def cluster_points_original(fragment, mu):
    dic = {}
    for x in enumerate(fragment):
        bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                         for i in enumerate(mu)], key=lambda t: t[1])[0]
        if bestmukey not in dic:
            dic[bestmukey] = [x[0]]
        else:
            dic[bestmukey].append(x[0])
    return dic


def cluster_points_original_defaultdict(fragment, mu):
    dic = defaultdict(list)
    for x in enumerate(fragment):
        bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                         for i in enumerate(mu)], key=lambda t: t[1])[0]

        dic[bestmukey].append(x[0])
    return dic
