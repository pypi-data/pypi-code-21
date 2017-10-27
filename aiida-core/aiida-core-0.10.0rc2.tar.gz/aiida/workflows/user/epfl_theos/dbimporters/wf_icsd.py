# -*- coding: utf-8 -*-
"""
Workflow to clean a cif file with cif_filter
"""
from aiida.common import aiidalogger
from aiida.orm.workflow import Workflow
from aiida.orm import Calculation, Code, Computer, Data, Group
from aiida.common.exceptions import WorkflowInputValidationError
from aiida.orm import CalculationFactory, DataFactory
from aiida.orm.calculation.inline import make_inline

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Andrius Merkys, Nicolas Mounet, Giovanni Pizzi, Philippe Schwaller."

logger = aiidalogger.getChild('WorkflowDemo')

def l_are_equals(a,b):
    # function to compare lengths
    return abs(a - b) <= 1e-5

def a_are_equals(a,b):
    # function to compare angles (actually, cosines)
    return abs(a - b) <= 1e-5


@make_inline
def lowdimfinder_inline(aiida_struc,lowdim_params):
    from aiida.tools.lowdimfinder import LowDimFinder
    import numpy as np

    ParameterData = DataFactory('parameter')

    lowdim_dict = lowdim_params.get_dict()

    low_dim_finder = LowDimFinder(
                            aiida_structure=aiida_struc, vacuum_space=lowdim_dict['vacuum_space'],
                            cov_bond_margin=lowdim_dict['cov_bond_margin'], max_supercell=lowdim_dict['max_supercell'],
                            min_supercell=lowdim_dict['min_supercell'], rotation=lowdim_dict['rotation'],
                            full_periodicity=False, cov_bond_list=lowdim_dict['cov_bond_list'], custom_bonds=lowdim_dict['custom_bonds'])
    dimensionality = low_dim_finder.get_group_data()['dimensionality']

    dimensionalty_params = ParameterData(dict={'dimensionality':dimensionality})
    aiida_reduced_struc_list = low_dim_finder.get_reduced_aiida_structures()
    rotated_3D_structures = low_dim_finder._get_rotated_structures()

    result_dict = {}
    for i, struc in enumerate(aiida_reduced_struc_list):
        # re-order the sites (that's to avoid color differences
        # between 3D and 2D in vmd...)
        struc._set_attr('sites',sorted(
            struc.get_attr('sites'),
            reverse=True))

        if dimensionality[i] == 2:
            # check the hexagonal case
            cell = struc.cell
            a = np.linalg.norm(np.array(cell[0]))
            b = np.linalg.norm(np.array(cell[1]))
            cosphi = np.dot(np.array(cell[0]),np.array(cell[1]))/a/b
            if l_are_equals(a,b) and a_are_equals(cosphi,0.5):
                # change the lattice vectors to get a "standard" hexagonal cell
                new_b = np.array(cell[1])-np.array(cell[0])
                the_cell = [cell[0], new_b.tolist(), cell[2]]
                struc.cell = the_cell
        result_dict['reduced_structure_{}'.format(str(i))] = struc

    for i, struc in enumerate(rotated_3D_structures):
        # re-order the sites (that's to avoid color differences
        # between 3D and 2D in vmd...)
        struc._set_attr('sites',sorted(
            struc.get_attr('sites'),
            reverse=True))
        result_dict['rotated3D_{}'.format(str(i))] = struc




    result_dict['dimensionality_params'] = dimensionalty_params

    return result_dict

@make_inline
def primitive_structure_inline(cif):
    aiida_struc_primitive = cif._get_aiida_structure(primitive_cell = True)
    return {"primitive_struc": aiida_struc_primitive}




