import os
import numpy as np
#import bobo.cluster
from sklearn.decomposition import TruncatedSVD
import scipy.sparse.linalg

class DiagonalPlusLowrankGaussian(object):
    def __init__(self, V=None, d=None, mu=None, diagCovariance=None, potentialVector=None, precisionMatrix=None):
        self.q = diagCovariance  
        self.d = d
        self.V = V  # Q = VDV' + diag(q) = J^{-1}
        self.mu = mu
        self.h = potentialVector
        self.J = precisionMatrix

        # Error check
        if not (self.ismomentform() or self.isinformationform()):
            raise ValueError('invalid parameters')
        
    def __repr__(self):
        return str('<janus.gmm.DiagonalPlusLowrankGaussian: dimensionality=%s, rank=%s>' % (str(self.dimensionality()), str(self.rank())))

    def display(self):
        print '[janus.gmm.DiagonalPlusLowrankGaussian]: dimensionality=%d, rank=%d>' % (self.dimensionality(), self.rank())
        print '[janus.gmm.DiagonalPlusLowrankGaussian]: mu, min=%1.3f, max=%1.3f' % (np.min(self.mu), np.max(self.mu))

        
    def ismomentform(self):
        return ((self.mu is not None) and # mean vector defined
                (self.q is not None) or # diagonal covariance
                 ((self.V is not None) and (self.d is not None))) # factored covariance 

    def isinformationform(self):
        return ((self.h is not None) and  (self.J is not None))

    def isfactored(self):
        return self.d is not None

    def isdiagonal(self):
        return self.q is not None

    def isinverted(self):
        return self.J is not None

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
        if self.ismomentform() and self.isfactored():
            VD = self.V * self.d  # broadcasting, multiply column k by dinv[k]
            Q = VD.dot(self.V.transpose())
        elif self.ismomentform() and self.isdiagonal():
            Q = np.diag(self.q)  # diagonal to full covariance
        else:
            raise ValueError('invalid form')                
        return Q

    def log_likelihood(self, x):
        x = np.array(x)
        dim = self.dimensionality()

        if self.ismomentform() and self.isfactored():
            k = np.nonzero(self.d)[0]            
            if len(k) < self.rank():
                print '[janus.gmm.log_likelihood][WARNING]: rank = %d < %d' % (len(k), self.rank())
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
            return DiagonalPlusLowrankGaussian(V=V_, d=d_, mu=mu_)
        elif self.ismomentform() and self.isdiagonal():
            mu_ = np.copy(self.mu[k_dims])
            q_ = np.copy(self.q[k_dims])
            return DiagonalPlusLowrankGaussian(mu=mu_, diagCovariance=q_)
        else:
            raise ValueError('invalid marginal')

        
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
        return DiagonalPlusLowrankGaussian(mu=mu_cond, V=V, d=d)                 
    
    def heatmap(self, dimX, dimY, M=128, N=128, xmin=-1.0, xmax=1.0, ymin=-1.0, ymax=1.0, covscale=0.0001):
        """Visualize the DiagonalPlusLowrankGaussian as a 2D gaussian mixture using dimensions (dimX,dimY) as 2D marginals to compute posterior to all pixels, output image dimension (M,N) domain defined by x/ymin and x/ymax"""

        # Gaussian mixture of 2D Marginals using dimensions (dimX, dimY)
        gsm = [DiagonalPlusLowrankGaussian(V=self.V[[i,j],:], d=covscale*self.d, mu=self.mu[[i,j]]) for (i,j) in zip(dimX, dimY)]

        # Posterior for each pixel to 2D gaussian mixture
        (I,J) = np.meshgrid(np.arange(xmin,xmax,float(xmax-xmin)/float(M)), np.arange(ymin,ymax,float(ymax-ymin)/float(N)))                              
        im = np.array([np.sum(np.array([g.likelihood(x) for g in gsm])) for x in zip(np.nditer(I), np.nditer(J))]).reshape( (M,N) )
        return mat2gray(im)

        
