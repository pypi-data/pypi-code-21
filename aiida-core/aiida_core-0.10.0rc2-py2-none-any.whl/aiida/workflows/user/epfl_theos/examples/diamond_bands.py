#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."

from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.kpoints import KpointsData
codename = 'pw-5.1.1-local@localhost'
relaxation_scheme = 'vc-relax'
npools = 2
npools_bands = 8
pseudo_family = 'pz-rrkjus-pslib031'
kpoints = KpointsData()
kpoints_mesh = [8,8,8]
kpoints.set_kpoints_mesh(kpoints_mesh)
kpoints.store()
num_machines = 1
max_seconds = 10
set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":max_seconds,
            }
band_set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":100,
            }
from ase.lattice.spacegroup import crystal
alat = 3.568
diamond_ase = crystal('C', [(0,0,0)], spacegroup=227,
                      cellpar=[alat, alat, alat, 90, 90, 90], primitive_cell=True)
structure = StructureData(ase=diamond_ase).store()
#structure = load_node(67386)
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
settings = {'cmdline':['-nk',str(npools)]}
band_settings = {'cmdline':['-nk',str(npools_bands)]}
pw_params = {'codename': codename,
            'pseudo_family': pseudo_family,
            'calculation_set': set_dict,
            'structure': structure,
            'kpoints': kpoints,
            'parameters': input_dict,
            'settings': settings,
            'input':{'volume_convergence_threshold': 1.e-2,
                     'relaxation_scheme': relaxation_scheme,
                     'finish_with_scf': False,
                     },
            'band_input':{'distance_kpoints_in_dispersion': 0.01,
                          #'kpoints_path': [],
                          },
            'band_parameters_update': {
                                       'ELECTRONS':{
                                                    'diagonalization':'cg',
                                                    }
                                       },
            'band_calculation_set': band_set_dict,
            'band_settings': band_settings,
            }
wf = PwWorkflow(params=pw_params)
wf.start()


