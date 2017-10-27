# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow
from aiida.orm import DataFactory, CalculationFactory, Group
from aiida.orm.calculation.inline import make_inline
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos import TheosWorkflowFactory
import numpy as np

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

_default_degauss_from_QE = 0. # Ry

@make_inline
def get_denser_kpoints_grid_inline(parameters,kpoints,structure):
    """
    Get new kpoints with a denser mesh than that in kpoints
    :param parameters: ParameterData object containing the dictionary
        {'distance_kpoints_step_factor': float indicating by which factor we multiply
                                 the current distance between k-points
         }
    :param kpoints: KPointsData object containing the current k-points 
        (must be defined from a mesh)
    :param structure: the structure (used to get the reciprocal cell)
    :return: dictionary of the form
        {'output_kpoints': KPointsData object with the new k-points,
         'output_parameters': ParameterData with dictionary
                             {'distance_kpoints_in_mesh': float with the new
                                                          distance between k-pts
                              }
         }
    """
    kpoints_mesh = kpoints.get_kpoints_mesh()[0]
    distance_step_factor = parameters.get_dict()['distance_kpoints_step_factor']
    pbcs = structure.pbc
    # get the current distance between k-points
    kpoints_dummy=KpointsData()
    kpoints_dummy.set_cell_from_structure(structure)
    distance_kpoints_in_mesh = np.average(np.array([np.linalg.norm(b)/float(k) 
                                for pbc,k,b in 
                                zip(pbcs,kpoints_mesh, kpoints_dummy.reciprocal_cell)
                                if pbc]))
    # update the distance between k-points and prepare the new kpoints
    the_kpoints_mesh = [int(np.ceil(round(np.linalg.norm(b)/(distance_kpoints_in_mesh*distance_step_factor),5)))
                        if pbc else 1 for pbc,b in zip(pbcs,kpoints_dummy.reciprocal_cell)]
    # force the mesh to be "even"
    the_kpoints_mesh = [k + (k % 2) if pbc else 1
                        for pbc,k in zip(pbcs,the_kpoints_mesh)]
    # force the mesh to increase in any case
    the_kpoints_mesh = [k if (k>kold or not pbc) else k+2 
                        for (pbc,k,kold) in zip(pbcs,the_kpoints_mesh,kpoints_mesh)]
    the_kpoints=KpointsData()
    # We keep the same mesh offset as before
    the_kpoints.set_kpoints_mesh(the_kpoints_mesh,kpoints.get_kpoints_mesh()[1])
    the_distance_kpoints_in_mesh = np.average(np.array([np.linalg.norm(b)/float(k) 
                                for pbc,k,b in 
                                zip(pbcs,the_kpoints_mesh, kpoints_dummy.reciprocal_cell)
                                if pbc]))
    return {'output_kpoints': the_kpoints,
             'output_parameters': ParameterData(dict={
                    'distance_kpoints_in_mesh': the_distance_kpoints_in_mesh})
            }


