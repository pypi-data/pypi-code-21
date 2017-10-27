#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
"""
Build the primitive cell structures of crystal found in CifNodes.
"""

from aiida.orm import Group
from aiida.workflows.user.epfl_theos.dbimporters.utils import \
        primitive_structure_inline, get_source_id, get_source_db_name
from aiida.orm.data.cif import parse_formula
from pyspglib import spglib
import numpy as np

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrius Merkys, Nicolas Mounet, Giovanni Pizzi, Philippe Schwaller."


KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
ParameterData = DataFactory('parameter')
CifData = DataFactory('cif')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with (groupname, suffix, precision).
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Refine and build the primitive structures from the CifData nodes a given group')
    
    parser.add_argument('-m', '--missingH_group', type=str, action='store',
                        help='The name of the group to put the cifs with missing H (or D) atoms (default = cifs_with_missing_H_atoms)')
    parser.add_argument('-p', '--precision', type=float, action='store',
                        help='The precision to be used to correct the spacegroup (default=5e-3)')
    parser.add_argument('-s', '--suffix', type=str, action='store',
                        help='The suffix of the new group to be created (default = _primitive)')
    parser.add_argument('GROUPNAME', type=str,
                        help='The name of the group of initial CifData nodes')
    parser.set_defaults(suffix='_primitive', precision=5e-3,
                        missingH_group='cifs_with_missing_H_atoms')

    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])

    return (parsed_data.GROUPNAME, parsed_data.suffix, 
            parsed_data.precision, parsed_data.missingH_group,)


def get_closest_cif(nodes):
    """
    Get closest cif data in the parents of all nodes
    :param nodes: list of nodes
    """
    node_type = 'CifData'
    depth=models.DbPath.objects.filter(child__in=nodes,
        parent__type__contains=node_type).distinct().order_by('depth').values_list('depth')[0][0]
    q = models.DbPath.objects.filter(parent__type__contains=node_type,
                            child__in=nodes,depth=depth).distinct()
    return CifData.query(children__in=nodes,child_paths__in=q).distinct().order_by('ctime')


if __name__ == '__main__':
    #############################################
    # CMDLINE PARSING
    group_name, suffix, symprec, missingH_group_name = parse_cmdline()
    
    converter = 'pymatgen'
    
    group = Group.get(name='{}'.format(group_name))
    group_new, _ = Group.get_or_create(name="{}{}".format(group_name,suffix))
    missingH_group, _ = Group.get_or_create(name='{}'.format(missingH_group_name))
    
    cifs = list(group.nodes)
    inline_params = ParameterData(dict={'symprec': symprec,
                                        'converter': converter})
    prim_structures = list(group_new.nodes)

    if prim_structures:
        # check CIFs that have already been analysed
        analysed_pks = [_[0] for _ in get_closest_cif(prim_structures).values_list('pk')]
        if len(analysed_pks) != len(prim_structures):
            raise ValueError("Number of closest cifs parents and number of structures "
                             "in {} is not the same (resp. {} and {})"
                             "".format(group_new.name,len(analysed_pks),len(cifs)))
    else:
        analysed_pks = []

    for cif in cifs:

        if cif.pk not in analysed_pks:
            
            try:
                structure_from_cif = cif._get_aiida_structure(
                    converter=converter, store=False)
            except (IndexError, TypeError, ValueError) as e:
                print "#################################################"
                print "Error in pymatgen CifParser"
                print "{}\n ({} ID: {}, cif formula: {})".format(
                            e.message,
                            get_source_db_name(cif, '?'),
                            get_source_id(cif, '?'),
                            cif.get_formulae()[0])
                print "#################################################"
                continue
            
            # skip if cif has some missing H (or D) atoms (present in the 
            # formula but not in the parsed structure)
            cif_species = parse_formula(cif.get_formulae()[0]).keys()
            structure_species = structure_from_cif.get_symbols_set()
            if ( cif.has_attached_hydrogens() or 
                 ('H' in cif_species and 'H' not in structure_species) or
                 ('D' in cif_species and 'D' not in structure_species) ):
                missingH_group.add_nodes([cif])
                print "================================================="
                print "Cif has missing H (or D) atoms (cif pk: {}, cif formula {},"\
                      " structure formula {})".format(cif.pk,cif.get_formulae(),
                                                      structure_from_cif.get_formula())
                continue

            #print "Refining structure {} ID: {}, cif pk: {}".format(
            #                get_source_db_name(cif, '?'),
            #                get_source_id(cif, '?'),
            #                cif.pk)
                
            spg_no_orig = cif.get_spacegroup_numbers()[0] # spg number from the initial cif file
            spg_no_raw = spglib.get_symmetry_dataset(structure_from_cif.get_ase())['number']
        
            # build primitive structure
            _,result_dict = primitive_structure_inline(
                    parameters=inline_params, cif=cif)
            primitive_structure = result_dict['primitive_structure_spg']
            
            primitive_structure.set_extras(cif.get_extras())
            
            spg_no_new = spglib.get_symmetry_dataset(primitive_structure.get_ase())['number']
            
            # check if primitive structure spacegroup differs from CIF spacegroup
            if spg_no_orig != spg_no_new:
                print "================================================="
                print "Warning: space groups from cif file and found by spglib do not match"
                print "Initial CifData pk: {}, final primitive StructureData pk: {}"\
                      "".format(cif.pk, primitive_structure.pk)
                print "{} {} {} {} {}".format(cif.get_formulae()[0],
                        primitive_structure.get_formula(),
                        spg_no_orig,spg_no_raw,spg_no_new)
            
            group_new.add_nodes([primitive_structure])
