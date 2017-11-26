#!/usr/bin/env python

import glob
import os

def cleanup_directory():
    for filename in glob.glob( '__result*/*' ): 
        os.unlink(filename)
    for directory_name in glob.glob( '__result*' ): 
        os.rmdir(directory_name)

cleanup_directory()

