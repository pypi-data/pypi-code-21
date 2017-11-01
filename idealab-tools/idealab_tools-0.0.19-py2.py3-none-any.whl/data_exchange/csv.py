# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 14:07:57 2017

@author: danaukes
"""

def write(filename,array,formatstring = '{0:0.5e}',delimiter=','):
    lines = []
    
    for row in array:
        line = []
        for element in row:
            line.append(formatstring.format(element))
        line = delimiter.join(line)
        lines.append(line)
    lines = '\n'.join(lines)
    with open(filename,'w') as file_object:
        file_object.writelines(lines)


def read(filename,*args,delimiter=','):
    import numpy
    with open(filename) as file_object:
        lines = file_object.readlines()
    
    lines = [line.split(delimiter) for line in lines]
    array = numpy.array(lines) 
    return array
        
