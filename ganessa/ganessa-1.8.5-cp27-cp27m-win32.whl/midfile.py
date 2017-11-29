# -*- coding: iso-8859-1 -*-
from __future__ import print_function
'''
Created on 17 févr. 2014
Revu 18 mai 2016 --- added utm20n, utm22n, utm40s
Revu 28 juin 2016 --- renomme lambCC42..49 par rgf93-cc42..49

@author: Jarrige_Pi
'''

import os.path as OP
from collections import OrderedDict

__version__ = '0.9.0'

POINT = 1
POLYLINE = 3
POLYGON = 5

_delimiter = ','
#           type datum unit Lon0 Lat0  std_par1    std_par2           
projs = {
    'lambN': '3, 1002, "m", 0, 49.5, 48.598522778, 50.39591167, 600000, 200000 Bounds (-823171, -1417628) (3371792, 2970651)',
    'lambC': '3, 1002, "m", 0, 46.8, 45.898918889, 47.69601444, 600000, 200000 Bounds (-864407, -1131785) (3440473, 3294928)',
    'lambS': '3, 1002, "m", 0, 44.1, 43.199291389, 44.99609389, 600000, 200000 Bounds (-912250,  -849417) (3519844, 3627271)',
    'lamb2E':'3, 1002, "m", 0, 46.8, 45.898918889, 47.69601444, 600000, 2200000 Bounds (-864407,  868215) (3440473, 5294928)',
    'lamb93':'3, 33, "m", 3, 46.5, 44, 49.00000000001, 700000, 6600000 Bounds (-792421, 5278231) (3520778, 9741029)',
    'rgf93-cc42':'3, 33, "m", 3, 42, 41.25, 42.75, 1700000, 1200000 Bounds (1000000, 1000000) (2400000, 1400000)',
    'rgf93-cc43':'3, 33, "m", 3, 43, 42.25, 43.75, 1700000, 2200000 Bounds (1000000, 2000000) (2400000, 2400000)',
    'rgf93-cc44':'3, 33, "m", 3, 44, 43.25, 44.75, 1700000, 3200000 Bounds (1000000, 3000000) (2400000, 3400000)',
    'rgf93-cc45':'3, 33, "m", 3, 45, 44.25, 45.75, 1700000, 4200000 Bounds (1000000, 4000000) (2400000, 4400000)',
    'rgf93-cc46':'3, 33, "m", 3, 46, 45.25, 46.75, 1700000, 5200000 Bounds (1000000, 5000000) (2400000, 5400000)',
    'rgf93-cc47':'3, 33, "m", 3, 47, 46.25, 47.75, 1700000, 6200000 Bounds (1000000, 6000000) (2400000, 6400000)',
    'rgf93-cc48':'3, 33, "m", 3, 48, 47.25, 48.75, 1700000, 7200000 Bounds (1000000, 7000000) (2400000, 7400000)',
    'rgf93-cc49':'3, 33, "m", 3, 49, 48.25, 49.75, 1700000, 8200000 Bounds (1000000, 8000000) (2400000, 8400000)',
    'lambRGR92': '8, 104, "m", 57, 0, 0.9996, 500000, 10000000 Bounds (-7745844.29597, 2035.05676326) (8745844.29597, 19997964.9432)',
    'lambRRAF1191':'8, 33, "m", 63, 0, 0.9996, 500000, 0 Bounds (-7745844.29605, -9997964.94315) (8745844.29605, 9997964.94315)',
    'utm20N':'',
    'utm22N':'',
    'utm40S':''
         }
projs = OrderedDict(sorted(projs.items(), key=lambda t: (len(t[0]), t[0])))

 
def strf3(val):
    '''Nicely formats a float (single precision), remove trailing zeros '''
    if val == 0.0:
        return "0.0"
    elif abs(val) > 1.0:
        strg = "{0:.3f}".format(val)
    elif abs(val) > 0.01:
        strg = "{0:.6f}".format(val)
    else:
        return "{0:.7e}".format(val)
    if strg[-3:] == "000":
        return strg[:-3]
    elif strg[-2:] == "00":
        return strg[:-2]
    else:
        return strg

