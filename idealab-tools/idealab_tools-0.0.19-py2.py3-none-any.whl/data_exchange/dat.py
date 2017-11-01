import os

"""
copyright 2016-2017 Dan Aukes
"""

import numpy

def read(filename,format = None):
    with open(filename) as f:
        text = f.readlines()
    
    text = ''.join(text)
    text = text.split('\n')
    rows = []
    for row in text:
        row = row.split('%')[0]
        if len(row)>0:
            row = row.split()
            if format is not None:
                row = [format(entry) for entry in row]
            rows.append(row)
    
    data = numpy.array(rows)
    return data
    
if __name__=='__main__':
    filename = 'dirichlet.dat'
    data = load(filename,int)