class DiagonalPlusLowrankGaussianMixture(object):
    def __init__(self, weights=None, modes=None):
        self.weights = weights.flatten() if weights is not None else weights
        self.modes = modes

    def __len__(self):
        return len(self.modes) if self.modes is not None else 0
    
    def __repr__(self):
        if len(self) > 0:
            return str('<janus.gmm: modes=%d, dimensionality=%d>' % (len(self.modes), self.dimensionality()))
        else:
            return str('<janus.gmm: modes=None>')

    def __getitem__(self, k):
        return self.modes(k);
        
    def display(self):
        if len(self.modes) > 0:        
            print '[janus.gmm]: modes=%d, dimensionality=%d, rank=%d>' % (len(self.modes), self.dimensionality(), self.rank())
            print '[janus.gmm]:   mu, min=%1.3f, max=%1.3f' % (np.min([g.mu for g in self.modes]), np.max([g.mu for g in self.modes]))
            print '[janus.gmm]:   weights, min=%1.3f, max=%1.3f' % (np.min(self.weights), np.max(self.weights))
        else:
            print self.__repr__()
    
    def dimensionality(self):
        return self.modes[0].dimensionality() if len(self)>0 else None
    
    def rank(self):
        return self.modes[0].rank() if len(self)>0 else None

    def normalize(self):
        self.weights = self.weights / (np.sum(self.weights) + 1E-16)
        return self
            
    def train(self, featset, k_rank=4, n_modes=128, n_iterations=20, r_pooling=0.25):
        """Low rank Gaussian Mixture Model for provided features"""
        
        # Gaussian mixture model
        #featset = featset.sample(withReplacement=False, fraction=0.001)  # TESTING
        gmm = train(featset, n_modes=n_modes, features=None, n_iterations=n_iterations, seed=42)
        (weights, modes) = (gmm.prior, [DiagonalPlusLowrankGaussian(diagCovariance=q, mu=mu) for (mu,q) in zip(gmm.mean, gmm.covariance)])        

        # Low Rank Gaussian 
        n_samples = featset.count()        
        print "[janus.gmm]: number of descriptors = %d" % n_samples
        print "[janus.gmm]: Pooling radius=%f, Rank=%d" % (r_pooling, k_rank)

        # FIXME: removed + np.log(w) from below
        data_gamma = (featset.map(lambda x: (x, [g.log_likelihood(x) for (g,w) in zip(modes, weights)]))  # NxK log likelihoods of soft assignment of datapoint n to mode k 
                             .map(lambda (x,g): (x, np.exp(g - np.max(g)) / np.sum(np.exp(g - np.max(g)))))  # NxK soft assignment of datapoint x to kth mode (eq 9.23)
                             .cache())
        N_k = np.maximum(data_gamma.map(lambda (x,g): g).sum().flatten(), 1E-6)   # 1xK column sum of gamma (eq 9.27)
                                    
        # Low rank gaussian (shared)
        #X = data_gamma.map(lambda (x,g): np.array([w*x for w in g]).flatten()).collect()
        X = np.array(featset.collect())
        svd = TruncatedSVD(n_components=k_rank).fit(X)
        
        # Done!
        self.modes = [DiagonalPlusLowrankGaussian(V=svd.components_.transpose(), d=np.maximum(svd.explained_variance_, 0), diagCovariance=q, mu=mu) for (mu,q) in zip(gmm.mean, gmm.covariance)]
        self.weights = weights        
        return self


    def sample(self, n=1, weights=None):
        if weights is None:
            return np.random.choice(self.modes, p=self.weights).sample(n)
        else:
            return np.random.choice(self.modes, p=weights).sample(n)

    def sampleMode(self, weights=None):
        if weights is None:
            return np.random.choice(self.modes, p=self.weights)
        else:
            return np.random.choice(self.modes, p=weights)
        
    def conditional(self, z):
        z_obs = np.where(np.isnan(z) == False)
        k_obs = np.argwhere(np.isnan(z) == False).flatten()        
        C = [g.conditional(z) for g in self.modes]
        W = np.array([g.marginal(k_obs).log_likelihood(z_obs) for g in self.modes])
        G = DiagonalPlusLowrankGaussianMixture(modes=C, weights=np.exp(W - np.max(W))).normalize()
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

    def log_likelihood(self, z):
        x = np.array([m.log_likelihood(z) for m in self.modes])
        return x