class WorkflowIcsdLowDim(Workflow):
    def __init__(self,**kwargs):
        super(WorkflowIcsdLowDim, self).__init__(**kwargs)




    # prepare cod calculation
    def prepare_cod_calculation(self, code_name):
        params                 = self.get_parameters()
        icsd_id                 = params['icsd_id']
        num_machines           = 1
        max_wallclock_seconds  = 60*15

        code = Code.get(code_name)

        calc = code.new_calc()

        computer = params.get('cod_computer', None)

        if computer is None:
            calc.set_computer(code.get_remote_computer())
        else:
            calc.set_computer(computer)

        calc.set_max_wallclock_seconds(max_wallclock_seconds)
        calc.set_resources({"num_machines": num_machines,
                            "num_mpiprocs_per_machine": 1})
        calc.store()
        return calc


    def add_group_name(self,aiida_node,subgroup=''):
        params = self.get_parameters()
        group_name = params.get('group_name',None)
        if group_name is not None:

            group_name =  group_name + subgroup
            # create or get the group, and add the calculation
            group, created = Group.get_or_create(name=group_name)
            if created:
                self.append_to_report("Creating group '{}'".format(group_name))
            self.append_to_report("Adding structure to group '{}'"
                                  "".format(group_name))
            group.add_nodes(aiida_node)



    @Workflow.step
    def start(self):


        self.next(self.fetch_and_filter)
        #self.next(self.search_low_dimensionality)


    @Workflow.step
    def fetch_and_filter(self):
        from aiida.tools.dbimporters.plugins.icsd import IcsdDbImporter
        CifData       = DataFactory('cif')
        ParameterData = DataFactory('parameter')

        params = self.get_parameters()
        icsd_id = params['icsd_id']






        calc = self.prepare_cod_calculation(params['cif_filter_code'])

        cif = params['cif']

        calc.use_cif(cif)

        filter_params = ParameterData(dict={'use-perl-parser':True}).store()

        calc.use_parameters(filter_params)

        self.append_to_report("Filtering of {} started".format(icsd_id))
        self.attach_calculation(calc)


        self.next(self.remove_bibliography)

    @Workflow.step
    def remove_bibliography(self):
        CifData       = DataFactory('cif')
        ParameterData = DataFactory('parameter')
        params = self.get_parameters()
        icsd_id = params['icsd_id']

        #get filtered cif
        completed = self.get_step_calculations(self.fetch_and_filter)[0]
        cif = completed.get_outputs(CifData)[0]

        self.append_to_report("Filtered cif obtained {}.".format(cif.pk))

        completed.out.remote_folder._clean()

        self.append_to_report("Cleaning remote_folder of calc {}".format(completed.pk))

        calc = self.prepare_cod_calculation(params['cif_select_code'])

        select_params = ParameterData(dict={'use-perl-parser':True,'invert':True, 'tags': '_publ_author_name,_citation_journal_abbrev'}).store()

        calc.use_cif(cif)
        calc.use_parameters(select_params)

        self.append_to_report("Removing bibliography of {}".format(icsd_id))
        self.attach_calculation(calc)
        self.next(self.search_low_dimensionality)

    @Workflow.step
    def search_low_dimensionality(self):
        import numpy as np
        from pyspglib import spglib
        from aiida.orm.node import Node
        import time, os

        layered_3D_list = []
        layered_2D_list = []


        CifData       = DataFactory('cif')
        ParameterData = DataFactory('parameter')
        KpointsData = DataFactory('array.kpoints')
        StructureData = DataFactory('structure')

        params = self.get_parameters()

        icsd_id = params['icsd_id']

        #completed = self.get_step_calculations(self.fetch_and_filter)[0]

        completed = self.get_step_calculations(self.remove_bibliography)[0]
        cif = completed.get_outputs(CifData)[0]

        self.append_to_report("Cleaning remote_folder of calc {}".format(completed.pk))

        completed.out.remote_folder._clean()

        #cif = Node.get_subclass_from_pk(484)

        self.append_to_report("Getting primitive structure of {}".format(icsd_id))

        calc, primitive_struc_dict = primitive_structure_inline(cif=cif)

        aiida_struc_primitive = primitive_struc_dict['primitive_struc']

        aiida_struc_primitive.set_extras({'icsd_nr': params['icsd_id']})

        self.add_group_name(aiida_struc_primitive,subgroup='_3D')



        self.append_to_report("Searching lower dimensionality structure".format(icsd_id))

        lowdim_dict = params['lowdim_params'].get_dict()

        self.append_to_report("Using covalent bond radius margins: {}".format(lowdim_dict['cov_bond_margin_list']))
        self.append_to_report("And supercell sizes from {} to {}".format(lowdim_dict['min_supercell'],lowdim_dict['max_supercell']))



        count = 0
        for cov_bond_margin in lowdim_dict['cov_bond_margin_list']:
            for supercell in range(lowdim_dict['min_supercell'],lowdim_dict['max_supercell']+1):

                lowdimfinder_inline_dict = {
                    'cov_bond_margin': cov_bond_margin,
                    'rotation': lowdim_dict['rotation'], # rotation = True puts the layer plane on x-y (for 2D)
                    'max_supercell': supercell,
                    'min_supercell': supercell,
                    'vacuum_space': lowdim_dict['vacuum_space'],
                    'cov_bond_list': lowdim_dict.get('cov_bond_list', 'b801115j'),
                    'custom_bonds': lowdim_dict.get('custom_bonds', []),
                    }

                lowdimfinder_inline_params = ParameterData(dict=lowdimfinder_inline_dict).store()


                calc, result_dict =  lowdimfinder_inline(aiida_struc = aiida_struc_primitive,lowdim_params=lowdimfinder_inline_params)

                # What's the way to store output of inline calculation??

                dimensionality_params = result_dict.pop('dimensionality_params')

                dimensionality_list = dimensionality_params.get_dict()['dimensionality']


                aiida_reduced_struc_list = [result_dict['reduced_structure_{}'.format(str(i))] for i in range(len(result_dict)/2)]

                rotated_3D_structures_list = [result_dict['rotated3D_{}'.format(str(i))] for i in range(len(result_dict)/2)]


                for dimensionality, aiida_reduced_struc, rotated3D in zip(dimensionality_list,aiida_reduced_struc_list,rotated_3D_structures_list):

                    if dimensionality == 2:

                        spacegroup_reduced = spglib.get_symmetry_dataset(aiida_reduced_struc.get_ase(),
                                                       symprec=1e-3)['number']
                        

                        aiida_reduced_struc.set_extras({'icsd_nr': params['icsd_id'],
                                                  'layer_nr':count,})



                        if params['icsd_id'] not in layered_3D_list:

                            self.add_group_name(aiida_struc_primitive,subgroup='_2D_3D')
                            aiida_struc_primitive.label ="primitive icsd"
                            layered_3D_list.append(params['icsd_id'])

                            self.add_group_name(rotated3D,subgroup='_rot3D')
                            rotated3D.label = "rotated 3D"


                            self.append_to_report("Initial formula of 3D structure: {}".format(aiida_struc_primitive.get_formula()))

                        if ( "{}_{}_{}".format(aiida_reduced_struc.get_formula(),spacegroup_reduced,params['icsd_id'])
                             not in layered_2D_list):

                            layered_2D_list.append("{}_{}_{}".format(aiida_reduced_struc.get_formula(),spacegroup_reduced,params['icsd_id']))
                            
                            self.add_group_name(aiida_reduced_struc,subgroup='_2D')
                            aiida_reduced_struc.label = "layer"


                        if ( "{}_{}_{}_{}".format(aiida_reduced_struc.get_formula(),spacegroup_reduced,params['icsd_id'],cov_bond_margin )
                             not in layered_2D_list):

                            layered_2D_list.append("{}_{}_{}_{}".format(aiida_reduced_struc.get_formula(),spacegroup_reduced,params['icsd_id'],cov_bond_margin))
                            count += 1

                            self.add_group_name(aiida_reduced_struc,subgroup='_2D_m{}'.format(cov_bond_margin))

                        self.append_to_report('For a covalent_bond_margin of {} and supercell {}'.format(cov_bond_margin,supercell))

                        self.append_to_report('Following 2D layer has been found: {}'.format(aiida_reduced_struc.pk))
                        self.append_to_report('spacegroup: {}, rotated 3D pk {}, icsd_id {}'.format(spacegroup_reduced,rotated3D.pk, icsd_id))


        #self.append_to_report('layered_3D_list: {}'.format(layered_3D_list))
        #self.append_to_report('layered_2D_list: {}'.format(layered_2D_list))

        self.next(self.final_step)

    @Workflow.step
    def final_step(self):


        self.next(self.exit)






