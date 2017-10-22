#!/usr/bin/python
# -*- coding: utf-8 -*-

# graph.py file is part of slpkg.

# Copyright 2014-2017 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import subprocess


class Graph(object):
    """Drawing dependencies diagram
    """
    def __init__(self, image):
        self.image = image
        self.file_format = [
            ".bmp", ".canon", ".cmap", ".cmapx", ".cmapx_np", ".dot",
            ".eps", ".fig", ".gd", ".gd2", ".gif", ".gtk", ".gv", ".ico",
            ".imap", ".imap_np", ".ismap", ".jpe", ".jpeg", ".jpg", ".pdf",
            ".pic", ".plain", ".plain-ext", ".png", ".pov", ".ps", ".ps2",
            ".svg", ".svgz", ".tif", ".tiff", ".tk", ".vml", ".vmlz",
            ".vrml", ".wbmp", ".x11", ".xdot", ".xlib"
        ]

    def dependencies(self, deps_dict):
        """Generate graph file with depenndencies map tree
        """
        try:
            import pygraphviz as pgv
        except ImportError:
            graph_easy, comma = "", ""
            if (self.image == "ascii" and
                    not os.path.isfile("/usr/bin/graph-easy")):
                comma = ","
                graph_easy = " graph-easy"
            print("Require 'pygraphviz{0}{1}': Install with 'slpkg -s sbo "
                  "pygraphviz{1}'".format(comma, graph_easy))
            raise SystemExit()
        if self.image != "ascii":
            self.check_file()
        try:
            G = pgv.AGraph(deps_dict)
            G.layout(prog="fdp")
            if self.image == "ascii":
                G.write("{0}.dot".format(self.image))
                self.graph_easy()
            G.draw(self.image)
        except IOError:
            raise SystemExit()
        if os.path.isfile(self.image):
            print("Graph image file '{0}' created".format(self.image))
        raise SystemExit()

    def check_file(self):
        """Check for file format and type
        """
        try:
            image_type = ".{0}".format(self.image.split(".")[1])
            if image_type not in self.file_format:
                print("Format: '{0}' not recognized. Use one of "
                      "them:\n{1}".format(self.image.split(".")[1],
                                          ", ".join(self.file_format)))
                raise SystemExit()
        except IndexError:
            print("slpkg: Error: Image file suffix missing")
            raise SystemExit()

    def graph_easy(self):
        """Draw ascii diagram. graph-easy perl module require
        """
        if not os.path.isfile("/usr/bin/graph-easy"):
            print("Require 'graph-easy': Install with 'slpkg -s sbo "
                  "graph-easy'")
            self.remove_dot()
            raise SystemExit()
        subprocess.call("graph-easy {0}.dot".format(self.image), shell=True)
        self.remove_dot()
        raise SystemExit()

    def remove_dot(self):
        """Remove .dot files
        """
        if os.path.isfile("{0}.dot".format(self.image)):
            os.remove("{0}.dot".format(self.image))