class Gaussian():
    mean = None
    covariance = None

    def __init__(self, mean=None, covariance=None, weight=None):
        self.mean = mean
        self.covariance = covariance  # diagonal or full
        self.weight = weight

    def __repr__(self):
        return str('<janus.gaussian: dimensionality=%d, covariance="diagonal">' % (self.dimensionality()))
        
    def dimensionality(self):
        return len(self.mean) if self.mean is not None else 0

    def isdiagonal(self):
        return np.min(self.covariance.shape) == 1 if self.dimensionality()>0 else False

    def isfull(self):
        return np.min(self.covariance.shape) == self.dimensionality() if self.dimensionality()>0 else False
                
    def marginal(self, dims):
        if self.dimensionality() > 0:
            return Gaussian(mean=np.array([self.mean(k) for k in dims]), covariance=self.covariance[[[j] for j in dims], dims])
        else:
            return None

    def log_likelihood(self, x):
        if self.isdiagonal():
            logDetSigma = np.sum(np.log(self.covariance))
            z = (np.array(x).reshape( (np.array(x).size, 1) ) - self.mu.reshape( (self.mu.size, 1) ))       
            ll = float(-0.5*z.transpose().dot(np.multiply(1.0 / self.covariance.reshape(self.covariance.size,1), z)) - 0.5*logDetSigma - 0.5*float(self.dimensionality())*np.log(2.0*np.pi))        
            return ll
        else:
            raise ValueError('FIXME')

                
        
