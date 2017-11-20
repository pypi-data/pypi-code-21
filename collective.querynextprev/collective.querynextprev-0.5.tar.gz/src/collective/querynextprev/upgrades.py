# -*- coding: utf-8 -*-
import logging
from plone import api

logger = logging.getLogger('collective.querynextprev: upgrade. ')


def v1001(context):
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile('profile-collective.querynextprev:default', 'plone.app.registry')
