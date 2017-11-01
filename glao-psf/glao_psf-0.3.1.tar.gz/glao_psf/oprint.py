"""
pprint is an enhanced pretty-print for objects
"""
import numpy as np
import pprint as up_pprint
import json
from collections import OrderedDict

def ppd(self,print_=True):
    """Pretty-print the dictionary
    """
    if isinstance(self,dict):
        try:
            r = json.dumps(self,indent=4)
        except:
            d = OrderedDict()
            valid_types = (int,long,float,complex,str)
            for key,val in zip(self.keys(),self.values()):
                if isinstance(val,valid_types):
                    d[key] = val
                else:
                    d[key] = str(type(val))
            r = json.dumps(d,indent=4)
    else:
        r = ''
    if print_:
        print r
    else:
        return r

def pprint(self,print_width=60, short=False, expand=0):
    """Pretty-print the object. This consists
    of reporting on the object's attributes.
    
    :param object self: an object of any type
    :param int print_width: widest printout width per attribute.
        After this the output is abreviated
    :param boolean short: short output. Just the name
        and object type, no attributes.
    "param boolean expand: expand all dictionaries in a nested indented form
        level 1 does only dicts, level 2 does lists of dicts

    """
    if isinstance(self,dict):
        ppd(self)
        return
    elif isinstance(self,(list,tuple)):
        for e in self:
            pprint(e,print_width=print_width,short=short,expand=expand)
        return
    elif not hasattr(self,'__dict__'):
        up_pprint.pprint(self)
        return
    bling = print_width*'='
    print bling
    print type(self),
    if hasattr(self,'longName'):
        print self.longName
    elif hasattr(self,'name'):
        print self.name
    else:
        print ''
    print print_width*'-'
    if short:
        return
    tab = ' '*4
    d = self.__dict__
    keys = sorted(d.keys())
    for key in keys:
        limit_length = True
        if key.endswith('_units'): continue
        val = d[key]
        units = None
        
        if isinstance(val,(str,unicode)):
            pv = "'"+val+"'"
        elif isinstance(val,(tuple,list)):
            if (len(val) < 5) and (np.array(map(np.isscalar,val)).all()):
                pv = str(val)
            elif expand > 1:
                pv = str(type(val)) + ' ' + str(len(val)) + ' entries'
                for e in val:
                    r = ppd(e,print_=False)
                    if r == '':
                        r = str(type(e))
                    else:
                        limit_length = False
                    pv += '\n' + r
            else:
                pv = str(type(val)) + ' ' + str(len(val)) + ' entries'
        elif expand > 0 and isinstance(val,dict):
            pv = ppd(val,print_=False)
            limit_length = False
        else:
            pv = str(val)
            
        if limit_length:
            if key.endswith('_doc'):
                pass
            elif len(pv) > print_width:
                pv = str(val.__class__)
                if isinstance(val,(np.ndarray,np.matrix)):
                    pv += ' '+str(val.shape)
                
        if key+'_units' in keys:
            units = d[key+'_units']
        line = key+':'+tab+pv
        if units is None:
            pass
        else:
            line += ' '+units
        if isinstance(val,object):
            if (hasattr(val,'longName')):
                line += " '"+val.longName+"'"
            elif (hasattr(val,'name')):
                line += " '"+val.name+"'"
        else:
            pass
        print line
    print bling

def methods(self):
    cm = dir(self.__class__)
    return [x for x in cm if not x.startswith('__')]

def test():
    from info_array import InfoArray
    pprint(1)
    pprint('hello')
    a = InfoArray([[1,2],[3,4]],name='foo')
    pprint(a)
    d = OrderedDict()
    d['one'] = 'hello'
    d['two'] = 12.34
    d['three'] = 24
    d['four'] = np.array([1,2])
    pprint(d)