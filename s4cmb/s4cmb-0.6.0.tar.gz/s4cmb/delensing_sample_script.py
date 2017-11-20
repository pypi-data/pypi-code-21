"""
Sample script for lensing and delensing maps.
This delens some input maps with their Wiener filtered input potential

e.g. python ./scripts/Peloton/delensing_sample_script.py
"""
import numpy as np
import healpy as hp
import argparse
from subprocess import call
import os
import sys
import copy
from weave import inline
from weave import converters
import cPickle as pickle

import fslens as fs
from fslens.misc.lens_utils import stats

class stats_expanded(stats):
    """ Expand the class stats from fslens """
    def __init__(self, ellmax, do_cov=True):
        stats.__init__(self, ellmax, do_cov=do_cov)
        self.mat = None
        self.ells = None

    def add(self, v):
        assert (v.shape == (self.size,)), "input not understood"
        self.sum += v
        if self.do_cov:
            self.mom += np.outer(v, v)
        self.N += 1

        ## Build the matrix as well
        try:
            self.mat = np.vstack((self.mat, v))
        except:
            self.mat = v

    def auto_corr(self, lmin=2, remove_diag=False):
        '''
        Compute correlation matrix from covariance matrix.
        The code makes use of C to speed up the computation.
        Input:
        * lmin: int, minimum multipole
        * remove_diag: boolean, return the correlation matrix
            with zero on the diagonal
        Output
        * corrmat: 2D array, correlation matrix. If remove_diag is True,
            the diagonal elements are subtracted.

        '''
        # covmat = self.cov()
        mat = np.array([i[self.ells] for i in self.mat])
        X = mat - np.mean(mat, axis=0)
        covmat = np.cov(X.T)
        size = covmat.shape[0]

        corrmat = np.zeros_like(covmat)

        code = r'''
            int l1, l2;
            for(l1 = lmin; l1 < size; l1++) {
                for(l2 = lmin; l2 < size; l2++) {
                    corrmat(l1,l2) = covmat(l1,l2) / sqrt(covmat(l1,l1)*covmat(l2,l2));
                }
            }
        '''

        inline(code,
               ['covmat', 'corrmat', 'size', 'lmin'],
               headers=["<math.h>"],
               type_converters=converters.blitz)

        if remove_diag:
            toremove = np.eye(size)
            toremove[0: lmin] = 0.0
            return corrmat - toremove
        else:
            return corrmat

    def auto_corr_binned(self, lmin=2, remove_diag=False):
        '''
        Compute correlation matrix from covariance matrix.
        The code makes use of C to speed up the computation.
        Input:
        * lmin: int, minimum multipole
        * remove_diag: boolean, return the correlation matrix
            with zero on the diagonal
        Output
        * corrmat: 2D array, correlation matrix. If remove_diag is True,
            the diagonal elements are subtracted.

        '''
        # covmat = self.cov()
        # bins = binner4cov(lmin,
        #   len(self.mat[0][self.ells])-1, step=20, method='CMB')
        # mat = np.array([bins.bin_this_spec(i[self.ells]) for i in self.mat])
        bins = binner4cov(lmin, len(self.mat[0])-1, step=20, method='CMB')
        mat = np.array([bins.bin_this_spec(i) for i in self.mat])
        X = mat - np.mean(mat, axis=0)
        covmat = np.cov(X.T)
        size = covmat.shape[0]

        corrmat = np.zeros_like(covmat)

        code = r'''
            int l1, l2;
            for(l1 = lmin; l1 < size; l1++) {
                for(l2 = lmin; l2 < size; l2++) {
                    corrmat(l1,l2) = covmat(l1,l2) / sqrt(covmat(l1,l1)*covmat(l2,l2));
                }
            }
        '''

        inline(code,
               ['covmat', 'corrmat', 'size', 'lmin'],
               headers=["<math.h>"],
               type_converters=converters.blitz)

        if remove_diag:
            return corrmat - np.eye(size)
        else:
            return corrmat

    def cross_corr(self, cov12, cov1, cov2, lmin=2):
        '''
        Compute cross-correlation matrix from cross-covariance
        matrix between 1 and 2.
        The self.data vector should contains the covmat(1,2).
        The code makes use of C to speed up the computation.
        Input:
        * lmin: int, minimum multipole
        * vec1: 1D array, the gaussian variance of 1
        * vec2: 1D array, the gaussian variance of 2
        Output
        * corrmat: 2D array, cross-correlation matrix.

        '''
        size = cov12.shape[0]

        corrmat = np.zeros_like(cov12)
        vec1 = np.diag(cov1)
        vec2 = np.diag(cov2)

        code = r'''
            int l1,l2;
            for(l1 = lmin; l1 < size; l1++) {
                for(l2 = lmin; l2 < size; l2++) {
                    corrmat(l1,l2) = cov12(l1,l2) / sqrt(vec1(l1)*vec2(l2));
                }
            }
        '''

        inline(code,
               ['cov12', 'corrmat', 'vec1', 'vec2', 'size', 'lmin'],
               headers=["<math.h>"],
               type_converters=converters.blitz)

        return corrmat

    def compute_covmat_cross(self,other):
        '''
        Cross-covariance for sims.
        Input:
        * lensingvec: 2D-array, contains the sims of
            the lensing potential [N_sims , N_bins]
        * CMBvec: 2D-array, contains the sims of the
            lensed CMB [N_sims , N_bins]
        Output:
        * covmat: 2D-array, cross-covariance matrix
        '''
        assert self.mat.shape[0] == other.shape[0], \
            'Not the same number of sims!'
        mat = self.mat
        nsims = self.mat.shape[0]
        size = self.mat.shape[1]
        size_other = other.shape[1]

        mean = np.mean(self.mat, axis=0)
        mean_other = np.mean(other, axis=0)
        covmat_cross = np.zeros((size_other, size))

        code = r'''
            int s,i,j;
            for(s = 0; s < nsims; s++) {
                for(i = 0; i < size_other; i++) {
                    for(j = 0; j < size; j++) {
                        covmat_cross(i,j) = covmat_cross(i,j) + (other(s,i) - mean_other(i))*(mat(s,j) - mean(j));
                    }
                }
            }
        '''

        inline(code,
               ['covmat_cross', 'other', 'mean_other', 'mat',
                'mean', 'nsims', 'size_other', 'size'],
               headers=["<math.h>"],
               type_converters=converters.blitz)

        return covmat_cross / (nsims-1)

