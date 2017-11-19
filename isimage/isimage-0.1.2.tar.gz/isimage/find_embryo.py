""" Algorithms for locating an embryo in the image
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import sys
import numpy as np
import scipy as sp
import scipy.linalg as la
import scipy.sparse as spr
import scipy.stats as st
from scipy.signal import fftconvolve
from sklearn import linear_model
from sklearn import mixture
from sklearn.feature_extraction.image import grid_to_graph
import matplotlib.pyplot as plt
import cv2
import matplotlib.patches as pt

def bounding_box(labels, th = 0, verbose=False):
    """ 
        Find bounding box from indicator function.
        
        Parameters
        ----------
            
        labels: array[heght, width]
            Object outline in the form of indicator function.
            
        th: float, optional, default: 0
            Relative threshold
        
        verbose=False: boolean, optional, default: False
            Plots the result if True.
                    
        Returns
        -------
        
        tuple(4)
            Bounding box: Left, Right, Top, Bottom
    """
    hs = np.float32(np.sum(labels, axis=0))
    horz = [i for i, x in enumerate(hs/np.max(hs)) if x > th]
    l, r = horz[0], horz[-1]+1

    vs = np.float32(np.sum(labels, axis=1))
    vert = [i for i, x in enumerate(vs/np.max(vs)) if x > th]
    t, b = vert[0], vert[-1]+1

    if verbose == True:
        plt.figure()
        ax = plt.subplot(121) 
        ax.plot(hs/np.max(hs))
        ax = plt.subplot(122) 
        ax.plot(vs/np.max(vs))

    return l, r, t, b

def get_subgraphs(L, th = 0.05, epsilon = 1.e-7):
    """ 
        Recursively cut connectivity graph
        
        Parameters
        ----------
            
        L: sparse matrix
            Laplacian of a connectivity graph.
            
        th: float, optional, default: 0.05
            Graph cut threshold
        
        epsilon: float, optional, default: 1.e-7
            Smallest non-zero float for eigen value decomposition.
                    
        Returns
        -------
        
        list
            List of disconnected subgraphs
    """

    size = L.shape[0]
    if size == 1:
        return [np.array([0])]
    
    #finding the smallest eigenvalue and associated eigenvector of the Laplacian
    try:
        evals_small, evecs_small = spr.linalg.eigsh(L, 1, sigma=epsilon, which='LM', tol=epsilon) # 
    except:
        print "get_subgraphs:", L.shape, th, epsilon 
        print str(sys.exc_info()[1])
        return []

    indx, ys = np.array(sorted(enumerate(evecs_small[:, 0]), key=lambda x: x[1])).T
    indx = np.uint32(indx)
    
    #max jump in sorted components of the eigenvector
    ys = ys[1:] - ys[:-1]
    cut = np.argmax(ys)

    #stop recursion if cannot cut
    if ys[cut] < th or abs(evals_small) > epsilon:
        return [indx]

    indl, indr = indx[:cut+1], indx[cut+1:]
    if L[indl, :].tocsc()[:, indl].tocsr().shape == (0, 0) or L[indr, :].tocsc()[:, indr].tocsr().shape == (0, 0):
        print ys.shape, cut
        print ys
        
    #split the Laplacian and recurse
    return (   [indl[l] for l in get_subgraphs(L[indl, :].tocsc()[:, indl].tocsr(), th, epsilon)]
             + [indr[l] for l in get_subgraphs(L[indr, :].tocsc()[:, indr].tocsr(), th, epsilon)] )

def smooth_contour(energy, initial, theta=-np.inf, nu=0, mu=1, max_iter=500): 
    """ 
        Contour smoothing by curvature minimization
        
        Parameters
        ----------
            
        energy: array [height, width]
            External potential.
            
        initial: array [height, width]
            Countour to smooth in the form of level set. 1 for the contour 
            inside; 0 for outside.
        
        theta: float, optional, default: -np.inf
            External potential threshold for baloon force
            
        nu: float, optional, default: 0
            Balloon force coeficient
        
        mu: integer, optional, default: 1
            Number of iterations of curvature force operators to apply
        
        max_iter: integer, optional, default: 500
            Maximum number of iterations to run.
        
        Returns
        -------
        
        array [height, width]
            Smoothed countour in the form of level set. 1 for the contour 
            inside; 0 for outside.
    """
    
    edkernel = np.ones((3, 3), dtype=np.uint8)
    balloon_force = (lambda ls: cv2.dilate(ls, edkernel)) 
    if nu < 0 :
        balloon_force = (lambda ls: cv2.erode(ls, edkernel))
        
    #Morphological kernel for curavture force    
    curv_kernels = np.zeros((4, 3, 3), dtype=np.uint8)
    curv_kernels[0, 1] = 1
    curv_kernels[2, :, 1] = 1
    curv_kernels[1] = np.eye(3)
    curv_kernels[3] = curv_kernels[1,::-1]
    
    def curvature_force(ls, mu, backward=0):
        si_ = lambda fn: np.max([cv2.erode (fn, kernel=k, anchor=(1, 1)) for k in curv_kernels], axis=0)
        is_ = lambda fn: np.min([cv2.dilate(fn, kernel=k, anchor=(1, 1)) for k in curv_kernels], axis=0)
        
        siis = lambda fn: si_(is_(fn))
        issi = lambda fn: is_(si_(fn))
        
        for i in range(mu):
            if i % 2 == 0:
                ls = siis(ls)
            else:
                ls = issi(ls)
        
        return ls
    
    #external potential gradient
    dE = np.transpose(np.gradient(energy, edge_order=2), axes=(1,2,0))
    
    u = initial.copy()
    u[u > 0] = 1
     
    nu_ = np.ones_like(u)*nu
    nu_[(energy < theta)] = 0

    ma = []
    for i in range(max_iter):
        u_ = u.copy()
        
        #balloon force
        u_[nu_ > 0] = cv2.dilate(u_, edkernel)[nu_ > 0]
        u_[nu_ < 0] = cv2.erode (u_, edkernel)[nu_ < 0]
        
        #external force
        du_ = np.transpose(np.gradient(u_, edge_order=2), axes=(1,2,0))
        f = np.sum(du_*dE, axis=-1)
        u_[f > 0] = 1
        u_[f < 0] = 0
        
        u_ = curvature_force(u_, mu, backward=i%2)
        
        #convergence condition, relative change of the coutour area over
        #last 5 iterations <= 1.e-5
        if len(ma) > 5:
            msk_1 = np.mean(ma, axis=0)
            ma = ma[1:] + [u_]
            
            pix = np.sum(np.abs(np.mean(ma, axis=0) - msk_1))
            
            if pix < 1 or round(np.log10(pix/np.sum(msk_1))) <= -5:
                break
        else:
            ma += [u_]
            
        u = u_
        
    return np.uint8(np.mean(ma, axis=0) > 0.5)
    
def extract_data(small, num_layers=1):
    """ 
        Extract intensity and texture data
        
        Parameters
        ----------
            
        small: array [height, width, 3]
            The image the data to be extracted from.
        
        num_layers: integer, optional, default: 1
            The number of Gaussian pyramid layers to use. 
        
        Returns
        -------
        
        X: array(2)
            The data extracted
        
        shape: tuple(2)
            Dimensions of the next Gaussian pyramid layer, i.e. that was
            not used in data extraction.
    """

    X = np.array([]).reshape(small.shape[0]*small.shape[1], -1)
    small2 = np.copy(small)
    for i in range(num_layers):
        #extract 2D data
        d = np.copy(small2[:, :, :])
        dx = cv2.Scharr(d,cv2.CV_64F,1,0)
        dy = cv2.Scharr(d,cv2.CV_64F,0,1)

        #enlarge 2D data to match original size
        for j in range(i):
            d = cv2.pyrUp(d)
            dx = cv2.pyrUp(dx)
            dy = cv2.pyrUp(dy)

        #Reshape and combine data
        X = np.hstack([X,
                d[:small.shape[0], :small.shape[1], :].reshape((-1, 3)),
                dx[:small.shape[0], :small.shape[1], :].reshape((-1, 3)),
                dy[:small.shape[0], :small.shape[1], :].reshape((-1, 3))])

        small2 = cv2.pyrDown(small2)
        
    return X, small2.shape

def find_embryo(img, max_comp=2, layer_size=200, num_layers=2, rel_threshold=.1, abs_threshold=25, smooth=True, verbose=False):
    """ 
        Locate an embryo in the image
        
        Parameters
        ----------
            
        img: array [height, width, 3]
            The RGB image to be searched. Range of values 0 - 255
        
        max_comp: integer, optional, default: 2
            The maximum number components to segment the image into. 
            
        layer_size: integer, optional, default: 200
            The upper limit on the largest dimension of the larges layer 
            of Gaussian pyramid to use in segmentation
        
        num_layers: integer, optional, default: 2
            Number of Gaussian pyramid layers toooo use in segemntation
            
        rel_threshold: float, optional, default: .1
            Threshold for filtering disconnected foregreound islands. All
            islands of size < rel_threshold*size_of_largest_island will
            be reassigned to the background
        
        abs_threshold: integer, optional, default: 25
            Threshold for filtering disconnected foregreound islands. All
            islands of size < abs_threshold will be reassigned to the 
            background
        
        smooth: Bool, optional, default: True
            Defines whether to smooth the embryo contour.
            
        verbose: Bool/str, optional, default: False
            Verbosity level:
            - False: silent run
            - True: report textual information
            - Path prefix: report textual information and report graphical
                information in verbose+<suffix>.jpg files
                
        
        Returns
        -------
        
        None: if nothing is found
        
        Otherwise:
                
        mask: array[heigth, width]
            Mask defining the position of the embryo.
            
        touches: Bool
            True if the embryo touches the image edge
            
        rect: tuple(4)
            Extended by 15% bounding box around the embryo (left, right, 
            top, bottom)
            
        scaling: float
            Subsampling ratio used.
            
    """

    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    small = np.float64(lab) + .25*np.random.randn(*lab.shape)

    #Compensating of linear gradients in the picture
    n_y, n_x = small.shape[:2]
    pos = np.vstack([np.arange(n_x*n_y)%n_x, np.arange(n_x*n_y)/n_x]).T
    lm = linear_model.LinearRegression().fit(pos, small.reshape(-1, 3))
    small += np.mean(small.reshape(-1, 3), axis=0).reshape(1, 1, 3) - lm.predict(pos).reshape(small.shape)
    small = np.maximum(0, np.minimum(255, small))
    
    pyramid = [small]
    
    while np.max(small.shape[:-1]) > layer_size:
        small = cv2.pyrDown(small)
        pyramid += [small.copy()]
    scaling = int(np.round(np.max(np.asarray(lab.shape, dtype=float)/np.asarray(small.shape, dtype=float))))
    
    em = 3
    X, small2_shape = extract_data(small, num_layers)
    Xnb = X.reshape(small.shape[:2]+(X.shape[-1],))[em:-em, em:-em].reshape(-1, X.shape[-1])
    
    max_scaling = int(np.round(np.max(np.asarray(lab.shape, dtype=float)/np.asarray(small2_shape, dtype=float))))
    
    # Whitening and PCA
    X = X.T
    Xnb = Xnb.T
    n, p = Xnb.shape
        
    X_mean = Xnb.mean(axis=-1)
    X   -= X_mean[:, np.newaxis]
    Xnb -= X_mean[:, np.newaxis]
    
    u, d, _ = la.svd(Xnb, full_matrices=False)
    del _
    
    n_components =  len(d[d/np.sum(d) > 1.e-6])

    K = (u / d).T[:n_components]  
    del u, d
    Xnb = np.dot(K, Xnb)
    Xnb *= np.sqrt(p)
    
    X = np.dot(K, X)
    X *= np.sqrt(p)
    
    X = X.T
    Xnb = Xnb.T
    
    X_ = Xnb.copy()
    np.random.shuffle(X_)
    
    sample_size = max(X.shape[0], 10*(max_comp + max_comp*n_components + max_comp*n_components*(n_components + 1)/2))

    best_model = (None, -1, -np.inf, None, None, -1)
    
    for it in range(3):
        #clustering pixels
        np.random.shuffle(X_)
        models = [mixture.GMM(i+1, covariance_type='full', n_iter=500, n_init=1).fit(X_[:sample_size]) for i in range(max_comp)]
        if not any([m.converged_ for m in models]):
            if verbose:
                print "GMM did not converge"
            return 

        bics = [m.bic(X_[:sample_size]) for m in models if m.converged_]
        best = models[np.argmin(bics)]

        HScomps  = best.get_params()['n_components']
        weights  = best.weights_ 
        meansHS  = best.means_ 
        HSlabels = best.predict(X)
        
        if HScomps == 1:
            if best_model[2] == -np.inf:
                if best_model[-1] == -1:
                    best_model = (best, 0, -np.inf, None, None, it)
                elif it - best_model[-1] > 5:
                    break
            continue

        #predicting embryo component
        n_y, n_x = small.shape[:2]
        pos = np.vstack([np.arange(n_x*n_y)%n_x, np.arange(n_x*n_y)/n_x]).T
        
        lps2 = []
        psi = np.diag([n_x/2., n_y/2.])**2 
        nu = 1.
        for l in range(HScomps):
            obj_x = pos[HSlabels != l] - np.array([n_x/2., n_y/2.])
            n = len(obj_x)
            A = obj_x.T.dot(obj_x)
            lx = nu/2*np.log(la.det(psi)) + sp.special.multigammaln((nu + n)/2, 2) - (nu + n)/2*np.log(la.det(psi + A)) - n*np.log(np.pi) 
            lx += -len(pos[HSlabels == l])*np.log(n_x*n_y)
            
            lps2 += [lx]
            
        bg = np.argmax(lps2)
        se, fi = sorted(lps2)[-2:]
        
        if verbose:
            print "fi", fi

        if best_model[2] < fi:
            best_model = (best, bg, fi, se, lps2, it)
        
    best, bg, fi, se, lps2, _ = best_model
    if verbose:
        print "Iterated ", it

    HScomps  = best.get_params()['n_components']
    weights  = best.weights_ 
    meansHS  = best.means_ 
    HSlabels = best.predict(X)
    proba = best.predict_proba(X)
    HSlabels_ = HSlabels.copy()
    
    del X_
    del X

    if type(verbose) == str:
        fig = plt.figure()
        ax = fig.gca()
        present = np.zeros(small.shape, dtype=float)
        present[HSlabels_.reshape(small.shape[:-1]) == 0] = np.array([0, 0xdc, 0xdc])
        present[HSlabels_.reshape(small.shape[:-1]) == 1] = np.array([0xdc, 0xdc, 0])
        present[HSlabels_.reshape(small.shape[:-1]) == 2] = np.array([0xdc, 0, 0xdc])
        present /= 255
        ax.imshow(present)
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')
        
        ver_name = verbose+'.labels.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

    if HScomps == 1:
        if verbose:
            print "No objects found"
        return 

    conf = (fi - se)/fi
    if abs(conf) < 1.e-3:
        if verbose:
            print "Mode used"
        borders = np.ones(small.shape[:2])
        borders[1:-1,1:-1] = 0
        bg = int(st.mode(HSlabels.reshape(small.shape[:2])[borders == 1])[0][0])
    
    if type(verbose) == str:
        fig = plt.figure()
        ax = fig.gca()

        present = np.ones(small.shape[:-1] + (3,), dtype=float)*0xcd
        present[HSlabels_.reshape(small.shape[:-1]) != bg] = np.array([0, 0xdc, 0])
        present /= 255
        ax.imshow(present) 
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')

        ver_name = verbose+'.object_component.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

    bg_colour = np.mean(small[HSlabels.reshape(small.shape[:-1]) == bg], axis=0)

    save = HSlabels.copy()
    
    proba = np.hstack([
          proba[:, np.arange(proba.shape[-1]) != bg].sum(axis=-1)[:, np.newaxis]
        , proba[:, bg][:, np.newaxis]
    ])
    
    proba[proba[:, 0] == 0, 0] = proba[proba[:, 0] > 0, 0].min()
    proba[proba[:, 1] == 0, 1] = proba[proba[:, 1] > 0, 1].min()
    
    logps = np.log(proba)
    
        
    for touch_check in range(2):
        dst = np.float32((HSlabels != bg).reshape(small.shape[:-1]))
        edge_margins = em*touch_check
        
        if edge_margins > 0:
            dst = dst[edge_margins : -edge_margins, edge_margins : -edge_margins]

        #making connectivity graph of non-background pixels
        conn = spr.csc_matrix(grid_to_graph(*dst.shape), dtype=float)
        conn.data *= dst.ravel()[conn.indices]
        conn = conn.multiply(conn.T)

        #removing disconnected background vertices
        colsum = conn.sum(axis=1).A1
        colsum[colsum > 0] = 1
        colsum[colsum > 0] = np.cumsum(colsum[colsum > 0])
        back_map = np.array([[i/dst.shape[1], i%dst.shape[1]] for i, x in enumerate(colsum) if x > 0], dtype=int)
        conn = conn[:, colsum > 0].tocsr()[colsum > 0, :]

        #making Laplacian matrix and getting subgraphs
        L = spr.dia_matrix((conn.sum(axis=1).reshape(-1), [0]), conn.shape).tocsr() - conn
        subgraphs = get_subgraphs(L, th=0.0001) 
        del conn
        del L

        subgraphs = [s for s in subgraphs if len(s) > 0]
        if len(subgraphs) == 0:
            return        
        
        #filtering noisy subgraphs
        largest = float(max([len(s) for s in subgraphs]))
        for s in subgraphs:
            if len(s)/largest <= rel_threshold or len(s) <= abs_threshold:
                loc = back_map[s]
                dst[loc[:, 0], loc[:, 1]] = 0
        
        subgraphs = [s for s in subgraphs if len(s)/largest > rel_threshold and len(s) > abs_threshold]
        
        if len(subgraphs) == 0:
            if verbose :
                print ("Objects are too small")
            return 
        
        lake_prob = []
        diff = []
        for s in subgraphs:
            loc = back_map[s]
            diff += [la.norm(np.mean(small[loc[:, 0], loc[:, 1]].reshape(-1, 3), axis=0) - bg_colour, 2)/255]
            lake_prob += [-logps[:, 1].reshape(small.shape[:2])[loc[:, 0], loc[:, 1]].mean()]
        
        diff = np.array(diff)
        slens = np.array([len(s) for s in subgraphs], dtype=float)

        lake_prob /= np.sum(lake_prob)

        obj_subgraph = np.argmax(np.sqrt(slens)*diff) 
        
        for i, s in enumerate(subgraphs):
            if i != obj_subgraph:
                loc = back_map[s]
                dst[loc[:, 0], loc[:, 1]] = 0
        
        l, r, t, b = bounding_box(dst*255, 0.01, verbose=False)
        touches = (l == 0 or r == dst.shape[1] or t == 0 or b == dst.shape[0])
        
        if not touches:
            break

    if edge_margins > 0:
        if touches:
            temp = np.float32((HSlabels != bg).reshape(small.shape[:-1]))
        else:
            temp = np.zeros(np.array(dst.shape) + 2*edge_margins)
            
        temp[edge_margins:-edge_margins, edge_margins:-edge_margins] = dst
        dst = temp
    
    contour_base = np.uint8(dst*255).copy()
    _, contour, _ = cv2.findContours(np.uint8(dst*255), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
    if len(contour) > 0:
        dst = cv2.fillPoly(np.zeros_like(dst), contour, 1)
    else:
        return

    if type(verbose) == str:
        fig = plt.figure()
        ax = fig.gca()

        present = np.ones(small.shape[:-1] + (3,), dtype=float)*0xcd
        present[HSlabels_.reshape(small.shape[:-1]) != bg] = np.array([0, 0xdc, 0])
        present[(HSlabels_.reshape(small.shape[:-1]) != bg) & (dst == 0)] = np.array([0xdc, 0, 0])
        present /= 255
        ax.imshow(present) 
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')

        ver_name = verbose+'.object.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name
        
        fig = plt.figure()
        ax = fig.gca()
        
        ax.imshow(cv2.cvtColor(np.uint8(np.round(small)), cv2.COLOR_LAB2RGB))

        lims = ax.get_xlim(), ax.get_ylim()

        _, contour, _ = cv2.findContours(np.uint8(dst*255), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        contour = [contour[np.argmax([cv2.contourArea(c) for c in contour])]]
        contour_simple = np.array(contour, dtype=int).reshape(-1, 2)
        contour_simple = np.vstack([contour_simple, contour_simple[0, :]])
        
        ax.plot(contour_simple[:, 0], contour_simple[:, 1], 'r-')

        ax.set_xlim(lims[0]), ax.set_ylim(lims[1])
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')

        ver_name = verbose+'.object_contour.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

    if not smooth:
        ksize = max(3, int(round(max_scaling/2)))
        
        borders = np.ones_like(dst)
        borders[ksize:-ksize,ksize:-ksize] = 0
        save_border = dst[borders == 1]
        
        morph_kernel = np.ones((ksize, )*2, dtype=np.uint8) 
        dst = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, morph_kernel)
        dst[borders == 1] = save_border
        
        temp = np.zeros_like(dst)
        temp[:-1, :-1] = dst[1:, 1:]
        dst = temp
        
    else:
        
        borders = np.ones_like(dst)
        borders[2:-2,2:-2] = 0
        
        mins = logps.min(axis=0)
        logps /= mins[np.newaxis, :]
        energy = logps.sum(axis=1).reshape(small.shape[:2])
        
        if touches:
            dst_ = dst.copy()
            prev_size = 0
            for round_ in range(100):
                noise = np.zeros_like(dst[borders == 1])
                noise[:int(noise.shape[0]*.25)] = 1
                np.random.shuffle(noise)
                noise_ = np.zeros_like(dst)
                noise_[borders == 1] = noise
                dst = np.maximum(dst, noise_)
                
                ksize = 3 
                iters = 1
                
                _, contour, _ = cv2.findContours(np.uint8(dst*255), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
                sizes = np.array([cv2.contourArea(c) for c in contour])
                contour = list(np.array(contour)[sizes > 1]) #(round_ + 1)**1]
                dst = cv2.fillPoly(np.zeros_like(dst), contour, 1)

                if round_ > 0 and sizes.max()/float(prev_size) > 1.05:
                    break
                
                prev_size = sizes.max()
                dst = np.maximum(dst_, dst)
                

        initial = dst
        dst = smooth_contour(energy, initial, theta=np.percentile(energy.ravel(), 50), mu=8)

    #scale the object back
    dst *= 255
    pyrpos = -1
    while min(dst.shape) < min(img.shape[:-1]):
        dst = cv2.pyrUp(dst)

    exc = 0 
    dst = dst[: img.shape[0], : img.shape[1]]
    
    dst = cv2.erode(np.uint8(dst >= 255) , np.ones((int(round(1*max_scaling + 0*scaling)),)*2, dtype=np.uint8))
    
    
    _, contour_sm, _ = cv2.findContours(np.uint8(dst), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
    if len(contour_sm) > 0:
        contour_sm = [contour_sm[np.argmax([cv2.contourArea(c) for c in contour_sm])]]
        dst = cv2.fillPoly(np.zeros_like(dst), contour_sm, 255)
    else:
        return

    if type(verbose) == str:
        fig = plt.figure()
        ax = fig.gca()

        ax.imshow(img)
        
        lims = ax.get_xlim(), ax.get_ylim()
        
        _, contour2, _ = cv2.findContours(np.uint8(dst >= 255), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        if len(contour2) > 0:
            contour2 = [contour2[np.argmax([cv2.contourArea(c) for c in contour2])]]
            contour_simple2 = np.array(contour2).reshape(-1, 2)
            contour_simple2 = np.vstack([contour_simple2, contour_simple2[0, :]])
            ax.plot(contour_simple2[:, 0], contour_simple2[:, 1], 'g-')
        
        ax.set_xlim(lims[0]), ax.set_ylim(lims[1])
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')

        ver_name = verbose+'.smoothed.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

    #getting bounding rect
    l, r, t, b = bounding_box(dst, 0.01, verbose=False)

    margins = np.max([.15*(b-t), .15*(r-l)])
    rect = np.array([t, b, l, r], dtype=float) + np.vstack([[-margins]*2, [margins]*2]).T.reshape(-1) 
    rect[0::2] = np.maximum(rect[0::2], [0, 0])
    rect[1::2] = np.minimum(rect[1::2], img.shape[:-1])
    t, b, l, r  = np.int32(np.round(rect))

    if type(verbose) == str:
        fig = plt.figure()
        ax = fig.gca()
        
        ax.imshow(img)
        
        lims = ax.get_xlim(), ax.get_ylim()
        
        plt.plot([l, l, r, r, l], [b, t, t, b, b], 'b')

        ax.set_xlim(lims[0]), ax.set_ylim(lims[1])
        ax.get_yaxis().set_ticks([])#(direction='out')
        ax.get_xaxis().set_ticks([])#(direction='out')

        ver_name = verbose+'.box.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name
        
    if verbose :
        print 'lps', lps2, bg
        print 'touches', touches
            
    
    return np.uint8(dst >= 255), touches, (l, r, t, b), scaling
