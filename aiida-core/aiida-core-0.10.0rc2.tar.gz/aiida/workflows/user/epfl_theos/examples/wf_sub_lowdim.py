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
    from aiida.workflows.wf_lowdimfinder import WorkflowLowDimFinder

    ParameterData = DataFactory('parameter')

    on_theos = True


    # ssh tunnel to get access to mysql database
    # ssh -L 3306:localhost:3306 schwaller@theospc2.epfl.ch

    # ssh tunnel to solve dynamic ip issue and have full access
    # on the ICSD web interface from any computer
    # ssh -L 8001:theospc2:80 schwaller@theospc16.epfl.ch
    if on_theos is True:
        importer = IcsdDbImporter(server="http://theospc2.epfl.ch", passwd="sql", host= "127.0.0.1",db = "icsd")
    else:
        importer = IcsdDbImporter(server="http://localhost:8001/", passwd="sql", host= "127.0.0.1",db = "icsd")

    # should replace 'server= "http://theospc2.epfl.ch"'

#all structures found in the paper "Two-Dimensional Materials from Data Filtering and Ab Initio Calculations"
# Lebegue et al., Phys. Rev. X 3, 031002 (2013)
    icsd_number_list = ["617290",
                        "35538 ",
                        "165226",
                        "158366",
                        "163559",
                        "610480",
                        "651404",
                        "651178",
                        "173923",
                        "653071",
                        "651465",
                        "652236",
                        "653213",
                        "638847",
                        "638899",
                        "638959",
                        "651361",
                        "652158",
                        "603582",
                        "645307",
                        "645369",
                        "645529",
                        "651089",
                        "651092",
                        "651948",
                        "651950",
                        "14390",
                        "75420",
                        "626718",
                        "152836",
                        "644245",
                        "644334",
                        "15431",
                        "202366",
                        "40752",
                        "73323",
                        "81816",
                        "75459",
                        "81813",
                        "625401",
                        "650448",
                        "33934 ",
                        "159382",
                        "166276",
                        "170327",
                        "649016",
                        "649534",
                        "649589",
                        "649747",
                        "652385",
                        "650992",
                        "651910",
                        "250250",
                        "280850",
                        "281551",
                        "391354",
                        "410924",
                        "413165",
                        "417149",
                        "418978",
                        "420302",
                        "626809",
                        "633094",
                        "633302",
                        "633877",
                        "637823",
                        "646436",
                        "647260",
                        "655780",
                        "660262",
                        "660273",
                        "660333",
                        "150193",
                        "150345",
                        "151468",
                        "155006",
                        "155009",
                        "155670",
                        "156662",
                        "158485",
                        "159356",
                        "165972",
                        "166578",
                        "170640",
                        "170642",
                        "170773",
                        "173940",
                        "246905",
                        "246906",
                        "246907",
                        "247089",
                        "250249",
                        "41715",
                        ]

    all_oblique_list =[ "33934",
                        "246906",
                        "250249",
                        "152836",
                        "155670",
                        "246905",
                        "626718",
                        "650992",
                        "651178",
                        "651361",
                        "165972",
                        "649534",
                        "651910",
                        "651465",
                        "650448",
                        "653213",
                        "651948",
                        "652385",
                        "75420",
                        "625401",
                        ]

    cg_test = [
                "250250",
                "159382",
                "651092",
                "166578",
                "645369",
                "173940",
                "163559",
                "633302",
                "660262",
                "418978",
                "637823",
                "170327",
                "166276",
                "150193",
                "73323",
                "391354",
                "250249",
                "646436",
                "420302",
                "637823",
                "410924",
                "170640",
                "660273",
                "81816",
                "247089",
                "75459",
                "170642",
                "14390",
                "170640",
                "81813",
                "158485",
                "417149",]


    leb3 = [
            "151468",
            "155006",
            "156662",
            "159356",
            "170642",
            "170773",
            "173923",
            "246907",
            "247089",
            "250250",
            "280850",
            "281551",
            "410924",
            "413165",
            "610480",
            "626809",
            "633094",
            "638959",
            "644245",
            "644334",
            "645307",
            "649589",
            "649747",
            "651089",
            "651092",
            "651361",
            "651404",
            "651948",
            "651950",
            "652158",
            "653071",
            "655780",
            "660333",
            "81816 ",
            "603582",]

    leb4 =[
            "151468",
            "155006",
            "156662",
            "170773",
            "280850",
            "413165",
            "626809",
            "633094",
            "645307",
            "660333",]

    leb5 = [
            "151468",
            "155009",
            "156662",
            "159356",
            "170642",
            "170773",
            "250250",
            "280850",
            "410924",
            "413165",
            "626809",
            "633094",
            "645307",
            "660333",
            ]



    icsd_numbers = ["155670",
                    "41715",
                    ]

    # how should we query for all results? what's the best way?
    # should we partition the entries into bunches of let's say 10000?
    # about 142000 entries in total, should there be more?

    #LowDimFinder parameters

    lowdim_dict ={
    'cov_bond_margin_list': [0.05, 0.075,0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.3],
    'rotation': True, # rotation = True puts the layer plane on x-y (for 2D)
    'max_supercell': 2,
    'min_supercell': 2,
    'vacuum_space': 40,
    }

    lowdim_params = ParameterData(dict=lowdim_dict).store()


    #query_results = importer.query(id=icsd_number_list)
    #query_results = importer.query(id=icsd_numbers)
    query_results = importer.query(id=leb5)

    for entry in query_results:


        print "----------------------"
        print entry.source["id"] # print cif number
        print "----------------------"

        params = {
            'icsd_id'               : entry.source["id"],
            'group_name'            : '2D_test',
            'kpointsmesh_spacing'   : 0.2, # spacing between k-points in the mesh (in angstrom^-1)
            'pseudo_family'         : 'pbe_gbrv_12',
            'epsilon_length'        : 1e-3,
            'epsilon_angle'         : 1e-4,
            'lowdim_params'         : lowdim_params,
            'num_machines'          : 1,
            'max_wallclock_seconds' : 30*60,
	        'on_theospc': on_theos,
        }

        wf = WorkflowLowDimFinder()
        wf.set_params(params)
        wf.start()

        print "Launched workflow {}".format(wf.uuid)

if __name__ == '__main__':
    from aiida import load_dbenv
    load_dbenv()
    launch_ws()
