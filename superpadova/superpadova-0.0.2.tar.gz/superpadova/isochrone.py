# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 21:57:16 2017

@author: cham

Aim: wrap astropy.table.Table as Isochrone class

"""

import numpy as np
from astropy.table import Table, vstack
from scipy.interpolate import Rbf
from tqdm import tqdm


class Isochrone(Table):

    interp_xks = ("M_ini", "logageyr", "feh")
    interp_yks = ("logTe", "logG", "feh")
    interp_xdim = 3
    interp_ydim = 3
    interp_eps = (0.3, 0.2, 0.2)
    interp_function = "linear"
    interp_kwargs = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        if np.max(self['Z']) == np.min(self['Z']):
            s_z = "Z={:.7f}([M/H]={:.2f})".format(
                self['Z'][0], np.log10(self['Z'][0]/0.0152))
            c_z = 1
        else:
            s_z = "Z=[{:.7f}, {:.7f}]([M/H]=[{:.2f}, {:.2f}])".format(
                np.min(self['Z']), np.max(self['Z']),
                np.log10(np.min(self['Z']) / 0.0152),
                np.log10(np.max(self['Z']) / 0.0152))
            c_z = len(np.unique(self['Z']))

        if np.max(self['logageyr']) == np.min(self['logageyr']):
            s_t = "logt={:.2f}".format(self['logageyr'][0])
            c_t = 1
        else:
            s_t = "logt=[{:.2f}, {:.2f}]".format(
                np.min(self['logageyr']), np.max(self['logageyr']))
            c_t = len(np.unique(self['logageyr']))

        s_m = "Minit=[{:.3f}, {:.3f}]".format(
            np.min(self['M_ini']), np.max(self['M_ini']))
        s_l = "length={}".format(len(self))

        # grid?
        if c_z * c_t > 1:
            s_grid = " Grid: ({:d} Z x {:d} logt)".format(c_z, c_t)
        else:
            s_grid = ""

        s = "<Isochrone{} {} {} {} {}>".format(s_grid, s_z, s_t, s_m, s_l)

        return s

    @staticmethod
    def join(isoc_list):

        # assert all isochrone tables have the same colnames
        colnames = isoc_list[0].colnames
        for i in range(len(isoc_list)):
            try:
                assert isoc_list[i].colnames == colnames
            except AssertionError as ae:
                print("Isochrone[0].colnames = ", colnames)
                print("Isochrone[{}].colnames = ", isoc_list[i].colnames)
                raise(ae)

        # try to join all isochrone tables
        return vstack([Isochrone(_) for _ in isoc_list])

    def interp_set(self, xks=("M_ini", "logageyr", "feh"),
                   yks=("logTe", "logG", "feh"), eps=(0.3, 0.2, 0.2),
                   function="linear", **kwargs):
        """ set the interpolation parameters

        :param xks:
            X coordinate keys
        :param yks:
            Y coordinate keys
        :param eps:
            the neighboring box
        :param function:
            interpolation function, conf scipy.interpolate.Rbf
        :param kwargs:
            will be passed to scipy.interpolate.Rbf
        """

        self.interp_xks = xks
        self.interp_yks = yks
        self.interp_eps = eps
        self.interp_function = function
        self.interp_kwargs = kwargs

        self.interp_xdim = len(xks)
        self.interp_ydim = len(yks)

        return

    def interp(self, Xs):
        try:
            assert Xs.ndim == 2
        except AssertionError as ae:
            print("@Cham: the dimension of input X must be 2!")
            raise(ae)

        result = []
        for i in tqdm(range(Xs.shape[0])):
            X = Xs[i]
            result.append(self.interp_one(X))

        return np.array(result)

    def interp_one(self, X):
        """ interpolate isochrone using scipy.interpolate.Rbf

        :param xs:
            X coordinates of the interpolated position, shape: (ndim,)

        :return:

        """
        try:
            assert X.ndim == 1
        except AssertionError as ae:
            print("@Cham: the dimension of input X must be 1!")
            raise (ae)

        try:
            X_upper = X + self.interp_eps
            X_lower = X - self.interp_eps

            ind = np.ones((len(self),), dtype=bool)
            for ixdim in range(self.interp_xdim):
                ind &= (self[self.interp_xks[ixdim]].data < X_upper[ixdim])
                ind &= (self[self.interp_xks[ixdim]].data >= X_lower[ixdim])

            X_nb = np.array(self[self.interp_xks][ind].to_pandas())
            Y_nb = np.array(self[self.interp_yks][ind].to_pandas())

            # if neighbors too few, return nan
            if X_nb.shape[0] < self.interp_xdim:
                print("\nWarning: for X = ", X, "returned nan, REASON: too few neighbors")
                return np.ones((self.interp_ydim,), dtype=float)*np.nan

            result = list()
            # interpolate necessary columns
            for iyk, yk in enumerate(self.interp_yks):
                if yk in self.interp_xks:
                    # Y key in X keys, directly return it
                    # print("{} is found in XKS".format(yk),
                    #       np.where(np.array(self.interp_xks) == yk)[0])
                    result.append(X[np.where(np.array(self.interp_xks) == yk)[0]])
                else:
                    # interpolate it
                    # print(X_nb.shape, Y_nb.shape)
                    rbfi = Rbf(*X_nb.T, Y_nb[:, iyk],
                               function=self.interp_function, **self.interp_kwargs)
                    result.append(rbfi(*X))
        except Exception as ee:
            print("\nWarning: for X = ", X, "returned nan, REASON: not sure...")
            result = np.ones((self.interp_ydim,), dtype=float)*np.nan

        return np.array(result)

    def interp_test(self, nstep=10):
        result = self.interp(
            np.array(self[self.interp_xks][::nstep].to_pandas()))
        return result













