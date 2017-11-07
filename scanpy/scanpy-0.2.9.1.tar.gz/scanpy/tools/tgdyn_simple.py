"""TGDYN simple

Compute tangential dynamics in subsets of the data and infer gene importance by
that.
"""

import numpy as np
from .. import utils
from .. import settings as sett


def tgdyn_simple(adata, smp='dpt_groups', names='all'):
    """Tangential dynamics along paths.

    For a given partitioning of the data into subsets - typically paths on the
    data graph - where each subset is associated with a stage in a biological
    process. Also, subsets might be segments obtained from DPT.
    1. fit a linear model to each subset, capturing the tangential dynamics
    [2. obtain a transition matrix from the linear model]
    [3. compute the dynamics induced by this transition matrix]

    Parameters
    ----------
    adata : AnnData
        groups_masks : np.ndarray of dtype bool
            Array of shape (number of groups) x (number of samples) that stores
            boolean mask arrays that identify subgroups (segments or paths).
    adata : dict, AnnData
        Data dictionary.
    smp : str, optional (default: 'dpt_groups')
        Key for getting the relevant grouping from adata.smp.
    names : str, list, np.ndarray (default: 'all')
        Subset of group names/categories - e.g. 'C1,C2,C3' or ['C1', 'C2', 'C3']
        - in adata.add[smp + '_names'] to which comparison shall be restricted.
    """
    adata = adata.copy() if copy else adata
    # for clarity, rename variable
    groups_names = names
    groups_names, groups_masks = utils.select_groups(adata, groups_names, smp=smp)
    adata.add['tgdyn_simple_groups'] = smp
    adata.add['tgdyn_simple_groups_names'] = groups_names
    sett.m(0, 'computing dynamics within', groups_names)

    if 'dpt_pseudotime' not in adata.smp_keys():
        sys.exit('Run DPT first.')

    # compute velocities for subgroups
    dlm = fit_linear_model(adata.X,
                           # regress on dpt_pseudotime
                           adata.smp['dpt_pseudotime'],
                           groups_masks)
    sett.mt(0, 'fitted linear model')

    # write results of linear model to tgdyn dictionary
    adata.add['tgdyn_simple_vs'] = dlm['vs']
    adata.add['tgdyn_simple_x0s'] = dlm['x0s']
    adata.add['tgdyn_simple_pt0s'] = dlm['pt0s']
    adata.add['tgdyn_simple_groups_ids_bigenough'] = dlm['groups_ids_bigenough']

    # which genes drive the process, e.g., differentiation?
    # store the normalized velocity and the genes with the strongest contributions
    vs_norm = np.zeros(dlm['vs'].shape)
    genes_sorted = np.zeros(dlm['vs'].shape, dtype=np.int_)
    for igroup, _ in enumerate(groups_masks):
        v = dlm['vs'][igroup]
        abs_v = np.abs(v)
        vs_norm[igroup] = v / np.max(abs_v)
        # sorted according to decreasing values
        genes_sorted[igroup] = np.argsort(np.abs(vs_norm[igroup]))[::-1]

    adata.add['tgdyn_simple_vs_norm'] = vs_norm
    adata.add['tgdyn_simple_genes_sorted'] = genes_sorted
    sett.mt(0, 'finished tgdyn_simple')
    return adata if copy else None


def fit_linear_model(X, pseudotimes, groups_masks, min_groupsize=5):
    """Fit standard linear regression.

    Parameters
    ----------
    X : np.ndarray
        Data array.
    peudotimes : np.ndarray
        Time covariate to regress on.
    groups_masks : np.ndarray
        Segment-like subsets of the data to which regressions are restricted. An
        array of dimension (number of subsets) x (number of data points). Each
        row correponds to a mask array that identifies the subgroup.
    min_groupsize : int
        Minimum number of samples in groups in order to be considered.

    Returns
    -------
    dlm : dict
        Dictionary storing the parameters of a linear model.
        vs : np.ndarray
            Array with dimension (n_groups x n_genes), storing the
            velocity/direction obtained in regressions on pseudotime.
        x0s : np.ndarray
            Array with dimension (n_groups x n_genes), indicating the
            offsets obtained in regressions on pseudotime.
        pt0s : np.ndarray
            Array with dimension (n_groups) storing the mean of pseudotimes in
            each subgroup.
        xsteps : np.ndarray
            Array with dimension (n_groups x n_genes) storing the expected
            step for a single transition from point i to its successor.
    """
    n_groups = groups_masks.shape[0]
    n_genes = X.shape[1]
    vs = np.zeros((n_groups, n_genes))
    x0s = np.zeros((n_groups, n_genes))
    pt0s = np.zeros((n_groups))
    groups_ids_bigenough = []

    for igroup, group in enumerate(groups_masks):
        # group size
        group_size = pseudotimes[group].size
        # only consider groups with a sufficiently high number of samples
        if group_size < min_groupsize:
            continue
        # mean of pseudotimes in the group
        t_mean = pseudotimes[group].mean()
        # mean of gene expression in the group
        X_mean = X[group].mean(axis=0)
        # shift X and t to mean
        Xshift = X[group] - X_mean
        tshift = pseudotimes[group] - t_mean
        # compute means
        Xt_mean = (Xshift * tshift[:, np.newaxis]).mean(axis = 0)
        tsq_mean = (tshift**2).mean()
        # velocity
        v = Xt_mean / tsq_mean
        # store velocity with finite value only if the variance of this estimate
        # is reasonably small. here we demand that the estimate has to be based
        # on more than a certain number of data points
        vs[igroup] = v
        x0s[igroup] = X_mean 
        pt0s[igroup] = t_mean
        groups_ids_bigenough.append(igroup)

    dlm = {}
    dlm['vs'] = vs
    dlm['x0s'] = x0s
    dlm['pt0s'] = pt0s
    dlm['groups_ids_bigenough'] = np.array(groups_ids_bigenough)
    return dlm

