#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

import sys
from aiida.orm import DataFactory
from aiida.orm.calculation.inline import optional_inline
from aiida.common.exceptions import NotExistent,InternalError

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


StructureData = DataFactory('structure')
ParameterData = DataFactory('parameter')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with (group name or pk, suffix, nostore, precision, additional_vacuum).
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Build the primitive cell, re-center it, and set the '
                    'vacuum space as 2*thickness + additional_vacuum, '
                    'for all the 2D AiiDA structures of a given group')
    
    parser.add_argument('-v', '--additional_vacuum', type=float, action='store',
                        help='Additional vacuum in angstrom (on top of 2*thickness) to be put in the cell (default = 12. angstrom)')
    parser.add_argument('-p', '--precision', type=float, action='store',
                        help='The precision to be used by spglib to correct the spacegroup (default=5e-3)')
    parser.add_argument('-s', '--suffix', type=str, action='store',
                        help='The suffix of the new group to be created (default = _primitive_recenter_vac_[ADDITIONAL_VACUUM])')
    parser.add_argument('-n', '--nostore', action='store_true',
                        help='True to avoid storing the resulting inline calculation (default = False, i.e. we store the inline calc. and its output')
    parser.add_argument('GROUPNAME_OR_PK',
                        help='The name or pk of the group of initial StructureData nodes')
    parser.set_defaults(suffix='_primitive_recenter_vac_{}', precision=5e-3,
                        additional_vacuum=12.0,nostore=False)

    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])

    return (parsed_data.GROUPNAME_OR_PK, parsed_data.suffix, parsed_data.nostore,
            parsed_data.precision, parsed_data.additional_vacuum)


@optional_inline
def get_primitive_recenter_reset_vacuum_2D_inline(structure,parameters):
    """
    For a 2D structure: get the primitice cell, put back the out-of-plane
    axis on the third cell vector, put the center of symmetry at the origin,
    and change the third cell parameter to 2*thickness + additional_vacuum
    :param structure: an AiiDA StructureData object
    :param parameters: a ParameterData object with the dictionary:
        {'symprec': symmetry precision  for the spglib refinement (default: 5e-3),
         'additional_vacuum': additional vacuum in angstrom (default: 12.),
         }
    :return: a dictionary of the form:
        {'output_structure': primitive, re-centered and vacuum-changed StructureData object,
         'output_parameters': ParameterData with the dict
                        {'warnings': a list of warnings,
                         'thickness': slab thickness in angstrom}
         }
    
    TODO: fix it! it can be buggy (use get_info_2D_structure to get the thickness)
    """
    from pyspglib import spglib
    import numpy as np
    from aiida.workflows.user.epfl_theos.dbimporters.utils import standardize_structure_inline
    
    # check the pbc
    if sum(structure.pbc)!=2 or structure.pbc[2]:
        raise ValueError("Structure should be 2D and non-periodic dimension"
                         " should be along z")
    
    params_dict = parameters.get_dict()
    additional_vacuum = params_dict.get('additional_vacuum',12.)
    symprec = params_dict.get('symprec',5e-3)
    warnings = []
    
    # get the primitive structure
    res_dict = standardize_structure_inline(parameters=ParameterData(
                        dict={'to_primitive': True,'symprec': symprec}),
                    structure=structure,store=False)
    prim_structure = res_dict['standardized_structure']
    
    # some checks (pbc and orthogonality of third axis)
    prim_cell = np.array(prim_structure.cell)
    if sum(prim_structure.pbc)!=2 or prim_structure.pbc[2]:
        warnings.append("Primitive structure not built")
        warnings.append("Wrong pbc of primitive structure ({}, cell {})"
                         "".format(prim_structure.pbc,prim_structure.cell))
        warnings.append("Volume ratio between primitive and initial "
                        "structures was {}".format(
                prim_structure.get_cell_volume()/structure.get_cell_volume()))
    if max(abs(prim_cell[2].dot(prim_cell[0])),
        abs(prim_cell[2].dot(prim_cell[1])))>1e-8:
        warnings.append("Primitive structure not built")
        warnings.append("Non orthogonal third axis in primitive structure "
                         "(cell: {})".format(prim_structure.cell))
        warnings.append("Volume ratio between primitive and initial "
                        "structures was {}".format(
                prim_structure.get_cell_volume()/structure.get_cell_volume()))
    if warnings:
        prim_structure = structure
        prim_cell = np.array(structure.cell)
    
    # get the thickness
    s_dummy=StructureData(ase=prim_structure.get_ase()*[1,1,2]) # supercell in z direction
    vacuum_z = max(np.diff(sorted([si.position[2] for si in s_dummy.sites])))
    thickness = prim_structure.cell[2][2]-vacuum_z
    
    # re-center position in z if needed
    if any([abs(vacuum_z-e)<1e-8 for e in np.diff(
            sorted([si.position[2] for si in prim_structure.sites]))]):
        prim_ase = prim_structure.get_ase()
        prim_ase.translate(prim_cell[2]/2.)
        # note: "get_scaled_positions" wraps inside the unit cell only 
        # coordinates along the pbc
        prim_ase.set_scaled_positions([p%[1.,1.,1.]
                                for p in prim_ase.get_scaled_positions()])
        prim_structure = StructureData(ase=prim_ase)
        prim_cell = np.array(prim_structure.cell)
    
    # change the vacuum space
    prim_cell[2,2] = 2.*thickness + additional_vacuum
    average_z = np.average([si.position[2] for si in prim_structure.sites])
    # build the structure with changed vacuum space (putting also the 
    # layer around z=0)
    structure_ase = prim_structure.get_ase()
    structure_ase.translate([0,0,-average_z])
    structure_ase.set_cell(prim_cell)
    # note: by default in ASE, atomic positions are NOT scaled when the cell is changed
    
    # now we check the inversion symmetry and if it is there we re-center
    # the structure
    sym_data = spglib.get_symmetry_dataset(structure_ase)
    translations = [t for r,t in zip(sym_data['rotations'],sym_data['translations'])
         if (r==-np.eye(3)).all()]
    if len(translations) > 1:
        raise InternalError("Several inversion symmetries detected")
    if translations:
        translation = translations[0]
        structure_ase.translate(-translation.dot(prim_cell)/2.)
    
    new_sym_data = spglib.get_symmetry_dataset(structure_ase)
    new_translations = [t for r,t in zip(new_sym_data['rotations'],
                new_sym_data['translations']) if (r==-np.eye(3)).all()]
    if new_translations and any([(abs(t)>1e-8 and abs(1.-t)>1e-8)
                                 for t in new_translations[0]]):
        warnings.append("still some translation(s) for inversion symmetry: {}".format(new_translations))
    
    the_structure=StructureData(ase=structure_ase)
    return {'output_structure': the_structure,
            'output_parameters': ParameterData(dict={'thickness': thickness,
                                                     'warnings': warnings})}