class GaussianMixtureModel():
    def __init__(self, mean=None, covariance=None, prior=None):
        self.mean = mean
        self.covariance = covariance
        self.prior = prior if prior is not None else np.ones(self.mean.shape[0])
        if self.prior is not None:
            self.normalize()
        
    def __repr__(self):
        return str('<janus.gmm: modes=%d, dimensionality=%d>' % (self.num_modes(), self.dimensionality()))

    def __iter__(self):
        for k in range(0,self.num_modes()):
            yield self.mode(k);
    
    def __getitem__(self, k):
        return self.mode(k);

    def __len__(self):
        return self.num_modes()
        
    def mode(self, k):
        if k >= 0 and k < len(self):
            return Gaussian(mean=self.mean[k,:], covariance=self.covariance[k,:])
        else:
            raise ValueError('Invalid mode index')

    def sampleMode(self):
        return self.mode(np.random.choice(range(0, len(self.prior))))  # FIXME: weighted sampling throws error that prior does not sum to one

        
    def num_modes(self):
        return len(self.prior) if self.prior is not None else 0

    def dimensionality(self):
        return self.mean.shape[1] if self.mean is not None else 0        

    def normalize(self):
        self.prior = np.divide(self.prior, np.sum(self.prior))
        return self
        
    def shape(self):
        print '[janus.gmm]: mean=%s, dtype=%s, %d bytes' % (str(self.mean.shape),self.mean.dtype,self.mean.nbytes)
        print '[janus.gmm]: covariance=%s, dtype=%s, %d bytes' % (str(self.covariance.shape),self.mean.dtype,self.covariance.nbytes)
        print '[janus.gmm]: prior=%s, dtype=%s, %d bytes' % (str(self.prior.shape),self.mean.dtype,self.prior.nbytes)
            

    def display(self):
        print '[janus.gmm]: modes=%d, dimensionality=%d>' % (self.num_modes(), self.dimensionality())
        print '[janus.gmm]: mean, min=%1.3f, max=%1.3f' % (np.min(self.mean.flatten()), np.max(self.mean.flatten()))
        print '[janus.gmm]: covariance, min=%1.3f, max=%1.3f' % (np.min(self.covariance.flatten()), np.max(self.covariance.flatten()))
        print '[janus.gmm]: prior, min=%1.3f, max=%1.3f' % (np.min(self.prior.flatten()), np.max(self.prior.flatten()))                

    def log_likelihood(self, x):
        """Assumes diagonal covariance"""
        d = self.dimensionality()
        traceLogSigma = np.sum(np.log(self.covariance), axis=1)  # Trace(log(A)) = log(det(A)) for diagonal A
        ll = -0.5*np.sum(np.power(np.divide(x-self.mean, np.sqrt(self.covariance)), 2.0), axis=1) - 0.5*traceLogSigma - 0.5*float(d)*np.log(2.0*np.pi) + np.log(self.prior)
        return ll

    def likelihood(self, x, minLikelihood=1E-8):
        """Assumes diagonal covariance"""
        ll = self.log_likelihood(x)
        p = np.exp(np.maximum(ll, np.log(minLikelihood))).flatten()  # minus maximum log-likelihood to avoid underflow
        return p
        
    def softassign(self, x):
        ll = self.log_likelihood(x)   # log-likeihood of data x to each k cluster
        p = np.exp(ll - np.max(ll)).flatten()  # minus maximum log-likelihood to avoid underflow            
        #p = np.maximum(np.divide(p, np.sum(p)), 1E-7)  # to density
        p = np.divide(p, np.maximum(np.sum(p), 1E-16)) # to density
        return p
            
    def visualize(self, dimX, dimY, M=256, N=256, xmin=-1, xmax=1, ymin=-1, ymax=1, covscale=0.05):
        """Visualize the GMM using dimensions X and Y to compute posterior to all pixels, output image dimension (M,N) domain defined by x/ymin and x/ymax"""
        (I,J) = np.meshgrid(np.arange(xmin,xmax,(xmax-xmin)/float(M)), np.arange(ymin,ymax,(ymax-ymin)/float(N)))
        marginal = GaussianMixtureModel(mean=self.mean[:,[dimX,dimY]], covariance=covscale*self.covariance[:,[dimX,dimY]], prior=self.prior)
        im = np.array([np.sum(marginal.likelihood(x)) for x in zip(np.nditer(I), np.nditer(J))]).reshape( (M,N) )
        return bobo.util.mat2gray(im)

