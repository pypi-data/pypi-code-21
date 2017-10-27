# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow
from aiida.orm import DataFactory, Group
from aiida.orm.calculation.inline import optional_inline
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.quantumespresso.pw import _default_nspin_from_QE
from aiida.workflows.user.epfl_theos.quantumespresso.chronos import _default_QE_conv_thr
from aiida.workflows.user.epfl_theos import TheosWorkflowFactory
import numpy as np

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."

ParameterData = DataFactory('parameter')
StructureData = DataFactory('structure')
PwWorkflow = TheosWorkflowFactory('quantumespresso.pw')

@optional_inline
def cohesive_energy_inline(parameters_energy_bulk,**kwargs):
    """
    Inline function to compute the formation (or cohesive) energy.
    :param parameters_energy_bulk: ParameterData object with the output
        parameters of an energy calculation on the bulk.
    :param parameters_energy_%s: (with %s the element name) ParameterData
        object(s) with the output parameters of energy calculation(s) on
        a single element structure. There should be as many as the number
        of species in the bulk.
    :return: a dictionary of the form
        {'output_parameters': ParameterData with the following dictionary:
            {'cohesive_energy': cohesive energy of the bulk w.r.t 
                                the isolated system(s),
             'cohesive_energy_units': 'eV/atom',
             }
         }
    """   
    output_dict = {'cohesive_energy_units': 'eV/atom'}
    
    # extract info from the bulk energy calculation output parameters
    pw_dict = parameters_energy_bulk.get_dict()
    pw_bulk_calc = parameters_energy_bulk.inp.output_parameters
    try:
        structure_bulk = pw_bulk_calc.out.output_structure
    except AttributeError:
        structure_bulk = pw_bulk_calc.inp.structure
    
    bulk_atoms = [structure_bulk.get_kind(kind_name).symbol
                  for kind_name in structure_bulk.get_site_kindnames()]
    # extract energy
    cohesive_energy = pw_dict['energy']
    if pw_dict['energy_units'] != 'eV':
        raise ValueError("Energy bulk calc.: Improper units for the"
                         " the energy (eV required)")

    for element in set(bulk_atoms):
        # extract info from the elemental energy calculation
        pw_elem_params = kwargs.pop("parameters_energy_{}".format(element))     
        pw_elem_calc = pw_elem_params.inp.output_parameters
        try:
            structure_elem = pw_elem_calc.out.output_structure
        except AttributeError:
            structure_elem = pw_elem_calc.inp.structure
        
        if structure_elem.get_formula(mode='hill_compact')!=element:
            raise ValueError("Element in link name and in structure should "
                             "be identical")
        
        pw_elem_dict = pw_elem_params.get_dict()
        # extract energy
        elem_energy = pw_elem_dict['energy']
        if pw_elem_dict['energy_units'] != 'eV':
            raise ValueError("Element {} energy calc.: Improper units for the"
                              " the energy (eV required)".format(element))
        cohesive_energy -= elem_energy/float(len(structure_elem.sites))\
                                        *bulk_atoms.count(element)
        for _ in range(bulk_atoms.count(element)):
             bulk_atoms.pop(bulk_atoms.index(element))
        
    # if there are some remaining atoms in the bulk, the cohesive 
    # energy cannot be computed
    if bulk_atoms:
        raise ValueError("Some elements are missing!")
    
    output_dict['cohesive_energy'] = cohesive_energy/float(len(structure_bulk.sites))            
    if kwargs:
        raise ValueError("Too many input parameters")
    
    return {'output_parameters': ParameterData(dict=output_dict)}


