# -*- coding: utf-8 -*-
"""
Workflow to clean a cif file with cod tools 
"""
from aiida.common import aiidalogger
from aiida.orm.workflow import Workflow
from aiida.orm import Calculation, Code, Computer, Data, Group
from aiida.common.exceptions import WorkflowInputValidationError
from aiida.orm import CalculationFactory, DataFactory
from aiida.orm.calculation.inline import make_inline
from aiida.workflows.user.epfl_theos.quantumespresso import helpers

CifData       = DataFactory('cif')
ParameterData = DataFactory('parameter')

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Andrius Merkys, Nicolas Mounet, Giovanni Pizzi, Philippe Schwaller."

logger = aiidalogger.getChild('WorkflowDemo')

class CleancifWorkflow(Workflow):
    """
    Workflow, which take a CifNode, filters it with codtools
    and return a corrected CifNode.

    Example of input parameter dictionary:

    params = {
        'group_name' : group_name,
        'cif': cif,
        'cif_filter_code': cif_filter_list[counter%n_filter],
        'cif_select_code': cif_select_list[counter%n_select],
        'remove_tags': '_publ_author_name,_citation_journal_abbrev',
    }
    """
    def __init__(self,**kwargs):
        super(CleancifWorkflow, self).__init__(**kwargs)


    # prepare cod calculation
    def prepare_cod_calculation(self, code_name):
        params                 = self.get_parameters()
        num_machines           = 1
        max_wallclock_seconds  = 60*15

        code = Code.get_from_string(code_name)

        calc = code.new_calc()

        computer = params.get('cod_computer', None)

        if computer is None:
            calc.set_computer(code.get_remote_computer())
        else:
            calc.set_computer(computer)

        calc.set_max_wallclock_seconds(max_wallclock_seconds)
        calc.set_resources({"num_machines": num_machines,
                            "num_mpiprocs_per_machine": 1})
        calc.store()
        return calc


    def add_group_name(self,aiida_node,subgroup=''):
        params = self.get_parameters()
        group_name = params.get('group_name',None)
        if group_name is not None:

            group_name =  group_name + subgroup
            # create or get the group, and add the calculation
            group, created = Group.get_or_create(name=group_name)
            if created:
                self.append_to_report("Creating group '{}'".format(group_name))
            self.append_to_report("Adding {} to group '{}'".format(aiida_node.pk, group_name))
            group.add_nodes(aiida_node)


    @Workflow.step
    def start(self):
        """
        Check input parameters
        """

        self.append_to_report("Checking input parameters")

        mandatory_keys = [   ('cif',CifData,"the cif (a previously stored CifData object)"),
                             ('cif_filter_code',basestring,'the cif_filter_code'),
                             ]

        main_params = self.get_parameters()
        helpers.validate_keys(main_params, mandatory_keys)

        self.next(self.filter_cif)


    @Workflow.step
    def filter_cif(self):
        """
        Filter the cif
        """
        params = self.get_parameters()

        calc = self.prepare_cod_calculation(params['cif_filter_code'])
        cif = params['cif']
        calc.use_cif(cif)
        filter_params = ParameterData(dict={'use-perl-parser':True,
                                            'fix-syntax-errors': True}).store()
        calc.use_parameters(filter_params)

        self.append_to_report("Filtering of CifData (pk: {}) started".format(cif.pk))
        self.attach_calculation(calc)

        remove_tags = params.get('remove_tags',False)

        if remove_tags is False:
            self.next(self.final_step)

        self.next(self.remove_tags)


    @Workflow.step
    def remove_tags(self):
        """
        Remove problematic tags, only executed if remove_tags is True
        Default tags to remove are '_publ_author_name' and 
        '_citation_journal_abbrev'
        """
        params = self.get_parameters()

        #get filtered cif
        completed = self.get_step_calculations(self.filter_cif)[0]
        cif = completed.get_outputs(CifData)[0]

        self.append_to_report("Filtered cif obtained (pk: {})".format(cif.pk))

        completed.out.remote_folder._clean()
        self.append_to_report("Cleaning remote_folder of calc {}".format(completed.pk))

        calc = self.prepare_cod_calculation(params['cif_select_code'])
        tags = params.get('tags', '_publ_author_name,_citation_journal_abbrev')
        select_params = ParameterData(dict={'use-perl-parser': True,
                                            'canonicalize-tag-names': True,
                                            'invert': True,
                                            'tags': tags}).store()

        calc.use_cif(cif)
        calc.use_parameters(select_params)

        self.append_to_report("Removing bibliography of CifData (pk: {})".format(cif.pk))
        self.attach_calculation(calc)
        self.next(self.final_step)


    @Workflow.step
    def final_step(self):
        """
        Store cleaned cif in group GROUPNAME_clean_cif
        """
        completed = self.get_step_calculations(self.remove_tags)[0]
        cif = completed.get_outputs(CifData)[0]

        self.add_result('cleaned_cif',cif)
        self.append_to_report("Clean cif workflow completed")

        completed.out.remote_folder._clean()
        self.append_to_report("Cleaning remote_folder of calc {}".format(completed.pk))
        
        # Copying source of initial CIF to the cleaned CIF
        initial_cif = self.get_parameter('cif')
        try:
            source = initial_cif.source
        except AttributeError:
            try:
                icsd_nr = initial_cif.get_extra('icsd_nr')
                icsd_version = initial_cif.get_extra('icsd_version')
                source = {
                    'db_name': 'Icsd',
                    'id': icsd_nr,
                    'version': icsd_version,
                }
            except AttributeError:
                pass
        try:
            cif.set_extra('original_source', source)
            # For backwards compatibility ICSD ID and version is given in
            # separate extras.
            if isinstance(source, dict) and source.get('db_name') == 'Icsd':
                cif.set_extras({
                    'icsd_nr': source.get('id'),
                    'icsd_version': source.get('version'),
                })
        except NameError:
            pass

        self.add_group_name(cif,subgroup='_clean_cif')

        self.next(self.exit)
