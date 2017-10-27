#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


from aiida.workflows.user.epfl_theos.quantumespresso.chronos import ChronosWorkflow
from aiida.orm.data.structure import StructureData
machine = 'ntyp200-rhoxml-piz-dora'
pw_codename = 'pw-5.1.2-{}'.format(machine)
npools = 8
pseudo_family = 'pbesol_gbrv_12'
num_machines = 1
max_seconds = 7200

set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds":max_seconds,
            }
band_set_dict = {'resources':{'num_machines': num_machines},
            "max_wallclock_seconds": max_seconds,
            }

if machine.endswith('piz-dora'):
    set_dict["custom_scheduler_commands"] = "#SBATCH -A, --account=mr0"
    band_set_dict["custom_scheduler_commands"] = "#SBATCH -A, --account=mr0"

#structure = load_node(115119) # 2D, VBr2
# refine the structure to get correct spacegroup
#from pyspglib import spglib
#s_ase = structure.get_ase()
#print spglib.get_spacegroup(s_ase)
#(a,b,c)=spglib.refine_cell(s_ase,symprec=1e-3)
#s2_ase=s_ase.copy()
#s2_ase.set_cell(a)
#s2_ase.set_scaled_positions(b)
#print spglib.get_spacegroup(s2_ase)
#structure = StructureData(ase=s2_ase).store()
structure = load_node(128154) # 2D, VBr2, spacegroup corrected
#structure = load_node(132502) # 2D, BN, spacegroup corrected

pw_input_dict = {'CONTROL': {
                 'etot_conv_thr': 1e-3,
                 'forc_conv_thr': 1e-2,
                 },
                'SYSTEM': {
                 'ecutwfc': 30.,
                 'ecutrho': 120.,
                 'occupations': 'smearing',
                 'smearing': 'cold',
                 'degauss': 0.02,
                 },
                'ELECTRONS': {
                 'conv_thr': 1.e-10,
                 'electron_maxstep': 50,
                 },
                 'CELL': {'cell_dofree': '2Dxy'},
                 }

settings = {'cmdline':['-nk',str(npools)]}
band_settings = {'cmdline':['-nk',str(npools)]}

params = {'input': { 'clean_workdir': False,
                     'num_random_magnetizations': 2, # number of random starting magnetization states to test
                     'max_size_supercell': 2, # maximum size of supercells (in each periodic dimension) to test for magnetization
                     'distance_kpoints_in_mesh': 0.2, # the distance (in A^-1) between k-points in the mesh
                     'significant_energy_difference_per_atom': 1e-2, # the minimum energy difference (eV/per atom) that is considered significant, 
                                                            # when selecting the lowest energy structure
                     'directory_for_density_files': '~/charge_density/', 
                     },
          'structure': structure,
          'pseudo_family': pseudo_family,
            
          'pw_codename': pw_codename,
#          'pw_settings': settings,
          'pw_parameters': pw_input_dict,
          'pw_calculation_set': set_dict,
          'pw_input':{'volume_convergence_threshold': 5e-2,
                      'finish_with_scf': False,
                       },
                        
          'band_input':{'distance_kpoints_in_dispersion': 0.005,
                        'diagonalization': 'cg',
                         #'kpoints_path': [],
                         },
          'band_group_name': 'test',
          'band_calculation_set': band_set_dict,
#          'band_settings': band_settings,
           }

wf = ChronosWorkflow(params=params)
wf.start()


