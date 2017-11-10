# -*- coding: utf-8 -*-

def findfiles(path, searchexp):
    """
    List all files and values corresponding to searchexp in directory specified with path.
    If groups are given in searchexp the corresponding values/strings are also returned.

    :type path: str
    :param path: Path to directory where it should be looked for files.
    :type searchexp: str
    :param searchexp: Regular expression search string with groups. Groups are marked by brackets ( ).
    :returns: filenames, values from groups
    """
    
    import re
    import os

    files = os.listdir(path)
           
    allvalues = []
    filenames = []
    for fi in files:
        x = re.search(searchexp, fi)
        if x:
            vals = x.groups()
            allvalues.append(vals)
            filenames.append(x.string)
            
    return filenames, allvalues