def train(trainset, n_modes=4, features=None, n_iterations=5, initialcondition='kmeans', fractionOfImages=1, fractionOfDescriptors=1, do_verbose=True, variance_floor=1E-9, variance_floor_factor=1E-2, seed=42, minGamma=1E-4, alpha=100):
    # Features extracted on subset of images in training set
    if features is not None:
        data = (trainset.sample(withReplacement=False, fraction=fractionOfImages, seed=seed)  # sample small fraction of images
                        .map(features) # feature extraction within bounding box 
                        .flatMap(lambda x: x)  # explode all features per image into an RDD of features
                        .sample(withReplacement=False, fraction=fractionOfDescriptors, seed=seed)  # sample small fraction of features
                        .cache())  # cache in memory so we don't recompute
    else:
        # Use provided training set of features
        data = trainset.cache()

    # Initialization using kmeans++
    n_samples = data.count()    
    if do_verbose:
        print "[janus.gmm.train]: number of descriptors = %d" % n_samples
        print "[janus.gmm.train]: computing initial means for %d clusters" % n_modes
    from pyspark.mllib.clustering import KMeans
    clusters = KMeans.train(data, n_modes, maxIterations=100, runs=1, initializationMode="k-means||");  # kmeans++ initialization, FIXME: add seed
    mean = np.array(clusters.centers, dtype=np.float32)  # KxD (D=dimensionality)
    data_with_mean = data.union(trainset.context.parallelize(mean))  # augment data with means to guarantee that all clusters have at least one assignment
    n_assignment = (data_with_mean.map(lambda x: (clusters.predict(x), 1.0)).reduceByKey(lambda x,y: x+y).sortByKey(ascending=True).values().collect())  # hard assignment count per cluster
    covariance = (data_with_mean.map(lambda x: (clusters.predict(x), x))  # (cluster_index, data) tuple
                                .map(lambda (k,x): (k, np.square(mean[k,:]-np.array(x))))  # (cluster_index, variance) tuple
                                .reduceByKey(lambda x,y: x+y).sortByKey(ascending=True)  # sum sqdiff over hard assignment
                                .map(lambda (k,x): x/float(n_assignment[k])).collect())  # expectation, ordered by cluster index
    adaptive_variance_floor = np.maximum(variance_floor_factor*data.variance(), variance_floor)    
    covariance = np.maximum(covariance, adaptive_variance_floor)  
    prior = (np.array(n_assignment) + float(alpha*n_samples)) / np.maximum(np.sum((np.array(n_assignment) + float(alpha*n_samples))), 1E-16)  # regularized prior (to avoid N_k[j]=0)   
    gmm = GaussianMixtureModel(mean, covariance, prior)
    
    # Expectation-Maximization estimation of Gaussian Mixture Model using RDD iteration
    #   Reference: Bishop, "Pattern Recognition and Machine Learning" 2006, Section 9.3, pg 438
    #   See also: http://www.vlfeat.org/api/gmm-fundamentals.html#gmm-em
    for k in range(0, n_iterations):
        if do_verbose:
            print "[janus.gmm.train][%d/%d]: Expectation-Maximization iteration" % (k+1, n_iterations)            
            gmm.display()
        
        # Expectation
        data_gamma = (data.map(lambda x: (x,gmm.softassign(x)), preservesPartitioning=True) # preserve partitioning for zip
                          .cache())  # NxK soft assignment, rows sum to one for soft assignment of datapoint x to kth mode (eq 9.23)
        N_k = data_gamma.map(lambda (x,g): g).sum().flatten()   # 1xK column sum of gamma (eq 9.27)        

        # Maximization        
        gmm.mean = np.divide(data_gamma.map(lambda (x,g): np.array(np.outer(np.multiply(np.array(g), np.float32(np.array(g) > minGamma)), x))).sum(), N_k.reshape( (n_modes, 1) ))  # KxD  (eq. 9.24)
        gmm.covariance = np.divide(data_gamma.map(lambda (x,g): np.array(np.multiply(np.array(np.multiply(g, np.float32(g > minGamma))).reshape( (n_modes,1) ), np.multiply(x-gmm.mean, x-gmm.mean)))).sum(), N_k.reshape( (n_modes,1) ))  # KxD (eq. 9.25)
        gmm.covariance = np.maximum(gmm.covariance, adaptive_variance_floor)  # truncated KxD (eq. 9.25)
        N_k_dirichlet = np.array(N_k) + float(alpha*n_samples)  # dirichlet prior for equal sized clusters (see fishervectorfaces/gmm-fisher/gmm.cxx)
        gmm.prior = np.divide(N_k_dirichlet, np.sum(N_k_dirichlet))  # (eq. 9.26), rows of gamma sum to one, so N_k sums to N

        # FIXME: Convergence? test log likelihood in (9.28)

        # Garbage collection
        data_gamma = data_gamma.unpersist()
        
    # Garbage collection
    data = data.unpersist()

    # Done!
    return gmm

def kmeans(trainset, n_modes=4, do_verbose=False, seed=None):
    """Return initial condition from EM training with n_iterations=0"""
    return train(trainset, n_modes, do_verbose, n_iterations=0, seed=seed)


