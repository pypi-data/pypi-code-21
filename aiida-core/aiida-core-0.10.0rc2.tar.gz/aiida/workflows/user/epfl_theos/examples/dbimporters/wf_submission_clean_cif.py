#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
"""
Launch the CleancifWorkflow on all results of a database query
"""
import time
from aiida.orm import DataFactory,Group
from aiida.tools.dbimporters import DbImporterFactory
from aiida.workflows.user.epfl_theos.dbimporters.cleancif import CleancifWorkflow
from aiida.workflows.user.epfl_theos.dbimporters.utils import get_source_id
from aiida.common.exceptions import NotExistent
from StarFile import StarError
from urllib2 import HTTPError

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrius Merkys, Giovanni Pizzi, Philippe Schwaller."


ParameterData = DataFactory('parameter')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with the parsed parameters.
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Launch the CleancifWorkflow on all results of a '
                    'database query')

    parser.add_argument('--species', type=int, dest='number_of_elements',
                        default=17, help='Number of species (default: 17)')
    parser.add_argument('--test', dest='test', action='store_true',
                        default=False,
                        help='Test the script with specific database entries')
    parser.add_argument('--test-id', type=int, metavar='N', nargs="+",
                        default=[617290, 35538, 165226],
                        help='Specify the structure IDs to run the test with')
    parser.add_argument('--run','--no-test', dest='test',
                        action='store_false',
                        help='Execute the script (as opposed to --test)')
    parser.add_argument('--prefix', '--group-prefix', type=str,
                        default="N_elements_{}",
                        help='Specify a prefix for a group name, where '
                             'the results will be stored. By default '
                             '"N_elements_{}" is used, where "{}" is '
                             'replaced by the number of species')
    parser.add_argument('--db','--database', type=str, default='ICSD',
                        help='Structure database (default ICSD)')
    parser.add_argument('--cif_filter-code', type=str, nargs="+",
                        default=['cif_filter-direct'],
                        help='Code label for cif_filter '
                             '(default: cif_filter-direct)')
    parser.add_argument('--cif_select-code', type=str, nargs="+",
                        default=['cif_select-direct'],
                        help='Code label for cif_select '
                             '(default: cif_select-direct)')
    parser.add_argument('--sleep', type=int, default=0,
                        help='Add sleeping time between the workflow '
                             'submissions (default: 0)')

    # Parse and return the values
    parsed_data = parser.parse_args(sys.argv[1:])
    data = vars(parsed_data)

    data['db'] = data['db'].lower()

    return data

default_importer_params = {
    'icsd': {
                # The importer, make you have a ssh tunnel open to the
                # workstation, which hosts the ICSD database.
                'server': 'http://theossrv2.epfl.ch/',
                'host': '127.0.0.1',
                'db': 'icsd',
                'passwd': 'sql',
            }
}

launch_params = parse_cmdline()

n_filter = len(launch_params['cif_filter_code'])
n_select = len(launch_params['cif_select_code'])

# Load the specific DbImporter
importer_class = DbImporterFactory(launch_params['db'])

# Prepare the importer parameters
importer_parameters = default_importer_params.get(launch_params['db'], {})

# Override the importer parameters
for key in importer_parameters.keys():
    if key in launch_params.keys():
        importer_parameters[key] = launch_params[key]


importer = importer_class(**importer_parameters)

if launch_params.get('test', False) is True:
    query_results = importer.query(id=launch_params['test_id'])

    # change group name.
    group_name = "test"

    group, created = Group.get_or_create(name="{}_clean_cif".format(group_name))
    analysed_structures = [int(get_source_id(cif)) for cif in group.nodes]

else:
    query_parameters = {
        'number_of_elements': launch_params.get('number_of_elements', None)
    }

    # If the database supports the selection by the determination method,
    # only experimental structures have to be selected. For the COD, this
    # can be achieved by selecting single crystal, powder diffraction as
    # as well as unknown experiments. Theoretical structures in COD are
    # marked as "theoretical".
    if 'determination_method' in importer.get_supported_keywords():
        query_parameters['determination_method'] = ["single crystal",
                                                    "powder diffraction",
                                                     None]

    query_results = importer.query(**query_parameters)

    group_name = launch_params.get('prefix').format(launch_params['number_of_elements'])

    # Get a list of already analysed structures
    try:
        group, created = Group.get_or_create(name="{}_clean_cif".format(group_name))
        analysed_structures = [int(get_source_id(cif)) for cif in group.nodes]
    except NotExistent:
        analysed_structures = []


for counter, entry in enumerate(query_results):
    if int(entry.source['id']) not in analysed_structures:
        try:
            cif = entry.get_cif_node()
            # skip CIFs with partial occupancies
            try:
                if cif.has_partial_occupancies():
                    continue
                else:
                    cif.store()
            except ValueError:
                # has_partial_occupancies() raises ValueError if occupancy
                # can not be converted to float value (usually it means
                # that there are occupancy values '?' or '.' -- in some
                # cases these values belong to dummy atoms). Such
                # structures are rare and can be skipped as incomplete so
                # as not to bias the research).
                continue

        except (StarError, HTTPError) as e:
            # weird errors happening sometimes
            import traceback
            trace = traceback.format_exc()
            print "{} for {} id {}:".format(str(e.__class__),
                                            entry.source['db_name'],
                                            entry.source['id'])
            if e.__class__==HTTPError:
                print "URI: {}".format(entry.source['uri'])
            print "\n".join(trace.split('\n')[-5:])

        else:
            params = {
                'group_name' : group_name,
                'cif' : cif,
                'cif_filter_code': launch_params['cif_filter_code'][counter%n_filter],
                'cif_select_code': launch_params['cif_select_code'][counter%n_select],
                'remove_tags': True,
            }

            wf = CleancifWorkflow()
            wf.set_params(params)
            wf.start()

            print "Launched clean cif wf with pk {} for {} ID {}".format(wf.pk,
                                                                         entry.source['db_name'],
                                                                         entry.source['id'])
            
            if launch_params['sleep'] > 0:
                time.sleep(launch_params['sleep'])

print 20 * "*"
print counter+1
