""" Export / Import adapters to be used within GenericSetup
"""
import os
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody

def importFacetedTool(context):
    """Import faceted settings."""
    logger = context.getLogger('eea.faceted.tool')

    body = context.readDataFile('faceted.xml')
    if body is None:
        logger.info("Nothing to import")
        return

    site = context.getSite()
    ftool = getToolByName(site, 'portal_faceted', None)
    if not ftool:
        logger.info('portal_faceted tool missing')
        return

    importer = queryMultiAdapter((ftool, context), IBody)
    if importer is None:
        logger.warning("Import adapter missing.")
        return

    # set filename on importer so that syntax errors can be reported properly
    subdir = getattr(context, '_profile_path', '')
    importer.filename = os.path.join(subdir, 'faceted.xml')

    importer.body = body
    logger.info("Imported.")

def exportFacetedTool(context):
    """Export faceted settings."""
    logger = context.getLogger('eea.faceted.tool')
    site = context.getSite()
    ftool = getToolByName(site, 'portal_faceted')

    if ftool is None:
        logger.info("Nothing to export")
        return

    exporter = queryMultiAdapter((ftool, context), IBody)
    if exporter is None:
        logger.warning("Export adapter missing.")
        return

    context.writeDataFile('faceted.xml', exporter.body, exporter.mime_type)
    logger.info("Exported.")
