import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import sklearn.decomposition
from bobo.app import loadlibrary
from janus.features import densesift, densePCAsift, denseMultiscaleSIFT
from bobo.util import matrix2yaml, mat2gray, jet, tolist, signsqrt, save, load, matread
from bobo.geometry import sqdist
import janus.gmm
import ctypes
import janus.reduction
#import cv2
from bobo.geometry import covariance_to_ellipse
#import math
import binascii
import os
import shutil


class DiagonalPlusLowRankGaussian(object):
    """Diagonal plus low rank decomposition of a Gaussian covariance"""

    def __init__(self, q_diagonal, V_lowrank, d_lowrank, mu):
        # Q = q_diagonal + V_lowrank*(1.0 / d_lowrank)*V_lowrank^T
        self._V_lowrank = V_lowrank
        self._d_lowrank = d_lowrank
        self._mu = mu
        self._q_diagonal = q_diagonal
        
    def __repr__(self):
        return str('<DiagonalPlusLowRankGaussian: dimensionality=%s, rank=%s>' % (self.dimensionality(), self.rank()))

    def __mul__(self, other):
        print 'self * other'
        raise ValueError('FIXME')
    
    def __rmul__(self, other):
        print 'other * self'
        raise ValueError('FIXME')
                
    def dimensionality(self):
        return int(self._mu.size)
    
    def rank(self):
        return self._V_lowrank.shape[1] if self._V_lowrank is not None else 0
                    
    def gmm(self, numModes, weights=None):
        """return a gaussian mixture model representation of diagonal component reshaped according to requested number of modes"""
        weights = (1.0/float(numModes)) * np.ones(numModes, dtype=np.float32) if weights is not None else weights
        return janus.gmm.GaussianMixtureModel(mean=self._mu.reshape( (numModes,-1) ), covariance=self._q_diagonal.reshape( (numModes,-1) ), prior=weights)

    def load(self, V_mtxfile, s_mtxfile):
        """Load csv files exported from BigTruncatedSVD as low rank component"""
        self._V_lowrank = matread(V_mtxfile, delimiter=',')
        self._d_lowrank = np.square(matread(s_mtxfile, delimiter=','))  
        return self
                
    def train(self, featset, k_rank=4, n_modes=128, n_iterations=20, r_pooling=0.25, seed=42, numSVD=1E5, textfile=None):
        """Train Low rank component for provided RDD of features"""
        
        # Gaussian mixture model
        gmm = janus.gmm.train(featset, n_modes=n_modes, features=None, n_iterations=n_iterations, seed=seed)
        
        # Low Rank Gaussian 
        print "[janus.gausshape.gmm]: number of descriptors = %d" % featset.count()        
        X = featset.map(lambda x: scipy.sparse.csr_matrix(np.array([np.float32(np.linalg.norm(x[-2:] - g.mean[-2:]) < r_pooling)*(x-g.mean) for g in gmm])))  # pooled and de-meaned

        if textfile is not None:
            print '[janus.gausshape.gmm]: Saving dense covariance features to textfile directory "%s"' % textfile                                    
            X.map(lambda x: ''.join(['%1.6f,' % v if v!=0 else '0,' for v in x.toarray().flatten()])[0:-1] if x.nnz>0 else None).filter(lambda x: x!=None).saveAsTextFile(textfile)

            # Format: cols,col_index,colvalue,...,
            #print '[janus.gausshape.gmm]: Saving sparse covariance features to textfile directory "%s"' % textfile                        
            #(X.map(lambda x: str('%d,' % x.shape[1] + ''.join(['%s,%s,' % (k,v) for (k,v) in zip(x.indices, x.data)])[0:-1]) if x.nnz>0 else None).filter(lambda x: x is not None).saveAsTextFile(textfile))

            print '[janus.gausshape.gmm]: Next, run training using BigTruncatedSVD on saved text file directory'
            
        else:
            print "[janus.gausshape.gmm]: Pooling radius=%f, Rank=%d, numSVD=%d" % (r_pooling, k_rank, numSVD)
            X = X.takeSample(withReplacement=False, num=int(numSVD), seed=seed)
            svd = sklearn.decomposition.TruncatedSVD(n_components=k_rank).fit(scipy.sparse.vstack(X))
            self._V_lowrank = svd.components_.transpose()  # N x K
            self._d_lowrank = np.maximum(svd.explained_variance_, 0).reshape( (svd.explained_variance_.size, 1) ) # column vector

        # Done!
        self._q_diagonal = gmm.covariance.flatten().reshape( (gmm.covariance.size, 1) )  # column vector
        self._mu = gmm.mean.flatten().reshape( (gmm.mean.size, 1) ) # column vector
        #self._weights = gmm.prior
        return self

    def precisionMatrix(self):
        raise ValueError('Use matrix inversion lemma for J = (Q+VdV^T)^{-1}')
        

    def marginal(self, k_dims):
        mu_ = np.copy(self._mu[k_dims])
        V_ = np.copy(self._V_lowrank[k_dims,:])
        d_ = np.copy(self._d_lowrank)
        q_ = np.copy(self._q_diagonal[k_dims])        
        return DiagonalPlusLowRankGaussian(q_, V_, d_, mu_)

    def sample(self):
        raise ValueError('FIXME: diagonal plus low rank needs new factorization Q=A*A^T to sample?  Better way?')

    def conditional(self):
        raise ValueError('FIXME from old GausshapeMode')
 

