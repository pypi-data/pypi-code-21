# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Contains the class that analizes one cycle."""


class rawDataSet:
    """rawDataSet class"""

    def __init__(self, data, ratioSet):
        """Initializes the object."""

        self.wishedTension = []
        self.current = []
        self.resistance = []
        self.time = []
        self.tension = []
        for i in range(len(data[0])):
            self.wishedTension.append(data[0][i])
            self.current.append(data[1][i])
            self.resistance.append(data[2][i])
            self.time.append(data[3][i])
            self.tension.append(data[4][i])
        onTension = 'no set'
        onCurrent = 'no set'
        onResistance = 'no set'

        # Finds the largest instantaneous reduction of resistance
        # and gives the on resistance near 0 V.
        maxDelta = 0.
        delta = abs(ratioSet * self.current[1])
        if self.wishedTension[3] - self.wishedTension[2] > 0:
            for i in range(1, (len(self.tension)) - 1):
                cond1 = -(-self.current[i + 1] + self.current[i]) > delta
                cond2 = -(-self.current[i + 1] + self.current[i]) > maxDelta
                if cond1 and cond2:
                    onTension = self.wishedTension[i]
                    onCurrent = self.current[i + 1]
                    onResistance = self.resistance[len(self.tension) - 2]
                    maxDelta = abs(-self.current[i + 1] + self.current[i])
        else:
            for i in range(1, (len(self.tension)) - 1):
                cond1 = (-self.current[i + 1] + self.current[i]) > delta
                cond2 = (-self.current[i + 1] + self.current[i]) > maxDelta
                if cond1 and cond2:
                    onTension = self.wishedTension[i]
                    onCurrent = self.current[i + 1]
                    onResistance = self.resistance[len(self.tension) - 2]
                    maxDelta = abs(-self.current[i + 1] + self.current[i])
        self.set = [onTension, onCurrent, onResistance]


class rawDataReset:
    """rawDataReset class"""

    def __init__(self, data, ratioReset):
        """Initializes the object."""

        self.wishedTension = []
        self.current = []
        self.resistance = []
        self.time = []
        self.tension = []
        for i in range(len(data[0])):
            self.wishedTension.append(data[0][i])
            self.current.append(data[1][i])
            self.resistance.append(data[2][i])
            self.time.append(data[3][i])
            self.tension.append(data[4][i])
        offTension = 'no reset'
        offCurrent = 'no reset'
        offResistance = 'no reset'

        # Finds the largest drop of electrical current
        # and gives the off resistance near 0 V.
        maxDelta = 0.
        if self.wishedTension[3] - self.wishedTension[2] > 0:
            for i in range(1, (len(self.tension)) - 2):  # /2)):
                delta = abs(ratioReset * self.current[i])
                cond1 = (-self.current[i + 1] + self.current[i]) > delta
                cond2 = (-self.current[i + 1] + self.current[i]) > maxDelta
                if cond1 and cond2:
                    offTension = self.wishedTension[i]
                    offCurrent = self.current[i]
                    offResistance = self.resistance[len(self.tension) - 2]
                    maxDelta = abs(-self.current[i + 1] + self.current[i])
        else:
            for i in range(1, (len(self.tension)) - 2):  # /2)):
                delta = -abs(ratioReset * self.current[i])
                cond1 = -(-self.current[i + 1] + self.current[i]) > delta
                cond2 = -(-self.current[i + 1] + self.current[i]) > maxDelta
                if cond1 and cond2:
                    offTension = self.wishedTension[i]
                    offCurrent = self.current[i]
                    offResistance = self.resistance[len(self.tension) - 2]
                    maxDelta = abs(-self.current[i + 1] + self.current[i])
        self.reset = [offTension, offCurrent, offResistance]
