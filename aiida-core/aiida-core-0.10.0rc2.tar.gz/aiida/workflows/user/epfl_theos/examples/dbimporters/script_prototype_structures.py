#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

from aiida.orm import Group, DataFactory, load_node
from aiida.workflows.user.epfl_theos.dbimporters.utils import \
    composition_string, get_filter_duplicate_structures_results, composition_tuple
import numpy as np
import collections
from fractions import gcd
from pyspglib import spglib

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet, Marco Gibertini."


ParameterData = DataFactory('parameter')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with the parsed parameters.
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description="Prototype structures of a given group (i.e. find "
                    "common 'structures types'). The corresponding inline"
                    " calculations are put in a new group. WARNING: for "
                    "low dimensional structures with a lot of vacuum, "
                    "stol has to be reduced.")
    
    parser.add_argument('--ltol',type=float,default=0.2,
                        help='Fractional length tolerance (default = 0.2)')
    parser.add_argument('--stol',type=float, default=0.3,
                        help='Site tolerance. Defined as fraction of the '
                             'the average free length per atom = '
                             '(V/Nsites) ** (1/3) (default = 0.3). '
                             'WARNING: for low dimensional structures '
                             'with a lot of vacuum (i.e. large V), stol '
                             'has to be reduced.')
    parser.add_argument('--atol',type=float, default=5.0,
                        help='Angle tolerance in degrees (default = 5)')
    parser.add_argument('-f', '--framework', action='store_true',default=False,
                        help='Use the FrameworkComparator, i.e. regardless'
                             ' of species (default = False). WARNING: this'
                             ' might be very VERY slow if there are more '
                             'than a few hundreds structures (days)')
    parser.add_argument('-j','--jsonfile',type=str, action='store',
                        default=None,
                        help='Path of a json file where to put a dictionary'
                             ' containing the prototypes information, for'
                             ' each composition tuple (structure pks, '
                             'formulas and spacegroup with symprec=the first'
                             ' symmetry precision given by the -p option')
    parser.add_argument('-p','--symmetry_precisions', type=float, nargs='+',
                        help='Specify the list of symmetry precision to be tried'
                             ' for the spacegroup comparison (default=[0.5, 0.3, 0.1])')
    parser.add_argument('-s', '--suffix', type=str, action='store',
                        default="_prototypes_inline",
                        help='Specify an additional suffix for the output '
                             'group name, added after the initial group '
                             'name (default = "_prototypes_inline").')
    parser.add_argument('-n','--nostore', action='store_true',default=False,
                        help='Specify that you do not want to store the '
                             'inline calculations (default = False, i.e. store them)')
    parser.add_argument('GROUPNAME', type=str,
                        help='The name of the group of structures')

    # Parse and return the values
    parser.set_defaults(symmetry_precisions=[0.5, 0.3, 0.1])
    parsed_data = parser.parse_args(sys.argv[1:])

    return (parsed_data.GROUPNAME, parsed_data.ltol, parsed_data.stol, parsed_data.atol,
            parsed_data.framework, parsed_data.suffix, parsed_data.nostore,
            parsed_data.jsonfile,parsed_data.symmetry_precisions)


if __name__ == '__main__':
    import ase
    # Cmdline parsing  
    group_name, ltol, stol, atol, framework, suffix, nostore, jsonfile, symprecs = parse_cmdline()
    
    group = Group.get(name=group_name)
    
    structures = list(group.nodes)

    inline_params = ParameterData(dict={'ltol': ltol,'stol': stol,'angle_tol': atol,
                                        'anonymous': not(framework), # anonymous is True unless framework is True
                                        'framework': framework,
                                        'check_full_graph': True,
                                        'symprecs': symprecs,
                                        'attempt_supercell': True,
                                        })
    
    if not framework:
        # order structure by number of different species
        structure_num_species = collections.defaultdict(list)
        for ind, structure in enumerate(structures):
            num_species = composition_tuple(structure)
            structure_num_species[num_species].append(ind)
    else:
        structure_num_species = {0: range(len(structures))}
            
    if not nostore:
        the_group, _ = Group.get_or_create(name="{}{}".format(group_name,suffix))
    counter = 0
    total_counter = 0
    prototypes_dict = {}
    for num_species, structure_indices in structure_num_species.iteritems():
        prototypes_dict["{}".format(num_species)] = {'prototypes': []}
        input_structures_dict = dict([("structure_{}".format(i), structures[ind])
                                      for i,ind in enumerate(structure_indices)])
        
        result_dict = get_filter_duplicate_structures_results(parameters=inline_params,
                                                              store=not(nostore),
                                                              **input_structures_dict)

        groups = result_dict['output_parameters'].get_dict()

        if not nostore:
            # adding the inline calc. to the final group
            the_group.add_nodes([result_dict['output_parameters'].inp.output_parameters])
            prototypes_dict["{}".format(num_species)]['prototype_inline_calc_pk'] =\
                    result_dict['output_parameters'].inp.output_parameters.pk
        
        uuids_ref,uuids = zip(*sorted(groups.iteritems(), key=lambda x:-len(x[1])))
        print num_species," number of prototypes =",len(uuids)
        if jsonfile:
            for uuid_ref,the_uuids in zip(uuids_ref,uuids):
                structures_group = [load_node(uuid) for uuid in the_uuids]
                prototypes_dict["{}".format(num_species)]['prototypes'].append({
                        'uuids': the_uuids,
                        'formulas': [s.get_formula(mode='hill_compact') for s in structures_group],
                        'spacegroups': [spglib.get_spacegroup(s.get_ase(),symprec=symprecs[0])
                                        for s in structures_group]})
               
        print [len(v) for v in groups.values()]
        counter += len(groups.keys())
        total_counter += sum([len(v) for v in groups.values()])
 
    print "{} structures analyzed, {} prototypes found".format(total_counter,counter)
    
    if jsonfile:
        # store in json
        import json
        with open(jsonfile,'w') as f:
            f.write(json.dumps(prototypes_dict))