class Gausshape(object):
    """Gausshape is a partitioned sparse + lowrank Gaussian"""

    def __init__(self, axx_blkpart=None, Bxy_blkpart=None, dyy_blkpart=None, Vxx_lowrank=None, dxx_lowrank=None, Vyy_lowrank=None, dyy_lowrank=None, mx=None, my=None):
        # J = V_lowrank*(1.0 / d_lowrank)*V_lowrank^T  + [diag(a) B; B^T diag(d)]
        self._Vxx_lowrank = Vxx_lowrank
        self._dxx_lowrank = dxx_lowrank
        self._Vyy_lowrank = Vyy_lowrank
        self._dyy_lowrank = dyy_lowrank
        self._mx = mx
        self._my = my        
        self._axx_blkpart = axx_blkpart
        self._Bxy_blkpart = Bxy_blkpart
        self._dyy_blkpart = dyy_blkpart
        
    def __repr__(self):
        return str('<gausshape: dimensionality=%s, rank=%s>' % (self.dimensionality(), self.rank()))

    def __mul__(self, other):
        print 'self * other'
        raise ValueError('FIXME')
    
    def __rmul__(self, other):
        print 'other * self'
        raise ValueError('FIXME')

    def ispartitioned(self):
        return self._mx is not None and self.my is None
    
    def dimensionality(self):
        return int(self._mx.size + self._my.size) if self._mx is not None and self._my is not None else 0
    
    def rank(self):
        return int(self._Vxx_lowrank.shape[1] + self._Vyy_lowrank.shape[1]) if self._Vxx_lowrank is not None and self._Vyy_lowrank is not None else 0
                    
    def gmm(self):
        """return a gaussian mixture model representation"""        
        #return janus.gmm.GaussianMixtureModel()
        raise ValueError('FIXME')

    def load(self, V_mtxfile, s_mtxfile):
        """Load csv files exported from BigTruncatedSVD as low rank component"""
        self._Vxx_lowrank = matread(V_mtxfile, delimiter=',')
        self._dxx_lowrank = np.square(matread(s_mtxfile, delimiter=','))  
        return self
            
    def export(self, yamlfile):
        """Save parameters to yaml file for opencv import"""
        print "[janus.gausshape]: writing parameters to '%s' " % yamlfile
        mtxlist = []; mtxname = [];
        mtxlist.append(self._Vxx_lowrank)  
        mtxname.append('V_lowrank')
        mtxlist.append(self._dxx_lowrank)  
        mtxname.append('d_lowrank')
        mtxlist.append(self._axx_blkpart)        
        mtxname.append('q_diagonal')              
        mtxlist.append(self._mx)
        mtxname.append('mu')
        mtxlist.append(self._gmm.prior)
        mtxname.append('weights')              
        matrix2yaml(yamlfile, mtxlist, mtxname)
        return yamlfile
    
    def train(self, featset, k_rank=4, n_modes=128, n_iterations=20, r_pooling=0.25, seed=42, numSVD=1E5, textfile=None, gmm=None):
        """Low rank Gauss-Shape Model for provided RDD of features"""
        
        # Gaussian mixture model
        if gmm is None:
            gmm = janus.gmm.train(featset, n_modes=n_modes, features=None, n_iterations=n_iterations, seed=int(seed))
        
        # Low Rank Gaussian 
        print "[janus.gausshape.gmm]: number of descriptors = %d" % featset.count()        
        X = featset.map(lambda x: scipy.sparse.csr_matrix(np.array([np.float32(np.linalg.norm(x[-2:] - g.mean[-2:]) < r_pooling)*(x-g.mean) for g in gmm])))  # pooled and de-meaned

        if textfile is not None:
            print '[janus.gausshape.gmm]: Saving dense covariance features to textfile directory "%s"' % textfile                                    
            X.map(lambda x: ''.join(['%1.6f,' % v if v!=0 else '0,' for v in x.toarray().flatten()])[0:-1] if x.nnz>0 else None).filter(lambda x: x!=None).saveAsTextFile(textfile)

            # Format: cols,col_index,colvalue,...,
            #print '[janus.gausshape.gmm]: Saving sparse covariance features to textfile directory "%s"' % textfile                        
            #(X.map(lambda x: str('%d,' % x.shape[1] + ''.join(['%s,%s,' % (k,v) for (k,v) in zip(x.indices, x.data)])[0:-1]) if x.nnz>0 else None).filter(lambda x: x is not None).saveAsTextFile(textfile))

            print '[janus.gausshape.gmm]: Next, from 0021 in "$JANUS/components/gausshape/BigTruncatedSVD" run "spark-submit --conf spark.default.parallelism=2048 --driver-memory 64G --master spark://ma01-5200-0020:7077 --class BigTruncatedSVD target/scala-2.10/big-truncated-svd_2.10-1.0.jar ${APPNAME} %d ${FRACTION=0.005} %s V.mtx S.mtx"' % (k_rank, textfile)
            
        else:
            print "[janus.gausshape.gmm]: Pooling radius=%f, Rank=%d, numSVD=%d" % (r_pooling, k_rank, numSVD)
            X = X.takeSample(withReplacement=False, num=int(numSVD), seed=seed)
            svd = sklearn.decomposition.TruncatedSVD(n_components=k_rank).fit(scipy.sparse.vstack(X))
            self._Vxx_lowrank = svd.components_.transpose()  # N x K
            self._dxx_lowrank = np.maximum(svd.explained_variance_, 0).reshape( (svd.explained_variance_.size, 1) ) # column vector

        # Done!
        self._axx_blkpart = gmm.covariance.flatten().reshape( (gmm.covariance.size, 1) )  # column vector
        self._mx = gmm.mean.flatten().reshape( (gmm.mean.size, 1) ) # column vector
        self._gmm = gmm
        return self


                