class sky_maps(object):
    """ Class to handle sky maps """
    def __init__(self, npix, reso):
        """
        Initialization
        Input
         * npix: int, number of pixels for the flat map
         * reso: float, pixel size in arcmin
        """
        ## Flat map parameters
        self.npix = npix
        self.reso = reso

        self.T, self.Q, self.U = self.create_sky_maps()

    def create_sky_maps(self):
        return [np.zeros((self.npix, self.npix)) for m in range(3)]

    def return_maps(self):
        return [self.T, self.Q, self.U]

    def copy(self):
        """ clone this object.
        Input
         * lmax: int, restrict copy to L<=lmax.
         * lmin: int, set spectra in copy to zero for L<lmin.
        Output
         * ret: camb_clfile object, the copy
        """
        ret = copy.deepcopy(self)
        for k, v in self.__dict__.items():
            setattr(ret, k, copy.deepcopy(v))
        return ret

    def plot(self, component, path_out):
        """
        Plot maps
        """
        import pylab as pl
        pl.clf()
        fig, ax = pl.subplots(1, 3)
        ax[0].imshow(self.T, vmin=-100, vmax=100)
        ax[1].imshow(self.Q, vmin=-10, vmax=10)
        ax[2].imshow(self.U, vmin=-10, vmax=10)
        pl.savefig(os.path.join(path_out, 'map_%s.pdf' % component))
        pl.clf()

    def __add__(self, other):
        """
        Sum two sky maps
        Input
        * other: sky_maps object, the maps that you want to add
        """
        if is_sky_maps(other):
            assert(self.npix == other.npix)
            ret = self.copy()
            zs = np.zeros((self.npix, self.npix))
            for attr in ['T', 'Q', 'U']:
                if (hasattr(self, attr) or hasattr(other, attr)):
                    setattr(ret, attr,
                            getattr(self, attr, zs) + getattr(other, attr, zs))
            return ret
        else:
            assert(0)

