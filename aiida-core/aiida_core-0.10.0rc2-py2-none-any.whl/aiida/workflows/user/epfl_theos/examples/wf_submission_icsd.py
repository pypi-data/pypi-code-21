#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller."

def launch_ws():
    #
    from aiida.orm import DataFactory
    from aiida.tools.dbimporters.plugins.icsd import IcsdDbImporter
    from aiida.workflows.wf_icsd_lowdim import WorkflowIcsdLowDim

    ParameterData = DataFactory('parameter')

    on_theos = True


    # ssh tunnel to get access to mysql database
    # ssh -L 3306:localhost:3306 schwaller@theospc2.epfl.ch

    # ssh tunnel to solve dynamic ip issue and have full access
    # on the ICSD web interface from any computer
    # ssh -L 8001:theospc2:80 schwaller@theospc16.epfl.ch
    if on_theos is True:
        importer = IcsdDbImporter(server="http://theospc2.epfl.ch/", passwd="sql", host= "127.0.0.1",db = "icsd")
    else:
        importer = IcsdDbImporter(server="http://localhost:8001/", passwd="sql", host= "127.0.0.1",db = "icsd")

    # should replace 'server= "http://theospc2.epfl.ch"'



    # how should we query for all results? what's the best way?
    # should we partition the entries into bunches of let's say 10000?
    # about 142000 entries in total, should there be more?

    #LowDimFinder parameters

    icsd_numbers = ["35538",
                    "165226",
                    "158366",
                    "163559",
                    ]

    lowdim_dict ={
    'cov_bond_margin_list': [0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.3],
    'rotation': True, # rotation = True puts the layer plane on x-y (for 2D)
    'max_supercell': 2,
    'min_supercell': 2,
    'vacuum_space': 40,
    }

    lowdim_params = ParameterData(dict=lowdim_dict).store()


    #query_results = importer.query(id=icsd_number_list)
    query_results = importer.query(id=icsd_numbers)
    #query_results = importer.query(year=2004)

    print len(query_results)

    for entry in query_results:

        cif = entry.get_cif_node().store()


        print "----------------------"
        print entry.source["id"] # print cif number
        print "----------------------"

        params = {
            'icsd_id'               : entry.source["id"],
            'cif'                   : cif,
            'group_name'            : 'icsd_test',
            'lowdim_params'         : lowdim_params,
            'num_machines'          : 1,
            'max_wallclock_seconds' : 30*60,
	        'on_theospc'            : on_theos,
        }

        wf = WorkflowIcsdLowDim()
        wf.set_params(params)
        wf.start()

        print "Launched workflow {}, {}".format(wf.uuid,wf.pk)

    print len(query_results)

if __name__ == '__main__':
    from aiida import load_dbenv
    load_dbenv()
    launch_ws()