class PwkpointsWorkflow(Workflow):
    """
    Workflow to check the convergence of pw scf vs k-points, and to find an optimal
    value for the smearing parameter (the one that leads to the smallest number
    of k-points when converged).

    Additional inputs (compared to the pw workflow) are (all optional, but you
    should have at least one convergence threshold defined and higher than zero):
        'force_convergence_threshold': a float -> the convergence threshold on the forces (eV/angstrom),
        'energy_convergence_threshold': a float -> the convergence threshold on the energy (eV)
        'stress_convergence_threshold': a float -> the convergence threshold on the stress (GPa)
        'smearing_parameters_to_test': a list -> the list of smearing parameters to test (Ry) (can be empty),
    
    .. note:: The units on the thresholds are NOT those of etot_conv_thr, forc_conv_thr 
        and press_conv_thr in QE-PW (resp. Ry, Ry/Bohr and kbar). All convergence 
        criteria are on absolute values (i.e. not in relative).
    """
    # Default values
    
    def __init__(self,**kwargs):
        super(PwkpointsWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        """
        Starting step only verifies the input parameters
        """
        self.append_to_report("Checking input parameters")
        
        # define the mandatory keywords and the corresponding description to be 
        # printed in case the keyword is missing, for the PW parameters
        mandatory_keys = []
        
        # retrieve and check the parameters
        params = self.get_parameters()
        helpers.validate_keys(params,mandatory_keys)
        
        if not any([k in ('force_convergence_threshold',
                          'energy_convergence_threshold',
                          'stress_convergence_threshold') for k in params.keys()]):
            raise ValueError("At least one of the keys 'force_convergence_threshold',"
                             " 'energy_convergence_threshold' or "
                             "'stress_convergence_threshold' should be present "
                             "in the parameters")
        # Note: I'm not checking extensively all the keys used by the workflow
        self.next(self.run_pw_smearing_loop)
        
    @Workflow.step
    def run_pw_smearing_loop(self):
        # do a loop on the list of smearings if present, otherwise do only
        # a single smearing (or no smearing), as defined in params['parameters']
        
        main_params = self.get_parameters()
        # retrieve PW parameters
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            elif k == 'group_name':
                # don't pass the group name (will be used to put only the final
                # calculations)
                pass
            else:
                pw_params[k] = v            
                
        if main_params.get('smearing_parameters_to_test',[]):
            
            for degauss in main_params['smearing_parameters_to_test']:
                # launch a wf for each smearing parameter
                update_input_dict = helpers.default_nested_dict()
                update_input_dict['SYSTEM']['degauss'] = degauss
                pw_params['parameters'] = helpers.update_nested_dict(pw_params['parameters'],
                                                                 update_input_dict)
                wf_pw = PwkpointsconvergenceWorkflow(params=pw_params)
                wf_pw.store()
                self.append_to_report("Launching PW k-points convergence "
                                      "sub-workflow with smearing parameter= {} "
                                      "(pk: {})".format(
                                        pw_params['parameters']['SYSTEM']['degauss'],
                                        wf_pw.pk))
                self.attach_workflow(wf_pw)
                wf_pw.start()        
        
        else:
            # launch a single k-points convergence workflow
            wf_pw = PwkpointsconvergenceWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching PW k-points convergence "
                                  "sub-workflow (pk: {})".format(wf_pw.pk))
            self.attach_workflow(wf_pw)
            wf_pw.start()        
       
        self.next(self.final_step)
                    
    @Workflow.step
    def final_step(self):
        
        main_params = self.get_parameters()
        # Retrieve the final PW calculation
        wf_list = list(self.get_step(self.run_pw_smearing_loop).get_sub_workflows())
        distance_kpoints_units = wf_list[0].get_result('distance_kpoints_units')
        # check what smearing parameter leads to the smallest kpoints mesh
        max_distance_kpoints = 0.
        for wf in wf_list:
            distance_kpoints = wf.get_result('distance_kpoints')
            if distance_kpoints > max_distance_kpoints:
                pw_calculation = wf.get_result('pw_calculation')
                kpoints_mesh = wf.get_result('kpoints_mesh')
                max_distance_kpoints = distance_kpoints
        
        smearing_parameter = pw_calculation.inp.parameters.get_dict(
                            )['SYSTEM'].get('degauss',_default_degauss_from_QE)
        
        self.add_result("pw_calculation", pw_calculation)
        self.add_result("smearing_parameter", smearing_parameter)
        self.add_result("smearing_parameter_units", "Ry")
        self.add_result("kpoints_mesh", kpoints_mesh)
        self.add_result("distance_kpoints", max_distance_kpoints)
        self.add_result("distance_kpoints_units", distance_kpoints_units)
        
        group_name = main_params.get('group_name',None)
        if group_name:
            # create or get the group
            group, created = Group.get_or_create(name=group_name)
            if created:
                self.append_to_report("Created group '{}'".format(group_name))
            # put the pw calculation into the group
            group.add_nodes(pw_calculation)
            self.append_to_report("Adding pw calculation to group '{}'".format(group_name))
               
        self.append_to_report("kpoints + smearing convergence workflow completed")
        
        # then exit
        self.next(self.exit)
        

