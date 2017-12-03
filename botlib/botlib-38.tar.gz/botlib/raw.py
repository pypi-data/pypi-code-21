# BOTLIB Framework to program bots
#
# botlib/raw.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" raw output using print. """

from .bot import Bot

class RAW(Bot):

    """ Bot that outputs to stdout, using self.verbose or cfg.verbose (-v option) to determine whether to output or not. """

    verbose = True
    
    def direct(self, txt):
        """ output directly to display. """
        from .space import cfg
        if self.verbose or cfg.verbose:
            print(txt)

    def raw(self, txt):
        """ raw output. """
        self.direct(txt)
        
    def say(self, channel, txt, type=""):
        """ output txt to stdout. """
        self.direct(txt)