# Class wrapper for write functions to mid/mif
class Writer:
    def __init__(self, gtype):
        self.gtype = gtype
        self.hfields = []
        self.fields = []
        self.gobjects = []
        self.records = []
        self.proj = 'lambN'
        
    def point(self, x, y):
        self.gobjects.append((POINT, (x, y)))
    
    def poly(self, parts=[], shapeType= POLYLINE):
        self.gobjects.append((shapeType, parts))
    
    def field(self, name, vtype='N', size= None):
        if vtype.upper() == 'C':
            self.hfields.append((name, 'Char('+ str(size) + ')'))
            self.fields.append(size)
        else:
            self.hfields.append((name, 'Float'))
            self.fields.append(0)
    
    def record(self, *args):
        self.records.append(args)
        
    def projection(self, proj):
        if proj in projs:
            self.proj = proj
    
    def save(self, fname):
        fname = OP.splitext(fname)[0]
        with open(fname + '.mif', 'w') as mif:
            mif.write('Version   300\nCharset "WindowsLatin1"\n')
            mif.write('Delimiter "{:s}"\n'.format(_delimiter))
            mif.write('CoordSys Earth Projection ' + projs[self.proj] + '\n')
            mif.write('Columns ' + str(len(self.fields)) + '\n')
            for field in self.hfields:
                mif.write('  {:s} {:s}\n'.format(*field))
            mif.write('Data\n\n')
            for objtyp, data in self.gobjects:
                if objtyp == POINT:
                    mif.write('Point {:.3f} {:.3f}\n'.format(*data))
                    mif.write('     Symbol (35,0,7,"Map Symbols",256,0)\n')
                elif objtyp == POLYLINE:
                    item = data[0]
                    mif.write('Pline {:d}\n'.format(len(item)))
                    for pt in item:
                        mif.write(' '.join([strf3(p) for p in pt]) + '\n')
                    mif.write('   Pen (1,2,0)\n')
        
        with open(fname + '.mid', 'w') as mid:
            for rec in self.records:
                out = []
                for tl, item in zip(self.fields, rec):
                    if tl:
                        out.append('"' + str(item) + '"')
                    else:
                        out.append(strf3(item))
                mid.write(_delimiter.join(out) + '\n')


class _Shape:
    def __init__(self, typ):
        self.shapeType = typ
        self.points = []

# Class wrapper for read functions to mid/mif
class Reader:
    def __init__(self, fname):
        self.fields = []
        self.gobjects = []
        self.records = []
        self.delim = _delimiter
        self.name = OP.splitext(fname)[0]
        self.count = 0
        if not OP.exists(self.name  + '.mif'):
            return
        # Lecture du fichier MIF
        with open(self.name  + '.mif', 'r') as mif:
            def readwords():
                line = mif.next()
                return line.strip().split(' ')
            while True:
                words = readwords()
                # Column
                if words[0] == u'Columns': 
                    nbcol = int(words[1])
                    break
            for icol in range(0,nbcol):
                words = readwords()
                field = (words[0], words[1][0])
                self.fields.append(field)
            # Data
            while len(words) != 1 or words[0] != u'Data': 
                words = readwords()
            while True:
                try:
                    words = readwords()
                except StopIteration:
                    break
                if words[0] == 'Point':
                    obj = _Shape(POINT)
                    point = tuple(map(float, words[1:]))
                    obj.points.append(point)
                elif words[0] == 'Pline':
                    nbval = int(words[1])
                    obj = _Shape(POLYLINE)
                    for ipt in range(0, nbval):
                        point = tuple(map(float, readwords()))
                        obj.points.append(point)
                elif words[0] in ('Pen', 'Symbol'):
                    continue
                else:
                    continue
                self.count += 1
                self.gobjects.append(obj)
        if not OP.exists(self.name  + '.mid'):
            return
        # Lecture du fichier MID
        with open(self.name  + '.mid', 'r') as mid:
            sep = self.delim
            for line in mid:
                fields = line.rstrip('\n').split(sep)
                values = []
                for field, (name, typ) in zip(fields, self.fields):
                    if typ == 'C':
                        values.append(field.strip('"'))
                    elif typ == 'F':
                        values.append(float(field))
                    elif typ == 'I':
                        values.append(int(field))
                    else:
                        values.append(field)
                self.records.append(tuple(values))
                 
    def iterShapes(self):
        for obj in self.gobjects:
            yield obj
    
    def record(self, pos):
        return self.records[pos]

    def iterRecords(self):
        for obj in self.records:
            yield obj

if __name__ == "__main__":
    sig = Reader(r'D:\PAJarrige\eclipse\SIG2Pic\mif_mid\noeuds_L2e.MIF')
    for i, item in enumerate(sig.iterShapes()):
        pass
    print('Termine')
                
                
                
                
        