class DeepGausshape(Gausshape):
    """Hierarchical Supervised learning of discriminiative mixture"""    
    pass




class GaussObject(Gausshape):
    def __init__(self, libfile, modelfile, reload=False):
        """YAML file exported from Gausshape training, dynamic library for gausshape inference"""
        self._load(libfile=libfile, modelfile=modelfile, reload=reload)
        
    def __repr__(self):
        return str('<janus.gausshape.GaussObject: lib="%s", model="%s">' % (self._libfile, self._modelfile))

    def __del__(self):        
        print '[janus.gausshape.GaussObject]: entering __del__'
        self.dylib.release(ctypes.c_void_p(self.obj))  # free all allocated resources when python garbage collects this library        
        self.dylib.dlclose(self.dylib._handle)

    def _load(self, libfile, modelfile, reload=None):
        self._libfile = libfile 
        self._modelfile = modelfile
        
        if reload == True:
            (filepath, ext) = os.path.splitext(self._libfile)
            newfile = '%s_%s%s' % (filepath, binascii.b2a_hex(os.urandom(4)), ext)
            shutil.copyfile(self._libfile, newfile)
            self._libfile = newfile
            print '[janus.gausshape.GaussObject]: forcing reload "%s" ' % self._libfile
        else:
            print '[janus.gausshape.GaussObject]: loading "%s" ' % self._libfile                                

        self.dylib = ctypes.CDLL(self._libfile)  # WARNING: does not use absolute path if library already on DYLD_LIBRARY_PATH
        initialize = self.dylib.initialize
        initialize.restype = ctypes.c_void_p
        self.obj = initialize(ctypes.c_char_p(self._modelfile))  # returns pointer to initialized C++ object
        return self
    
    def display(self):
        self.dylib.display(ctypes.c_void_p(self.obj))        

        
    def posterior(self, im, numIterations=3, tau=1.0):
        
        # Feature extraction
        f_features = (lambda im: denseMultiscaleSIFT(im, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25], dx=4, dy=4, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False))        
        D = f_features(im)
        
        # Output buffers size
        mc = ctypes.c_int(0)
        nc = ctypes.c_int(0)
        self.dylib.posteriorshape(ctypes.c_void_p(self.obj), ctypes.byref(mc), ctypes.byref(nc))
        (m,n) = (mc.value,nc.value)

        # Output buffer allocation
        mu = np.ascontiguousarray(np.zeros( (m,n), dtype=np.float32))
        q = np.ascontiguousarray(np.zeros( (m,n), dtype=np.float32))
        B = np.ascontiguousarray(np.zeros( (D.shape[0], m), dtype=np.float32 ))

        # Input buffer
        D = np.ascontiguousarray(D, dtype=np.float32)
        assert D.shape[1] == n
                
        # Posterior!
        print '[janus.gausshape.GaussObject]: computing posterior for DSIFT (%d x %d)' % (D.shape[0], D.shape[1])
        self.dylib.posterior(ctypes.c_void_p(self.obj),
                             D.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
                             ctypes.c_int(D.shape[0]),
                             ctypes.c_int(D.shape[1]),
                             mu.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  
                             ctypes.c_int(mu.size),
                             q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  
                             ctypes.c_int(q.size),
                             B.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  
                             ctypes.c_int(B.shape[0]),
                             ctypes.c_int(B.shape[1]),                             
                             ctypes.c_int(numIterations),
                             ctypes.c_float(tau))
        
        # Posterior gaussian mixture model
        return B
        #return janus.gmm.GaussianMixtureModel(mu, q, np.sum(B, axis=1))

    def test(self):
        self.dylib.test(ctypes.c_void_p(self.obj))                    
    
    def prior(self, imset, k_rank=4, n_iterations=20, seed=42, numSVD=1E5, r_pooling=0.125, n_modes=128, textfile=None, fractionSVD=0.1):
        f_densesift = (lambda im: denseMultiscaleSIFT(im, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25], dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False))
        featset = imset.flatMap(lambda im: f_densesift(im)).sample(withReplacement=False, fraction=fractionSVD)
        return self.train(featset, k_rank=k_rank, n_modes=n_modes, n_iterations=n_iterations, r_pooling=r_pooling, seed=seed, numSVD=numSVD, textfile=textfile)


