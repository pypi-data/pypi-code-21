#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Nicolas Mounet, Giovanni Pizzi."


from aiida.workflows.user.epfl_theos.quantumespresso.phonondispersion import PhonondispersionWorkflow
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


pw_codename = "pw@theospc2"
ph_codename = "ph@theospc2"
q2r_codename = "q2r@theospc2"
matdyn_codename = "matdyn@theospc2"
pseudo_family = 'pbesol'
send = True
relaxation_scheme = 'scf'
kpoints_mesh = [4,4,4]
qpoints_mesh = [2,2,2]
max_seconds = 60*60
npools = 2
num_machines = 1
asr = 'simple'

set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":max_seconds,
            }
        
try:
    structure = StructureData.get_subclass_from_pk(structure_pk)
except NameError:
    from ase.lattice.spacegroup import crystal
    alat = 3.568
    diamond_ase = crystal('C', [(0,0,0)], spacegroup=227,
                          cellpar=[alat, alat, alat, 90, 90, 90], primitive_cell=True)
    structure = StructureData(ase=diamond_ase).store()
    
# validate
test_and_get_code(pw_codename,'quantumespresso.pw')
test_and_get_code(ph_codename,'quantumespresso.ph')
test_and_get_code(q2r_codename,'quantumespresso.q2r')
test_and_get_code(matdyn_codename,'quantumespresso.matdyn')
validate_upf_family(pseudo_family, structure.get_kind_names())
    
kpoints = KpointsData()
kpoints.set_kpoints_mesh(kpoints_mesh)
kpoints.store()

qpoints = KpointsData()
qpoints.set_kpoints_mesh(qpoints_mesh)
qpoints.store()

settings = {'cmdline':['-nk',str(npools)]}

pw_input_dict = {'CONTROL': {
                 'tstress': True,
                 },
              'SYSTEM': {
                 'ecutwfc': 40.,
                 'ecutrho': 320.,
                 },
              'ELECTRONS': {
                 'conv_thr': 1.e-10,
                 }}

ph_input_dict = {'INPUTPH':{'tr2_ph' : 1e-10}
                 }

pw_params = {'structure': structure,
             'pseudo_family': pseudo_family,
             
             'pw_calculation': load_node(60),
#              'pw_codename': pw_codename,
#              'pw_settings': settings,
#              'pw_parameters': pw_input_dict,
#              'pw_calculation_set': set_dict,
#              'pw_kpoints': kpoints,
#              'pw_input':{'relaxation_scheme': relaxation_scheme,
#                          'volume_convergence_threshold': 1.e-2,
#                          },
#             'ph_calculation': load_node(157),
             
             'ph_codename': ph_codename,
             'ph_parameters': ph_input_dict,
             'ph_settings': settings,
             'ph_calculation_set': set_dict,
             'ph_qpoints': qpoints,
             'ph_input': {'use_qgrid_parallelization': True},
             
             'dispersion_matdyn_codename': matdyn_codename,
             'dispersion_q2r_codename': q2r_codename,
             'dispersion_calculation_set': set_dict,
             'dispersion_settings': settings,
             'dispersion_input':{'distance_qpoints_in_dispersion':0.01,
                                 'asr': asr,
                                 'zasr': asr,
                                 }
            }

wf = PhonondispersionWorkflow(params=pw_params)
if send:
    wf.start()
    print ("Launch PwWorkflow {}".format(wf.pk))
    print ("Parameters: {}".format(wf.get_parameters()))
else:
    print ("Would launch PwWorkflow")
    print ("Parameters: {}".format(wf.get_parameters()))



