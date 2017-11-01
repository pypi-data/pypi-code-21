# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

def equal_axes(ax, out):
    out_max = out.max(0)
    out_min = out.min(0)
    out_mid = (out_max+out_min)/2
    max_range = (out_max-out_min).max()/2

    ax.set_xlim(out_mid[0] - max_range, out_mid[0] + max_range)
    ax.set_ylim(out_mid[1] - max_range, out_mid[1] + max_range)
    ax.set_zlim(out_mid[2] - max_range, out_mid[2] + max_range)