#-----------------------------
#
# ARCHIVE
#
#-----------------------------


class _GausshapeMode(object):
    def __init__(self, V=None, d=None, mu=None, fullCovariance=None, diagCovariance=None, potentialVector=None, precisionMatrix=None):
        self.q = diagCovariance  
        self.Q = fullCovariance
        self.d = d
        self.V = V  # Q = VDV' = diag(q) = J^{-1}
        self.mu = mu
        self.h = potentialVector
        self.J = precisionMatrix

        # Error check
        if not (self.ismomentform() or self.isinformationform()):
            raise ValueError('invalid Gausshape parameters')
        
    def __repr__(self):
        return str('<gausshape.gaussian: dimensionality=%s, rank=%s>' % (str(self.dimensionality()), str(self.rank())))

    def display(self):
        print '[janus.gausshape]: dimensionality=%d, rank=%d>' % (self.dimensionality(), self.rank())
        print '[janus.gausshape]: mu, min=%1.3f, max=%1.3f' % (np.min(self.mu), np.max(self.mu))

        
    def ismomentform(self):
        return ((self.mu is not None) and # mean vector defined
                (((self.Q is not None) or (self.q is not None)) or # diagonal or full covariance
                 ((self.V is not None) and (self.d is not None)))) # factored covariance 

    def isinformationform(self):
        return ((self.h is not None) and  (self.J is not None))

    def isfactored(self):
        return self.d is not None

    def isdiagonal(self):
        return self.q is not None

    def isinverted(self):
        return self.J is not None

    #def momentform(self, mu, q):
    #    self.mu = mu.reshape( (mu.size,1) ) # nx1 column
    #    self.J = np.diag(1.0 / q)   # diagonal covariance q
    #    self.h = np.array(self.J.dot(mu))  # nx1 column      
    #    return self

    def dimensionality(self):
        return self.mu.size if self.mu is not None else None

    def position(self):
        return self.mu[-2:]  # final two rows

    def rank(self):
        if self.isfactored():
            return self.d.size
        elif self.isdiagonal():
            return np.count_nonzero(self.q)
        else:
            raise ValueError('rank only defined for factored or diagonal covariance')
            
    def mean(self):
        if self.mu is not None:
            return self.mu
        else:
            return self.covariance().dot(self.h)

    def potentialvector(self):
        if self.h is not None:
            return self.h
        elif self.ismomentform():
            return self.precisionmatrix().dot(self.mu)
        else:
            raise ValueError('cannot construct potentialvector')
    
        
    def precisionmatrix(self):
        self.J = None
        if self.J is None:
            if self.isfactored():
                k = np.nonzero(self.d)
                dinv = np.copy(self.d)
                dinv[k] = np.array((float(1.0) / self.d[k]))
                VDinv = self.V * np.reshape(dinv, (1, dinv.size)) # broadcasting, multiply column k by dinv[k]
                self.J = VDinv.dot(self.V.transpose()) # low rank inverse
            elif self.isdiagonal():
                self.J = np.diag(1.0 / self.q)  # diagonal covariance q            
            else:
                raise ValueError('precision matrix only supported for low rank or diagonal covariance')
        return self.J

    def covariance(self):
        if self.Q is None:
            if self.ismomentform() and self.isfactored():
                VD = self.V * self.d  # broadcasting, multiply column k by dinv[k]
                self.Q = VD.dot(self.V.transpose())
            elif self.ismomentform() and self.isdiagonal():
                self.Q = np.diag(self.q)  # diagonal to full covariance
            else:
                raise ValueError('invalid form')                
        return self.Q

    def log_likelihood(self, x):
        x = np.array(x)
        dim = self.dimensionality()

        if self.ismomentform() and self.isfactored():
            k = np.nonzero(self.d)[0]            
            if len(k) < self.rank():
                print '[janus.gausshape.log_likelihood][WARNING]: rank = %d < %d' % (len(k), self.rank())
            dinv = np.copy(self.d)
            dinv[k] = np.array((float(1.0) / self.d[k]))
            VDinv = self.V * dinv.reshape(1,dinv.size) # broadcasting, multiply column k by dinv[k], V*diag(dinv)
            logDetSigma = np.sum(np.log(self.d[k]))  # log(det(A)) = sum(log(eigenvalues(A)))            
            z = (x.reshape( (x.size, 1) ) - self.mu.reshape( (self.mu.size, 1) ))       
            ll = float(-0.5*z.transpose().dot(VDinv.dot(self.V.transpose().dot(z))) - 0.5*logDetSigma - 0.5*float(dim)*np.log(2.0*np.pi))            
            
        elif self.ismomentform() and self.isdiagonal():
            logDetSigma = np.sum(np.log(self.q))
            z = (x.reshape( (x.size, 1) ) - self.mu.reshape( (self.mu.size, 1) ))       
            ll = float(-0.5*z.transpose().dot(np.multiply(1.0 / self.q.reshape(self.q.size,1), z)) - 0.5*logDetSigma - 0.5*float(dim)*np.log(2.0*np.pi))
        else:
            raise ValueError('log_likelihood only supported for low rank or diagonal covariance')
        return ll

    def likelihood(self, x, maxLL=0):
        x = np.array(x)
        ll = self.log_likelihood(x)
        p = np.exp(ll + maxLL).flatten()  # minus maximum log-likelihood to avoid underflow
        return p
            
    def marginal(self, k_dims):
        if self.ismomentform() and self.isfactored():
            mu_ = np.copy(self.mu[k_dims])
            V_ = np.copy(self.V[k_dims,:])
            d_ = np.copy(self.d)
            return GausshapeMode(V=V_, d=d_, mu=mu_)
        elif self.ismomentform() and self.isdiagonal():
            mu_ = np.copy(self.mu[k_dims])
            q_ = np.copy(self.q[k_dims])
            return GausshapeMode(mu=mu_, diagCovariance=q_)
        elif self.ismomentform():
            mu_ = np.copy(self.mu[k_dims])
            Q_ = np.copy(self.Q[np.ix_(k_dims, k_dims)])  # numpy submatrix extraction is just terrible
            return GausshapeMode(mu=mu_, fullCovariance=Q_)

    def sample(self, n=1, sigma=0.95):
        """One sigma random normal sample"""
        A = self.V.dot(np.diag(np.sqrt(np.maximum(self.d, 1E-16).flatten())))  # Sigma=VDV^T,  A = VD^{1/2}
        z = sigma*np.random.randn(self.rank(), n)  #  z ~ N(0,1)
        x = self.mu.reshape(self.mu.size, 1) + A.dot(z)  # x = \mu + Az, with numpy broadcasting
        return x   # x ~ N(mu, Sigma)

    def completion(self, z):
        """Fill in NaN dimensions with a conditional sample"""
        k_obs = np.argwhere(np.isnan(z) == False).flatten()
        k_unobs = np.argwhere(np.isnan(z) == True).flatten()
        Z = self.conditional(z).sample(1)
        #Z = self.conditional(z).mean()   # TESTING     
        X = np.zeros(z.size, dtype=np.float32)
        X[k_obs] = z[k_obs]   # observed dimensions
        X[k_unobs] = Z[:,0]  # fill in unobserved data
        return X    
    
    def conditional(self, z):
        """Non-NaN dimensions of z are observed"""
        k_obs = np.argwhere(np.isnan(z) == False).flatten()  # index of observed dimensions
        k_unobs = np.argwhere(np.isnan(z) == True).flatten()  # index of unobserved dimensions        
        J = np.copy(self.precisionmatrix())
        h = np.copy(self.potentialvector())
        h = h.reshape(h.size,1)
        J_xx = J[np.ix_(k_unobs, k_unobs)]  # numpy submatrix extraction is just terrible
        J_xy = J[np.ix_(k_unobs, k_obs)]  # numpy submatrix extraction is just terrible                
        V_xx = np.copy(self.V[k_unobs,:])        
        h_cond = h[k_unobs] - J_xy.dot(z[k_obs].reshape(k_obs.size,1)).reshape(k_unobs.size,1)
        Q_xx = self.covariance()[np.ix_(k_unobs, k_unobs)]  # numpy submatrix extraction is just terrible
        Q_xy = self.covariance()[np.ix_(k_unobs, k_obs)]  # numpy submatrix extraction is just terrible
        Q_yy = self.covariance()[np.ix_(k_obs, k_obs)]  # numpy submatrix extraction is just terrible

        (d,V) = scipy.sparse.linalg.eigsh(Q_yy, k=self.rank(), return_eigenvectors=True)  # low rank covariance matrix
        J_yy = V.dot(np.diag(1.0/np.maximum(d,1E-16)).dot(V.transpose()))
                
        mu_cond = self.mu[k_unobs].reshape(k_unobs.size,1) + Q_xy.dot(J_yy.dot((z[k_obs] - self.mu[k_obs]).reshape(k_obs.size,1)))        
        J_yy = J[np.ix_(k_obs, k_obs)]  # numpy submatrix extraction is just terrible                
        Q = Q_xx - Q_xy.dot(J_yy.dot(Q_xy.transpose()))
        (d,V) = scipy.sparse.linalg.eigsh(Q, k=self.rank(), return_eigenvectors=True)  # low rank covariance matrix
        return GausshapeMode(mu=mu_cond, V=V, d=d)                 
                
    

    
