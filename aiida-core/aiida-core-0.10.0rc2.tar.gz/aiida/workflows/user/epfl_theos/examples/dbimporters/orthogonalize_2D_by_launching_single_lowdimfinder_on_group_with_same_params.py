#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

"""
On a group of 2D structures (pk as first argument), launch the single_lowdimfinder
inline calc. with the same parameters as the ones used to get the initial 2D,
except that orthogonal_axis_2D is set to True (and we output also the rotated structures).
Puts all the resulting 2D structures into a group (name=second argument)
"""
import sys
from aiida.orm import DataFactory
from aiida.orm import Group
from aiida.common.exceptions import NotExistent
from aiida.orm.calculation.inline import InlineCalculation
from aiida.workflows.user.epfl_theos.dbimporters.utils import get_single_lowdimfinder_results

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


ParameterData = DataFactory('parameter')

grp = sys.argv[1]
try:
    group = Group.get(pk=grp)
except NotExistent:
    group = Group.get(grp)
store = True

print group.pk, group.name

# create the new 2D group
if store:
    new_group_name = sys.argv[2]
    new_group_2D, _ = Group.get_or_create(name=new_group_name)

for structure in group.nodes:
    print 20*"*"
    ic = structure.get_inputs(InlineCalculation)[0]
    bulk_structure = ic.inp.structure
    inline_params_dict = ic.inp.parameters.get_dict()
    # deactivate outputs
    inline_params_dict['output'] = {'rotated_parent_structure': True}
    inline_params_dict['lowdim_dict']['orthogonal_axis_2D'] = True
    inline_params = ParameterData(dict=inline_params_dict)
    try:
        print "Searching layers in structure {} with pk {}"\
              "".format(structure.get_formula(),bulk_structure.pk)

        result_dict = get_single_lowdimfinder_results(structure=bulk_structure,
                                                      parameters=inline_params,
                                                      store=store)

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
        if k.startswith('reduced_structure_') and sum(v.pbc)==2:
            if store:
                new_group_2D.add_nodes([v])
            print "The following 2D layer has been found: pk {}, "\
                  "formula {}".format(v.pk,v.get_formula())
            #if abs(structure.cell[2][0])>1e-8:
            #    print structure.cell,v.cell

print "Done"
