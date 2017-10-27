#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
"""
Build the primitive cell structures of crystal found in CifNodes.
"""

from aiida.orm import Group
from aiida.workflows.user.epfl_theos.dbimporters.utils import \
		get_standardize_structure_results

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet, Philippe Schwaller."


ParameterData = DataFactory('parameter')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with (groupname, suffix, precision).
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Refine and build the primitive structures from the StructureData nodes a given group')
    
    parser.add_argument('-p', '--precision', type=float, action='store',
                        help='The precision to be used to correct the spacegroup (default=5e-3)')
    parser.add_argument('-s', '--suffix', type=str, action='store',
                        help='The suffix of the new group to be created (default = _primitive)')
    parser.add_argument('-n','--nostore', action='store_true',default=False,
                        help='Specify that you do not want to store the '
                             'inline calculations (default = False, i.e. store them)')
    parser.add_argument('GROUPNAME', type=str,
                        help='The name of the group of initial CifData nodes')
    parser.set_defaults(suffix='_primitive', precision=5e-3)

    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])

    return (parsed_data.GROUPNAME, parsed_data.suffix, 
            parsed_data.precision, parsed_data.nostore)


if __name__ == '__main__':
    #############################################
    # CMDLINE PARSING
    group_name, suffix, symprec, nostore = parse_cmdline()
    
    group = Group.get(name='{}'.format(group_name))
    if not(nostore):
		group_new, _ = Group.get_or_create(name="{}{}".format(group_name,suffix))
    
    structures = list(group.nodes)
    inline_params = ParameterData(dict={'symprec': symprec,
                                        'to_primitive': True})

    for structure in structures:
		result_dict = get_standardize_structure_results(parameters=inline_params,
														structure=structure,
														store=not(nostore),
														print_progress=True)
        
		#print "Old: {},{}".format(structure.cell,structure.get_formula())
		#print "New: {},{}".format(result_dict['standardized_structure'].cell,
		#						   result_dict['standardized_structure'].get_formula())
		if not(nostore):
			try:
				group_new.add_nodes([result_dict['standardized_structure']])
			except KeyError:
				print " Pb for structure {}: {}\n -> adding to the group "\
					   "the initial structure".format(structure.pk,
					result_dict['output_parameters'].get_dict()['warnings'])
				group_new.add_nodes([structure])
        