#    def show(self, im, partlist=range(1,21), do_ellipse=False):
#
#        raise ValueError('changed order of sift features')
#
#        img = np.uint8(im.clone().bgr()) # overwritten
#        bgr = jet(len(partlist), bgr=True) # jet colormap
#        for k in partlist:
#            g = self.shape(k)  # part position
#            mu = (int(g.mean()[0] * im.width() + float(im.width())/2.0), int(g.mean()[1] * im.height() + float(im.height()) / 2.0))  # (-0.5,0.5) -> (0,width)
#            
#            # Draw point
#            #cv2.circle(img, center=mu, radius=20, color=bgr[k-1,:], thickness=-1)
#            cv2.circle(img, center=mu, radius=1, color=(0,255,0), thickness=-1, lineType=cv2.CV_AA) # center=(int,int)         
#
#            # Draw covariance ellipse
#            if do_ellipse:
#                (sx,sy,r) = covariance_to_ellipse(g.covariance())  # ellipse parameters (major_axis_len, minor_axis_len, angle_in_radians)
#                sx = int(np.square(sx * im.width()))
#                sy = int(np.square(sy * im.height()))
#                cv2.ellipse(img, center=mu, axes=(sx,sy), angle=math.degrees(-r), startAngle=0, endAngle=360, color=(0,255,0), thickness=1, lineType=cv2.CV_AA)  # center=(int,int), axes=(int,int)#
#
#        return img
        
    
    def heatmap(self, dimX, dimY, M=128, N=128, xmin=-1.0, xmax=1.0, ymin=-1.0, ymax=1.0, covscale=0.0001):
        """Visualize the GausshapeMode as a 2D gaussian mixture using dimensions (dimX,dimY) as 2D marginals to compute posterior to all pixels, output image dimension (M,N) domain defined by x/ymin and x/ymax"""

        # Gaussian mixture of 2D Marginals using dimensions (dimX, dimY)
        gsm = [GausshapeMode(V=self.V[[i,j],:], d=covscale*self.d, mu=self.mu[[i,j]]) for (i,j) in zip(dimX, dimY)]

        # Posterior for each pixel to 2D gaussian mixture
        (I,J) = np.meshgrid(np.arange(xmin,xmax,float(xmax-xmin)/float(M)), np.arange(ymin,ymax,float(ymax-ymin)/float(N)))                              
        im = np.array([np.sum(np.array([g.likelihood(x) for g in gsm])) for x in zip(np.nditer(I), np.nditer(J))]).reshape( (M,N) )
        return mat2gray(im)

        
