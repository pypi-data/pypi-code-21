#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
"""
Search for layered structures.
"""

from aiida.orm import Group
import numpy as np
from aiida.orm import DataFactory
from aiida.workflows.user.epfl_theos.dbimporters.utils import \
        get_lowdimfinder_results, get_source_id, get_source_db_name

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller, Nicolas Mounet, Giovanni Pizzi."


KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
ParameterData = DataFactory('parameter')
CifData = DataFactory('cif')


def parse_cmdline():
    """
    Parse the command line. Most important is to pass the GROUPNAME
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Extract 2D layers from a group of structures')

    parser.add_argument('--margin_min', type=float, action='store',
                        help='Specify the minimum margin to be used (default=0.)')
    parser.add_argument('--margin_max', type=float, action='store',
                        help='Specify the maximum margin to be used (default=0.)')
    parser.add_argument('--margin_step', type=float, action='store',
                        help='Specify the margin step to be used (default=0.025)')
    parser.add_argument('--offsets', type=float, nargs='+',
                        help='Specify the list of offsets to be tried (added to the atomic radii) (default=[-0.75,-0.7,-0.65,-0.6,-0.55])')
    parser.add_argument('-v','--vacuum', type=float, action='store',
                        help='Specify the vacuum space (in angstrom) to be used between layers (default=40)')
    parser.add_argument('-r', '--rotation', action='store_false',
                        help='Specify if we store the rotated 3D structure (the one corresponding to the layer in the x-y plane) (default = True)')
    parser.add_argument('-o', '--orthogonal_axis_2D', action='store_false',
                        help='Specify if you want to have the 3rd axis orthogonal to the layer, for 2D crystals (default = True)')
    parser.add_argument('-s', '--radii_source', type=str, action='store',
                        help='Specify which source to use for the atomic radii list: choose between alvarez (vdw radii), batsanov (vdw radii), cordero (cov. radii) or pyykko (cov. radii) (default=alvarez). Note that typically when using van der Waals radii one needs to specify negative offsets.')
    parser.add_argument('-g', '--groupname_suffix', type=str, action='store',
                        help='Specify an additional suffix for the output group names, added after the initial group name but before the suffixes added by the layer finder (default = "").')
    parser.add_argument('GROUPNAME', type=str,
                        help='The name of the group of 3D structures')
    parser.set_defaults(vacuum=40, rotation=True, offsets=[-0.75,-0.7,-0.65,-0.6,-0.55],
                        margin_min=0., margin_max=0., margin_step=0.025, 
                        orthogonal_axis_2D=True, radii_source='alvarez',
                        groupname_suffix="")

    
    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])

    return parsed_data

if __name__ == '__main__':
    
    #############################################
    # CMDLINE PARSING
    parsed_data = parse_cmdline()
    if parsed_data.radii_source == 'batsanov':
        parsed_data.radii_source = 'vdw'
    
    group_name = parsed_data.GROUPNAME
    group = Group.get(name="{}".format(group_name))
    
    groupname_suffix = parsed_data.groupname_suffix
    
    if parsed_data.orthogonal_axis_2D:
        ortho_suffix = "_orthogonal"
    else:
        ortho_suffix = ""

    params_dict = { 'bond_margins': np.arange(parsed_data.margin_min,
                            parsed_data.margin_max+parsed_data.margin_step,
                            parsed_data.margin_step).tolist(),
                    'radii_offsets': parsed_data.offsets,
                    'lowdim_dict': {'rotation': True, # rotation = True puts the layer plane on x-y
                                    'vacuum_space': parsed_data.vacuum,
                                    'radii_source': parsed_data.radii_source,
                                    'orthogonal_axis_2D': parsed_data.orthogonal_axis_2D,
                                    'full_periodicity': False,
                                    },
                    'target_dimensionality': 2,
                    'output': {
                                'parent_structure_with_layer_lattice': not(parsed_data.orthogonal_axis_2D),
                                'rotated_parent_structure': parsed_data.rotation, # True to store the rotated 3D structure
                                'group_data': True,
                                },
                    }

    print "We use radius margins {}".format(params_dict['bond_margins'])
    
    # create all the groups
    group_2D, _ = Group.get_or_create(name="{}{}_2D{}".format(
                group_name,groupname_suffix,ortho_suffix))
    group_3D, _ = Group.get_or_create(name="{}{}_3D_layered".format(
                group_name,groupname_suffix))
    if params_dict['output']['parent_structure_with_layer_lattice']:
        group_3Dlattice, _ = Group.get_or_create(name="{}{}_3D_with2Dlattice"
                    "".format(group_name,groupname_suffix))
    if params_dict['output']['rotated_parent_structure']:
        group_3Drot, _ = Group.get_or_create(name="{}{}_3D_rotated"
                    "".format(group_name,groupname_suffix))        
    group_singlelayer, _ = Group.get_or_create(name="{}{}_3D_singlelayer"
                "".format(group_name,groupname_suffix))

    inline_params=ParameterData(dict=params_dict)

    for structure in group.nodes:
        print 20*"*"
        try:
            result_dict = get_lowdimfinder_results(structure=structure,
                                                   parameters=inline_params,
                                                   store=True)

        except KeyError as e:
            print "Missing atomic number in list of radii ({})".format(e.message)
            import traceback
            print "\n".join(traceback.format_exc().split('\n')[-5:])
            continue
        
        except Exception as e:
            import traceback
            print "full traceback: {0}".format(traceback.format_exc())
            raise e
            
        for k,v in result_dict.iteritems():
            if k.startswith('reduced_structure_'):
                group_3D.add_nodes([structure])
                group_2D.add_nodes([v])
                v.set_extras(structure.get_extras())
                print "The following 2D layer has been found: pk {}, "\
                      "{} ID {}, formula {}".format(v.pk,
                                                    get_source_db_name(structure, '?'),
                                                    get_source_id(structure, '?'),
                                                    v.get_formula())
                idx = int(k.split('reduced_structure_')[1].split('_')[0])
                group_data = result_dict['group_data_{}'.format(idx)].get_dict()
                #print result_dict['output_parameters'].get_dict()
                #print group_data['dimensionality']
                if len(group_data['dimensionality']) == 1:
                    group_singlelayer.add_nodes([structure])
            
            if k.startswith('rotated3D_structure_'):
                v.set_extras(structure.get_extras())
                group_3Drot.add_nodes([v])
            
            if k.startswith('layerlattice3D_structure_'):
                v.set_extras(structure.get_extras())
                group_3Dlattice.add_nodes([v])

    print "Done"
