# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

"""tCell Agent

This agent communicates with the tCell service and instruments your
application (when run as a command line tool) or can be used as an
SDK.

Example:
        $ tcell_agent python manage.py run 0.0.0.0:8000

https://www.tcell.io
"""


def init():
    from tcell_agent.instrumentation import run_instrumentations
    from tcell_agent.version import VERSION
    try:
        started = run_instrumentations()
        if started:
            print("tCell.io Agent: [Info]  Started tCell.io agent v{version} (sitecustomize)".format(version=VERSION))
    except Exception as e:
        print("tCell.io Agent: [Error] Could not start tCell.io agent v{version} {e} (sitecustomize)".format(
            version=VERSION, e=e))
        print(e)
        import traceback
        traceback.print_exc()
