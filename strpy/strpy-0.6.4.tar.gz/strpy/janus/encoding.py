import strpy.bobo.app
import numpy as np
from strpy.bobo.util import quietprint, seq, signsqrt, load, save
from strpy.bobo.geometry import similarity_imtransform, sqdist
import ctypes
import pickle
import pdb
from math import pi
import scipy.sparse

    
def bagofwords(im, features, gmm):
    """Bag-of-words encoding using provided gmm and feature extraction function (features must match GMM) """
    D = sqdist(features(im), gmm.mean)  # all pairs squared euclidean distance
    k_asgn = np.argmin(D, axis=1)  # greedy assignment of observation to closest word in euclidean distance
    (bow, binedges) = np.histogram(k_asgn, bins=seq(-0.5,D.shape[0]-1+0.5,1.0), density=False)  # normalized histogram of words
    return bow

def random_jitter(im):
    # Create a random rotation between +/- 10 deg
    # deg = np.random.random() * 20 - 10
    # r = deg / 180 * pi
    # FIXME: Rotation is from image origin, not center
    r = 0

    # Create a random translation between +/- 2 pixels in x and y
    t = np.random.random(2) * 4 - 2

    # Create a random scale between .95 and 1.05
    sc = np.random.random() / 10 + 0.95

    A = similarity_imtransform(txy=t, r=r, s=sc)
    return im.transform(A)


def fishervector_pooling(tmpl, f_encoding, do_jitter=False, do_signsqrt=True, do_normalized=True, do_verbose=False, do_random_jitter=False):
    """Fishervector encoding with jittered pooling for Janus templates"""
    
    # Template fisher vector encoding and pooling
    fv = None
    for y in tmpl:  # for images and videos in template
        # Random jitter: Optionally add some image copies randomly perturbed
        #xp = [ y ]  # This is a bug for pooling over templates when a template is defined over media and not images/frames.  For a video iterators - for x in xp will yield video y and not the frames in y
        xp = y
        
        if do_random_jitter:
            # Add 4 slightly perturbed images from this image
            #xp.extend( [ random_jitter(y) for i in range(32) ]  )  
            raise ValueError('FIXME')  # removing xp = [ y ] will break this
        
        for x in xp:  # frames in video or image
            fv = fv + f_encoding(x) if fv is not None else f_encoding(x)
            if do_jitter:
                fv += f_encoding(x.clone().fliplr())  # clone for idemponence
                
    # Final normalization after video encoding
    if do_signsqrt:
        fv = signsqrt(fv)
    if do_normalized:
        fv = fv / np.linalg.norm(fv)

    # Debugging
    if do_verbose:
        quietprint('[fishervector_with_jittered_pooling]: len(fv)=%d, max(fv)=%1.3f, min(fv)=%1.3f, isnan(fv)=%s' % (np.array(fv).size, np.amax(fv) , np.amin(fv), np.isnan(fv).any()), 2)

    # Done!
    return fv


def augment_fishervector(fv1, fv2):
    fv = fv1 + fv2
    fv = signsqrt(fv)
    fv = fv / np.linalg.norm(fv)
    return fv