class _GausshapeMixture(object):
    def __init__(self, weights=None, modes=None):
        self.weights = weights
        self.modes = modes
        
    def __len__(self):
        return len(self.modes) if self.modes is not None else 0
    
    def __repr__(self):
        if len(self) > 0:
            return str('<janus.gausshape.gmm: modes=%d, dimensionality=%d>' % (len(self.modes), self.dimensionality()))
        else:
            return str('<janus.gausshape.gmm: modes=None>')

    def display(self):
        if len(self.modes) > 0:        
            print '[janus.gausshape]: modes=%d, dimensionality=%d, rank=%d>' % (len(self.modes), self.dimensionality(), self.rank())
            print '[janus.gausshape]:   mu, min=%1.3f, max=%1.3f' % (np.min([g.mu for g in self.modes]), np.max([g.mu for g in self.modes]))
            #print '[janus.gausshape]: V, min=%1.3f, max=%1.3f' % (np.min([g.V.flatten() for g in self.modes]), np.max([g.V.flatten() for g in self.modes])) 
            print '[janus.gausshape]:   weights, min=%1.3f, max=%1.3f' % (np.min(self.weights), np.max(self.weights))
        else:
            print self.__repr__()
    
    def dimensionality(self):
        return self.modes[0].dimensionality() if len(self)>0 else None
    
    def rank(self):
        return self.modes[0].rank() if len(self)>0 else None

    def normalize(self):
        self.weights = np.divide(self.weights, np.sum(self.weights))
        return self
        
