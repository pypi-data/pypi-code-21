#!/usr/bin/env python
import sys

def calc_strike_temp(WaterVolInQuarts, GrainMassInPounds, GrainTemp, MashTemp):
    WaterToGrainRatio = WaterVolInQuarts / GrainMassInPounds
    StrikeWaterTemp = ((0.2 / WaterToGrainRatio) *
                       (MashTemp - GrainTemp)) + MashTemp
    return round(StrikeWaterTemp, 1)
