""" Evolve to version 5.0
"""
import logging
from zope.component import queryAdapter
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
logger = logging.getLogger('eea.alchemy')

def upgrade(context):
    """ Move Alchemy API token to Plone Registry
    """
    site = getSite()
    ptool = getToolByName(site, 'portal_properties')
    atool = getattr(ptool, 'alchemyapi', None)
    key = getattr(atool, 'key', '')
    if isinstance(key, str):
        key = key.decode('utf-8')

    settings = queryAdapter(site, IAlchemySettings)
    settings.token = key

    if atool:
        ptool.manage_delObjects(ids=['alchemyapi'])
