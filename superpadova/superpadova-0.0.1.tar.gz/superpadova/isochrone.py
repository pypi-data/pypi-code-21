# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 21:57:16 2017

@author: cham

Aim: wrap astropy.table.Table as Isochrone class

"""

import numpy as np
from astropy.table import Table, vstack


class Isochrone(Table):

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

