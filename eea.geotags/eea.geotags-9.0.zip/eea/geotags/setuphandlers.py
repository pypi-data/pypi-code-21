""" Setuphandlers
"""
import logging
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.utils.vocabs import createHierarchicalVocabs
from eea.geotags.vocabularies.data.groups import VOC
from eea.geotags.vocabularies.data.biogroups import VOC as BIOVOC

logger = logging.getLogger('eea.geotags.setuphandlers')


def setupGeonames(site):
    """ Add geonames_key properties
    """
    ptool = getToolByName(site, 'portal_properties')
    if 'geographical_properties' not in ptool.objectIds():
        ptool.addPropertySheet(id='geographical_properties',
                               title='Geographical properties')
    gprops = getattr(ptool, 'geographical_properties')
    if not hasattr(gprops, 'geonames_key'):
        gprops.manage_addProperty('geonames_key', '', 'string')


def importVocabularies(context):
    """ Import groups vocabulary
    """
    site = context.getSite()
    atvm = getToolByName(site, 'portal_vocabularies', None)

    createHierarchicalVocabs(atvm, VOC)
    logger.info("Added 'Geotags Tree' vocabulary")

    createHierarchicalVocabs(atvm, BIOVOC)
    logger.info('Added "Biogeographical regions" vocabulary')


def importVarious(context):
    """ Import various
    """
    if context.readDataFile('eea.geotags.txt') is None:
        return

    importVocabularies(context)
