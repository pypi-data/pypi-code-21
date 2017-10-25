#!/usr/bin/env python

import numpy as np
from scipy.signal import medfilt

def fix_baseline_wander(data, sr):
    """BaselineWanderRemovalMedian.m from ecg-kit.  Given a list of amplitude values
    (data) and sample rate (sr), it applies two median filters to data to
    compute the baseline.  The returned result is the original data minus this
    computed baseline.
    """
    data = np.array(data)
    WinSize = int(round(0.2*sr))
    # delayBLR = round((WinSize-1)/2)
    if WinSize % 2 == 0:
        WinSize += 1
    BaselineEstimation = medfilt(data, kernel_size=WinSize)
    WinSize = int(round(0.6*sr))
    # delayBLR = delayBLR + round((WinSize-1)/2)
    if WinSize % 2 == 0:
        WinSize += 1
    BaselineEstimation = medfilt(BaselineEstimation, kernel_size=WinSize)
    ECGblr = data - BaselineEstimation
    return ECGblr.tolist()
