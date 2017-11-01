# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

#import glob

#path = 'C:\\Users\\danaukes\\Documents\\code\\popupcad'
#filenames = glob.glob(path + '*/*.py')
#for filename in glob.glob
#print filenames

import fnmatch
import os
import sys
import importlib

openclose = [('"""','"""'),("'''","'''")]

def recombine(inputlines,ii1,jj1,ii2,jj2,string1):
    a = inputlines[:ii1]
    b = inputlines[ii1][:jj1]+'\n'
    c = string1
    d = '\n'+inputlines[ii2][jj2:]
    e = inputlines[ii2+1:]
    out = a+[b]+c+[d]+e
    return out
    
def convertfile(filename,header):
    with open(filename,'r') as f:
        inputlines = f.readlines()

    opens = []
    closes = []
    for openstring,closestring in openclose:
        if openstring==closestring:
            level = 0
            for ii,line in enumerate(inputlines):
                kk = 0
                jj = line.find(openstring,kk)
                while jj!=-1:
                    if level==0:                
                        opens.append((ii,jj+len(openstring)))
                        level+=1
                    else:
                        closes.append((ii,jj))
                        level-=1

                    kk = jj+1
                    jj = line.find(openstring,kk)
        else:
            for ii,line in enumerate(inputlines):
                kk = 0
                jj = line.find(openstring,kk)
                while jj!=-1:
                    opens.append((ii,jj))
#                    level+=1
                    kk = jj+1
                    jj = line.find(openstring,kk)
            for ii,line in enumerate(inputlines):
                kk = 0
                jj = line.find(closestring,kk)
                while jj!=-1:
                    closes.append((ii,jj))
#                    level-=1
                    kk = jj+1
                    jj = line.find(closestring,kk)

    openscloses = [item for item in zip(opens,closes)]
    openscloses.sort()
    
    if len(opens)>0:
        for (ii1,jj1),(ii2,jj2) in openscloses[0:1]:
            out = recombine(inputlines,ii1,jj1,ii2,jj2,header)
    else:
        ii1 = 1
        jj1 = 0
        ii2 = 1
        jj2 = 0
        out = recombine(inputlines,ii1,jj1,ii2,jj2,['"""']+header+['"""\n'])
        
    return out    


def convert_module(module_name):
    importlib.import_module(module_name)
    p = sys.modules[module_name]
    file = p.__file__
    path = os.path.split(file)[0]
    path = os.path.split(path)[0]
    
    with open(os.path.normpath(os.path.join(path,'HEADER')),'r') as f:
        header = f.readlines()    
    matches = []
    
    for root, dirnames, filenames in os.walk(path):
      for filename in fnmatch.filter(filenames, '*.py'):
          matches.append(os.path.join(root, filename))
    
    for match in matches:
        print(match)
        out  = convertfile(match,header)
        with open(match,'w') as f:
            f.writelines(out)    

if __name__=='__main__':
    items = sys.argv[1:]
    
    for item in items:
        convert_module(item)
