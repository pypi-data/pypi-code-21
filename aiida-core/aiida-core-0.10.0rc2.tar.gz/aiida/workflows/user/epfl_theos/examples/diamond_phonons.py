#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


from aiida.workflows.user.epfl_theos.quantumespresso.phonondispersion import PhonondispersionWorkflow
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.kpoints import KpointsData
pw_codename = 'pw-5.1.2-local'
ph_codename = 'ph-5.1.2-local'
q2r_codename = 'q2r-5.1.2-local'
matdyn_codename = 'matdyn-5.1.2-local'
relaxation_scheme = 'vc-relax'
npools = 2
pseudo_family = 'pz-rrkjus-pslib031'
num_machines = 1
max_seconds = 10
relaxation_scheme = 'scf'
kpoints_mesh = [4,4,4]
qpoints_mesh = [2,2,2]
asr = 'simple'

kpoints = KpointsData()
kpoints.set_kpoints_mesh(kpoints_mesh)
kpoints.store()

qpoints = KpointsData()
qpoints.set_kpoints_mesh(qpoints_mesh)
qpoints.store()

set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":max_seconds,
            }
band_set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":100,
            }
dispersion_set_dict = {'resources':{'num_machines': 1},
            "max_wallclock_seconds":100,
            }

from ase.lattice.spacegroup import crystal
alat = 3.568
diamond_ase = crystal('C', [(0,0,0)], spacegroup=227,
                      cellpar=[alat, alat, alat, 90, 90, 90], primitive_cell=True)
structure = StructureData(ase=diamond_ase).store()
#structure = load_node(67386) # diamond structure
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

ph_input_dict = {'INPUTPH':{'tr2_ph' : 1e-16}
                 }
settings = {'cmdline':['-nk',str(npools)]}
band_settings = {'cmdline':['-nk',str(npools)]}
#dispersion_settings = {}

params = {'structure': structure,
          'pseudo_family': pseudo_family,
            
          'pw_codename': pw_codename,
          'pw_settings': settings,
          'pw_parameters': pw_input_dict,
          'pw_calculation_set': set_dict,
          'pw_kpoints': kpoints,
          'pw_input':{'relaxation_scheme': relaxation_scheme,
                      'volume_convergence_threshold': 1.e-2,
                      'finish_with_scf': False,
                       },
                        
          'band_input':{'distance_kpoints_in_dispersion': 0.05,
                        #'kpoints_path': [],
                        'clean_workdir': True,
                        },
          'band_group_name': 'test',
          'band_calculation_set': band_set_dict,
          'band_settings': band_settings,
          'band_parameters_update': {
                                       'ELECTRONS':{
                                                    'diagonalization':'cg',
                                                    }
                                     },
             
          'ph_codename': ph_codename,
          'ph_parameters': ph_input_dict,
          'ph_settings': settings,
          'ph_calculation_set': set_dict,
          'ph_qpoints': qpoints,
          'ph_input': {'use_qgrid_parallelization': True,
                       'clean_workdir': True,
                       },
            
          'dispersion_matdyn_codename': matdyn_codename,
          'dispersion_q2r_codename': q2r_codename,
          'dispersion_calculation_set': dispersion_set_dict,
          #'dispersion_settings': dispersion_settings,
          'dispersion_group_name': 'test',
          'dispersion_input':{'distance_qpoints_in_dispersion':0.01,
                              'asr': asr,
                              'zasr': asr,
                              'clean_workdir': True,
                              }
           }

wf = PhonondispersionWorkflow(params=params)
wf.start()


