#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
from . import _decor


def bisplev(x, y, tck):
    tx = tck[0].astype(np.float32)
    ty = tck[1].astype(np.float32)
    c = tck[2].astype(np.float32)
    kx = tck[3]
    ky = tck[4]
    x = x.astype(np.float32)
    y = y.astype(np.float32)
    return np.asarray(_decor._bispev(tx, ty, c, kx, ky, x, y))


class Spline(object):
    def __init__(self, filename):
        self.spline_order = 3  # This is the default, so cubic splines
        self.len_float_str = 14  # by default one float is 14 char in ascii
        self.filename = filename
        self._parse()

    def _parse(self):
        string_spline = [i.rstrip() for i in open(self.filename)]
        index_line = 0
        for oneLine in string_spline:
            striped_line = oneLine.strip().upper()
            if striped_line == 'VALID REGION':
                data = string_spline[index_line + 1]
                self.xmin = float(data[self.len_float_str * 0:self.len_float_str * 1])
                self.ymin = float(data[self.len_float_str * 1:self.len_float_str * 2])
                self.xmax = float(data[self.len_float_str * 2:self.len_float_str * 3])
                self.ymax = float(data[self.len_float_str * 3:self.len_float_str * 4])
            elif striped_line == 'GRID SPACING, X-PIXEL SIZE, Y-PIXEL SIZE':
                data = string_spline[index_line + 1]
                self.grid = float(data[:self.len_float_str])
                self.pixel_size = (
                    float(data[self.len_float_str:self.len_float_str * 2]),
                    float(data[self.len_float_str * 2:self.len_float_str * 3])
                )
            elif striped_line == 'X-DISTORTION':
                data = string_spline[index_line + 1]
                spline_knots_x_len, spline_knots_y_len = [int(i) for i in data.split()]
                databloc = []
                for line in string_spline[index_line + 2:]:
                    if len(line) > 0:
                        for i in range(len(line) // self.len_float_str):
                            databloc.append(float(line[i * self.len_float_str: (i + 1) * self.len_float_str]))
                    else:
                        break
                self.x_knots_x = np.array(databloc[:spline_knots_x_len], dtype=np.float32)
                self.x_knots_y = np.array(databloc[spline_knots_x_len:spline_knots_x_len + spline_knots_y_len],
                                          dtype=np.float32)
                self.x_coeff = np.array(databloc[spline_knots_x_len + spline_knots_y_len:], dtype=np.float32)
            elif striped_line == 'Y-DISTORTION':
                data = string_spline[index_line + 1]
                spline_knots_x_len, spline_knots_y_len = [int(i) for i in data.split()]
                databloc = []
                for line in string_spline[index_line + 2:]:
                    if len(line) > 0:
                        for i in range(len(line) // self.len_float_str):
                            databloc.append(float(line[i * self.len_float_str:(i + 1) * self.len_float_str]))
                    else:
                        break
                self.y_knots_x = np.array(databloc[:spline_knots_x_len], dtype=np.float32)
                self.y_knots_y = np.array(databloc[spline_knots_x_len:spline_knots_x_len + spline_knots_y_len],
                                          dtype=np.float32)
                self.y_coeff = np.array(databloc[spline_knots_x_len + spline_knots_y_len:], dtype=np.float32)
            index_line += 1

    def func_x_y(self, x, y, r):
        if abs(x[1:, :] - x[:-1, :] - np.zeros((x.shape[0] - 1, x.shape[1]))).max() < 1e-6:
            x = x[0]
            y = y[:, 0]
        elif abs(x[:, 1:] - x[:, :-1] - np.zeros((x.shape[0], x.shape[1] - 1))).max() < 1e-6:
            x = x[:, 0]
            y = y[0]
        if r == 0:
            tck = self.x_knots_x, self.x_knots_y, self.x_coeff, self.spline_order, self.spline_order
        else:
            tck = self.y_knots_x, self.y_knots_y, self.y_coeff, self.spline_order, self.spline_order
        return bisplev(x, y, tck)
