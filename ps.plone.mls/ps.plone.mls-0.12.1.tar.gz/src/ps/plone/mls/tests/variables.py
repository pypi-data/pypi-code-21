# -*- coding: utf-8 -*-
"""Variables used by plone.app.robotframework."""

# python imports
import pkg_resources


CMFPLONE_VERSION = pkg_resources.get_distribution('Products.CMFPlone').version

if CMFPLONE_VERSION.startswith('5.'):
    PSPLONEMLS_PLONE_SELECTORS = 'selectors/plone-5.x.robot'
elif CMFPLONE_VERSION.startswith('4.3'):
    PSPLONEMLS_PLONE_SELECTORS = 'selectors/plone-4.3.x.robot'
elif CMFPLONE_VERSION.startswith('4.2'):
    PSPLONEMLS_PLONE_SELECTORS = 'selectors/plone-4.2.x.robot'
elif CMFPLONE_VERSION.startswith('4.1'):
    PSPLONEMLS_PLONE_SELECTORS = 'selectors/plone-4.1.x.robot'
elif CMFPLONE_VERSION.startswith('4.'):
    PSPLONEMLS_PLONE_SELECTORS = 'selectors/plone-4.x.robot'

PSPLONEMLS_DEFAULT_SELECTORS = 'selectors/default.robot'
