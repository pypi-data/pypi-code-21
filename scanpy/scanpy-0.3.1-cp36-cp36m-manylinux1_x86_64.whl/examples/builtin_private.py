"""
Example Data and Use Cases - Private Builtin Examples
"""

from __future__ import absolute_import
import numpy as np
import scanpy as sc

#--------------------------------------------------------------------------------
# The 'dexdata dictionary' stores information about example data.
#--------------------------------------------------------------------------------

dexdata = {
    'nestorowa16' : {
        'doi': '10.1182/blood-2016-05-716480',
    }
}

#--------------------------------------------------------------------------------
# The 'example dictionary' provides information about tool parameters 
# that deviate from default parameters.
#--------------------------------------------------------------------------------

dexamples = {
    'nestorowa16': {
        'dpt/diffmap': {'k': 4, 'knn': True},
        'paths': {'k': 4, 'knn': True},
        'diffrank': {'names': 'C1,C2,start', 'log': False},
    },
    'nestorowa16_tf': {
        'dpt/diffmap': {'k': 4, 'knn': True},
        'paths': {'k': 4, 'knn': True},
        'diffrank': {'names': 'C1,C2,start', 'log': False},
    },
}

#--------------------------------------------------------------------------------
# One function per example that reads, annotates and preprocesses data
# - one function 'exkey()' per 'exkey'
#--------------------------------------------------------------------------------

def anika():
    """
    For Sophie.
    """
    adata = sc.read('data/anika/myexample.csv')
    dgroups = sc.read('data/anika/mygroups.csv', as_strings=True)
    adata.smp['groups'] = dgroups['X'][:, 0]
    adata['xroot'] = adata.X[336]
    return adata

def drukkerAPA():
    """
    For Lukas.
    """
    adata = sc.read('data/drukkerAPA/hESC.UMI.matrix.newline_inserted.csv')
    adata = adata.transpose()
    return adata

def maehr17():
    """
    David: Thymus collab (Pseudodynamics) [UMASS]
    """
    filename = 'data/maehr17/blood_counts_raw.data'
    adata = sc.read(filename)
    adata = adata.transpose()

    meta = np.genfromtxt('data/maehr17/blood_metadata.data', dtype=str)
    adata.smp['groups'] = meta[1:, 3]
    adata.smp['time'] = meta[1:, 4].astype(float)

    adata = maehr17_annotate(adata)
    adata = sc.pp.weinreb16(adata)  # contains already X_pca
    return adata

def maehr17_MybGate():
    """
    David: Thymus collab (Pseudodynamics) [UMASS]
    """
    filename = 'data/maehr17/blood_counts_raw.data'
    adata = sc.read(filename)
    adata = adata.transpose()

    meta = np.genfromtxt('data/maehr17/blood_metadata_mybgate.data', dtype=str)
    cell_filter = np.in1d(adata.smp_names, meta[:, 0])
    adata = adata[cell_filter]
    adata.smp['groups'] = meta[:, 3]
    adata.smp['time'] = meta[:, 4].astype(float)

    adata = maehr17_annotate(adata)
    adata = sc.pp.weinreb16(adata)  # contains already X_pca
    # root for DPT: find with R script of dm coordinates:
    # Python indexing starts at 0 and R at 1: 1703-1
    adata['xroot'] = adata['X_pca'][1702]
    return adata

def nestorowa16():
    """
    Data from Nestorowa et al. (2016).

    For Fiona.
    """
    adata = nestorowa16_raw()
    adata = sc.pp.weinreb16(adata, svd_solver='arpack')

    # add transcription factor filtering
    tf_genes = np.genfromtxt('data/nestorowa16/data/tf_gene_list.txt', dtype=str)
    tf_gene_filter = np.in1d(adata.var_names, tf_genes)
    adata['tf_gene_filter'] = tf_gene_filter
    return adata

def nestorowa16_tf():
    """
    Filtered for transcription factors.
    """
    adata = nestorowa16_raw()

    tf_genes = np.genfromtxt('data/nestorowa16/data/tf_gene_list.txt', dtype=str)
    tf_gene_filter = np.in1d(adata.var_names, tf_genes)
    adata = adata[:, tf_gene_filter]
    adata = sc.pp.weinreb16(adata, svd_solver='arpack')
    return adata

def tenx_GRCh38():
    """
    For Lukas.

    Play around with very large sparse matrices.

    TODO: Need to update Scanpy infrastructure in order to deal with this.
    """
    adata = sc.read('data/tenx_GRCh38/matrix.mtx')
    adata = adata.transpose()
    return adata

#--------------------------------------------------------------------------------
# Optional functions for Raw Data, Annotation, Postprocessing, respectively
#--------------------------------------------------------------------------------

def maehr17_annotate(adata):
    """
    David: Put in raw expression of marker genes
    """
    # TC (Nat Im review 2014 Yui)
    tc_surface_receptors = ['Flt3', 'Cd44', 'Il2ra', 'Il7r', 'Cd3e', 'Cd4', 'Cd8a']
    tc_markers = [
        'Gata2', 'Hoxa9', 'Meis1', 'Lmo2', 'Mef2c', 'Gfi1b', 'Lyl1', 'Spi1', 'Bcl11a', 'Hhex', 'Mycn', 'Erg', 'Tcf3',
        'Ikzf1', 'Tcf12', 'Notch1', 'Runx1', 'Gfi1', 'Myb', 'Myc', 'Gata3', 'Tcf7', 'Ets1', 'Hes1', 'Ahr', 'Tcf12',
        'Bcl11b', 'Notch3', 'Spib', 'Ets2', 'Lef1', 'Rorc', 'Id3',
    ]

    # DC, NK (Abcam poster)
    dc_markers = ['Itgax', 'Cd24a', 'Ptprc']
    nk_markers = ['Itgam', 'Il2rb', 'Klrb1', 'Ncr1']

    all_markers = tc_surface_receptors + tc_markers + dc_markers + nk_markers

    adata.smp[all_markers] = adata[:, all_markers].X.T
    return adata


def nestorowa16_raw():
    datadir = 'data/nestorowa16/data/'
    adata = sc.read(datadir + 'norm_counts_nestorowa_data.txt')
    adata.smp_names = np.genfromtxt(datadir + 'cell_names_nestorowa_data.txt', dtype=str)
    adata.var_names = np.genfromtxt(datadir + 'gene_names_nestorowa_data.txt', dtype=str)
    groups = np.genfromtxt(datadir + 'start_and_end_cells.txt', dtype=str)
    groups = np.array([n.replace('start_cells', 'start') for n in groups])
    # deal with one outlier in the C9 group
    groups[718] = 'no_gate'
    adata.smp['groups'] = groups
    adata['iroot'] = np.where(groups == 'start')[0][0]
    adata['xroot'] = adata.X[adata['iroot']]
    # define fates for paths
    # unique group names in array of length (number of groups)
    from natsort import natsorted
    groups_names = np.array(natsorted(np.unique(groups)))
    # move 'dontknow' group to the very end
    dontknow_id = np.argwhere(groups_names == 'no_gate')[0]
    groups_names[dontknow_id] = groups_names[-1]
    groups_names[-1] = 'no_gate'
    adata['groups_names'] = groups_names[:-1]
    # compute fates for putting in dexamples
    if False:
        from collections import OrderedDict
        fates = OrderedDict([])
        for key in groups_names[:-2]:
            fates[key] = np.where(groups == key)[0]
        print(fates)
    return adata