def is_sky_maps(object):
        """ check (by ducktyping) if object is a sky_maps """
        if not hasattr(object, 'npix'):
            return False
        if not hasattr(object, 'reso'):
            return False
        return set(object.__dict__.keys()).issubset(
            set(['npix', 'reso', 'T', 'Q', 'U']))

class foregrounds(object):
    """ Class to handle foregrounds """
    def __init__(self, nsims, rot, npix, reso,
                 path_to_data='temp/foreground_maps'):
        """
        Initialization
        Input
         * nsims: int, number of realizations for each
         * rot: array of float, center of the patch ([Ra, Dec] in deg)
         * npix: int, number of pixels for the flat map
         * reso: float, pixel size in arcmin
         * path_to_data (opt): where data will be read/saved
        """
        self.nsims = nsims

        ## Flat map parameters
        self.rot = rot
        self.npix = npix
        self.reso = reso

        ## If the folder exists, files will be read from it,
        ## otherwise it is created and files will be stored there.
        self.path_to_data = path_to_data

        try:
            os.makedirs(path_to_data)
            print 'Simulating foregrounds on-the-fly...'
        except:
            print 'Reading foreground maps from %s' % path_to_data

    def dust(self, idx):
        """
        Module for dust
        """
        smaps = sky_maps(self.npix, self.reso)

        fn_base = os.path.join(self.path_to_data, 'dust_%d.fits' % idx)
        if os.path.isfile(fn_base):
            smaps.T, smaps.Q, smaps.U = hp.read_map(fn_base, (0, 1, 2))
        else:
            ## Put here call to PySM
            ## save data
            pass

        ## From Healpix to flat
        smaps.T, smaps.Q, smaps.U = self.curve2flat(
            idx, maps=[smaps.T, smaps.Q, smaps.U])

        return smaps

    def synchrotron(self, idx):
        """
        Module for synchrotron
        """
        smaps = sky_maps(self.npix, self.reso)

        fn_base = os.path.join(self.path_to_data, 'synchrotron_%d.fits' % idx)
        if os.path.isfile(fn_base):
            smaps.T, smaps.Q, smaps.U = hp.read_map(fn_base, (0, 1, 2))
        else:
            ## Put here call to PySM
            ## save data
            pass

        ## From Helapix to flat
        smaps.T, smaps.Q, smaps.U = self.curve2flat(
            idx, maps=[smaps.T, smaps.Q, smaps.U])

        return smaps

    def curve2flat(self, idx, maps):
        """
        Convert from curve sky (Healpix) to flat sky.
        Inputs:
        * idx: int, number of the simulation
        * maps: list of array(s), the maps you want to convert
        """
        out = [hp.gnomview(m,
                           rot=self.rot,
                           reso=self.reso,
                           xsize=self.npix,
                           return_projected_map=True) for m in maps]
        pl.clf()
        return out

