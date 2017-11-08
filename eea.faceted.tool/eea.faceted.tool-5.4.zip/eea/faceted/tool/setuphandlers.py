""" Various setup
"""

def setupVarious(context):
    """ Do some various setup.
    """
    if context.readDataFile('eea.faceted.tool.txt') is None:
        return
