# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow
from aiida.orm import CalculationFactory, Code, DataFactory, Group
from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.quantumespresso.phonondispersion import PhonondispersionWorkflow
from aiida.orm.calculation.inline import make_inline
from aiida.common.example_helpers import test_and_get_code

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Marco Gibertini, Nicolas Mounet, Giovanni Pizzi."

ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')

@make_inline
def get_transformations_inline(amplitudes,deformation):
    """
    Inline calculation to produce a set of transformations obtained by 
    multiplying the deformation matrix with each amplitude, and
    adding the identity.
    :param amplitudes: ParameterData with a dictionary of the form
        {'amplitudes': list of amplitude of deformation}
    :param deformation: ParameterData with a dictionary of the form
        {'deformation_matrix': a 3x3 deformation matrix (as a list of 
                           length-3 tuples)
         }
    :return: a dictionary of the form
        {'transformation_0': ParameterData containing the first 3x3 
                             transformation matrix
         'transformation_1': ParameterData containing the second 3x3 
                             transformation matrix
         etc.
         }
    
    .. note:: All the ParameterData objects in the output dictionary
        contain a dictionary of the form:
        {'transformation_matrix': 3x3 matrix (list of length-3 tuples)
         }
    """
    import numpy as np
    
    amplitudes = parameters_scaling.get_dict()['amplitudes']
    deformation = deformation.get_dict()['deformation_matrix']
    
    result_dict = {}
    for i,amplitude in enumerate(amplitudes):
        result_dict['transformation_{}'.format(i)] = ParameterData(
            dict={'transformation_matrix': (np.identity(3) + 
                        amplitude*np.array(deformation)).tolist()})
        
    return result_dict
    

@make_inline
def deform_structure_inline(structure, transformation):
    """
    Method to deform a structure according to a 3x3 general linear 
    transformation. Both site positions and cell are affected.
    :param structure: the initial structure to be deformed
    :param transformation: a ParameterData with a dictionary of the form
        {'transformation_matrix': 3x3 matrix (encoded as a list of
                                  length-3 tuples) representing the
                                  transformation (i.e. the matrix to be 
                                  multiplied by the old cell & atomic positions,
                                  to get the new cell & atomic positions)
         }
    
    :return: a dictionary of the form
        {'deformed_structure': deformed_structure}
        where deformed_structure is the StructureData object representing the
        new (deformed) structure
    """
    from copy import deepcopy
    import numpy as np

    # initialize the new structure
    deformed_structure = StructureData()
    
    # retrieve all kinds from structure and append to the deformed structure
    for kind in structure.kinds:
        deformed_structure.append_kind(kind)
    
    # build the new structure cell
    deformed_structure.cell = np.array(structure.cell).dot(np.array(
                            transformation.get_dict['transformation']))
    
    # build the new position of each site
    for site in structure.sites:
        deformed_site = deepcopy(site)
        deformed_site.position = np.array(site.position).dot(transformation.get_array('transformation'))
        deformed_structure.append_site(deformed_site)
    
    return {'deformed_structure': deformed_structure}