class lensed_CMB(object):
    """ Class to handle CMB """
    def __init__(self, nsims, HDres, LDres, reso, exp):
        """
        Initialization
        Input
         * nsims: int, number of realizations for each
         * npix: int, number of pixels for the flat map
         * reso: float, pixel size in arcmin
         * path_to_data (opt): where data will be read/saved
        """
        self.nsims = nsims
        self.HDres = HDres
        self.LDres = LDres
        self.exp = exp
        self.reso = reso

        self.npix = 2**LDres

        self.sim_lib = fs.get_120maps_lib(exp,
                                          LDres,
                                          HDres=HDres,
                                          cache_maps=True,
                                          cache_lenalms=True,
                                          nsims=nsims)

    def cmb(self, idx):
        """
            Return sky_maps object containing lensed simulated T, Q, U maps
        """
        smaps = sky_maps(self.npix, self.reso)

        ## T * Bl + Nl
        smaps.T = self.sim_lib.get_sim_tmap(idx)

        ## Q * Bl + Nl, U * Bl + Nl
        smaps.Q, smaps.U = self.sim_lib.get_sim_qumap(idx)

        # smaps.Q = smaps.Q + smaps.T * 0.01
        # smaps.U = smaps.U + smaps.T * 0.01
        # smaps.T = smaps.T + smaps.T * 0.01

        return smaps

