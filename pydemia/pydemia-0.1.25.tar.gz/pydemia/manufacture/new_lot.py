#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 19:39:21 2017

@author: pydemia
"""


import os
import numpy as np
import pandas as pd
from datetime import datetime as dt
import itertools as it
import random
import string
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from skimage import draw

from pydemia.math.Geometry import Ellipse


class Wafer(object):

    # Create lotData DataFrame
    def __init__(self, fac_id=None, lot_cd=None, end_tm=None, size=None,
                 unit_cnt=25, f_type='none', y_val=.8, print_ok=False,
                 pattern=['G', 'B'], *args, **kwargs):

        assert len(size) == 2
        assert y_val < 1
        assert isinstance(unit_cnt, int)
        self.fac_id = fac_id
        self.lot_cd = lot_cd
        self.end_tm = end_tm
        self.size = size
        self.unit_cnt = unit_cnt
        self.f_type=f_type
        self.y_val = y_val
        self.f_val = 1 - y_val
        self.pattern = pattern
        self.print_ok = print_ok

        #self.lotData = super(wafer, cls).__new__(cls, *args, **kwargs)
        self.lotData = self._create()

#    def __new__(cls, *args, **kwargs):
#
#        obj = super(wafer, cls).__create__(lot, *args, **kwargs)
#        obj.dd = obj
#        return obj

    def _create(self):
        
        fac_id = self.fac_id
        lot_cd = self.lot_cd
        end_tm = self.end_tm
        size = self.size
        unit_cnt = self.unit_cnt
        f_type=self.f_type
        y_val = self.y_val
        f_val = self.f_val
        pattern = self.pattern
        print_ok = self.print_ok
        
        
        
        assert len(size) == 2
        assert y_val < 1
        assert isinstance(unit_cnt, int)

        f_val = 1 - y_val
        good_mark = pattern[0]  # 'G'
        fail_mark = pattern[1]  # 'B'

        # Adjust Egde Coordinates
        adjusted_size = tuple(np.add(size, 1))
        coords = Ellipse(adjusted_size).coordinates()
        
        x_cnt = coords.groupby('xcoord')['ycoord'].nunique()
        y_cnt = coords.groupby('ycoord')['xcoord'].nunique()
        
        x_except = x_cnt[x_cnt < 3].index.values[0]
        y_except = y_cnt[y_cnt < 3].index.values[0]

        coords = coords[(coords.xcoord!=x_except) & (coords.ycoord!=y_except)]
        
        # For the compatibility with the real
        coords.xcoord = coords.xcoord + 9
        coords.ycoord = coords.ycoord + 9

        # xsize, ysize = coords.xcoord.max(), coords.ycoord.max()
        lotDataKey = ['fac_id', 'lot_cd', 'lot_id', 'unit_id',
                      'end_dt', 'end_tm', 'xcoord', 'ycoord', 'val']
        lotData = pd.DataFrame(columns=lotDataKey,
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

            # f_type = 'Line''line'
            if f_type == 'line':

                # -  res_val : pattern
                xcoord_range = range(min(coords.xcoord), max(coords.xcoord))
                ycoord_range = range(min(coords.ycoord), max(coords.ycoord))

                dist = 0
                while dist <= 15:
                    adot_x, bdot_x = np.random.choice(xcoord_range, size=2)
                    adot_y, bdot_y = np.random.choice(ycoord_range, size=2)

                    adot = adot_x, adot_y
                    bdot = bdot_x, bdot_y
                    dist = pdist([adot, bdot])[0]

                rr, cc = draw.line(adot_x, adot_y, bdot_x, bdot_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                patt_coord = random.sample(patt_coord,
                                           k=int(len(patt_coord)*random.choice(np.arange(.78, .9, .05))))
                pattFail = [fail_mark if (x, y) in patt_coord else good_mark for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * f_val - pattFail.count(fail_mark)
                
                if new_fail_num < 0:
                    pass
                else:
                    new_fail_per = new_fail_num / pattFail.count(good_mark)
                    adjusted_per = 1 - new_fail_per, new_fail_per
    
                    wfFailList = [np.random.choice(pattern, p=adjusted_per)\
                                  if patt == good_mark else patt for patt in\
                                  pattFail]

                lotFailList += wfFailList

            elif f_type == 'bold_line':

                # -  res_val : pattern
                xcoord_range = range(min(coords.xcoord), max(coords.xcoord))
                ycoord_range = range(min(coords.ycoord), max(coords.ycoord))

                dist = 0
                while dist <= 15:
                    adot_x, bdot_x = np.random.choice(xcoord_range, size=2)
                    adot_y, bdot_y = np.random.choice(ycoord_range, size=2)

                    adot = adot_x, adot_y
                    bdot = bdot_x, bdot_y
                    dist = pdist([adot, bdot])[0]

                rr, cc, val = draw.line_aa(adot_x, adot_y, bdot_x, bdot_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                patt_coord = random.sample(patt_coord,
                                           k=int(len(patt_coord)*random.choice(np.arange(.78, .9, .05))))
                pattFail = [fail_mark if (x, y) in patt_coord else good_mark for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * f_val - pattFail.count(fail_mark)
                
                if new_fail_num < 0:
                    pass
                else:
                    new_fail_per = new_fail_num / pattFail.count(good_mark)
                    adjusted_per = 1 - new_fail_per, new_fail_per
    
                    wfFailList = [np.random.choice(pattern, p=adjusted_per)\
                                  if patt == good_mark else patt for patt in pattFail]

                lotFailList += wfFailList

            elif f_type == 'arc':

                # -  res_val : pattern
                arc_xx, arc_yy = draw.ellipse(int(size[0]/2), int(size[1]/2), size[0]*.8, size[1]*.8)
                adot_x, adot_y = random.choice(tuple(zip(arc_xx, arc_yy)))
                adot = adot_x, adot_y

                rad = int(np.random.randint(min(size), max(size))/2)
                rad_x = int(rad * size[0]/size[1])
                rad_y = rad

                rr, cc = draw.ellipse_perimeter(adot_x, adot_y, rad_x, rad_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                patt_coord = random.sample(patt_coord,
                                           k=int(len(patt_coord)*random.choice(np.arange(.78, .9, .05))))
                pattFail = [fail_mark if (x, y) in patt_coord else good_mark for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * f_val - pattFail.count(fail_mark)
                
                if new_fail_num < 0:
                    pass
                else:
                    new_fail_per = new_fail_num / pattFail.count(good_mark)
                    adjusted_per = 1 - new_fail_per, new_fail_per
    
                    wfFailList = [np.random.choice(pattern, p=adjusted_per)\
                                  if patt == good_mark else patt for patt in pattFail]

                lotFailList += wfFailList

            elif f_type == 'bold_arc':

                # -  res_val : pattern
                arc_xx, arc_yy = draw.ellipse(int(size[0]/2), int(size[1]/2), size[0]*.8, size[1]*.8)
                adot_x, adot_y = random.choice(tuple(zip(arc_xx, arc_yy)))
                adot = adot_x, adot_y

                rad = int(np.random.randint(min(size), max(size))/2)
                rad_x = int(rad * size[0]/size[1])
                rad_y = rad

                rr, cc = draw.ellipse_perimeter_aa(adot_x, adot_y, rad_x, rad_y)
                patt_coord = [(x, y) for x, y in zip(rr, cc)]
                patt_coord = random.sample(patt_coord,
                                           k=int(len(patt_coord)*random.choice(np.arange(.78, .9, .05))))
                pattFail = [fail_mark if (x, y) in patt_coord else good_mark for x, y in
                            zip(coords.xcoord, coords.ycoord)]

                # - res_val : add random
                new_fail_num = len(pattFail) * f_val - pattFail.count(fail_mark)
                
                if new_fail_num < 0:
                    pass
                else:
                    new_fail_per = new_fail_num / pattFail.count(good_mark)
                    adjusted_per = 1 - new_fail_per, new_fail_per
    
                    wfFailList = [np.random.choice(pattern, p=adjusted_per) if patt == good_mark else patt for patt in
                                  pattFail]

                lotFailList += wfFailList

            elif f_type == 'curve':
                pass

            elif f_type == 'none':

                wfFailList = [np.random.choice(pattern, size=len(coords), p=(y_val, f_val)) for num in range(1, unit_cnt + 1)]
                lotFailList = list(it.chain.from_iterable(wfFailList))

        lotData.val = lotFailList

        # Print a message in console
        if print_ok:
            msg1 = ' LOT_ID : {}'.format(lot_cd + id1 + id2)
            msg2 = ' WF_CNT : {}'.format(unit_cnt)

            print('-' * (len(msg1) + 2))
            print(msg1)
            print(msg2)
            print('-' * (len(msg1) + 2))

        return lotData

    # lotData Visualization
    def unitplot(self, columns=['xcoord', 'ycoord'], lot_id=None, unit_id=None,
                 val='val', figsize=(11, 10), pattern=['B'], m=['s'],
                 s=[120], c=['black'], a=[1.], background=True,
                 title_off=False, tight_on=False, axis_off=False,
                 shown=True):

        data = self.lotData
        assert len(figsize) == 2
        assert len(columns) == 2
        assert len(pattern) == len(m) == len(s) == len(c) == len(a)

        # Lot ID
        if lot_id is None:    
            lot_id = data.lot_id.unique()[0]

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
        #            plt.4ioff()

        canvas = {'pattern': '+',
                  's': 1000,
                  'c': 'grey',
                  'a': .2}

        # Draw plot
        fig = plt.figure(figsize=figsize)
        
        if background == True:
            plt.scatter(pltData.xcoord, pltData.ycoord,
                        marker='s', s=120, alpha=1.,
                        facecolors='white', edgecolors='lightgrey')

        for idx in range(0, len(pattern)):
            plt.scatter(pltData.loc[pltData.val == pattern[idx], 'xcoord'],
                        pltData.loc[pltData.val == pattern[idx], 'ycoord'],
                        marker=m[idx], s=s[idx], c=c[idx], alpha=a[idx])

        if title_off == False:
            fig.suptitle('{}, {}'.format(lot_id, unit_id))

        if tight_on == True:
            fig.tight_layout()

        if axis_off == True:
            plt.axis('off')

        if shown == False:
            plt.close(fig)

        return fig


    def to_txt(self, dirname, *args, **kwargs):

        lotData = self.lotData.copy()
        frame = lotData[['lot_id', 'unit_id', 'xcoord', 'ycoord', 'val']]
        frame.columns = ['alias_lot_id', 'wf_id', 'xcoord', 'ycoord', 'val']

        grouped = frame.groupby(['alias_lot_id', 'wf_id'])

        os.makedirs(dirname, exist_ok=True)
        grouped.apply(lambda x: x.to_csv(dirname + '/' +\
                                         '_'.join([x['alias_lot_id'].unique()[0],
                                                   x['wf_id'].unique()[0]]) +\
                                         '.txt', index=False, header=True, *args, **kwargs))


if __name__ == '__main__':
    
    alot = Wafer(fac_id='Factory1', lot_cd='ABC', end_tm='20161101123456',
                 size=(55, 45), unit_cnt=20, y_val=.8, f_type='line')
    alot.lotData
    alot.unitplot(unit_id='02',figsize=(11, 10),
                  m=['s'], s=[120], c=['black'], a=[1.], axis_off=True)


