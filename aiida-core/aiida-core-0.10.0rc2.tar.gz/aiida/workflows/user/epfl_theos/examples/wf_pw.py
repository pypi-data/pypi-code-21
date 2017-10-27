#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Nicolas Mounet, Giovanni Pizzi."


from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
from aiida.orm import DataFactory
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.kpoints import KpointsData
from aiida.common.example_helpers import test_and_get_code


def validate_upf_family(pseudo_family, all_species):
    """
    Validate if the pseudo_family is correct.
    """
    elements = all_species
    UpfData = DataFactory('upf')
    valid_families = UpfData.get_upf_groups(filter_elements=elements)
    valid_families_names = [family.name for family in valid_families]
    if pseudo_family not in valid_families_names:
        raise ValueError("Invalid pseudo family '{}'. "
                         "Valid family names are: {}".format(
            pseudo_family, ",".join(valid_families_names)))


codename = "pw-v6.1@localhost"
pseudo_family = 'SSSP'
send = True
relaxation_scheme = 'vc-relax'
target_time_seconds = 60 * 60
max_time_seconds = 24 * 60 * 60
max_num_machines = 1

set_dict = {'resources':{'num_machines': max_num_machines},
           "max_wallclock_seconds":max_time_seconds,
           }
# set_dict = {'custom_scheduler_commands': '#PBS -A e89-ucl_p'}

try:
    structure = StructureData.get_subclass_from_pk(structure_pk)
except NameError:
    from ase.lattice.spacegroup import crystal

    alat = 3.568
    diamond_ase = crystal('C', [(0, 0, 0)], spacegroup=227,
                          cellpar=[alat, alat, alat, 90, 90, 90], primitive_cell=True)
    structure = StructureData(ase=diamond_ase).store()

# validate
test_and_get_code(codename, 'quantumespresso.pw')
validate_upf_family(pseudo_family, structure.get_kind_names())

kpoints = KpointsData()
kpointsmesh = [4, 4, 1]
# the lines below are generating the k-points from a density in reciprocal space
# distance_kpoints = 0.2 # in 1/angstrom
# kpoints = KpointsData()
# kpoints.set_cell_from_structure(initial_structure)
# kpoints.set_kpoints_mesh_from_density(distance_kpoints,force_parity=True)
kpoints.set_kpoints_mesh(kpointsmesh)
kpoints.store()

# settings = {'cmdline':['-nk',str(npools)]}
settings = {}

input_dict = {
    'CONTROL': {
        'tstress': True,
    },
    'SYSTEM': {
        'ecutwfc': 40.,
        'ecutrho': 320.,
    },
    'ELECTRONS': {
        'conv_thr': 1.e-10,
    }
}

pw_params = {
    'codename': codename,
    'pseudo_family': pseudo_family,
    'calculation_set': set_dict,
    'structure': structure,
    'kpoints': kpoints,
    'parameters': input_dict,
    'settings': settings,
    'input': {
        'volume_convergence_threshold': 0.1,
        'relaxation_scheme': relaxation_scheme,
        'automatic_parallelization': {
            'max_wall_time_seconds': max_time_seconds,
            'target_time_seconds': target_time_seconds,
            'max_num_machines': max_num_machines
        }
    },
}

wf = PwWorkflow(params=pw_params)
if send:
    wf.start()
    print ("Launch PwWorkflow {}".format(wf.pk))
    print ("Parameters: {}".format(wf.get_parameters()))
else:
    print ("Would launch PwWorkflow")
    print ("Parameters: {}".format(wf.get_parameters()))
