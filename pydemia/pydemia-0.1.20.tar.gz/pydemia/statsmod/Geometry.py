#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 20:33:37 2017

@author: dawkiny
"""

import math
from pandas import DataFrame as df


class Ellipse:

    def __init__(self, diameter):

        assert isinstance(diameter, tuple)
        assert len(diameter) == 2
        self.diameter = diameter
        self.radius = (int(diameter[0]/2), int(diameter[1]/2))
        self.center = (int(math.floor(diameter[0]/2 + 1)),
                       int(math.floor(diameter[1]/2 + 1)))
        self.angle = 0

    def coordinates(self):

        diameter = self.diameter

        """
        Ellipse equation:
        (x-center_x)^2/radius_x^2 + (y-center_y)^2/radius_y^2 = 1
        x = center_x + radius_x * cos(t)
        y = center_y + radius_y * sin(t)
        """

        # sine, cosine = math.sin(self.angle), math.cos(self.angle)

        # Get Center Coordinates
        center_x, center_y = self.center
        radius_x, radius_y = self.radius

        # Define an Ellipse Function
        coord_list = [(x, y)
                      for x in range(0, diameter[0])
                      for y in range(0, diameter[1])
                      if (pow(x - center_x, 2) / pow(radius_x, 2)) +
                         (pow(y - center_y, 2) / pow(radius_y, 2)) <= 1]

        coords = df(coord_list, columns=['xcoord', 'ycoord'])
        return coords
