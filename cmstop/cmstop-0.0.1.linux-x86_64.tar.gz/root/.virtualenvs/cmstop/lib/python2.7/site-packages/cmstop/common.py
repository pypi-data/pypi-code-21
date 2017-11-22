#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

"""
Common functions.
"""

def is_exists(path_name):
    return os.path.exists(path_name)
        
def is_dir(dirname):
    return os.path.isdir(dirname)

def is_file(filename):
    return os.path.isfile(filename)


def main():
    is_file('ass') 
    is_dir('ass') 

if __name__ == "__main__":
    main()