def sparsefishervector(descriptors, mean, covariance, prior, do_signsqrt=False, do_normalized=False, do_fastfisher=False, do_improvedfisher=False, do_verbose=False, do_typecast=True):
    """vlfeat-0.9.18 fisher vector encoding"""

    # Feature extraction (descriptors provided)
    d_obs = descriptors
    if d_obs.ndim == 1:
        d_obs = d_obs.reshape( (1, d_obs.size) )
    d_obs = np.ascontiguousarray(d_obs.astype(np.float32), dtype=np.float32)

    # Preallocate output buffer
    m_fishervector = mean.size * 2  # length of fisher vector encoding
    x = np.zeros( (1, m_fishervector), dtype=np.float32)  # preallocated output (row vector)

    # Typecast inputs (otherwise assume typecast already)
    if do_typecast:
        mean = np.asarray(mean, dtype=np.float32, order='C')  # row major, num_modes x dimensionality
        covariance = np.asarray(covariance, dtype=np.float32, order='C') # row major, num_modes x dimensionality
        prior = np.asarray(prior, dtype=np.float32, order='C') # row major, num_modes x 1

    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    fv.lib.fishervector(d_obs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
                        mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # mean pointer
                        covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # covariance pointer
                        prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # prior pointer
                        x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # fisher vector output buffer
                        ctypes.c_int(mean.shape[1]),  # dimensionality of data
                        ctypes.c_int(mean.shape[0]),  # number of modes in GMM
                        ctypes.c_int(d_obs.shape[0]),  # number of observations
                        ctypes.c_int(do_signsqrt),  # options
                        ctypes.c_int(do_normalized),
                        ctypes.c_int(do_fastfisher),
                        ctypes.c_int(do_improvedfisher),
                        ctypes.c_int(do_verbose))
    
    # Sparse fisher vector
    return scipy.sparse.coo_matrix(x.flatten(), dtype=np.float32)
    
def fishervector(im, features, gmm, do_signsqrt=False, do_normalized=False, do_fastfisher=False, do_improvedfisher=False, do_verbose=False):
    """vlfeat-0.9.18 fisher vector encoding"""

    # Feature extraction
    d_obs = features(im)        
    
    # Preallocate output buffer
    m_fishervector = gmm.num_modes() * gmm.dimensionality() * 2  # length of fisher vector encoding
    x = np.zeros( (1, m_fishervector), dtype=np.float32)  # preallocated output (row vector)

    # Typecast inputs
    mean = np.asarray(gmm.mean, dtype=np.float32, order='C')  # row major, num_modes x dimensionality
    covariance = np.asarray(gmm.covariance, dtype=np.float32, order='C') # row major, num_modes x dimensionality
    prior = np.asarray(gmm.prior, dtype=np.float32, order='C') # row major, num_modes x 1

    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    fv.lib.fishervector(d_obs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
                        mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # mean pointer
                        covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # covariance pointer
                        prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # prior pointer
                        x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # fisher vector output buffer
                        ctypes.c_int(gmm.dimensionality()),  # dimensionality of data
                        ctypes.c_int(gmm.num_modes()),  # number of modes in GMM
                        ctypes.c_int(d_obs.shape[0]),  # number of observations
                        ctypes.c_int(do_signsqrt),  # options
                        ctypes.c_int(do_normalized),
                        ctypes.c_int(do_fastfisher),
                        ctypes.c_int(do_improvedfisher),
                        ctypes.c_int(do_verbose))

    # Fisher vectors!
    return x

def fishervector_posterior(im, features, gmm):
    """vlfeat-0.9.18 fisher vector encoding"""

    # Feature extraction
    d_obs = features(im)        
    
    # Preallocate output buffer
    m_fishervector = gmm.num_modes() * gmm.dimensionality() * 2  # length of fisher vector encoding
    x = np.zeros( (d_obs.shape[0], m_fishervector), dtype=np.float32)  # preallocated output (matrix)

    # Typecast inputs
    mean = np.asarray(gmm.mean, dtype=np.float32, order='C')  # row major, num_modes x dimensionality
    covariance = np.asarray(gmm.covariance, dtype=np.float32, order='C') # row major, num_modes x dimensionality
    prior = np.asarray(gmm.prior, dtype=np.float32, order='C') # row major, num_modes x 1

    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    fv.lib.fishervector_posterior(d_obs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
                                  mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # mean pointer
                                  covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # covariance pointer
                                  prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),     # prior pointer
                                  x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # posterior output buffer
                                  ctypes.c_int(gmm.dimensionality()),  # dimensionality of data
                                  ctypes.c_int(gmm.num_modes()),  # number of modes in GMM
                                  ctypes.c_int(d_obs.shape[0]))  # number of observations

    # posteriors!
    return x

