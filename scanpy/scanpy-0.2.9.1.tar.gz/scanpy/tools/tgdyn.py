"""
TGDYN - single-cell dynamics on the graph

Compute tangential dynamics in subsets of the data and infer gene importance by
that.
""" 

import numpy as np
from .. import utils
from .. import settings as sett
from scipy.stats import t
import statsmodels.stats.multitest as smm

def tgdyn(adata, smp='dpt_groups', names='all'):
    """Tangential dynamics along paths.

    For a given partitioning of the data into subsets - typically paths on the
    data graph - where each subset is associated with a stage in a biological
    process. Also, subsets might be segments obtained from DPT.
    1. fit a linear model to each subset, capturing the tangential dynamics
    [2. obtain a transition matrix from the linear model]
    [3. compute the dynamics induced by this transition matrix]

    Parameters
    ----------
    dprev : dict containing
        groups_masks : np.ndarray of dtype bool
            Array of shape (number of groups) x (number of samples) that stores
            boolean mask arrays that identify subgroups (segments or paths).
    adata : dict, AnnData
        Data dictionary.
    smp : str, optional (default: 'groups')
        Specify the name of the grouping to consider.
    names : str, list, np.ndarray
        Subset of groupnames - e.g. 'C1,C2,C3' or ['C1', 'C2', 'C3'] - in
        dgroups[smp + '_names'] to which comparison shall be restricted.
    """
    # for clarity, rename variable
    groups_names = names
    if smp == 'paths_groups': # Temporary solution to  storing paths with non-zero distance in a different way
        groups_names, _ = utils.select_groups(adata, groups_names, smp='paths_groups')
        groups_masks = adata.add['paths_groups_masks']
    else:
        groups_names, groups_masks = utils.select_groups(adata, groups_names, smp=smp)
    adata.add['tgdyn_groups'] = smp
    adata.add['tgdyn_groups_names'] = groups_names
    sett.m(0, 'computing dynamics within', groups_names)

    if 'dpt_pseudotime' not in adata.smp_keys():
        sett.m(0, 'compute dpt first')
        from sys import exit
        exit(0)

    # compute velocities for subgroups
    dlm = fit_linear_model(adata.X,
                           # regress on dpt_pseudotime
                           adata.smp['dpt_pseudotime'],
                           groups_masks)
    sett.mt(0, 'fitted linear model')

    # write results of linear model to tgdyn dictionary
    adata.add['tgdyn_vs'] = dlm['vs']
    adata.add['tgdyn_x0s'] = dlm['x0s']
    adata.add['tgdyn_pvals'] = dlm['pvals']
    adata.add['tgdyn_padj'] = dlm['padj']    
    adata.add['tgdyn_pt0s'] = dlm['pt0s']
    adata.add['tgdyn_groups_ids_bigenough'] = dlm['groups_ids_bigenough']
    adata.add['tgdyn_nquant'] = dlm['n_quantiles']

    # which genes drive the process, e.g., differentiation?
    # store the normalized velocity and the genes with the strongest contributions
    vs_norm = np.zeros(dlm['vs'].shape)
    genes_sorted = np.zeros(dlm['vs'].shape, dtype=np.int_)
    nquant = dlm['n_quantiles']
    for igroup, _ in enumerate(groups_masks):
        for quant in range(nquant):
            v = dlm['vs'][igroup*nquant+quant]
            abs_v = np.abs(v)
            vs_norm[igroup*nquant+quant] = v / np.max(abs_v)
            # sorted according to decreasing values
            genes_sorted[igroup*nquant+quant] = np.argsort(np.abs(vs_norm[igroup*nquant+quant]))[::-1]
            
    adata.add['tgdyn_vs_norm'] = vs_norm
    adata.add['tgdyn_genes_sorted'] = genes_sorted
    sett.mt(0, 'finished tgdyn_simple')
    return adata

