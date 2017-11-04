#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 19:39:21 2017

@author: pydemia
"""


import os
import scipy as sp
import numpy as np
from pandas import DataFrame as df
from datetime import datetime as dt
import itertools as it
import random
import string
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from skimage import draw

from pydemia.math.Geometry import Ellipse


class wafer:
    # Create lotData DataFrame
    def __init__(self, fac_id=None, lot_cd=None, end_tm=None, size=None,
                 unit_cnt=25, f_type='line', p=[.8, .2], pattern=['G', 'B']):

        assert len(size) == 2
        assert len(pattern) == len(p)
        assert sum(p) == 1
        assert isinstance(unit_cnt, int)
        self.fac_id = fac_id
        self.lot_cd = lot_cd
        self.end_tm = end_tm
        self.size = size
        self.unit_cnt = unit_cnt
        self.failrate = p[0]

    def __new__(cls, fac_id=None, lot_cd=None, end_tm=None, size=None,
                unit_cnt=25, f_type='line', p=[.8, .2], pattern=['G', 'B']):

        coords = Ellipse(size).coordinates()

        # xsize, ysize = coords.xcoord.max(), coords.ycoord.max()
        lotDataKey = ['fac_id', 'lot_cd', 'lot_id', 'unit_id',
                      'end_dt', 'end_tm', 'xcoord', 'ycoord', 'val']
        lotData = df(columns=lotDataKey,
                     index=range(0, coords.shape[0] * unit_cnt))

        # Import values to each Field

        # - fab_id, lot_cd
        lotData.fac_id, lotData.lot_cd = fac_id, lot_cd

        # -  alias_lot_id
        id1 = ''.join([random.choice(string.ascii_uppercase +
                                     string.digits) for n in range(1)])
        id2 = ''.join([random.choice(string.digits) for n in range(3)])
        lotData.lot_id = lot_cd + id1 + id2

        # -  wf_id
        unitIter = [list(it.repeat(num, len(coords))) for num in
                    range(1, unit_cnt + 1)]
        lotData.unit_id = list(it.chain.from_iterable(unitIter))
        lotData.unit_id = lotData.unit_id.astype(str).str.zfill(2)

        # -  end_tm, end_dt
        lotData.end_tm = dt.strptime(end_tm, '%Y%m%d%H%M%S')
        lotData.end_dt = lotData.end_tm.map(lambda x: x.date())

        # -  x_coordinate, y_coordinate
        lotData.xcoord = list(coords.xcoord) * unit_cnt
        lotData.ycoord = list(coords.ycoord) * unit_cnt

        # Fail Type Drawing
        lotFailList = []
        for num in range(unit_cnt):

            # f_type = 'Line'
            if f_type == 'line':

                # -  res_val : pattern
                xcoord_range = range(min(coords.xcoord), max(coords.xcoord))
                ycoord_range = range(min(coords.ycoord), max(coords.ycoord))

                dist = 0
                while dist <= 10:
                    adot_x = np.random.choice(xcoord_range)
                    adot_y = np.random.choice(ycoord_range)
                    bdot_x = np.random.choice(xcoord_range)
                    bdot_y = np.random.choice(ycoord_range)

                    adot = adot_x, adot_y
                    bdot = bdot_x, bdot_y
                    dist = pdist([adot, bdot])[0]

                rr, cc = draw.line(adot_x, adot_y, bdot_x, bdot_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                pattFail = [pattern[1] if (x, y) in patt_coord else pattern[0] for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * p[1] - pattFail.count(pattern[1])
                new_fail_per = new_fail_num / pattFail.count(pattern[0])
                adjusted_per = 1 - new_fail_per, new_fail_per

                wfFailList = [np.random.choice(pattern, p=adjusted_per) if patt == pattern[0] else patt for patt in
                              pattFail]

                lotFailList += wfFailList

            elif f_type == 'bold_line':

                # -  res_val : pattern
                xcoord_range = range(min(coords.xcoord), max(coords.xcoord))
                ycoord_range = range(min(coords.ycoord), max(coords.ycoord))

                dist = 0
                while dist <= 10:
                    adot_x = np.random.choice(xcoord_range)
                    adot_y = np.random.choice(ycoord_range)
                    bdot_x = np.random.choice(xcoord_range)
                    bdot_y = np.random.choice(ycoord_range)

                    adot = adot_x, adot_y
                    bdot = bdot_x, bdot_y
                    dist = pdist([adot, bdot])[0]

                rr, cc, val = draw.line_aa(adot_x, adot_y, bdot_x, bdot_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                pattFail = [pattern[1] if (x, y) in patt_coord else pattern[0] for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * p[1] - pattFail.count(pattern[1])
                new_fail_per = new_fail_num / pattFail.count(pattern[0])
                adjusted_per = 1 - new_fail_per, new_fail_per

                wfFailList = [np.random.choice(pattern, p=adjusted_per) if patt == pattern[0] else patt for patt in
                              pattFail]

                lotFailList += wfFailList

            else:
                pass

        lotData.val = lotFailList

        # Print a message in console
        msg = 'LOT_ID : ' + lot_cd + id1 + id2

        print('-' * len(msg))
        print(msg)
        print('-' * len(msg))
        return lotData

    # lotData Visualization
    def unitplot(data, columns=['xcoord', 'ycoord'], lot_id='', unit_id=None,
                 val='val', figsize=(12, 9), pattern=['B'], m=['s'],
                 s=[100], c=['red'], a=[.5], shown='y'):

        assert len(figsize) == 2
        assert len(columns) == 2
        assert isinstance(lot_id, str)
        assert len(pattern) == len(m) == len(s) == len(c) == len(a)

        # Check if there is a given Wafer ID
        if unit_id is not None:
            pltData = data.loc[data.unit_id == unit_id,
                               [columns[0], columns[1], val]]
        else:
            pltData = data.loc[:, [columns[0], columns[1], val]]
            unit_id = ''

            # Decide if the plot is shown
        #        if shown == 'y':
        #            matplotlib.use('Agg')
        #            plt.ion()
        #
        #        elif shown == 'n':
        #            # Turn interactive plotting off
        #            matplotlib.use('Agg')
        #            plt.ioff()

        canvas = {'pattern': '+', 's': 1000, 'c': 'grey', 'a': .2}

        # Draw plot
        fig = plt.figure(figsize=figsize)
        plt.scatter(pltData.xcoord, pltData.ycoord,
                    marker=canvas['pattern'], s=canvas['s'], c=canvas['c'],
                    alpha=canvas['a'])

        for idx in range(0, len(pattern)):
            plt.scatter(pltData.loc[pltData.val == pattern[idx], 'xcoord'],
                        pltData.loc[pltData.val == pattern[idx], 'ycoord'],
                        marker=m[idx], s=s[idx], c=c[idx], alpha=a[idx])

        fig.suptitle(str(lot_id + unit_id))
        # fig.tight_layout()

        if shown == 'n':
            plt.close(fig)

        return fig


class displaypanel(wafer):
    # Create lotData DataFrame
    def __init__(self, fac_id=None, lot_cd=None, end_tm=None, size=None,
                 unit_cnt=25, pattern=['G', 'B'], p=[.8, .2]):
        assert len(size) == 2
        assert len(pattern) == len(p)
        assert sum(p) == 1
        assert isinstance(unit_cnt, int)

        self.fac_id = fac_id
        self.lot_cd = lot_cd
        self.end_tm = end_tm
        self.size = size
        self.unit_cnt = unit_cnt
        self.failrate = p[0]

    def __new__(cls, fac_id=None, lot_cd=None, end_tm=None, size=None,
                unit_cnt=25, pattern=['G', 'B'], p=[.8, .2]):
        xsize, ysize = size
        lotDataKey = ['fac_id', 'lot_cd', 'lot_id', 'unit_id',
                      'end_dt', 'end_tm', 'xcoord', 'ycoord', 'val']

        lotData = df(columns=lotDataKey,
                     index=range(0, xsize * ysize * unit_cnt))

        # Import values to each Field

        # -  fab_id, lot_cd
        lotData.fac_id, lotData.lot_cd = fac_id, lot_cd

        # -  alias_lot_id
        id1 = ''.join([random.choice(string.ascii_uppercase +
                                     string.digits) for n in range(1)])
        id2 = ''.join([random.choice(string.digits) for n in range(3)])
        lotData.lot_id = lot_cd + id1 + id2

        # -  pn_id
        unitIter = [list(it.repeat(num, xsize * ysize)) for num
                    in range(1, unit_cnt + 1)]
        lotData.unit_id = list(it.chain.from_iterable(unitIter))
        lotData.unit_id = lotData.unit_id.astype(str).str.zfill(2)

        # -  end_tm, end_dt
        lotData.end_tm = dt.strptime(end_tm, '%Y%m%d%H%M%S')
        lotData.end_dt = lotData.end_tm.map(lambda x: x.date())

        # -  x_coordinate, y_coordinate
        coords = tuple(it.product(list(range(1, xsize + 1)),
                                  list(range(1, ysize + 1))))
        lotData.xcoord, lotData.ycoord = zip(*coords * unit_cnt)

        # -  res_val
        failList = [np.random.choice(pattern,
                                     size=len(coords),
                                     p=p) for num in range(1, unit_cnt + 1)]
        lotData.val = list(it.chain.from_iterable(failList))

        # Print a message in console
        msg = 'LOT_ID : ' + lot_cd + id1 + id2
        print('-' * len(msg))
        print(msg)
        print('-' * len(msg))
        return lotData



def draw_wf(data, plot_ok=True, save_ok=False):
    name = data['lotwf_id'].unique()[0]
    img = sp.sparse.scr_matrix((data['val'].values, (data['x_axis'].values, data['y_axis'].values))).toarray()
    img = sp.misc.imresize(img[11:, 11:], size=(400, 400))
    if save_ok:
        os.makedirs('wfmap', exist_ok=True)
        sp.misc.imsave('wfmap/{lotwf}.jpg'.format(lotwf=name), img)



if __name__ == '__main__':

    alot = wafer(fac_id='Factory1', lot_cd='ABC', end_tm='20161101123456',
                 size=(55, 35), unit_cnt=20, p=[.85, .15], f_type='bold_line')
    aplt = wafer.unitplot(alot, columns=['xcoord', 'ycoord'],
                          lot_id='', unit_id='02', val='val', figsize=(11, 10),
                          pattern=['F'], m=['s'], s=[250], c=['red'], a=[.8], shown='y')
    aplt.show()
    
