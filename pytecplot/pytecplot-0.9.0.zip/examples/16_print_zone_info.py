from __future__ import print_function

import os
from textwrap import dedent

import tecplot
from tecplot.constant import ZoneType

def zone_info(zone):
    """Generate a dict of parameters describing a Zone"""
    info = dict()
    attrs = '''
        name
        zone_type
        strand
        num_elements
        num_variables
        dimensions
        num_points_per_element
        num_faces
        num_points
        rank
    '''.split()
    for attr in attrs:
        info[attr] = getattr(zone, attr, None)
    return info

examples_dir = tecplot.session.tecplot_examples_directory()

for root, dirs, files in os.walk(examples_dir):
    for name in files:
        if name.endswith('.plt'):
            infile =  os.path.join(root,name)
            print(infile)
            tecplot.data.load_tecplot(infile)
            ds = tecplot.active_frame().dataset
            for zone in ds.zones():
                info = zone_info(zone)
                print(dedent('''\
                Name: {name}
                Type: {zone_type}
                Strand: {strand}
                Elems: {num_elements}
                Points: {num_points}
                Variables: {num_variables}'''.format(**info)))
                if zone.zone_type == ZoneType.Ordered:
                    print(dedent('''\
                    Dimensions: {dimensions}
                    Points/Elem: {num_points_per_element}'''.format(**info)))
                elif zone.zone_type in [ZoneType.FEPolygon,
                                        ZoneType.FEPolyhedron]:
                    print(dedent('''\
                    Faces: {num_faces}
                    Rank: {rank}'''.format(**info)))
                else:
                    print(dedent('''\
                    Rank: {rank}
                    Points/Elem: {num_points_per_element}'''.format(**info)))
                print('\n')
