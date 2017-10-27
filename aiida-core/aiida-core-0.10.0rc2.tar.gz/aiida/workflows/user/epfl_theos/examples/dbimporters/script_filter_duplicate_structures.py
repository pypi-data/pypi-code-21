#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

from aiida.orm import Group, DataFactory, load_node
from aiida.workflows.user.epfl_theos.dbimporters.utils import \
    composition_string, get_filter_duplicate_structures_results
import numpy as np
import collections
import re
from itertools import groupby

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Marco Gibertini, Nicolas Mounet."


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
        description='Filter out duplicates of structures in a given group. '
                    'WARNING: for low dimensional structures with a lot of '
                    'vacuum, stol has to be reduced.')
    
    parser.add_argument('--ltol',type=float,default=0.2,
                        help='Fractional length tolerance (default = 0.2)')
    parser.add_argument('--stol',type=float, default=0.3,
                        help='Site tolerance. Defined as fraction of the '
                             'average free length per atom = '
                             '(V/Nsites) ** (1/3) (default = 0.3). '
                             'WARNING: for low dimensional structures '
                             'with a lot of vacuum (i.e. large V), stol '
                             'has to be reduced.')
    parser.add_argument('--atol',type=float, default=5.0,
                        help='Angle tolerance in degrees (default = 5)')
    parser.add_argument('-c', '--composition', type=str, nargs='*',
                        help='The composition to be considered for '
                             'structure filtering (default = None)')
    parser.add_argument('-s', '--suffix', type=str, action='store',
                        default="_dup_filtered",
                        help='Specify an additional suffix for the output '
                             'group name, added after the initial group '
                             'name (default = "_dup_filtered").')
    parser.add_argument('-n','--nostore', action='store_true',default=False,
                        help='Specify that you do not want to store the '
                             'inline calculations (default = False, i.e. '
                             'store them)')
    parser.add_argument('GROUPNAME', type=str,
                        help='The name of the group of structures')

    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])

    return (parsed_data.GROUPNAME, parsed_data.ltol, parsed_data.stol, parsed_data.atol,
            parsed_data.composition, parsed_data.suffix, parsed_data.nostore)


if __name__ == '__main__':
    import ase
    # Cmdline parsing  
    group_name, ltol, stol, atol, composition, suffix, nostore = parse_cmdline()
    
    group = Group.get(name=group_name)
    
    structures = list(group.nodes)

    inline_params = ParameterData(dict={'ltol': ltol,'stol': stol,'angle_tol': atol})
    
    # TODO: if we decide to add an extra it is better to check if the extra already exists or not
    #       Is it needed to add extra? Or we simply create the structure_string_id each time?

    # Add to each structure an extra corresponding to the unique string identifying the composition
    structure_string_id = collections.defaultdict(list)
    for ind, structure in enumerate(structures):
        string_id = composition_string(structure)
        # structure.set_extra('composition_string_id',string_id)
        structure_string_id[string_id].append(ind)   

    if composition: 
        # Rewrite the composition string in a unique way as defined in the composition_string function
        # first we join the entries in a single string
        composition = ''.join(composition)

        # Separate the string into elements and create a dictionary with element, occurrence pairs
        elem_occ_pair = collections.defaultdict(int)
        for elem in re.findall('[A-Z][^A-Z]*',composition):
            if elem.isalpha():
                elem_occ_pair[ase.atom.atomic_numbers[elem]] += 1
            else:
                elem, num = [''.join(g) for _,g in groupby(elem,str.isdigit)]
                elem_occ_pair[ase.atom.atomic_numbers[elem]] += int(num)

        # finally, create the unique string by calling the function
        composition = composition_string(dict(elem_occ_pair))
        the_group, _ = Group.get_or_create(name="{}_{}{}".format(group_name,composition,suffix))
        
        input_structures_dict = dict([("structure_{}".format(i), structures[ind])
                                      for i,ind in enumerate(structure_string_id.get(composition,[])) ])
        if input_structures_dict:
            result_dict = get_filter_duplicate_structures_results(parameters=inline_params,
                                                                  store=not(nostore),
                                                                  **input_structures_dict)

            # next line is for testing purposes (if we comment @make_inline)
            #result_dict =  filter_duplicate_structures_inline(inline_params, **input_structures_dict)            

            groups = result_dict['output_parameters'].get_dict()

            # adding the filtered structures to the final group
            the_group.add_nodes([load_node(_) for _ in groups.keys()])

            print [len(v) for v in groups.values()]
            counter = len(groups.keys())
            total_counter = sum([len(v) for v in groups.values()])
            
    else:
        the_group, _ = Group.get_or_create(name="{}{}".format(group_name,suffix))
        counter = 0
        total_counter = 0
        for string_id, structure_indices in structure_string_id.iteritems():
            input_structures_dict = dict([("structure_{}".format(i), structures[ind])
                                          for i,ind in enumerate(structure_indices)])
            result_dict = get_filter_duplicate_structures_results(parameters=inline_params,
                                                                  store=not(nostore),
                                                                  **input_structures_dict)

            # next line is for testing purposes (if we comment previous line and @make_inline)
            #result_dict =  filter_duplicate_structures_inline(inline_params, **input_structures_dict)

            groups = result_dict['output_parameters'].get_dict()

            # adding the filtered structures to the final group            
            the_group.add_nodes([load_node(_) for _ in groups.keys()])
            
            print [len(v) for v in groups.values()]
            counter += len(groups.keys())
            total_counter += sum([len(v) for v in groups.values()])
 
    print "{} structures analyzed, {} of them finally selected".format(total_counter,counter)
