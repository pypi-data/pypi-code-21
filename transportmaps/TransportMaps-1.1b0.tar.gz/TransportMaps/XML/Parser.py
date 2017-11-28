#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2017 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Authors: Daniele Bigoni
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

try:
    from lxml import etree
    LXML_SUPPORT = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML_SUPPORT = False

__all__ = ['load_xml', 'from_xml_element',
           'store_xml', 'to_xml_element',
           'id_parser', 'vars_parser',
           'num_parser', 'midx_parser']

def load_xml(fname):
    import os
    if LXML_SUPPORT:
        tmxml_dir = os.path.dirname(os.path.realpath(__file__))
        schema_path = tmxml_dir + '/schema/map.xsd'
        schema_tree = etree.parse(schema_path)
        schema_root = schema_tree.getroot()
        schema = etree.XMLSchema(schema_root)
        parser = etree.XMLParser(schema=schema)
        tree = etree.parse(fname, parser)
        root = tree.getroot()
    else:
        tree = etree.parse(fname)
        root = tree.getroot()

    return from_xml_element(root)

def from_xml_element(node):
    from TransportMaps import XML_NAMESPACE
    from TransportMaps import Maps as MAPS
    if node.tag == XML_NAMESPACE + 'trimap':
        return MAPS.TriangularTransportMap.from_xml_element(node)

def store_xml(obj, fname):
    raise NotImplementedError("Coming soon")
    
def to_xml_element(obj):
    raise NotImplementedError("Coming soon")
    
def id_parser(id_field, dim):
    if id_field == '*':
        ncomp_list = range(dim)
    elif ':' in id_field:
        sp = id_field.split(':')
        sp_int = [num_parser(s, d=dim-1) for s in sp]
        if id_field[0] == ':':
            ncomp_list = range(sp_int[1])
        elif id_field[-1] == ':':
            ncomp_list = range(sp_int[0],dim)
        else:
            ncomp_list = range(sp_int[0],sp_int[1])
    else:
        ncomp_list = [ num_parser(id_field, dim) ]
    return ncomp_list

def vars_parser(vars_field, d):
    if vars_field == '*':
        vars_list = range(d+1)
    elif ':' in vars_field:
        sp = vars_field.split(':')
        sp_int = [ num_parser(s, d=d) for s in sp ]
        if vars_field[0] == ':':
            vars_list = range(sp_int[1])
        elif vars_field[-1] == ':':
            start = max(0, sp_int[0])
            vars_list = range(start, d+1)  # Changed to d+1
        else:
            start = max(0, sp_int[0])
            vars_list = range(start, sp_int[1])
    else: # Regular string
        vars_list = [ num_parser(vars_field, d) ]
    return vars_list

def num_parser(nstr, d):
    if nstr == '':
        out = None
    elif nstr[0] == 'd': # Format d-x or d+x
        sp_plus = nstr.split('+')
        sp = [ s.split('-') for s in sp_plus ]
        out = 0
        for s0 in sp:
            if s0[0] == 'd':
                sub = d
            else:
                sub = int(s0[0])
            for s1 in s0[1:]:
                sub -= int(s1)
            out += sub
    else:
        out = int(nstr)
    return out

def midx_parser(midx_str):
    midx = tuple([ int(s) for s in midx_str.split(',') ])
    return midx
    