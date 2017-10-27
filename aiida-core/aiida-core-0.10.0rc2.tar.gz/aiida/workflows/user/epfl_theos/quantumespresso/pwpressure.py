# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow
from aiida.orm import DataFactory, CalculationFactory
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos import TheosWorkflowFactory
import numpy as np
from numbers import Number

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


UpfData = DataFactory('upf')
ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')
PwWorkflow = TheosWorkflowFactory('quantumespresso.pw')


class PwpressureWorkflow(Workflow):
    """
    Workflow to do two scf (one "normal", with the parameters in params['parameters'] and 
    one with much higher cutoffs), followed by a vc-relax where we apply the pressure
    difference found during the scf calcs (difference between highly converged
    and "normal").
    The "normal" scf calculation and the vc-relax one use the same input
    parameters.
    The "normal" scf calc. can be skipped if the key "low_cutoff_pressure" is present
    in the parameters, with the low cutoff pressure already given there 
    (units should be  GPa).
    """
    # Default values
    
    def __init__(self,**kwargs):
        super(PwpressureWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        """
        Starting step only verifies the input parameters
        """
        self.append_to_report("Checking input parameters")
        
        # define the mandatory keywords and the corresponding description to be 
        # printed in case the keyword is missing, for the PW parameters
        mandatory_keys = [('high_ecutwfc',Number,'the wave function cutoff for the initial highly converged scf calc.'),
                          ('high_ecutrho',Number,'the rho cutoff for the initial highly converged scf calc.'),
                          ]
        
        # retrieve and check the parameters
        params = self.get_parameters()
        helpers.validate_keys(params,mandatory_keys)
        
        # Note: I'm not checking extensively all the keys used by the workflow
        self.next(self.run_pw_scf)
        
    @Workflow.step
    def run_pw_scf(self):
        """
        initial scf step, to get the pressure difference between low and high
        cutoffs, to then apply to the stresses during a subsequent vc-relax
        """
        main_params = self.get_parameters()
        
        # retrieve PW parameters
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            elif k == 'group_name':
                # only the last vc-relax will be put into the group
                pass
            elif k.startswith('band_'):
                # only the last vc-relax will compute bands (if requested)
                pass
            else:
                pw_params[k] = v
        
        pw_params['input']['relaxation_scheme'] = 'scf'
        pw_params['input']['finish_with_scf'] = False

        for namelist in ['IONS', 'CELL']:
            pw_params['parameters'].pop(namelist,None)
        
        # force to print stress
        update_input_dict = helpers.default_nested_dict()
        update_input_dict['CONTROL']['tstress'] = True
        pw_params['parameters'] = helpers.update_nested_dict(pw_params['parameters'],
                                                                 update_input_dict)
        if 'low_cutoff_pressure' not in main_params.keys():
            # launch a first wf with cutoffs as in pw_params['parameters']
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching scf PW sub-workflow with ecutwfc={} "
                                  "and ecutrho={} (pk: {})".format(
                                    pw_params['parameters']['SYSTEM']['ecutwfc'],
                                    pw_params['parameters']['SYSTEM']['ecutrho'],
                                    wf_pw.pk))
            self.attach_workflow(wf_pw)
            wf_pw.start()        
        
        # change cutoffs in input parameters and relaunch
        pw_params['parameters']['SYSTEM']['ecutwfc'] = main_params['high_ecutwfc']
        pw_params['parameters']['SYSTEM']['ecutrho'] = main_params['high_ecutrho']
        wf_pw = PwWorkflow(params=pw_params)
        wf_pw.store()
        self.append_to_report("Launching scf PW sub-workflow with ecutwfc={} "
                              "and ecutrho={} (pk: {})".format(
                                pw_params['parameters']['SYSTEM']['ecutwfc'],
                                pw_params['parameters']['SYSTEM']['ecutrho'],
                                wf_pw.pk))
        self.attach_workflow(wf_pw)
        wf_pw.start()
        
        self.next(self.run_pw_vcrelax)
        
    @Workflow.step   
    def run_pw_vcrelax(self):
        """
        vc-relax step where cutoffs are back to their low values, applying
        the final pressure found in the previous step
        """
        main_params = self.get_parameters()
        # retrieve PW parameters
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            else:
                pw_params[k] = v
        
        pw_params['input']['relaxation_scheme'] = 'vc-relax'
        pw_params['input']['pressure_convergence'] = True
       
        # Retrieve the initial PW scf calculations
        wf_pw_list = list(self.get_step(self.run_pw_scf).get_sub_workflows().order_by('ctime'))
        high_cutoff_pw_calc = wf_pw_list[-1].get_result('pw_calculation')
        high_cutoff_pressure = np.trace(np.array(high_cutoff_pw_calc.res.stress))/3.
        if high_cutoff_pw_calc.res.stress_units not in ['GPascal', 'GPa']:
            raise ValueError("Wrong units for stresses, pw calc pk: {}"
                             "".format(high_cutoff_pw_calc.pk))
        
        try:
            low_cutoff_pressure = main_params['low_cutoff_pressure']
        except KeyError:
            low_cutoff_pw_calc = wf_pw_list[0].get_result('pw_calculation')
            low_cutoff_pressure = np.trace(np.array(low_cutoff_pw_calc.res.stress))/3.
            if low_cutoff_pw_calc.res.stress_units not in ['GPascal', 'GPa']:
                raise ValueError("Wrong units for stresses, pw calc pk: {}"
                                 "".format(low_cutoff_pw_calc.pk))
        
        delta_pressure = 10.*(high_cutoff_pressure - low_cutoff_pressure) # converted into KBar
        self.append_to_report("Applying target pressure P={} Kbar in vc-relax"
                              "".format(-delta_pressure))
        update_input_dict = helpers.default_nested_dict()
        update_input_dict['CELL']['press'] = - delta_pressure
        pw_params['parameters'] = helpers.update_nested_dict(pw_params['parameters'],
                                                             update_input_dict)

        wf_pw = PwWorkflow(params=pw_params)        
        wf_pw.store()
        self.append_to_report("Launching vc-relax PW sub-workflow (pk: {})".format(wf_pw.pk))
        self.attach_workflow(wf_pw)
        wf_pw.start()
        
        self.next(self.final_step)
            
    @Workflow.step
    def final_step(self):
        
        # Retrieve the final PW calculation
        wf_pw_list = list(self.get_step(self.run_pw_vcrelax).get_sub_workflows())
        pw_calculation = wf_pw_list[0].get_result('pw_calculation')
        self.add_result("pw_calculation", pw_calculation)
                
        # if the calculation has modified the structure, store it in output
        try:
            self.add_result("structure", pw_calculation.out.output_structure)
        except AttributeError:
            self.add_result("structure", pw_calculation.inp.structure)
        
        self.append_to_report("Scf + vc-relax workflow completed")
        
        # then exit
        self.next(self.exit)
        
