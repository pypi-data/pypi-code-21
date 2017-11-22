#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Track.py

# Copyright (c) 2015-2016, Richard Gerum, Sebastian Richter
#
# This file is part of ClickPoints.
#
# ClickPoints is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ClickPoints is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClickPoints. If not, see <http://www.gnu.org/licenses/>

from __future__ import print_function, division
import clickpoints

#Pengu Tool: Huddlegröße in Pinguhöhen

class Addon(clickpoints.Addon):
    initialized = False

    def __init__(self, *args, **kwargs):
        clickpoints.Addon.__init__(self, *args, **kwargs)

        self.db.setMarkerType("PenguSize", "#FFFF00", self.db.TYPE_Line)
        self.db.setMarkerType("HuddleSize", "#00FF00", self.db.TYPE_Line)
        self.cp.reloadTypes()

        self.type1 = self.db.getMarkerType("PenguSize")
        self.type2 = self.db.getMarkerType("HuddleSize")

    def markerMoveEvent(self, marker):
        if marker.type == self.type2:# or marker.data.type == self.type2:
            pengu_size = self.db.getLines(image=marker.image, type=self.type1)
            huddle_size = self.db.getLines(image=marker.image, type=self.type2)
            if len(pengu_size) >= 1 and len(huddle_size) >= 1:
                size = huddle_size[0].length()/pengu_size[0].length()
                marker.text = "%.2f" % (size)
                marker.save()