def get_primitive_recenter_reset_vacuum_2D_results(print_progress=True,
                                                   store=True,**kwargs):

    """
    Get the results from the get_primitive_recenter_reset_vacuum_2D_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the get_primitive_recenter_reset_vacuum_2D_inline function
    and get its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    from aiida.workflows.user.epfl_theos.dbimporters.utils import objects_are_equal
    
    structure = kwargs['structure']
    result_dict = None
    for ic in InlineCalculation.query(inputs=structure).order_by('ctime'):
        try:
            if ( ic.get_function_name() == 'get_primitive_recenter_reset_vacuum_2D_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), kwargs['parameters'].get_dict())
                 and ic.get_inputs_dict().get('structure',Node()).pk == structure.pk
                 and ('output_structure' in ic.get_outputs_dict())):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass

    if result_dict is not None:
        if print_progress:
			print " get_primitive_recenter_reset_vacuum_2D_inline already run for {} -> "\
				   "we do not re-run".format(structure.pk)
    else:
        if print_progress:
			print "Launch get_primitive_recenter_reset_vacuum_2D_inline for {}...".format(structure.pk)
        result_dict = get_primitive_recenter_reset_vacuum_2D_inline(store=store,
                                                                    **kwargs)
    return result_dict

if __name__ == '__main__':

    group_name_or_pk, suffix, nostore, precision, additional_vacuum = parse_cmdline()
    
    parameters = ParameterData(dict={'additional_vacuum': additional_vacuum,
                                     'symprec': precision})

    try:
        g = Group.get(group_name_or_pk)
    except NotExistent:
        g = Group.get(pk=int(group_name_or_pk))
    
    if not nostore:
        new_g, _ = Group.get_or_create(name="{}{}".format(g.name,
                suffix.format(str(additional_vacuum).replace('.','p').replace('p0',''))))
        print "New group name:",new_g.name

    for structure in g.nodes:
        print "="*30
        print structure.get_formula(),structure.pk
        result_dict = get_primitive_recenter_reset_vacuum_2D_results(
                                                    structure=structure,
                                                    parameters=parameters,
                                                    store=not(nostore))
        output_params = result_dict['output_parameters'].get_dict()
        print "thickness=",output_params['thickness']
        if output_params['warnings']:
            print "warnings:\n","\n".join(output_params['warnings'])

        if not nostore:
            new_g.add_nodes([result_dict['output_structure']])
    