def average_semilocalfishervector(im,
                                  features,
                                  gmmMean,
                                  gmmCovar,
                                  gmmPrior,
                                  dl,
                                  ql): # a list of scales
    """vlfeat-0.9.18 fisher vector encoding, with local spatial pooling"""

    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    
    # Feature extraction
    descriptors = features(im)
        
    # Typecast inputs
    mean = np.ascontiguousarray(gmmMean.astype(np.float32), dtype=np.float32)
    covariance = np.ascontiguousarray(gmmCovar.astype(np.float32), dtype=np.float32)
    prior = np.ascontiguousarray(gmmPrior.astype(np.float32), dtype=np.float32)
    ql = np.array(ql)

    # Preallocate output buffer
    fvdim = 2*gmmMean.shape[0]*descriptors.shape[1]  # length of fisher vector encoding
    fvbuf = np.ascontiguousarray(np.zeros((1,fvdim),dtype=np.float32), dtype=np.float32)  # preallocated FV array

    # assert that the data dimensionality matches the gmm dimensionality
    assert descriptors.shape[1]==gmmMean.shape[1]

    im_width = im.width()
    im_height = im.height()
    frames=np.zeros((descriptors.shape[0],2),dtype=np.float32) # buffer to hold frames
    frames[:,0] = (descriptors[:,-2]+0.5)*im_width # unpack back to original coordinates
    frames[:,1] = (descriptors[:,-1]+0.5)*im_height
    frames = np.ascontiguousarray(frames, dtype=np.float32)
    descriptors = np.ascontiguousarray(descriptors, dtype=np.float32)
    
    fv.lib.average_semilocalfishervector(
        descriptors.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
        frames.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # frames pointer
        ctypes.c_int(descriptors.shape[0]), # number of descriptors
        ctypes.c_int(descriptors.shape[1]), # descriptor dimensionality
        ctypes.c_int(im_width),  # number of descriptors across the image
        ctypes.c_int(im_height),  # number of descriptors down the image
        mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM mean pointer
        covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM covariance pointer
        prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM prior pointer
        ctypes.c_int(mean.shape[0]),  # number of modes in GMM
        ctypes.c_int(dl),  # stride for spatial pooling
        ql.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), # array of spatial window sizes for pooling
        ctypes.c_int(len(ql)),  # the number of spatial window sizes in ql
        fvbuf.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))  # fisher vector output buffer

    assert np.any(np.isnan(fvbuf))==False
    return fvbuf

def numel_semilocalfishervector(dl,
                                nql,
                                im_width,
                                im_height):
  return nql*len(range(0,im_height,dl))*len(range(0,im_width,dl))

def get_descriptor_posterior(im,
                             features,
                             gmmMean,
                             gmmCovar,
                             gmmPrior):
    """vlfeat-0.9.18 data posterior calculation"""
    
    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    
    # Feature extraction
    descriptors = features(im)
        
    # Preallocate output buffer
    N = descriptors.shape[0]
    D = descriptors.shape[1]
    K = gmmMean.shape[0]
    num_posteriors = N*K
    posterior = np.ascontiguousarray(np.zeros((N,K),dtype=np.float32), dtype=np.float32)

    # Typecast inputs
    descriptors = np.ascontiguousarray(descriptors, dtype=np.float32)
    mean = np.ascontiguousarray(gmmMean, dtype=np.float32)
    covariance = np.ascontiguousarray(gmmCovar, dtype=np.float32)
    prior = np.ascontiguousarray(gmmPrior, dtype=np.float32)

    fv.lib.get_descriptor_posterior(
        descriptors.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
        ctypes.c_int(N), # number of descriptors
        ctypes.c_int(D), # descriptor dimensionality
        mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM mean pointer
        covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM covariance pointer
        prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM prior pointer
        ctypes.c_int(K),  # number of modes in GMM
        posterior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))  # posterior output buffer

    return posterior

