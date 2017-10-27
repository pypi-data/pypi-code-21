#!/usr/bin/env runaiida

import sys,subprocess
from matplotlib.compat.subprocess import CalledProcessError

'''
=======================================================
Input for the SsspWorkflow (loop over pseudo families)
=======================================================

sys.argv[1] = element

Note: you must insert below the full path of the 'run_ssspworkflow.py' script.
      
'''


pseudo_families = [
                    'pslib.0.3.1_PBE_US',
                    'pslib.0.3.1_PBE_PAW',
                    'pslib.1.0.0_PBE_US',
                    'pslib.1.0.0_PBE_PAW',
                    'GBRV_1.2',
                    'GBRV_1.4',
                    'GBRV_1.5',
                    'SG15',
                    'SG15_1.1',
                    'THEOS',
                    'RE_Wentz',
                    'Goedecker',
                   ]

pseudo_dict = {                    
              'pslib.0.3.1_PBE_US': '031US',
              'pslib.0.3.1_PBE_PAW': '031PAW',
              'pslib.1.0.0_PBE_US': '100US',
              'pslib.1.0.0_PBE_PAW': '100PAW',
              'GBRV_1.2': 'GBRV-1.2',
              'GBRV_1.4': 'GBRV-1.4',
              'GBRV_1.5': 'GBRV-1.5',
              'SG15': 'SG15',
              'SG15_1.1': 'SG15-1.1',
              'THEOS': 'THEOS',
              'Goedecker': 'Goedecker',
              'RE_Wentz': 'Wentzcovitch',
#              'RE_Wentz_plus_nitrogen': 'Wentzcovitch',
#              'RE_pslib.1.0.0_PBE_US_plus_nitrogen': '100US',
#              'RE_pslib.1.0.0_PBE_PAW_plus_nitrogen': '100PAW',
                                  }


element = sys.argv[1]

print '***************************************'
print 'Launching SsspWorkflow for element={}'.format(element)
print '***************************************'

pseudos_not_launched = []
pseudos_launched = []
for pseudo_family in pseudo_families:
    if pseudo_family in ['SG15','SG15_1.1','Goedecker']:
        dual = 4
    else:
        if element in ['Fe','Mn']:
            dual = 12 # or 16?
        else:
            dual = 8

    results_group_name = '{}_{}'.format(element, pseudo_dict[pseudo_family])
    bands_group_name = '{}_{}_bands'.format(element, pseudo_dict[pseudo_family])
    
    print "    -> Launching", pseudo_family,"..."
    try:
        # WRITE YOUR FULL PATH IN THE FOLLOWING VARIABLE
        full_path = '/home/prandini/git/aiida/aiida/workflows/user/epfl_theos/examples/run_ssspworkflow.py'
        
        subprocess.check_output([full_path] + [element]  + [pseudo_family] + [str(dual)] + \
                                 [results_group_name] + [bands_group_name] )
        pseudos_launched.append(pseudo_family)
    except CalledProcessError:
        print 'WARNING! Impossible to launch SsspWorkflow for pseudofamily "{}"'.format(pseudo_family)
        pseudos_not_launched.append(pseudo_family)

print ''
print ''    
print "Pseudofamilies launched for element={} are: {}".format(element, [_ for _ in pseudos_launched])
print ''
print "Pseudofamilies not launched for element={} are: {}".format(element, [_ for _ in pseudos_not_launched])
print ''
    
    
    
    
    