def plot_tgdyn(adata):
    """ 
    Plot analysis of single-cell dynamics on the graph.

    Parameters
    ----------
    dtgdyn : dict
        Dictionary returned by tgdyn.
    dprev : dict
        Dictionary returned by dpt or scct.
    adata : dict
        Dictionary returned by get_data.
    """
    # Make ranking plot
    plot_ranking(adata)
    
    # Make heatmap plot
    plot_heatmap(adata)
    
    # Make main heatmap plot
    correlation_segments(adata)
    

def fit_linear_model(X, pseudotimes, groups_masks, min_groupsize=5, n_quantiles=10):
    """ 
    Fit standard linear regression.

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
    vs = np.zeros((n_groups*n_quantiles, n_genes))
    x0s = np.zeros((n_groups*n_quantiles, n_genes))
    pvals = np.zeros((n_groups*n_quantiles, n_genes))
    padj = np.zeros((n_groups*n_quantiles, n_genes))    
    pt0s = np.zeros((n_groups*n_quantiles))
    groups_ids_bigenough = []

    for igroup, group in enumerate(groups_masks):
        # group size
        group_size = pseudotimes[group].size
        print('group', igroup, 'has size', group_size)
        # only consider groups with a sufficiently high number of samples
        if group_size < min_groupsize*n_quantiles:
            continue
        # storage for quantile
        vs_seg = np.zeros((n_quantiles, n_genes))
        x0s_seg = np.zeros((n_quantiles, n_genes))
        pvals_seg = np.zeros((n_quantiles, n_genes))
        padj_seg = np.zeros((n_quantiles, n_genes))
        pt0s_seg = np.zeros((n_quantiles))
        # calculate quantiles
        ts = pseudotimes[group]
        quantiles = np.percentile(ts, np.linspace(0,100,n_quantiles+1))
        
         # iterate through the quantiles
        for quant in range(n_quantiles):
            # set segment mask
            segment = np.copy(group)
            segment[(pseudotimes < quantiles[quant]) | (pseudotimes > quantiles[quant+1])] = 0

            # segment size
            segment_size = pseudotimes[segment].size                           
            # mean of pseudotime in the group
            t_mean = pseudotimes[segment].mean()
            # mean of gene expression in the group
            X_mean = X[segment].mean(axis=0)
            # shift X and t to mean
            Xshift = X[segment] - X_mean
            tshift = pseudotimes[segment] - t_mean
            # compute means
            Xt_mean = (Xshift * tshift[:,np.newaxis]).mean(axis=0)
            tsq_mean = (tshift**2).mean()
            # velocity
            v = Xt_mean / tsq_mean
            vs_seg[quant] = v
            x0s_seg[quant] = X_mean
            pt0s_seg[quant] = t_mean
            # calculate standard error
            se = np.sqrt(np.divide(np.square(Xshift).sum(axis=0)-np.square(v)*np.square(tshift).sum(), segment_size-2))
            # caculate t statistic, set to zero if se=0 as in this case v=0 anyway
            T0 = np.divide(v*np.sqrt((tshift**2).sum()), se, out=np.zeros_like(v*np.sqrt((tshift**2).sum())), where=se!=0)
            pval = t.sf(np.abs(T0), segment_size-2)*2
            pvals_seg[quant] = pval
            # correct for multiple testing
            sig_level = 0.1
            rej, pval_corr = smm.multipletests(pval, alpha=sig_level, method='fdr_bh')[:2]
            # calculate p-value
            padj_seg[quant] = pval_corr
           
            # save quantile values
            vs[(igroup*n_quantiles):(igroup*n_quantiles+n_quantiles)] = vs_seg
            x0s[(igroup*n_quantiles):(igroup*n_quantiles+n_quantiles)] = x0s_seg
            pvals[(igroup*n_quantiles):(igroup*n_quantiles+n_quantiles)] = pvals_seg
            padj[(igroup*n_quantiles):(igroup*n_quantiles+n_quantiles)] = padj_seg
            pt0s[(igroup*n_quantiles):(igroup*n_quantiles+n_quantiles)] = pt0s_seg
            
        groups_ids_bigenough.append(igroup)

    dlm = {}
    dlm['vs'] = vs
    dlm['x0s'] = x0s
    dlm['pvals'] = pvals
    dlm['padj'] = padj
    dlm['pt0s'] = pt0s
    dlm['groups_ids_bigenough'] = np.array(groups_ids_bigenough)
    dlm['n_quantiles'] = n_quantiles
    return dlm

def plot_ranking(adata):
    """ 
    Plot ranking.

    TODO
    ----
    Replace with call to plotting.plot_ranking.

    Parameters
    ----------
    dtgdyn : dict
        Dictionary returned by tgdyn.
    adata : dict
        Dictionary returned by get_data.
    """
    from ..compat.matplotlib import pyplot as pl
    
    # how many quantiles
    n_quant = adata.add['tgdyn_nquant']
    
    n_panels = adata.add['tgdyn_groups_ids_bigenough'].shape[0] * n_quant
    # number of genes shown
    n_genes = 10

    # find minimum velocity to set y-axis limit
    ymin = 1
    for igroup in adata.add['tgdyn_groups_ids_bigenough']:
        for iquant in range(n_quant):
            quant_pos = igroup*n_quant + iquant
            genes = adata.add['tgdyn_genes_sorted'][quant_pos, :n_genes] 
            ymin = np.min([ymin, 
                           np.min(np.abs(adata.add['tgdyn_vs_norm'][quant_pos, genes]))])

    # determine n_panels in x and y direction
    if n_panels <= 5:
        n_panels_y = 1
        n_panels_x = n_panels
    else:
        n_panels_y = 2
        n_panels_x = int(n_panels/2+0.5)

    # do the actual plotting
    fig = pl.figure(figsize=(n_panels_x*4, n_panels_y*4))
    pl.subplots_adjust(left=0.15, right=0.98, bottom=0.13)
    count = 1
    for igroup in adata.add['tgdyn_groups_ids_bigenough']:
        for iquant in range(n_quant):
            quant_pos = igroup*n_quant + iquant
            fig.add_subplot(n_panels_y, n_panels_x, count)
            # get the velocity to plot
            v = adata.add['tgdyn_vs_norm'][quant_pos]
            # loop over the top-ranked genes
            for ig, g in enumerate(adata.add['tgdyn_genes_sorted'][quant_pos, :n_genes]):
                marker = r'\leftarrow' if v[g] < 0 else r'\rightarrow'
                color = 'red' if v[g] < 0 else 'green'
                pl.text(ig,
                        np.abs(v[g]),
                        r'$ ' + marker + '$ ' + adata.var_names[g],
                        color=color,
                        rotation='vertical',
                        verticalalignment='bottom',
                        horizontalalignment='center',
                        fontsize=8)
            title = adata.add['tgdyn_groups'] + ' ' + str(adata.add['tgdyn_groups_names'][igroup] + '_' + str(iquant))
            pl.title(title)   
            pl.xlim(-0.9, ig+1-0.1)
            pl.ylim(-0.02+ymin, 1.15)
            if count > n_panels_x:
                pl.xlabel('ranking')
            if count == 1 or count == n_panels_x + 1: 
                pl.ylabel('|velocity$_{gene}$|/max$_{genes}$|velocity$_{gene}$|')
            else:
                pl.yticks([])
            count += 1

    writekey = sett.basekey + '_tgdyn_' + adata.add['tgdyn_groups'] + sett.plotsuffix
    plott.savefig(writekey + '_ranking')
    if not sett.savefigs and sett.autoshow:
        pl.show()

def plot_heatmap(adata):
    # May want to split this into separate function
    
    from ..compat.matplotlib import pyplot as pl
    #from scipy.cluster.hierarchy import leaves_list, linkage
    
    n_genes = 10
    n_quant = adata.add['tgdyn_nquant']
    
    # determine n_panels in x and y direction
    n_panels = adata.add['tgdyn_groups_ids_bigenough'].shape[0]
    if n_panels <= 5:
        n_panels_y = 1
        n_panels_x = n_panels
    else:
        n_panels_y = 2
        n_panels_x = int(n_panels/2+0.5)
    
    fig = pl.figure(figsize=(n_panels_x*4, n_panels_y*4))
    pl.subplots_adjust(left=0.15, right=0.98, bottom=0.13)
    count = 1
    for igroup in adata.add['tgdyn_groups_ids_bigenough']:
        ax = fig.add_subplot(n_panels_y, n_panels_x, count)
        
        # Get genes to plot
        top_genes = np.ndarray.flatten(adata['tgdyn_genes_sorted'][(igroup*n_quant):(igroup*n_quant+n_quant), :n_genes])
        
        # Plot velocities of genes
        #v = adata['tgdyn_vs'][(igroup*n_quant):(igroup*n_quant+n_quant), top_genes]
        v = adata.add['tgdyn_vs_norm'][(igroup*n_quant):(igroup*n_quant+n_quant), top_genes]
        #v_clust = linkage(v.transpose(), 'ward')
        #leaves = leaves_list(v_clust)
        #v = v[:,leaves]

        im = pl.imshow(np.transpose(v), cmap=pl.cm.coolwarm, aspect='auto')
        ax.set_xticks(list(range(n_quant)))
        ax.set_xticklabels([str(igroup) + '_' + str(i+1) for i in list(range(n_quant))], fontsize=10, rotation='vertical')
        ax.set_yticks(list(range(len(top_genes))))
        #ax.set_yticklabels(adata.var_names[top_genes][leaves], fontsize=7)
        ax.set_yticklabels(adata.var_names[top_genes], fontsize=7)
        #fig.colorbar(im)
        
        count += 1
    
    writekey = sett.basekey + '_tgdyn_' + adata.add['tgdyn_groups'] + sett.plotsuffix
    plott.savefig(writekey + '_heatmap')
    if not sett.savefigs and sett.autoshow:
        pl.show()

def correlation_segments(adata):
    from ..compat.matplotlib import pyplot as pl
    from itertools import compress
    import seaborn as sns
    import pandas as pd
    
    # May want this as separate part of analysis
    # For now do on normalised velocities - may not completely make sense
    n_genes = 10
    n_quant = adata.add['tgdyn_nquant']
    top_genes = np.unique(adata.add['tgdyn_genes_sorted'][:, :n_genes])
    
    # Get velocities for these genes
    v = adata.add['tgdyn_vs_norm'][:, top_genes]
    
    # Remove the zero rows
    #row_select = ~np.all(v == 0, axis=1) # Need this if doing on absolute velcoties rather than normalised
    row_select = ~np.all(np.isnan(v), axis=1)
    column_names = [str(igroup) + '_' + str(i+1) for igroup in adata.add['tgdyn_groups_ids_bigenough'] for i in list(range(n_quant))]
    column_names = list(compress(column_names, np.ndarray.tolist(row_select)))
    v = v[row_select]
    
    # Use inbuilt functions for calculating correlation matrix and clustering
    df = pd.DataFrame(v.transpose(), columns=column_names)
    corrmat = pd.DataFrame(df.corr(method='spearman'))

    # Draw the heatmap using seaborn
    g = sns.clustermap(corrmat)
    pl.setp(g.ax_heatmap.get_yticklabels(), rotation=30)
    pl.setp(g.ax_heatmap.get_xticklabels(), rotation=30)
    
    writekey = sett.basekey + '_tgdyn_' + adata.add['tgdyn_groups'] + sett.plotsuffix
    plott.savefig(writekey + '_combined_heatmap')
    if not sett.savefigs and sett.autoshow:
        pl.show()
