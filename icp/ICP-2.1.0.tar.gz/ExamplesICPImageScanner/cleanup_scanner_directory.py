#!/usr/bin/env python

##  cleanup_scanner_directory.py

import glob
import os

def cleanup_data_directories():
    for filename in glob.glob( '__result*/*' ): 
        os.unlink(filename)
    for filename in glob.glob( '__model/*' ): 
        os.unlink(filename)
    for filename in glob.glob( '__color_model/*' ): 
        os.unlink(filename)
    for directory_name in glob.glob( '__result*' ): 
        os.rmdir(directory_name)
    os.rmdir('__model')

cleanup_data_directories()