class QuasiharmonicWorkflow(Workflow):
    """
    Workflow to compute the free energy using the quasi-harmonic approximation.
    
    Results posted in results depend on the input parameters. 
    The largest set of data that can be put in the results consists in:
    * relaxed structure, if relaxed
    * pw_calculation, if the total energy needed to be computed
    * band_structure or band_structure1, band_structure2 (for spin polarized 
      calculations), containing the electronic band structure
    * ph_folder, i.e. the folder with all dynamical matrices
    * ph_calculation, if the phonon calculation was not parallelized over qpoints
    * phonon_dispersion, a BandsData object
    
    Input description.
    The input includes first a dictionary with the parameters of the quasi-harmonic calculations

    'input': { 'deformation_amplitudes':[-0.01,0.00,0.01,0.02], # This is a list of deformation amplitudes 
               'scale_directions': [[0,1],[2]], # The deformations will be just a scaling of the directions that are grouped together in a list
                OR 
               'deformations': list_of_3x3_deformations, # Each deformation matrix will be multiplied by the scaling factors 
                                                         # and added to the identity to get the full transformation
    },

    Then we have other entries that follow closely the input of the various subworkflows    
    Electronic part:
    'structure': structure,
    'pseudo_family': pseudo_family,    
    'pw_codename': pw_codename,
    'pw_settings': settings,
    'pw_parameters': pw_input_dict,
    'pw_calculation_set': set_dict,
    'pw_kpoints': kpoints,
    'pw_input':{'relaxation_scheme': relaxation_scheme,
                  'volume_convergence_threshold': 1.e-2,
                  },

    OR

    'pw_calculation': load_node(60),

    Phonon dispersion part:
    'phdisp_pw_settings': settings,
    'phdisp_pw_parameters': pw_input_dict,
    'phdisp_pw_calculation_set': set_dict,
    'phdisp_pw_kpoints': kpoints,
    'phdisp_pw_input':{'relaxation_scheme': relaxation_scheme,
                                 'volume_convergence_threshold': 1.e-2,
                                 },
     
     
    'phdisp_ph_codename': ph_codename,
    'phdisp_ph_parameters': ph_input_dict,
    'phdisp_ph_settings': settings,
    'phdisp_ph_calculation_set': set_dict,
    'phdisp_ph_qpoints': qpoints,
    'phdisp_ph_input': {'use_qgrid_parallelization': True},
    
    'phdisp_dispersion_matdyn_codename': matdyn_codename,
    'phdisp_dispersion_q2r_codename': q2r_codename,
    'phdisp_dispersion_calculation_set': set_dict,
    'phdisp_dispersion_settings': settings,
    'phdisp_dispersion_input':{'distance_qpoints_in_dispersion':0.01,
                   'asr': asr,
                   'zasr': asr,
                   'threshold_length_for_Bravais_lat': 1e-4,
                   'threshold_angle_for_Bravais_lat': 1e-4,
                   },

    """
    _default_deformation_amplitudes = [-0.01, 0., 0.02]
    
    def __init__(self,**kwargs):
        super(QuasiharmonicWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        """
        Checks the parameters
        """
        self.append_to_report("Checking input parameters")
        
        mandatory_pw_keys = [('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             ('pseudo_family',basestring,'the pseudopotential family'),
                             ('pw_kpoints',KpointsData,'A KpointsData object with the kpoint mesh used by PWscf'),
                             #('pw_calculation_set',dict,'A dictionary with resources, walltime, ...'),
                             ('pw_parameters',dict,"A dictionary with the PW input parameters"),
                             ]
                        
        main_params = self.get_parameters()
        
        # validate the codes
        for kind,key in [['quantumespresso.pw','pw_codename']]:
            try:
                test_and_get_code(main_params[key], kind, use_exceptions=True)
            except KeyError:
                # none of the codes is always required
                pass
        
        if 'pw_calculation' in main_params:
            if isinstance(main_params['pw_calculation'],PwCalculation):
                # if pw is a calculation, launch directly from the phonon dispersions step
                self.next(self.run_dispersions)
                return
            else:
                raise TypeError("parameter 'pw_calculation' should be a "
                                "PwCalculation")
    
        # validate Pw keys
        helpers.validate_keys(main_params, mandatory_pw_keys)
        
        # start from Pw calculation
        self.next(self.run_pw)
    
                
    @Workflow.step
    def run_pw(self):
        """
        Launch the PwWorkflow
        """
        main_params = self.get_parameters()
        # take the parameters needed for the PW computation
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('phdisp_') or k == 'input':
                pass
            elif k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            else:
                pw_params[k] = v
        
        # Force the calculation to be a vc-relax
        try:
            pw_params['input']['relaxation_scheme'] = 'vc-relax' 
        except KeyError:
            pw_params['input']['relaxation_scheme'] = 'vc-relax'

        wf_pw = PwWorkflow(params=pw_params)        
        wf_pw.store()
        self.append_to_report("Launching PW sub-workflow (pk: {})".format(wf_pw.pk))
        self.attach_workflow(wf_pw)
        wf_pw.start()
        
        self.next(self.run_dispersions)
        
        
    @Workflow.step
    def run_dispersions(self):
        main_params = self.get_parameters()
        
        try:
            pw_calculation = main_params['pw_calculation']
        except KeyError:
            wf_pw = self.get_step(self.run_pw).get_sub_workflows()[0]
            pw_calculation = wf_pw.get_result('pw_calculation')
            
            # Save results of the subworkflow in the main
            for k,v in wf_pw.get_results().iteritems():
                self.add_result(k,v)

        try: 
            structure = pw_calculation.out.output_structure
        except AttributeError:
            structure = pw_calculation.inp.structure

        # Load or construct the possible deformations from input
        if 'deformations' in main_params.get('input',{}).keys():
            deformations = main_params['input']['deformations']
        elif 'scale_directions' in main_params.get('input',{}).keys():
            scale_directions = main_parmas['input']['scale_directions']
            deformations = [] 
            for dirs in scale_directions:
                this_deformation = [[0,0,0],[0,0,0],[0,0,0]]
                for i in dirs:
                    this_deformation[i][i] = 1.
                deformations.append(this_deformation)
        else:
            # If no specific deformation was specified 
            # by default we consider only a uniform scaling of the volume 
            deformations = [[[1.,0,0],[0,1.,0],[0,0,1.]]]
            
        # Load the set of deformation amplitudes or use default values
        amplitudes = main_params.get('input',{}).get('deformation_amplitudes',
                            self._default_deformation_amplitudes)
        deformation_amplitudes = ParameterData(dict={'amplitudes': amplitudes})
        # the same without the zero (to avoid redundancy of calculations)
        _ = amplitudes.pop(0.,None)
        deformation_amplitudes_without_zero = ParameterData(
                                        dict={'amplitudes': amplitudes})
        
        # Cycle over possible kinds of deformations
        for i,deformation in enumerate(deformations):
            the_deformation = ParameterData(
                            dict={'deformation_matrix':deformation})
            # we do the phonon calculation for the undeformed structure
            # only once -> if i>1, we do not include the zero amplitude
            the_amplitudes = deformation_amplitudes if i==0 else \
                                deformation_amplitudes_without_zero
            _, transformations_dict = get_transformations_inline(
                                    amplitudes=the_amplitudes,
                                    deformation=the_deformation)
            
            for transformation in transformations_dict.values():
                phdisp_params = {}        
                # load the parameters for the Phonondispersion Workflow      
                for k,v in main_params.iteritems():
                    if k.startswith('phdisp_'):
                        new_k = k[7:] # remove phdisp_
                        phdisp_params[new_k] = v
                
#                if np.max(np.array(transformation.get_dict()['transformation_matrix'])
#                    - np.identity(3)) < 1.e-8:
#                    # the transformation matrix is the identity -> we use
#                    # the initial calculation as an input of the
#                    # phonon dispersion workflow
#                    phdisp_params['pw_calculation'] = pw_calculation
#                else:
                    # deform the structure                
                _, deformed_structure_dict = deform_structure_inline(
                    structure=structure,
                    transformation=transformation)
                phdisp_params['structure'] = deformed_structure_dict['deformed_structure']
                        
                # Launch the Phonondispersion sub-workflow
                wf_phdisp = PhonondispersionWorkflow(params=phdisp_params)
                wf_phdisp.store()
                self.append_to_report("Launching Phonondispersion sub-workflow (pk: {})".format(wf_phdisp.pk))
                self.attach_workflow(wf_phdisp)
                wf_phdisp.start()
        
        self.next(self.final_step)
        return
    
    @Workflow.step
    def final_step(self):
        """
        This is the final step to compute and optimize the free energy
        """
        main_params = self.get_parameters()
        

        self.next(self.exit)
    