#    def features(self, im, frames=None, pca=None, scales=[0.25,0.5,1.0]):
#        d = None
#        for s in scales:
#            (d_sift, fr_sift) = densesift(im, scale=s, dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False, frames=True)  # nx128
#            if pca is not None:
#                f_densePCAsift = (lambda d: reduce(lambda x,y: np.concatenate( (pca.dot(x.transpose()).transpose(),y), axis=1), np.split(d, [128], axis=1)))  
#                d_sift = f_densePCAsift(d_sift)
#            if frames is not None:
#                d_sift = d_sift[np.argmin(sqdist(fr_sift, frames), axis=0), :]  # k x m            
#            d = np.concatenate( (d, d_sift), axis=0) if d is not None else d_sift  # k x (num_scales*m)            
#        return d
            
    def export(self, yamlfile):
        print "[janus.gausshape.export]: writing gausshape parameters to '%s' " % yamlfile
        mtxlist = [np.array([len(self.modes)]), self.weights];  
        mtxname = ['num_modes', 'weights']
        
        mtxlist.append(self.modes[0].V)  # shared low rank
        mtxname.append('V')
        mtxlist.append(self.modes[0].d)  # shared low rank
        mtxname.append('d')

        for k in range(0, len(self.modes)):
            mtxlist.append(self.modes[k].q)
            mtxname.append('q_%d' % k)
            mtxlist.append(self.modes[k].mu)
            mtxname.append('mu_%d' % k)      

        #if pca is not None:
        #    mtxlist.append(pca)
        #    mtxname.append('pca')
            
        matrix2yaml(yamlfile, mtxlist, mtxname)
        return yamlfile

    
    
    def train(self, featset, k_rank=4, n_modes=128, n_iterations=20, r_pooling=0.25):
        """Low rank Gaussian Mixture Model for provided features"""
        
        # Gaussian mixture model
        #featset = featset.sample(withReplacement=False, fraction=0.001)  # TESTING
        gmm = janus.gmm.train(featset, n_modes=n_modes, features=None, n_iterations=n_iterations, seed=42)
        (weights, modes) = (gmm.prior, [GausshapeMode(diagCovariance=q, mu=mu) for (mu,q) in zip(gmm.mean, gmm.covariance)])        

        # Low Rank Gaussian 
        n_samples = featset.count()        
        print "[janus.gausshape.gmm]: number of descriptors = %d" % n_samples
        print "[janus.gausshape.gmm]: Pooling radius=%f, Rank=%d" % (r_pooling, k_rank)

        # FIXME: removed + np.log(w) from below
        data_gamma = (featset.map(lambda x: (x, [g.log_likelihood(x) for (g,w) in zip(modes, weights)]))  # NxK log likelihoods of soft assignment of datapoint n to mode k 
                             .map(lambda (x,g): (x, np.exp(g - np.max(g)) / np.sum(np.exp(g - np.max(g)))))  # NxK soft assignment of datapoint x to kth mode (eq 9.23)
                             .cache())
        N_k = np.maximum(data_gamma.map(lambda (x,g): g).sum().flatten(), 1E-6)   # 1xK column sum of gamma (eq 9.27)
                                    
        # Low rank gaussian
        # FIXME: pooling radius
        X = data_gamma.map(lambda (x,g): np.array([w*x for w in g]).flatten()).collect()
        svd = sklearn.decomposition.TruncatedSVD(n_components=k_rank).fit(X)
        
        # Done!
        self.modes = [GausshapeMode(V=svd.components_, d=np.maximum(svd.explained_variance_, 0), diagCovariance=q, mu=mu) for (mu,q) in zip(gmm.mean, gmm.covariance)]
        self.weights = weights        
        return self


    def sample(self, n=1):
        return np.random.choice(self.modes, p=self.weights).sample(n)

    def sampleMode(self):
        return np.random.choice(self.modes, p=self.weights)
    
    def conditional(self, z):
        z_obs = np.where(np.isnan(z) == False)
        k_obs = np.argwhere(np.isnan(z) == False).flatten()        
        C = [g.conditional(z) for g in self.modes]
        W = np.array([g.marginal(k_obs).log_likelihood(z_obs) for g in self.modes])
        G = GausshapeMixture(modes=C, weights=np.exp(W - np.max(W))).normalize()
        return G

    def conditional_sample(self, z, n=1):
        k_obs = np.argwhere(np.isnan(z) == False).flatten()
        k_unobs = np.argwhere(np.isnan(z) == True).flatten()                
        Z = self.conditional(z).sample(n)  # n independent samples of conditional distribution
        print Z.shape
        X = np.zeros( (z.size, n), dtype=np.float32)
        for k in range(0,n):
            X[k_obs,k] = z[k_obs]   # observed dimensions
            X[k_unobs,k] = Z[:,k]  # fill in unobserved data
        return X


    def likelihood(self, z):
        x = [m.log_likelihood(z) for m in self.modes]
        l = np.exp(x - np.max(x)) / np.sum(np.exp(x - np.max(x)))
        return l

    def position(self, partlist=None, im=None):
        """position marginal (last two dimensions) of each mode"""
        k_shapedims = np.array([self.dimensionality()-2, self.dimensionality()])
        return np.array([g.marginal(k_shapedims) for g in self.modes])



    