def get_cohesive_energy_results(store=True,**kwargs):
    """
    Get the results from the cohesive_energy_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead 
    the output dictionary of the previously launched function,
    - otherwise, launches the formation_energy_inline
    function and gets its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    from aiida.workflows.user.epfl_theos.dbimporters.utils import objects_are_equal
    
    result_dict = None
    params = kwargs.values()[0]
    for ic in params.get_outputs(InlineCalculation):
        try:
            if ( ic.get_function_name() == 'cohesive_energy_inline'
                 and all([any([objects_are_equal(p_ic.get_dict(),p.get_dict())
                               for p in kwargs.values()])
                          for p_ic in ic.get_inputs(ParameterData)])
                 and all([any([objects_are_equal(p_ic.get_dict(),p.get_dict())
                               for p_ic in ic.get_inputs(ParameterData)])
                          for p in kwargs.values()])
                 and 'output_parameters' in ic.get_outputs_dict() ):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is not None:
        print " cohesive_energy_inline already run with "\
               "the same inputs -> we do not re-run"
        created = False
    else:
        print "Launch cohesive_energy_inline ... "
        result_dict = cohesive_energy_inline(store=store,**kwargs)
        created = True
    return result_dict,created


class FormationenergyWorkflow(Workflow):
    """
    Workflow to compute the formation energy of a structure.

    Inputs are those of the PwWorkflow with 'pw_' added to the keys
    except for:
     'structure':       the initial structure on which to compute the 
                        formation energy (mandatory)
     'pseudo_family':   the name of the pseudopotential family
                        (mandatory)
     'group_name':      the name of the group where to put the pw calc.
                        of the initial structure
    
    In addition, there are several inputs specific to this workflow:
    
     'elemental_structures_group_name':     the name of the group where
                                            to find the structures for
                                            the bare elements (mandatory)
     'elemental_calculations_group_name':   the name of the group where
                                            to put the pw calcs. of the
                                            elemental structures
     'formation_energies_group_name':       the nae of the group where
                                            to put the ParameterData
                                            objections with the formation
                                            energies
    
    """
    
    def __init__(self,**kwargs):
        super(FormationenergyWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        """
        Starting step only verifies the input parameters
        """
        self.append_to_report("Checking input parameters")
        
        # define the mandatory keywords and the corresponding description to be 
        # printed in case the keyword is missing, for the PW parameters
        mandatory_keys = [('structure',StructureData,
                           'The structure on which to compute the formation energy'),
                          ('elemental_structures_group_name',basestring,
                           'The name of the group where to find the elemental structures')]
        
        # retrieve and check the parameters
        params = self.get_parameters()
        helpers.validate_keys(params,mandatory_keys)
        
        # Note: I'm not checking extensively all the keys used by the workflow
        self.next(self.run_pw)
        
    @Workflow.step
    def run_pw(self):
        # run a PwWorkflow for the structure to analyse, and a PwWorkflow
        # for each of the elemental structures corresponding to its
        # elemental consituents. Checks that they were not already
        # launched beforehand with the same parameters.
        
        main_params = self.get_parameters()
        
        # retrieve PW parameters
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            elif k in ['pseudo_family','group_name']:
                pw_params[k] = v            
        
        # do first the full structure
        pw_params['structure'] = main_params['structure']
        
        old_wfs_pw = helpers.get_pw_wfs_with_parameters(pw_params,also_bands=False)
        self.add_attribute('old_pw_wfs',[_.pk for _ in old_wfs_pw])
        if old_wfs_pw:
            self.append_to_report("Found {} previous PW workflow{} "
                                  "on structure {} with pk {}".format(
                                len(old_wfs_pw),"s" if len(old_wfs_pw)>1 else "",
                                pw_params['structure'].get_formula(),
                                pw_params['structure'].pk))
            
        else:
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            # add an attribute to identify the calc. on the bulk structure
            wf_pw.add_attribute('formula',pw_params['structure'].get_formula())
            self.append_to_report("Launching PW workflow (pk: {}) on "
                                  "structure {} with pk {}".format(
                                  wf_pw.pk,pw_params['structure'].get_formula(),
                                  pw_params['structure'].pk))
            self.attach_workflow(wf_pw)
            wf_pw.start()

        # keep nspin, starting_magnetization and conv_thr (per atom) for later use
        nspin = pw_params['parameters']['SYSTEM'].get('nspin',_default_nspin_from_QE)
        start_mag = pw_params['parameters']['SYSTEM'].get('starting_magnetization',{})
        conv_thr_per_atom = pw_params['parameters']['ELECTRONS'].get(
                'conv_thr',_default_QE_conv_thr)/float(len(main_params['structure'].sites))
        
        # do then all elemental structures corresponding to its constituents
        for kind in main_params['structure'].kinds:
            element = kind.symbol
            structs = [s for s in StructureData.query(
                 dbgroups__name=main_params['elemental_structures_group_name'])
                 if s.get_formula(mode='hill_compact')==element]
            if len(structs)!=1:
                self.append_to_report("ERROR: group {} does not contain "
                                      "the {} structure or contains too "
                                      "many of them".format(
                                      elemental_structures_group_name,element))
                raise ValueError("ERROR: cannot get elemental structure")
            pw_params['structure'] = structs[0]
            pw_params['parameters']['ELECTRONS']['conv_thr'] = \
                conv_thr_per_atom*float(len(pw_params['structure'].sites))
            if start_mag.get(element,0.) and nspin==2:
                pw_params['parameters']['SYSTEM']['nspin'] = nspin
                pw_params['parameters']['SYSTEM']['starting_magnetization'] = start_mag[element]
            else:
                pw_params['parameters']['SYSTEM'].pop('nspin',None)
                pw_params['parameters']['SYSTEM'].pop('starting_magnetization',None)
            
            if 'elemental_calculations_group_name' in main_params:
                pw_params['group_name'] = main_params['elemental_calculations_group_name']
            else:
                _ = pw_params.pop('group_name',None)
            
            old_elem_wfs_pw = helpers.get_pw_wfs_with_parameters(pw_params,also_bands=False)
            self.add_attribute('old_{}_pw_wfs'.format(element),[_.pk for _ in old_elem_wfs_pw])
            if old_elem_wfs_pw:
                self.append_to_report("Found {} previous PW workflow{} "
                                      "on elem. structure {} with pk {}".format(
                                    len(old_elem_wfs_pw),"s" if len(old_elem_wfs_pw)>1 else "",
                                    pw_params['structure'].get_formula(),
                                    pw_params['structure'].pk))
                
            else:
                wf_pw = PwWorkflow(params=pw_params)
                wf_pw.store()
                # add an attribute to identify the element treated by the wf
                wf_pw.add_attribute('formula',element)
                self.append_to_report("Launching PW workflow (pk: {}) on "
                                      "elem. structure {} with pk {}".format(
                                      wf_pw.pk,pw_params['structure'].get_formula(),
                                      pw_params['structure'].pk))
                self.attach_workflow(wf_pw)
                wf_pw.start()
       
        self.next(self.final_step)
                    
    @Workflow.step
    def final_step(self):
        # collect the results into a single ParameterData object
        
        main_params = self.get_parameters()
        structure = main_params['structure']
        
        bulk_wf = (list(Workflow.query(pk__in=self.get_attribute('old_pw_wfs'))) +
              [wf for wf in self.get_step(self.run_pw).get_sub_workflows()
               if wf.get_attribute('formula')==structure.get_formula()])[0]
               
        bulk_calc = bulk_wf.get_result('pw_calculation')
        self.add_result('bulk_calculation',bulk_calc)
        if 'group_name' in main_params:
            group, created = Group.get_or_create(name=main_params['group_name'])
            if created:
                self.append_to_report("Created group '{}'".format(group.name))
            # put the bulk calculation into the group
            group.add_nodes([bulk_calc])
            self.append_to_report("Adding bulk calc. {} to group '{}'".format(
                    bulk_calc.pk,group.name))

        input_dict = {'parameters_energy_bulk': bulk_calc.out.output_parameters}
        
        for kind in structure.kinds:
            element = kind.symbol
            elem_wf =  (list(Workflow.query(pk__in=self.get_attribute('old_{}_pw_wfs'.format(element)))) +
              [wf for wf in self.get_step(self.run_pw).get_sub_workflows()
               if wf.get_attribute('formula')==element])[0]
            elem_calc = elem_wf.get_result('pw_calculation')
            self.add_result('element_{}_calculation'.format(element),elem_calc)
            if 'elemental_calculations_group_name' in main_params:
                group, created = Group.get_or_create(
                            name=main_params['elemental_calculations_group_name'])
                if created:
                    self.append_to_report("Created group '{}'".format(group.name))
                # put the bulk calculation into the group
                group.add_nodes([elem_calc])
                self.append_to_report("Adding elem calc. {} on {} to group '{}'".format(
                        element,elem_calc.pk,group.name))

            input_dict['parameters_energy_{}'.format(element)] = \
                                        elem_calc.out.output_parameters
            
        result_dict,_ = get_cohesive_energy_results(store=True,**input_dict)
        self.add_result('cohesive_energy_parameters',result_dict['output_parameters']) 
        
        if 'formation_energies_group_name' in main_params:
            group, created = Group.get_or_create(
                        name=main_params['formation_energies_group_name'])
            if created:
                self.append_to_report("Created group '{}'".format(group.name))
            # put the parameters into the group
            group.add_nodes([result_dict['output_parameters']])
            self.append_to_report("Adding parameters {} to group '{}'".format(
                    result_dict['output_parameters'].pk,group.name))
        
        self.append_to_report("formation energy workflow completed")
        
        # then exit
        self.next(self.exit)
