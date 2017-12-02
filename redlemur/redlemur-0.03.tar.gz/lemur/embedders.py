from sklearn.manifold import TSNE, MDS
import pandas as pd
import numpy as np

import lemur.datasets as lds

class BaseEmbedder:
    """A generic embedder object to be extended.

    Parameters
    ----------
    num_components : int
	The number of dimensions the embedding should have.

    Attributes
    ----------
    num_components : int
        The number of dimensions the embedding should have.

    """
    def __init__(self, num_components = 2):
        self.num_components = num_components

class MDSEmbedder(BaseEmbedder):
    embedding_name = "MDS"
    def embed(self, DM):
        """Embed a distance matrix using MDS.

        Parameters
        ----------
        M : :obj:`ndarray`
            The distance matrix to be embedded

        Returns
        -------
        :obj:`ndarray`
            A :obj:`ndarray` of the embedding.

        """
        mds = MDS(n_components = self.num_components, dissimilarity="precomputed")
        mds.fit(DM.getMatrix())
        emb = mds.embedding_
        emb = pd.DataFrame(emb)
        emb.index = DM.labels
        emb.index.name = DM.label_name
        name = DM.dataset.name + " " + \
               DM.metric_name + " " + \
               self.embedding_name
        EDS = lds.DataSet(emb, name)
        return EDS

class TSNEEmbedder(BaseEmbedder):
    """A TSNE embedder.

    This uses the sklearn.manifold.TSNE function.

    Attributes
    ----------
    embedding_name : str
        The name of this embedding (default is `TSNE`)

    """
    embedding_name = "TSNE"
    def embed(self, M):
        """Embed a distance matrix using TSNE.

        Parameters
        ----------
        M : :obj:`ndarray`
            The distance matrix to be embedded

        Returns
        -------
        :obj:`ndarray`
            A :obj:`ndarray` of the embedding.

        """
        tsne = TSNE(n_components = self.num_components, metric="precomputed")
        tsne.fit(M)
        emb = tsne.embedding_
        return emb 

def SVD(D):
    """A helper function to do SVD.

    Parameters
    ----------
    D : :obj:`ndarray`
        The matrix to compute SVD on.

    Returns
    -------
    U : :obj:`ndarray`
        An :obj:`ndarray` of the left singular matrix.
    s : :obj:`ndarray`
        An :obj:`ndarray` of the singular values (just a vector, not a square matrix).
    Vt : :obj:`ndarray`
        An :obj:`ndarray` of the right singular matrix.
    m : :obj:`ndarray`
        An :obj:`ndarray` of the affine translation required to center the data  (just a vector, not a square matrix).

    """
    d, n = D.shape
    mu = np.mean(D, axis=1).reshape(d, 1)
    D = D - mu
    U, s, Vt = np.linalg.svd(D, full_matrices=False)
    return U, s, Vt, mu

class PCAEmbedder(BaseEmbedder):
    embedding_name = "PCA"
    def embed(self, M):
        U, s, Vt, m = SVD(M) 
        return (U[:, :self.num_components].T.dot(M)).T  
