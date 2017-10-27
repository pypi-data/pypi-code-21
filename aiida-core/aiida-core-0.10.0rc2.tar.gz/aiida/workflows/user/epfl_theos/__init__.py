# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrea Cepellotti, Nicolas Mounet, Giovanni Pizzi."

def TheosWorkflowFactory(module):
    """
    Return a suitable Workflow subclass for the workflows defined here.
    """
    from aiida.common.pluginloader import BaseFactory

    return BaseFactory(module, Workflow, "aiida.workflows.user.epfl_theos")