def semilocalfishervector_reduce_and_stack2x2(im,
                                              features,
                                              gmmMean,
                                              gmmCovar,
                                              gmmPrior,
                                              dl,
                                              ql, # a list of scales
                                              W, # 128 x (2*K*D) DDR matrix
                                              do_signsqrt,
                                              do_normalized,
                                              scale_factor=1.0):
    """vlfeat-0.9.18 fisher vector encoding, with local spatial pooling"""
    
    # vl-feat-0.9.18 C library
    fv = bobo.app.loadlibrary('fishervector-0.9.18')  # FIXME: should this go at top of module?
    
    # Feature extraction
    descriptors = features(im)
        
    im_width = im.width()
    im_height = im.height()
    descriptor_frames=np.zeros((descriptors.shape[0],2),dtype=np.float32) # buffer to hold frames
    descriptor_frames[:,0] = (descriptors[:,-2]+0.5)*im_width # unpack back to original coordinates
    descriptor_frames[:,1] = (descriptors[:,-1]+0.5)*im_height

    # Preallocate output buffer
    num_fvs = numel_semilocalfishervector(dl,len(ql),im_width,im_height)
    fvdim = 2*gmmMean.shape[0]*descriptors.shape[1]  # length of fisher vector encoding

    # preallocated FV array
    hl = W.shape[0]
    fvbuf = np.ascontiguousarray(np.zeros((num_fvs,4*hl),dtype=np.float32), dtype=np.float32)
    fvframes = np.ascontiguousarray(np.zeros((num_fvs,2),dtype=np.float32), dtype=np.float32)

    # Typecast inputs
    descriptors = np.ascontiguousarray(descriptors, dtype=np.float32)
    descriptor_frames = np.ascontiguousarray(descriptor_frames, dtype=np.float32)
    mean = np.ascontiguousarray(gmmMean, dtype=np.float32)
    covariance = np.ascontiguousarray(gmmCovar, dtype=np.float32)
    prior = np.ascontiguousarray(gmmPrior, dtype=np.float32)
    W_float32 = np.ascontiguousarray(W, dtype=np.float32)

    fv.lib.semilocalfishervector_reduce_and_stack2x2(
        descriptors.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # data pointer
        descriptor_frames.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # frames pointer
        ctypes.c_int(descriptors.shape[0]), # number of descriptors
        ctypes.c_int(descriptors.shape[1]), # descriptor dimensionality
        ctypes.c_int(im_width),  # number of descriptors across the image
        ctypes.c_int(im_height),  # number of descriptors down the image
        mean.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM mean pointer
        covariance.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM covariance pointer
        prior.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # GMM prior pointer
        ctypes.c_int(mean.shape[0]),  # number of modes in GMM
        ctypes.c_int(dl),  # stride for spatial pooling
        ql.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), # array of spatial window sizes for pooling
        ctypes.c_int(len(ql)),  # the number of spatial window sizes in ql
        W_float32.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # DDR matrix pointer
        ctypes.c_int(hl),  # FV dim after reduction
        fvbuf.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),  # fisher vector output buffer, num_fvs x 4*W.shape[0]
        fvframes.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))  # fisher vector frames output buffer

    assert np.any(np.isnan(fvbuf))==False
    assert np.any(np.isnan(fvframes))==False

    # remove any all-zero FVs
    idx = np.any(fvbuf,axis=1)
    fvbuf = fvbuf[idx,:]
    fvframes = fvframes[idx,:]

    if do_signsqrt:
        fvbuf = signsqrt(fvbuf)
    if do_normalized:
        fvbuf = fvbuf / np.sqrt(np.sum(np.power(fvbuf,2), axis=1)).reshape((fvbuf.shape[0],1)) # axis=1 ensures vector norm and not matrix norm

    assert np.any(np.isnan(fvbuf))==False

    # apply scale_factor after normalization
    fvbuf *= scale_factor
    fvbuf = np.concatenate((fvbuf, (fvframes[:,[0]]/im_width)-0.5, (fvframes[:,[1]]/im_height)-0.5), axis=1)
    return fvbuf
