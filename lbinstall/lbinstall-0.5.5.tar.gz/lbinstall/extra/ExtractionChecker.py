#!/usr/bin/env python
###############################################################################
# (c) Copyright 2012-2016 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Tool to check that the rpmfile extraction is correct

:author: Ben Couturier
'''

import os
import tempfile
from lbinstall.PackageManager import PackageManager
from lbinstall.extra.RPMExtractor import extract


def checkExtraction(filename):
    ''' Extracts a given RPM with rpm2cpio and rpmfile an compares the result

    :param filename: the rpm filename

    :returns: result of the comparison
    '''
    topdir = tempfile.mkdtemp(prefix="checkExtraction")

    rpmfiledir = os.path.join(topdir, "rpmfile")
    os.makedirs(rpmfiledir)
    cpiodir = os.path.join(topdir, "cpio")
    os.makedirs(cpiodir)

    # Extracting with rpmfile
    relocatemap = {"/opt/LHCbSoft/lhcb": rpmfiledir}
    pm = PackageManager(filename, '', relocatemap)
    pm.extract()

    # extracting with cpio
    extract([filename], cpiodir)

    cpiodir_mdata = set(extractDirInfo(cpiodir))
    rpmfiledir_mdata = set(extractDirInfo(rpmfiledir))

    # Cleaning up
    import shutil
    shutil.rmtree(cpiodir)
    shutil.rmtree(rpmfiledir)
    return(cpiodir_mdata - rpmfiledir_mdata,
           rpmfiledir_mdata - cpiodir_mdata)


def extractDirInfo(dirname):
    """
    Extracts the metadata recursivly form all the subdirs/files

    :param dirname: the top directory
    :returns: the list of metadata tuples: name, size, link, st_mode, st_nlink
    """
    from os import walk, lstat
    from os.path import join, islink
    metadata = []
    for root, _dirs, files in walk(dirname):
        for f in files:
            n = join(root, f)
            sr = lstat(n)
            ret = (n.replace(dirname, ""), sr.st_size, islink(n),
                   sr.st_mode, sr.st_nlink),
            metadata.append(ret)
    return sorted(metadata)
