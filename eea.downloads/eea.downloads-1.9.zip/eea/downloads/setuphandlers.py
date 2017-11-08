""" Various setup
"""
from eea.downloads.config import PROJECTNAME, ENVNAME
from eea.downloads.content.DirectoryView import createDirectoryView

def setupVarious(context):
    """ Do some various setup.
    """
    if context.readDataFile('eea.downloads.txt') is None:
        return

    site = context.getSite()
    name = ENVNAME()
    if name not in site.objectIds():
        createDirectoryView(site, PROJECTNAME, name)
