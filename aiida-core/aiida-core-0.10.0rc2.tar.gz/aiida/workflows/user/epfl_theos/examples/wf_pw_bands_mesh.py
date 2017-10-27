#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Nicolas Mounet, Giovanni Pizzi."


from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.kpoints import KpointsData
from aiida.common.example_helpers import test_and_get_code

def validate_upf_family(pseudo_family, all_species):
    """
    Validate if the pseudo_family is correct.

    :return: None
    """
    from aiida.orm import DataFactory

    elements = all_species
    UpfData = DataFactory('upf')
    valid_families = UpfData.get_upf_groups(filter_elements=elements)
    valid_families_names = [family.name for family in valid_families]
    if pseudo_family not in valid_families_names:
        raise ValueError("Invalid pseudo family '{}'. "
                         "Valid family names are: {}".format(
                         pseudo_family, ",".join(valid_families_names)))


send = True
codename = "pw_svn@theospc6"
pseudo_family = 'GBRV'
relaxation_scheme = 'scf'
kpoints_mesh = [4,4,4]

# bands parameters (npools is chosen automatically)
distance_kpoints_mesh = 0.2
number_of_bands = 10
bands_max_seconds = 60*60
#npools = 2

# PwRestartWorkflow parameters for automatic parallelization
target_time_seconds = 60 * 60
max_time_seconds = 4 * 60 * 60
max_num_machines = 1

bands_set_dict = {'resources':{
                               'num_machines': max_num_machines,
                               },
                  'max_wallclock_seconds':bands_max_seconds,
            }

try:
    structure = StructureData.get_subclass_from_pk(structure_pk)
except NameError:
    from ase.lattice.spacegroup import crystal
    alat = 3.568
    diamond_ase = crystal('C', [(0,0,0)], spacegroup=227,
                          cellpar=[alat, alat, alat, 90, 90, 90], primitive_cell=True)
    structure = StructureData(ase=diamond_ase)
    if send:
        structure.store()

# validate
test_and_get_code(codename,'quantumespresso.pw')
validate_upf_family(pseudo_family, structure.get_kind_names())
    
kpoints = KpointsData()
kpoints.set_kpoints_mesh(kpoints_mesh)
if send:
    kpoints.store()
#bands_kpoints = KpointsData()
#bands_kpoints.set_kpoints_mesh(bands_kpoints_mesh)
#if send:
#    bands_kpoints.store()    
    
settings = {}
bands_settings = {
                  #'cmdline':['-nk',str(npools)],
                  ## Uncomment the above line if you want to specify manually
                  ## the number of pools for the bands calculation
                  }

input_dict = {'CONTROL': {
                 'tstress': True,
                 },
              'SYSTEM': {
                 'ecutwfc': 40.,
                 'ecutrho': 320.,
                 },
              'ELECTRONS': {
                 'conv_thr': 1.e-10,
                 }}

pw_params = {#'pw_calculation':load_node(777),
            'codename': codename,
            'pseudo_family': pseudo_family,
            'structure': structure,
            'kpoints': kpoints,
            'parameters': input_dict,
            'settings': settings,
            'input': {
                      'volume_convergence_threshold': 0.01,
                      'relaxation_scheme': relaxation_scheme,
                      'automatic_parallelization': {
                                                    'max_wall_time_seconds': max_time_seconds,
                                                    'target_time_seconds': target_time_seconds,
                                                    'max_num_machines': max_num_machines
                                                    }
                      },
            'band_settings': settings,
            'band_calculation_set': bands_set_dict,
#            'band_kpoints':bands_kpoints,          
            'band_input':{
                           'number_of_bands': number_of_bands,
                           'distance_kpoints_in_mesh': distance_kpoints_mesh},
            'band_parameters_update': {
                                       'ELECTRONS':{
                                                    'diagonalization':'cg',
                                                    }
                                       }
            }

wf = PwWorkflow(params=pw_params)
if send:
    wf.start()
    print ("Launch PwWorkflow {}".format(wf.pk))
    print ("Parameters: {}".format(wf.get_parameters()))
else:
    print ("Would launch PwWorkflow")
    print ("Parameters: {}".format(wf.get_parameters()))