class powerspectra(object):
    """ """
    def __init__(self, lib_qlm, components):
        """
        """
        self.components = components
        self.lib_qlm = lib_qlm
        self.ells = None

        self.delensed = {i: self.create_full_dic() for i in components}
        self.lensed = {i: self.create_full_dic() for i in components}
        self.potential = {i: self.create_lensing_dic() for i in components}

    def create_full_dic(self):
        dic = {}
        dic['tt'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        dic['te'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        dic['ee'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        dic['bb'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        return dic

    def create_lensing_dic(self):
        dic = {}
        dic['pp'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        dic['N0'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        dic['RDN0'] = stats_expanded(self.lib_qlm.ellmax + 1, do_cov=True)
        return dic

def addargs(parser):
    ''' Parse command line arguments '''
    parser.add_argument('-exp', dest='exp', default='Planck', type=str,
                        help='expr. settings')
    parser.add_argument('-LD', dest='LDres', default=11, type=int,
                        help='coarse data resolution ')
    parser.add_argument('-HD', dest='HDres', default=12, type=int,
                        help='high resolution (put 14 for full sky)')
    parser.add_argument('-nsims', dest='nsims', default=1, type=int,
                        help='number of sims to delens')
    parser.add_argument('--reconstruct_lensing', dest='reconstruct_lensing',
                        action='store_true',
                        help='Reconstruct lensing potential')
    parser.add_argument('--do_delensing', dest='do_delensing',
                        action='store_true',
                        help='Delens CMB power-spectra')
    parser.add_argument('-rot', dest='rot', default=[0.0, -57.5],
                        type=float, nargs=2,
                        help='Center of the patch in deg [ra, dec]')
    parser.add_argument('-map_in', dest='map_in', default='',
                        type=str, help='CMB maps to analyse')
    parser.add_argument('-path_out', dest='path_out', default='temp/out',
                        type=str, help='folder to store outputs')
    parser.add_argument('-components', dest='components',
                        help='cmb, dust, synch, ... Should be in the format comp1_comp2_etc',
                        type=str, default='cmb_dust')
    parser.add_argument('-fig', dest='figname', default='./delens.pdf',
                        type=str, help='output figure name')

def grabargs(args_param=None):
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser(description='delensing script')
    addargs(parser)
    args = parser.parse_args(args_param)
    return args

def get_datTQUlms(cov, maps, idx, nobeam_deconv=False):
    """
    Spin 0 TQU data alms of sim idx, beam deconvolved
    """
    if not nobeam_deconv:
        return np.array([
            cov.lib_datalm.almxfl(
                cov.lib_datalm.map2alm(_m), 1./cov.cl_transf) for _m in maps])
    else:
        return np.array([
            cov.lib_datalm.almxfl(cov.lib_datalm.map2alm(_m),
                                  np.ones_like(cov.cl_transf)) for _m in maps])

def get_filtered_datTQUlms(cov, maps, idx, nobeam_deconv=False):
    """
    Put here you custom filtering of the map prior delensing
    """
    # Now simple cuts according to exp config.
    return get_datTQUlms(cov, maps, idx, nobeam_deconv=nobeam_deconv)

def get_plm(cov, lib_qlm, sim_lib, idx):
    """
    Put here your deflection field to delensing with
    """
    # Now (-1) Wiener filter input of MV estimator
    Cpp = cov.cls_unl['pp'][:lib_qlm.ellmax + 1]
    N0 = cov.get_N0cls('TQU', lib_qlm)[0][:lib_qlm.ellmax + 1]
    clWF = Cpp.copy()
    clWF[np.where((N0 + Cpp) > 0)] /= (N0 + Cpp)[np.where((N0 + Cpp) > 0)]
    return lib_qlm.almxfl(
        lib_qlm.udgrade(sim_lib.lencmbs.lib_skyalm,
                        sim_lib.lencmbs.get_sim_plm(idx)), -clWF)

def get_delensTQUlms(cov, lib_qlm, sim_lib, maps, idx, nobeam_deconv=False):
    """
    Outputs the delensed TQU alms
    """
    # Get displacement instance from potential alms
    f = fs.displacements.displacement_fromplm(
        cov.lib_skyalm,
        cov.lib_skyalm.udgrade(lib_qlm,
                               get_plm(cov, lib_qlm, sim_lib, idx)))

    # Delens the maps (Here at resolution set by HDres,
    ## not necessarily necessary)
    return np.array([
        f.lens_alm(cov.lib_skyalm,
                   cov.lib_skyalm.udgrade(
                       cov.lib_datalm,
                       _alm)) for _alm in get_filtered_datTQUlms(
                           cov, maps, idx, nobeam_deconv=nobeam_deconv)])

def reconstruct_pp(cov, lib_qlm, maps, idx, cls_obs, getRDN0=True):
    """
    """
    Rpp, ROO = cov.get_qlm_resprlm('TQU', lib_qlm)
    iblms = cov.get_iblms('TQU',
                          get_datTQUlms(cov, maps, idx, nobeam_deconv=True))
    plm, Olm = cov.get_qlms('TQU', iblms[0], lib_qlm)
    plm *= Rpp

    if idx == 0:
        N0 = 2 * lib_qlm.alm2cl(np.sqrt(Rpp))[: lib_qlm.ellmax + 1]
    else:
        N0 = np.zeros(lib_qlm.ellmax + 1)

    # Compute Semi-analytical N0
    # cls_obs to be defined like cls_len but
    # containing non-interp observed spectra.
    if getRDN0:
        for flavor in ['tt', 'ee', 'bb', 'te']:
            cls_obs[flavor][0: 2] = 0.0

        Rpp_RDN0, ROO_RDN0 = cov.get_qlm_resprlm('TQU', lib_qlm,
                                                 use_cls_len=True,
                                                 cls_obs=cls_obs)
        RDN0_ = Rpp**2 / Rpp_RDN0
        RDN0 = 2. * lib_qlm.alm2cl(np.sqrt(RDN0_))[: lib_qlm.ellmax + 1]
        print N0, RDN0

        return lib_qlm.alm2cl(plm)[: lib_qlm.ellmax + 1], N0, RDN0

    else:
        return lib_qlm.alm2cl(plm)[: lib_qlm.ellmax + 1]

def pickle_save(d, fn):
    '''
    Save data d into fn (.pkl) file
    Input:
    * d: dictionary, the data to be saved.
    * fn: string, the name of the file where data will be stored.
    '''
    with open(fn, 'wb') as f:
        pickle.dump(d, f, protocol=2)

def pickle_load(fn):
    '''
    Load fn (.pkl) file
    Input:
    * fn: string, the name of the file (.pkl) containing data
    '''
    with open(fn, 'rb') as f:
        x = pickle.load(f)
    return x

def write_on_disk(path_out, obj, name, potential=False):
    dic = {}
    components = obj.keys()
    for component in components:
        if potential:
            keys = obj[component].keys()
            for k in keys:
                dic[k] = obj[component][k].mat
            dic['ells'] = obj[component][k].ells
            dic['N'] = obj[component][k].N
        else:
            keys = obj[component].keys()
            for k in keys:
                dic[k] = obj[component][k].mat
            dic['ells'] = obj[component][k].ells
            dic['N'] = obj[component][k].N
        pickle_save(dic,
                    os.path.join(path_out,
                                 'results_%s_%s.pkl' % (name, component)))

def main():
    args_param = None
    args = grabargs(args_param)

    ## Init the out folder
    try:
        os.makedirs(args.path_out)
    except:
        pass

    ## Sky components
    components = [c for c in args.components.split('_')]
    if len(components) > 1:
        components.append(args.components)
    ncomponents = len(components)

    ## Map parameters
    # TODO make uniform reso and npix (step back from routines in __init__)
    npix = 2**args.LDres
    reso = hp.nside2resol(2048, arcmin=True)

    ## isocov is for the phi reconstruction, cov is for the delensing
    isocov = fs.get_isocov(args.exp,
                           args.LDres,
                           HD_res=args.HDres,
                           pyFFTWthreads=8)
    cov = fs.get_lencov(args.exp,
                        args.LDres,
                        HD_res=args.HDres,
                        pyFFTWthreads=8)

    # Change this for custom multipole range for the potential
    # TODO Understand how twicking that
    lib_qlm = cov.lib_datalm
    lib_qlm_iso = isocov.lib_datalm

    ## Data (input maps and output spectra)
    # TODO Link to PySM directly
    lensed_CMB_maps_data = lensed_CMB(args.nsims,
                                      args.HDres,
                                      args.LDres,
                                      reso, args.exp)
    # foreground_maps_data = foregrounds(args.nsims,
    #                                    args.rot,
    #                                    npix, reso,
    #                                    path_to_data='temp/foreground_maps')
    powerspectra_data = powerspectra(lib_qlm, components)

    # collecting lensed and delensed spectra
    # for pos,idx in enumerate(np.arange(args.nsims)[rank::size]):
    for idx in np.arange(args.nsims):
        for component in components:

            ## Collect maps
            smaps = sky_maps(npix, reso)
            if len(args.map_in) == 0:
                if len(component.split('_')) == 1:
                    print '+---------------------------------+'
                    print 'single component - %s (%d/%d)' % (component,
                                                             idx, args.nsims)
                    print '+---------------------------------+'
                    if component == 'cmb':
                        smaps += getattr(lensed_CMB_maps_data, component)(idx)
                    else:
                        smaps += getattr(foreground_maps_data, component)(idx)

                else:
                    print '+---------------------------------+'
                    print 'multi components - %s (%d/%d)' % (component,
                                                             idx, args.nsims)
                    print '+---------------------------------+'
                    for c in component.split('_'):
                        if c == 'cmb':
                            smaps += getattr(lensed_CMB_maps_data, c)(idx)
                        else:
                            smaps += getattr(foreground_maps_data, c)(idx)
                w2 = 1.0
                w4 = 1.0
            else:
                ## Plot in case you want to see maps
                # smaps.plot(component,args.path_out)
                data = np.load(args.map_in.format(idx))
                npix = int(len(data['I'])**.5)
                smaps.T = data['I'].reshape((npix, npix)) * data['wI'].reshape((npix, npix)) / np.max(data['wI'])
                smaps.Q = data['Q'].reshape((npix, npix)) * data['wP'].reshape((npix, npix)) / np.max(data['wP'])
                smaps.U = data['U'].reshape((npix, npix)) * data['wP'].reshape((npix, npix)) / np.max(data['wP'])
                print "Need to multiply by pixsize!"
                w2 = np.sum(data['wP']**2)/np.max(data['wP'])**2 / npix**2
                w4 = np.sum(data['wP']**4)/np.max(data['wP'])**4 / npix**2
                print w2, w4

            ## lensed T, E, B alms
            TEBlen = fs.spectralmatrices.TQU2TEBlms(
                'TQU', cov.lib_datalm, get_datTQUlms(
                    cov, smaps.return_maps(), idx))
            if args.do_delensing:
                TEBdel = fs.spectralmatrices.TQU2TEBlms(
                    'TQU', cov.lib_skyalm, get_delensTQUlms(
                        cov, lib_qlm,
                        lensed_CMB_maps_data.sim_lib,
                        smaps.return_maps(), idx))

            ## Lensed CMB power-spectra and delensing
            cl_obs = {}
            for kspec in ['tt', 'ee', 'te', 'bb']:
                id0 = {'t': 0, 'e': 1, 'b': 2}[kspec[0]]
                id1 = {'t': 0, 'e': 1, 'b': 2}[kspec[1]]

                cl_lensed = cov.lib_datalm.alm2cl(
                    TEBlen[id0], alm2=TEBlen[id1])[:lib_qlm.ellmax + 1]
                cl_obs[kspec] = cl_lensed / w2
                powerspectra_data.lensed[component][kspec].add(cl_lensed / w2)
                if args.do_delensing:
                    cl_delensed = cov.lib_skyalm.alm2cl(
                        TEBdel[id0], alm2=TEBdel[id1])[:lib_qlm.ellmax + 1]
                    powerspectra_data.delensed[component][kspec].add(
                        cl_delensed / w2)
                if idx == 0:
                    if kspec == 'tt':
                        ells = np.where(cl_lensed > 0)[0]
                    powerspectra_data.lensed[component][kspec].ells = ells
                    if args.do_delensing:
                        powerspectra_data.delensed[component][kspec].ells = ells

            ## Lensing reconstruction (actually not required for the delensing)
            if args.reconstruct_lensing:
                cl_pp, N0x, RDN0 = reconstruct_pp(
                    isocov, lib_qlm_iso,
                    smaps.return_maps(), idx,
                    cl_obs, getRDN0=True)
                if idx == 0:
                    N0 = N0x
                else:
                    pass
                powerspectra_data.potential[component]['pp'].add(cl_pp / w4)
                powerspectra_data.potential[component]['N0'].add(N0)
                powerspectra_data.potential[component]['RDN0'].add(RDN0)
                # import pylab as pl
                # w = lambda ell: (ell * (ell + 1))**2 / 2. / np.pi
                # pl.plot(ells, cl_pp[ells] / w4 * w(ells))
                # pl.plot(ells, N0[ells] / w4 * w(ells))
                # pl.plot(ells, RDN0[ells] / w4 * w(ells))
                # pl.savefig('toto.png')
                # pl.yscale('log')
                # pl.show()
                if idx == 0:
                    powerspectra_data.potential[component]['pp'].ells = ells
                    powerspectra_data.potential[component]['N0'].ells = ells
                    powerspectra_data.potential[component]['RDN0'].ells = ells

        if idx % 10 == 0:
            ## Save intermediate results
            # TODO write proper pkl files.
            write_on_disk(args.path_out,
                          powerspectra_data.lensed, 'lensed')
            if args.do_delensing:
                write_on_disk(args.path_out,
                              powerspectra_data.delensed, 'delensed')
            if args.reconstruct_lensing:
                write_on_disk(args.path_out,
                              powerspectra_data.potential,
                              'potential', potential=True)

    ## Save final results
    # TODO write proper pkl files.
    write_on_disk(args.path_out,
                  powerspectra_data.lensed, 'lensed')
    if args.do_delensing:
        write_on_disk(args.path_out,
                      powerspectra_data.delensed, 'delensed')
    if args.reconstruct_lensing:
        write_on_disk(args.path_out,
                      powerspectra_data.potential, 'potential', potential=True)


if __name__ == "__main__":
    main()