class _Gausshape():
    def __init__(self, yamlfile, libfile=None, reload=False):
        """YAML file exported from GausshapeMixture training, dynamic library for gausshape inference"""
        if libfile is None:
            self.libfile = bobo.app.libfile('gausshape');
        else:
            self.libfile = libfile

        if reload == True:
            (filepath, ext) = os.path.splitext(self.libfile)
            newfile = '%s_%s%s' % (filepath, binascii.b2a_hex(os.urandom(4)), ext)
            shutil.copyfile(self.libfile, newfile)
            self.libfile = newfile
            print '[gausshape]: forcing reload "%s" ' % self.libfile
        else:
            print '[gausshape]: loading "%s" ' % self.libfile                        

            
        self.dylib = ctypes.CDLL(self.libfile)  # WARNING: does not use absolute path if library already on DYLD_LIBRARY_PATH
        initialize = self.dylib.initialize
        initialize.restype = ctypes.c_void_p
        self.obj = initialize(ctypes.c_char_p(yamlfile))  # returns pointer to initialized C++ object
        
    def __repr__(self):
        return str('<Gausshape: "%s">' % (self.libfile))

    def __del__(self):        
        print '[gausshape]: entering __del__'
        self.dylib.release(ctypes.c_void_p(self.obj))  # free all allocated resources when python garbage collects this library        
        self.dylib.dlclose(self.dylib._handle)
     
    def display(self):
        self.dylib.display(ctypes.c_void_p(self.obj))        

#    def num_parts(self):
#        return self.dylib.num_parts(ctypes.c_void_p(self.obj))        

    def num_modes(self):
        return self.dylib.num_modes(ctypes.c_void_p(self.obj))        

    def dimensionality(self):
        return self.dylib.dimensionality(ctypes.c_void_p(self.obj))        
    
    def modes(self):
#        p = self.num_parts()
        d = self.dimensionality()  
        n = self.num_modes()
        mu = np.zeros( (n,d), dtype=np.float32)
        Q = np.zeros( (n,d,d), dtype=np.float32)
        w = np.zeros( (1,n), dtype=np.float32)
        self.dylib.modes(ctypes.c_void_p(self.obj),
                         mu.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                         Q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                         w.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

        modes_ = [GausshapeMode(mu=mu[i,:], fullCovariance=Q[i,:,:]) for i in range(0,n)]
        return GausshapeMixture(modes=modes_, weights=w)

    def regression(self, im, n_iterations=5):
        d = self.dimensionality()
        mu = np.zeros( (d,1), dtype=np.float32)
        Q = np.zeros( (d,d), dtype=np.float32)

        self.dylib.regression(ctypes.c_void_p(self.obj),
                       im.load().ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
                       ctypes.c_int(im.height()),
                       ctypes.c_int(im.width()),
                       mu.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                       Q.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                       ctypes.c_int(n_iterations));
    
        return GausshapeMode(mu=mu, fullCovariance=Q)

    def posterior(self, im, n_iterations=10):
        self.dylib.posterior(ctypes.c_void_p(self.obj),
                             im.load().ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
                             ctypes.c_int(im.height()),
                             ctypes.c_int(im.width()),
                             ctypes.c_int(n_iterations))

    def encoding(self, im, n_iterations=10, do_signsqrt=True, do_normalized=True):
        fv = np.zeros( (dimensionality()*2*num_modes(), 1), dtype=np.float32)
        
        self.dylib.encoding(ctypes.c_void_p(self.obj),
                             im.load().ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
                             ctypes.c_int(im.height()),
                             ctypes.c_int(im.width()),
                             fv.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),                             
                             ctypes.c_int(n_iterations))

        if do_signsqrt:
            fv = signsqrt(fv)
        if do_normalized:
            fv = fv / np.linalg.norm(fv)                
        return fv

    
