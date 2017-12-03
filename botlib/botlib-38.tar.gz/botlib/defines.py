# BOTLIB Framework to program bots
#
# botlib/bot.py
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

""" definitions. """

from .object import Object

permissions = [
    "ANNOUNCE",
    "CFG",
    "EDIT",
    "RSS",
    "LOUD",
    "LOAD",
    "MEET",
    "PS",
    "RESTORE",
    "RM",
    "SAVE",
    "SHOW",
    "WATCH",
    "DEADLINE",
    "FLOOD",
    "FORCED",
    "FUNCS",
    "TESTS",
    "USER",
    "WRONGXML"
    ]


exclusive = [
    "ALL",
    "SHUTDOWN",
    "EXIT",
    "LOGLEVEL",
    "START",
    "STOP",
    "OPER"
    ]

defaults = Object()
defaults.log = ["log", ]
defaults.config = ["cfg", ]
defaults.event = ["origin", ]
defaults.user = ["origin", ]
defaults.email = ["Subject", ]
defaults.feed = ["title", ]
defaults.runtime = ["type", ]
defaults.todo = ["todo", ]
defaults.rss = ["rss", ]