class PwkpointsconvergenceWorkflow(Workflow):
    """
    Workflow to check the convergence of pw scf vs k-points (for a single
    smearing parameter).

    Additional inputs (compared to the pw workflow) are (all optional, but you
    should have at least one convergence threshold defined and higher than zero):
        'force_convergence_threshold': a float -> the convergence threshold on the forces (eV/angstrom),
        'energy_convergence_threshold': a float -> the convergence threshold on the energy (eV)
        'stress_convergence_threshold': a float -> the convergence threshold on the stress (GPa)
    
    .. note:: The units on the thresholds are NOT those of etot_conv_thr, forc_conv_thr 
        and press_conv_thr in QE-PW (resp. Ry, Ry/Bohr and kbar). All convergence 
        criteria are on absolute values (i.e. not in relative).
    """
    # Default values
    _default_distance_kpoints_step_factor = 0.8
    _max_kpoints_iterations = 10
    
    def __init__(self,**kwargs):
        super(PwkpointsconvergenceWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        self.next(self.run_pw_loop)
        
    @Workflow.step
    def run_pw_loop(self):
        """
        loop of scf calculations to get convergence over number of k-points
        """
        params = self.get_parameters()
        # Retrieve the list of pw calculations already done in this step
        wf_pw_list = list(self.get_step(self.run_pw_loop).get_sub_workflows().order_by('ctime'))
        
        has_to_launch = False
        if wf_pw_list:
            pw_calc = wf_pw_list[-1].get_result('pw_calculation')

            if len(wf_pw_list) > params.get('max_kpoints_iterations',
                                            self._max_kpoints_iterations):
                self.append_to_report("ERROR: Max number of iterations for"
                                      " k-points convergence reached "
                                      "(last calc={})".format(pw_calc.pk))
                raise Exception("ERROR: maximum number of iterations reached "
                                "(increase 'max_kpoints_iterations')")
            elif len(wf_pw_list) > 1:
                older_pw_calc = wf_pw_list[-2].get_result('pw_calculation')
            else:
                try:
                    older_pw_calc = params['pw_calculation']
                except KeyError:
                    pass
            energy_thr = params.get('energy_convergence_threshold',np.inf)
            force_thr = params.get('force_convergence_threshold',np.inf)
            stress_thr = params.get('stress_convergence_threshold',np.inf)
            try:
                delta_energy = abs(pw_calc.res.energy - older_pw_calc.res.energy) 
                delta_force = np.max(np.abs(older_pw_calc.out.output_array.get_array('forces')[0]
                                            - pw_calc.out.output_array.get_array('forces')[0]))
                delta_stress = np.max(np.abs(np.array(older_pw_calc.res.stress)
                                             - np.array(pw_calc.res.stress)))
                has_to_launch = (delta_energy > energy_thr or
                                 (delta_force > force_thr or delta_stress > stress_thr))
                self.append_to_report("k-points convergence {}reached; max "
                                      "differences between 2 last calculations: "
                                      "energy: {}, forces: {}, stresses: {}"
                                      "".format("not " if has_to_launch else "",
                                                delta_energy, delta_force,
                                                delta_stress))
            except NameError:
                has_to_launch = True
            
            if has_to_launch:
                # generate new kpoints
                inline_params = ParameterData(dict={
                    'distance_kpoints_step_factor': params.get('distance_kpoints_step_factor',
                                                           self._default_distance_kpoints_step_factor)
                                                })
                _, result_dict = get_denser_kpoints_grid_inline(parameters=inline_params,
                                            kpoints=pw_calc.inp.kpoints,
                                            structure=params['structure'])
                the_kpoints = result_dict['output_kpoints']
                the_distance_kpoints_in_mesh = result_dict['output_parameters'].get_dict(
                                                    )['distance_kpoints_in_mesh']

        else:
            the_kpoints = params['kpoints']
            kpoints_dummy=KpointsData()
            kpoints_dummy.set_cell_from_structure(params['structure'])
            the_distance_kpoints_in_mesh = np.average(np.array([np.linalg.norm(b)/float(k) 
                    for pbc,k,b in zip(params['structure'].pbc,the_kpoints.get_kpoints_mesh()[0],
                    kpoints_dummy.reciprocal_cell) if pbc]))
            has_to_launch = True
            
        if has_to_launch:
            # retrieve PW parameters
            pw_params = {}
            for k,v in params.iteritems():
                if k.startswith('pw_'):
                    new_k = k[3:] # remove pw_
                    pw_params[new_k] = v
                else:
                    pw_params[k] = v
            
            pw_params['input']['relaxation_scheme'] = 'scf'
            pw_params['input']['finish_with_scf'] = False
    
            for namelist in ['IONS', 'CELL']:
                pw_params['parameters'].pop(namelist,None)
                
            update_input_dict = helpers.default_nested_dict()
            update_input_dict['CONTROL']['tstress'] = True
            update_input_dict['CONTROL']['tprnfor'] = True
            pw_params['parameters'] = helpers.update_nested_dict(pw_params['parameters'],
                                                                 update_input_dict)
            
            pw_params['kpoints'] = the_kpoints
            
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching scf PW sub-workflow with "
                                  "distance between kpoints in mesh= {} ,"
                                  " kpoints mesh= {} (pk: {})"
                                  "".format(the_distance_kpoints_in_mesh,
                                    the_kpoints.get_kpoints_mesh(),wf_pw.pk))
            self.attach_workflow(wf_pw)
            wf_pw.start()
            self.next(self.run_pw_loop)
        
        else:
            self.next(self.final_step)
        
    @Workflow.step
    def final_step(self):
        
        # Retrieve the two last PW calculations
        wf_pw_list = list(self.get_step(self.run_pw_loop).get_sub_workflows())
        # the following is the last calculation, over converged
        pw_calculation = wf_pw_list[-1].get_result('pw_calculation')
        self.add_result("pw_calculation_over_convergence", pw_calculation)
        # get now last but one calculation, that is converged
        if len(wf_pw_list) > 1:
            older_pw_calculation = wf_pw_list[-2].get_result('pw_calculation')
        else:
            older_pw_calculation = self.get_parameter('pw_calculation')
        self.add_result("pw_calculation", older_pw_calculation)
        distance_kpoints = older_pw_calculation.inp.kpoints.inp.output_kpoints.out.output_parameters.get_dict(
                                                                    )['distance_kpoints_in_mesh']
        self.add_result("kpoints_mesh", older_pw_calculation.inp.kpoints.get_kpoints_mesh())
        self.add_result("distance_kpoints", distance_kpoints)
        self.add_result("distance_kpoints_units", "1 / Angstrom")
        self.append_to_report("k-points convergence workflow completed")
        
        # then exit
        self.next(self.exit)
        
