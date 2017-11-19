""" Algorithms for expression pattern extraction 
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import numpy as np
import scipy.linalg as la
import scipy.stats as st
import itertools as it
from sklearn import mixture
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

from sklearn.decomposition import FastICA
from sklearn.decomposition import PCA

def extract_staining (img, mask, expected, white_threshold=.15, verbose=False):
    """ 
        Extract spatial distribution of the stain and pigment in the image
        
        Parameters
        ----------
            
        img: array [height, width, 3]
            The RGB image to be decomposed. Range of values 0 - 255
        
        mask: array [height, width]
            The mask showing the embryo location. 
            
        expected: [(array [3], float), (array [3], float), (array [3], float)]
            List of pairs (RGB colour, confidence) for expected stain, 
            pigment and background colour respectively. If any of the 
            colours    is not expected to be present corresponding RGB value 
            should be set to white ([255, 255, 255])
            
        white_threshold: float, optional, default: .15
            Maximal length of a colour vector in CMY unit cube, which is 
            still considered white.
            
        verbose: Bool/str, optional, default: False
            Verbosity level:
            - False: silent run
            - True: report textual information
            - Path prefix: report textual information and report graphical
                information in verbose+<suffix>.jpg files
                
        
        Returns
        -------
        
        strain: array [height, width]
            Spatial distribution of the stain 
        
        confidence: float
            Confidence level that the exp[ected stain is actually present 
            in the image [0..1]
            
        pigment: array [height, width]
            Spatial distribution of the pigment 

        colours: array [3, 3]
            RGB colours estimated from the image. If a colour is not
            present it is set to white
    """
    
    img_ = img.copy()
    img = 1 - img/255.
    c = 1 - np.vstack([colour for colour, p in expected])/255.
    
    c_save = c.copy()

    norms = np.array([la.norm(c[0], 2), la.norm(c[1], 2), la.norm(c[2], 2)])
    
    _, d, _ = la.svd([clr/n for clr, n in zip(c, norms) if n > 1.e-2])
    if d[-1]/d[0] < .05 and c.shape[0] > 1:
        dist = []
        for i in range(1, c.shape[0]):
            comb = (0, i)
            if np.all(norms[list(comb)] > 0.01):
                dist += [(comb, la.norm(c[comb[0]]/norms[comb[0]] - c[comb[1]]/norms[comb[1]] ,2))]
        farthest = list(max(dist, key= lambda x: x[1])[0])
        norms_ = np.zeros_like(norms)
        norms_[farthest] = norms[farthest]
        norms = norms_
    
    c = np.array([clr/n for clr, n in zip(c, norms) if n > 1.e-2])
    
            
    prior = np.array([p for colour, p in expected])[norms > 1.e-2]

    X = img[(mask == 1)].reshape(-1, 3)
    np.random.shuffle(X)
    X = X[:500000] #
    non_white_x = np.sum(X**2, axis=-1) > white_threshold**2 
    
    if np.all(~non_white_x):
        c_est = np.ones((len(norms), c.shape[1]))
        c_est[norms > 1.e-2] -= c
        
        return np.zeros(img.shape[:2]), 0, np.zeros(img.shape[:2]), np.uint8(np.maximum(0, np.minimum(1, c_est))*255)
    
    #estimating number of independent components
    infos = []
    icamodels = []
    n_comp = 3 
    for j in range(n_comp):
        w0 = np.ones((1, 1))
        if j > 0:
            rot = np.ones((2, 2))*np.sqrt(0.5)
            rot[1, 0] *= -1
            w0 = np.eye(j + 1)
            for i in range(j):
                R = np.eye(j + 1)
                R[np.kron(np.arange(j + 1) != 2 - i, np.arange(j + 1) != 2 - i).reshape(R.shape)] = rot.ravel()
                w0 = w0.dot(R)

        ws = [np.eye(j + 1), w0]

        icas = []
        for k, w in enumerate(ws):
            ica = FastICA(j + 1, fun='exp', max_iter=500, w_init=w)
            
            res = ica.fit_transform(X)#
            
            if type(verbose) == str:
                res_ = ica.transform(img.reshape(-1, 3))
                
            ms = np.mean(res, axis=0)
            ss = np.std(res, axis=0)
            kln = 0
            for i, d in enumerate(res.T):
                q, bins = np.histogram(d, bins=50)
                q = np.asarray(q, dtype=float) + 1.
                q /= np.sum(q)
                 
                p = st.norm(ms[i], ss[i]).pdf(.5*(bins[:-1] + bins[1:]))
                p /= np.sum(p)
                
                kl = st.entropy(p, q) #
                
                kln += kl
                
            icas += [(kln, ica)]                
        
        info, ica = sorted(icas, key=lambda x : -x[0])[0]
        infos += [info/(j + 1)]
        icamodels += [ica]

    n_comp = min(c.shape[0], np.argmax(infos) + 1)
    rerun = True
    
    c_initial = c.copy()
    
    while rerun:
        rerun = False
        c = c_initial.copy()
        
        ica = icamodels[n_comp - 1]
        res = ica.transform(X)
        s0 = ica.transform(np.zeros((1, X.shape[1])))
        res -= s0

        adj_ica = icamodels[1] 
        dirs = adj_ica.mixing_.T.copy()
        dirs /= np.sqrt(np.sum(dirs**2, axis=-1))[:, np.newaxis]
        icas = np.cross(dirs[0], dirs[1])
        
        #deciding on which expected components are present
        models = []
        for ind in it.combinations(range(c.shape[0]), n_comp):
            S = np.array([[np.corrcoef(np.vstack([es, ex]))[0, 1] for es in res.T] for ex in (X.dot(la.pinv(c[list(ind)]))).T])
            sc = np.abs(la.det(S))
            acs = 0
            if n_comp == 2 and c.shape[0] > 2:
                acs = np.abs(icas.dot(np.cross(c[ind[0]], c[ind[1]])))
                
            models += [(sc + 10*acs, S, ind)]

        if c.shape[0] != n_comp:
            stain_score, corrs, best_ind = sorted([(sc, S, ind) for sc, S, ind in models if 0 in ind], key = lambda x: x[0])[-1]
        else:
            stain_score, corrs, best_ind = models[0]
            
        best_ind = sorted(list(best_ind))
        
        # adjusting expected colours
        if 1 in best_ind: 
            adj_ind = [0, 1]
            
            adj_ica = icamodels[1] 
            dirs = adj_ica.mixing_.T.copy()
            dirs /= np.sqrt(np.sum(dirs**2, axis=-1))[:, np.newaxis]
            icas = np.cross(dirs[0], dirs[1])
            
            rot_axis = c[adj_ind].mean(axis=0)
            rot_axis /= la.norm(rot_axis, 2)            
            
            angles = np.arange(-15., 16.)/180 * np.pi
            rotated = np.zeros((angles.shape[0], 3))
            rotCMY = np.zeros((angles.shape[0], len(adj_ind), 3))
        
            length = c[adj_ind].dot(rot_axis)
            project = c[adj_ind] - c[adj_ind].dot(rot_axis)[:, np.newaxis] * rot_axis[np.newaxis, :]
            e1 = project[np.argmax(np.sum(project**2, axis=1))].copy()
            e1 /= la.norm(e1, 2)
            e = np.array([e1, np.cross(rot_axis, e1)])
            project = e.dot(project.T)

            for i, a in enumerate(angles):
                A = e.T.dot(
                    np.array([[np.cos(a), np.sin(a)]
                            ,[-np.sin(a), np.cos(a)]]))
                rotCMY[i] = (A.dot(project) + length[np.newaxis, :]*rot_axis[:, np.newaxis]).T
                rotated[i] = np.cross(rotCMY[i, 0], rotCMY[i, 1])

            acs = np.abs(rotated.dot(icas))
            
            c[adj_ind] = rotCMY[np.argmax(acs)]
            
            if verbose: 
                print "Adjusting expected colours: rotation angle = ", angles[np.argmax(acs)]/np.pi * 180
                
        
        # choosing the best decomposition
            
        ps = np.abs(corrs)
        P = np.zeros_like(ps)
        
        sh = np.array(P.shape) # - 1
        s = min(sh)
        best_score =  np.inf
        best_est = 0

        pr = prior[best_ind]

        X_ = X[non_white_x].T - ica.mean_[:, np.newaxis]

        dirs = ica.mixing_.T.copy()
        dirs /= np.sqrt(np.sum(dirs**2, axis=-1))[:, np.newaxis]
        dist2 = np.array([np.sum((np.eye(3) - ci[:, np.newaxis].dot(ci[np.newaxis, :])).dot(X_)**2, axis=0) for ci in dirs])
        comps_prjs_ = dirs.dot(X_)
        
        pw = np.exp(-dist2/(2*0.05**2))*comps_prjs_        
        
        for i0 in it.combinations(range(max(sh)), max(sh) - min(sh)):
            sl = [r for r in range(sh[0]) if r not in i0]
            for i1 in it.permutations(range(s), s):
                Q = np.zeros(sh)
                I = np.eye(s)
                Q[sl] = I[list(i1)]
                
                for i2 in range(s + 1):
                    for i3 in it.combinations(range(s), i2):
                        ones_ = np.ones(s)
                        ones_[list(i3)] *= -1
                        R = Q * ones_
                
                        comps = R.dot(dirs) 
                        
                        comps_prjs = R.dot(comps_prjs_)        
                        
                        est = np.diag(comps_prjs[np.arange(comps_prjs.shape[0]), np.argmax(R.dot(pw), axis = -1)]).dot(comps) + ica.mean_ 
                        est /= np.sqrt(np.sum(est**2, axis=-1))[:, np.newaxis]
                        
                        Dist = np.sqrt(np.sum((c[best_ind][(np.arange(len(best_ind)**2)%len(best_ind)).reshape((len(best_ind),)*2).T.ravel()] 
                                            - est[np.arange(len(best_ind)**2)%len(best_ind)])**2, axis=-1)).reshape((len(best_ind),)*2) 

                        if Dist.shape[0] > 1:
                            sc = np.mean(np.array([Dist[I[:, i4] == 1, i4]**2/np.mean(Dist[I[:, i4] == 0, i4]) for i4 in range(Dist.shape[0])]).ravel()*pr)
                        else:
                            sc = np.mean(np.array([Dist[I[:, i4] == 1, i4]**2 for i4 in range(Dist.shape[0])]).ravel()*pr)
                            
                            
                        if sc < best_score:
                            best_score = sc
                            P = R
                            best_est = est
                
        _, d, _ = la.svd(c)
        
        mean_check = np.maximum(0, (ica.mean_/la.norm(ica.mean_, 2)).dot(la.pinv(c)))
        mean_check = mean_check/np.sum(mean_check)
        
        if( d[-1]/d[0] > 0.05 and mean_check[1] > 5*mean_check[np.arange(mean_check.shape[0]) != 1].max()
            and np.all(np.abs(best_est - (ica.mean_/la.norm(ica.mean_, 2))[np.newaxis, :]) < white_threshold) ):
            conf = 0
            if 1 not in best_ind:
                best_ind = sorted(best_ind + [1])
                best_est_ = np.zeros((best_est.shape[0] + 1, best_est.shape[1]))
                best_est_[1:] = best_est
                best_est = best_est_
                n_comp += 1
            best_est[0] = np.zeros(3)
                
        #decomposing image and checking the result
        res = img.reshape(-1, 3).dot(la.pinv(best_est))
        
        _, d, _ = la.svd(best_est) 
        if n_comp == 3 and d[-1]/d[0] < 0.05 and la.norm(best_est[0], 2) > 0:
            infos[-1] = 0
            n_comp = np.argmax(infos) + 1
            rerun = True
            if verbose: 
                print "Rerun on unstable decomposition"
                print "singular values", d, d/d[0]
                print "infos", infos, n_comp
            
            continue

        if n_comp == 3 and len(np.where(np.vstack([c[1], best_est[1]]).dot(np.cross(best_est[0], best_est[2])) < 0)[0]) % 2 == 1:
            best_ind = [0, 2]
            best_est = best_est[best_ind]
            n_comp = 2
            res = img.reshape(-1, 3).dot(la.pinv(best_est))
            if verbose :
                print 'Dropping the pigment due to inconsistency'
        
        stain_m = c[ 0] - np.ones(3)/la.norm(np.ones(3), 2)
        stain_m /= la.norm(stain_m, 2)
        backg_m = c[-1] - np.ones(3)/la.norm(np.ones(3), 2)
        backg_m /= la.norm(backg_m, 2)
            
        
        def mode(data):
            h, b = np.histogram(data, bins=50)
            m = np.argmax(h)
            return .5*(b[m] + b[m+1])
        
        if( n_comp == 1 and mode(res[:, 0].reshape(img.shape[:2])[mask == 0]) > 1.0*mode(res[:, 0].reshape(img.shape[:2])[mask == 1]) and len(c) > 1
            and stain_m.dot(backg_m) < .95 ):
            infos[0] = 0
            n_comp = min(c.shape[0], np.argmax(infos) + 1)
            rerun = True
            if verbose: 
                print "Rerun on weak stain"
                print "stain_m.dot(backg_m)", stain_m.dot(backg_m)
            
            continue
                
        #Checking if pigment is confused with saturated stain
        if n_comp > 1 and 1 in best_ind:
            best_est_ = best_est.copy()
            best_est_[0] = np.ones(3)/np.sqrt(3)
            
            pigm_ = img.reshape(-1, 3).dot(la.pinv(best_est))
            pigm = pigm_[mask.ravel() == 1][:, 1]
            
            th = np.percentile(pigm_[mask.ravel() == 1, 1], 99)
            sqlens = (img**2).reshape(-1, 3).sum(axis=-1).reshape(img.shape[:2])
            darkest = img[(mask == 1) & (sqlens >= np.percentile(sqlens[mask == 1], 99.5))].reshape(-1, 3)
            
            pigm_ = img.reshape(-1, 3).dot(la.pinv(best_est_))

            _, d_, _ = la.svd(best_est_)
            
            dark_part = np.zeros(img.shape[:2])
            dark_part[sqlens >= np.sqrt(3)*(1 - white_threshold)] = sqlens[sqlens >= np.sqrt(3)*(1 - white_threshold)]
            dark_part[mask == 0] = 0
            
            plt.figure()
            ax=plt.subplot(121)
            toshow = np.zeros(img.shape[:2])
            toshow[mask == 1] = pigm
            ax.imshow(toshow)
            ax=plt.subplot(122)
            ax.imshow(dark_part)        
            
            if (d_[-1]/d_[0] < 0.01 or 
                    np.corrcoef(np.vstack([pigm, dark_part[mask == 1].ravel()]))[0,1] > 0.75
                    ) and np.any(np.abs(1 - darkest.mean(axis=0)) < white_threshold):
                best_ind = [ind for ind in best_ind if ind != 1]
                best_est = best_est[best_ind]
                n_comp = len(best_ind)
                res = img.reshape(-1, 3).dot(la.pinv(best_est))
                if verbose:
                    print 'Dropping pigment due to saturated stain'
            
        check = np.maximum(0, best_est[0].dot(la.pinv(c[best_ind])))
        conf = check[0]/np.sum(check)
    
    if type(verbose) == str:
        data = X
        steps = 15
        stainHist, _ = np.histogramdd(data, bins = [np.arange(np.min(data), np.max(data) + (np.max(data) - np.min(data))/steps, (np.max(data) - np.min(data))/steps)]*3)
        colors = []
        sizes = []
        for i in range(steps):
            for j in range(steps):
                for k in range(steps):
                    colors += [[(i + 0.5)*((np.max(data) - np.min(data))/steps) + np.min(data)
                              , (j + 0.5)*((np.max(data) - np.min(data))/steps) + np.min(data)
                              , (k + 0.5)*((np.max(data) - np.min(data))/steps) + np.min(data)]]
                    sizes += [stainHist[i, j, k]]

        colorsCMY = np.array(colors)
        sizes = np.array(sizes)
        colorsRGB = 1. - colorsCMY
        
        fig = plt.figure(figsize=(24, 20))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(colorsCMY[:, 0][(sizes > 0) ]
                 , colorsCMY[:, 1][(sizes > 0) ]
                 , colorsCMY[:, 2][(sizes > 0) ]
                 , s=np.log(sizes[ (sizes > 0) ] + 1)*50
                 , c = colorsRGB[  (sizes > 0) ]) 
        limits = (ax.get_xlim(), ax.get_ylim(), ax.get_zlim())
        
        ax.scatter([ica.mean_[0]], [ica.mean_[1]], [ica.mean_[2]], c = 'k', marker='+')
        p0, p1 = (ica.mean_ - .67*ica.mixing_.dot(P.T).T[0]/la.norm(ica.mixing_.dot(P.T).T[0], 2)), (ica.mean_ + .67*ica.mixing_.dot(P.T).T[0]/la.norm(ica.mixing_.dot(P.T).T[0], 2)) 
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1) 
        if ica.mixing_.shape[1] > 1:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.dot(P.T).T[1]/la.norm(ica.mixing_.dot(P.T).T[1], 2)), (ica.mean_ + .67*ica.mixing_.dot(P.T).T[1]/la.norm(ica.mixing_.dot(P.T).T[1], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1) 
        if ica.mixing_.shape[1] > 2:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.dot(P.T).T[2]/la.norm(ica.mixing_.dot(P.T).T[2], 2)), (ica.mean_ + .67*ica.mixing_.dot(P.T).T[2]/la.norm(ica.mixing_.dot(P.T).T[2], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1)  
                
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
        ax.set_zlim(limits[2])
        ax.set_xlabel('C')
        ax.set_ylabel('M')
        ax.set_zlabel('Y')

        pca2 = PCA(2).fit(X)
        n = np.cross(pca2.components_[0], pca2.components_[1])
        n /= la.norm(n, 2)
        
        az = np.arctan2(n[0], n[1])*90./np.pi
        el = np.arccos(n[2])*90./np.pi
        ax.view_init(elev=el, azim=az)

        ver_name = verbose+'.independent_axes.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name
        
        dirs = ica.mixing_.T.copy()
        dirs /= np.sqrt(np.sum(dirs**2, axis=-1))[:, np.newaxis]
        dist2 = np.array([np.sum((np.eye(3) - ci[:, np.newaxis].dot(ci[np.newaxis, :])).dot(colorsCMY.T - ica.mean_[:, np.newaxis])**2, axis=0) for ci in dirs])
        
        pw_ = np.exp(-dist2/(2*0.05**2))    
        
        pwth = 0.5
        
        fig = plt.figure(figsize=(24, 20))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(colorsCMY[:, 0][(sizes > 0) & np.any(pw_ > pwth, axis=0)]
                 , colorsCMY[:, 1][(sizes > 0) & np.any(pw_ > pwth, axis=0)]
                 , colorsCMY[:, 2][(sizes > 0) & np.any(pw_ > pwth, axis=0)]
                 , s=np.log(sizes[ (sizes > 0) & np.any(pw_ > pwth, axis=0)] + 1)*50
                 , c = colorsRGB[  (sizes > 0) & np.any(pw_ > pwth, axis=0)]) 
        
        R = np.eye(P.shape[0])
        if P.shape[0] > n_comp:
            R[n_comp:] = 0

        R[0] *= -1
        
        if 0 in best_ind:
            est = np.diag(comps_prjs_[np.arange(comps_prjs_.shape[0]), np.argmax(R.dot(pw), axis = -1)]).dot(dirs) + ica.mean_ 
            est /= np.sqrt(np.sum(est**2, axis=-1))[:, np.newaxis]

            p0, p1 = np.zeros(3) , est[0] 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2) 
            if n_comp > 1:
                p0, p1 = np.zeros(3) , est[1] 
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2) 
            if n_comp > 2:
                p0, p1 = np.zeros(3) , est[2] 
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2)  

        ax.scatter([ica.mean_[0]], [ica.mean_[1]], [ica.mean_[2]], c = 'k', marker='+')
        p0, p1 = (ica.mean_ - .67*ica.mixing_.T[0]/la.norm(ica.mixing_.T[0], 2)), (ica.mean_ + .67*ica.mixing_.T[0]/la.norm(ica.mixing_.T[0], 2)) 
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67) 
        if ica.mixing_.shape[1] > 1:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.T[1]/la.norm(ica.mixing_.T[1], 2)), (ica.mean_ + .67*ica.mixing_.T[1]/la.norm(ica.mixing_.T[1], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67) 
        if ica.mixing_.shape[1] > 2:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.T[2]/la.norm(ica.mixing_.T[2], 2)), (ica.mean_ + .67*ica.mixing_.T[2]/la.norm(ica.mixing_.T[2], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67)  

        class Arrow3D(FancyArrowPatch):
            def __init__(self, xs, ys, zs, *args, **kwargs):
                FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
                self._verts3d = xs, ys, zs

            def draw(self, renderer):
                xs3d, ys3d, zs3d = self._verts3d
                xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
                self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
                FancyArrowPatch.draw(self, renderer)

        p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[0]/la.norm(ica.mixing_.dot(R.T).T[0], 2))
        a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
        ax.add_artist(a)
        if ica.mixing_.shape[1] > 1:
            p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[1]/la.norm(ica.mixing_.dot(R.T).T[1], 2)) 
            a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
            ax.add_artist(a)
        if ica.mixing_.shape[1] > 2:
            p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[2]/la.norm(ica.mixing_.dot(R.T).T[2], 2)) 
            a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
            ax.add_artist(a)
                
        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
        ax.set_zlim(limits[2])
        ax.set_xlabel('C')
        ax.set_ylabel('M')
        ax.set_zlabel('Y')

        ax.view_init(elev=el, azim=az)

        ver_name = verbose+'.proposing_colours.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

        fig = plt.figure(figsize=(24, 20))
        ax = fig.add_subplot(111, projection='3d')
        
        R = P
        if P.shape[0] > n_comp:
            R[n_comp:] = 0
        
        est = best_est 

        p0, p1 = np.zeros(3) , est[0] 
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2)
        if n_comp > 1:
            p0, p1 = np.zeros(3) , est[1] 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2) 
        if n_comp > 2:
            p0, p1 = np.zeros(3) , est[2] 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 1 - np.maximum(0, p1), linewidth=2)  

        ax.scatter([ica.mean_[0]], [ica.mean_[1]], [ica.mean_[2]], c = 'k', marker='+')
        p0, p1 = (ica.mean_ - .67*ica.mixing_.T[0]/la.norm(ica.mixing_.T[0], 2)), (ica.mean_ + .67*ica.mixing_.T[0]/la.norm(ica.mixing_.T[0], 2)) 
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67) 
        if ica.mixing_.shape[1] > 1:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.T[1]/la.norm(ica.mixing_.T[1], 2)), (ica.mean_ + .67*ica.mixing_.T[1]/la.norm(ica.mixing_.T[1], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67) 
        if ica.mixing_.shape[1] > 2:
            p0, p1 = (ica.mean_ - .67*ica.mixing_.T[2]/la.norm(ica.mixing_.T[2], 2)), (ica.mean_ + .67*ica.mixing_.T[2]/la.norm(ica.mixing_.T[2], 2)) 
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], c = 'k', linewidth=1, alpha=.67)  

        p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[0]/la.norm(ica.mixing_.dot(R.T).T[0], 2))
        a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
        ax.add_artist(a)
        if ica.mixing_.shape[1] > 1:
            p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[1]/la.norm(ica.mixing_.dot(R.T).T[1], 2)) 
            a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
            ax.add_artist(a)
        if ica.mixing_.shape[1] > 2:
            p0, p1 = ica.mean_, (ica.mean_ + .15*ica.mixing_.dot(R.T).T[2]/la.norm(ica.mixing_.dot(R.T).T[2], 2)) 
            a = Arrow3D([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], mutation_scale=20, lw=2, arrowstyle="-|>", color="b")
            ax.add_artist(a)
                
        ax.plot([0, c[best_ind[0], 0]], [0., c[best_ind[0], 1]], [0., c[best_ind[0], 2]], c = 1-c[best_ind[0]], ls='--', linewidth=2)
        if c[best_ind].shape[0] > 1:
            ax.plot([0, c[best_ind[1], 0]], [0., c[best_ind[1], 1]], [0., c[best_ind[1], 2]], c = 1-c[best_ind[1]], ls='--', linewidth=2)
        if c[best_ind].shape[0] > 2:
            ax.plot([0, c[best_ind[2], 0]], [0., c[best_ind[2], 1]], [0., c[best_ind[2], 2]], c = 1-c[best_ind[2]], ls='--', linewidth=2)

        ax.set_xlim(limits[0])
        ax.set_ylim(limits[1])
        ax.set_zlim(limits[2])
        ax.set_xlabel('C')
        ax.set_ylabel('M')
        ax.set_zlabel('Y')

        ax.view_init(elev=el, azim=az)

        ver_name = verbose+'.classifying_colours.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name

    if verbose :
        print "infos", infos
        print "check", check
        print 'conf', conf
        
        
    pigm = np.zeros_like(res[:, 0])
    if 1 in best_ind:
        pigm = res[:, 1]
        
    c_est = np.ones((len(norms), c.shape[1]))
    c_est_ = np.ones_like(c)
    c_est_[best_ind] -= best_est
    c_est[norms > 1.e-2] = c_est_
    
    return res[:, 0].reshape(img.shape[:2]), conf, pigm.reshape(img.shape[:2]), np.uint8(np.maximum(0, np.minimum(1, c_est))*255)

def compute_threshold(data, minth=.25, maxth=.67, verbose=False):
    """ 
        Compute threhold based on GMM  
        
        Parameters
        ----------
            
        data: array [N]
            Data to be used to fit GMM
        
        minth: float, optional, default: .25
            The minimum threhold value allowed
        
        maxth: float, optional, default: .67        
            The maximum threhold value allowed
        
        verbose: Bool/str, optional, default: False
            Verbosity level:
            - False: silent run
            - True: report textual information
            - Path prefix: report textual information and report graphical
                information in verbose+<suffix>.jpg files
                
        
        Returns
        -------
        
        threshold: float
            Estimated threshold
        
    """
    mu_, sig_ = data.mean(), data.std()
    if sig_ < 1.e-5:
        sig_ = 1
        
    X_ = (data - mu_)/sig_
    
    models = []
    bics = []
    
    for i in range(2):
        sn, sx = 0, 1
        resamples = []
        for _ in range(10):
            model = mixture.GMM(i+1, covariance_type='full', n_iter=500, n_init=1).fit(np.random.permutation(X_.ravel())[:max(len(X_.ravel())/100, 1000), np.newaxis])
            sn, sx = np.array(sorted(np.sqrt(model.covars_).ravel()))[[0, -1]]
            resamples += [(sn/sx, model)]
            if sn/sx > .1:
                break

        models += [sorted(resamples, key=lambda x: x[0])[-1][1]]
        bics += [model.bic(X_.ravel()[:, np.newaxis])]
        
    model = models[np.argmin(bics)]
    
    th = np.min(model.means_.ravel() + 2*np.sqrt(model.covars_).ravel())
    mus, sigs, ws = np.array(sorted(zip(model.means_.ravel(), np.sqrt(model.covars_).ravel(), model.weights_), key=lambda x: x[0])).T
    
    th = th*sig_ + mu_
    th = np.minimum(maxth, np.maximum(minth, th))
    
    if verbose:
        print "Threshold", th
    
    if type(verbose) == str:
        fig = plt.figure() 
        ax = fig.gca()
        
        ax.hist(data.ravel(), bins=50, normed=True, color='k', alpha=.25)
        xlim = ax.get_xlim() 
        
        x = np.arange(*(xlim + (.001,)))
        for i in range(model.n_components):
            ax.plot(x, model.weights_[i]*st.norm(model.means_[i].ravel()*sig_ + mu_, np.sqrt(model.covars_[i]).ravel()*sig_).pdf(x), 'b-')
        
        ylim = ax.get_ylim()
        ax.plot([th, th], list(ylim), 'g-')
        ylim = ax.get_ylim()
        ax.plot([minth, minth], list(ylim), 'r--')
        ylim = ax.get_ylim()
        ax.plot([maxth, maxth], list(ylim), 'r--')

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        ver_name = verbose+'_threshold.jpg'
        fig.savefig(ver_name)
        
        print "saving", ver_name
  

    return th

def ta_and_sb(pattern, mask, ksize=5, verbose=False):
    """
        Threhold adaptively and suppress background
        
        Parameters
        ----------
            
        pattern: array [height, width]
            Noisy pattern
        
        mask: array [height, width]
            The mask showing the embryo location. 
        
        ksize: float, optional, default: 5    
            Size of structuring element to use
        
        verbose: Bool/str, optional, default: False
            Verbosity level:
            - False: silent run
            - True: report textual information
            - Path prefix: report textual information and report graphical
                information in verbose+<suffix>.jpg files
                
        
        Returns
        -------
        
        pattern: array [height, width]
            Denoised pattern
        
    """
    th = .25
    if len(pattern[(mask == 1) & (pattern >= 0)]) > 0:    
        th = compute_threshold(pattern[(mask == 1) & (pattern >= 0)], verbose=verbose)
    
    pattern = np.maximum(0, pattern - th) 

    bgav, bgst = np.mean(pattern[mask == 0]), np.std(pattern[mask == 0])
    if bgav > 0:
        morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(round(ksize)), )*2) 
        grad = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, morph_kernel)
        
        mask = cv2.dilate(mask, morph_kernel, iterations=1) 
        
        mask2 = np.copy(mask)
        grad2 = cv2.morphologyEx(mask2, cv2.MORPH_GRADIENT, morph_kernel)
        means = [] 
        for i in range(int(round(ksize))):
            mask2 = cv2.erode(mask2, morph_kernel, iterations=1)
            grad2 = cv2.morphologyEx(mask2, cv2.MORPH_GRADIENT, morph_kernel)
            if grad2.sum() == 0:
                break
            gav, gst = np.mean(pattern[grad2 == 1]), np.std(pattern[grad2 == 1])
            if np.isnan(gav) or gav > bgav + 2*bgst:
                break
            means += [gav]
        
        if len(means) > 0:
            stop = np.argmin(means)
            if stop >= len(means) - 1:
                stop = np.argmax(means)/2
        else:
            stop = 0
        
        mask2 = np.copy(mask)
        for i in range(stop*2 + 1):
            mask2 = cv2.erode(mask2, morph_kernel, iterations=1)
            mask += mask2
        
        mask = mask / float(np.max(mask))
        
        smrounds = 3
        mask_ = np.copy(mask)
        for i in range(smrounds):
            mask_ = cv2.pyrDown(mask_)
            
        for i in range(smrounds):
            mask_ = cv2.pyrUp(mask_)
        
        mask = mask_[:mask.shape[0], :mask.shape[1]] 
        
        mask = 1/(1 + np.exp(-20*(mask - 0.5)))
        mask = mask / float(np.max(mask))
        
        pattern *= mask
        pattern = cv2.pyrDown(cv2.pyrUp(pattern))[:pattern.shape[0], :pattern.shape[1]]
    
        
    return pattern

def extract_pattern (img, mask, expected, ksize=5, verbose=False):
    """ 
        Extract the stain and pigment p[attern from the image
        
        Parameters
        ----------
            
        img: array [height, width, 3]
            The RGB image to be decomposed. Range of values 0 - 255
        
        mask: array [height, width]
            The mask showing the embryo location. 
            
        expected: [(array [3], float), (array [3], float)]
            List of pairs (RGB colour, confidence) for expected stain, 
            pigment colour respectively.
            
        ksize: float, optional, default: 5    
            Size of structuring element to use
            
        verbose: Bool/str, optional, default: False
            Verbosity level:
            - False: silent run
            - True: report textual information
            - Path prefix: report textual information and report graphical
                information in verbose+<suffix>.jpg files
                
        
        Returns
        -------
        
        strain: array [height, width]
            Stain pattern 
        
        pigment: array [height, width]
            Pigment pattern

        colours: array [3, 3]
            RGB colours estimated from the image. If a colour is not
            present it is set to white
    """

    if mask is None:
        mask = np.ones(img.shape[:2], dtype=int)

    bg = np.mean(img[mask == 0].reshape(-1, 3), axis = 0)
    expected = list(expected) + [(bg, 1.)]
    
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(round(ksize*2)), )*2) 
    pattern, conf, pigm, c_est = extract_staining(img, mask, expected=expected, verbose=verbose)
    stained = conf >= .05 and len(pattern[(mask == 1) & (pattern > 0)]) > 0
    
    ptrn = pattern.copy()
    
    if not stained:
        return np.zeros(img.shape[:2]), ta_and_sb(pigm, mask, ksize, verbose=verbose), c_est #[c for c, p in expected[:2]]

    verbose_ = np.copy(verbose)
    
    if type(verbose) == str:
        verbose_ = verbose+'.pigment'
    pigm_ = ta_and_sb(pigm, mask, ksize, verbose=verbose_)
    if type(verbose) == str:
        verbose_ = verbose+'.stain'

    return ta_and_sb(pattern, mask, ksize, verbose=verbose_), pigm_, c_est

