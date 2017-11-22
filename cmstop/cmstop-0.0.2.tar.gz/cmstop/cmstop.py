#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base module for cmstop.
"""

import os
import sys

import logging

class CmsTop(object):
    """
    Base class of cmstop.
    """

    def __init__(self):
        self.config = ""

    def cmstop_dir(self):
        pass


def main():
    """
    Entry of cmstop tools.
    """
    print 'Thank you for chosing cmstop!'


if __name__ == "__main__":
    main()
