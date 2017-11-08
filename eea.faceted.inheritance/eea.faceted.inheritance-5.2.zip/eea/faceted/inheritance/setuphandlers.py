""" EEA Faceted Inheritance various setup
"""

def setupVarious(context):
    """ Various setup
    """
    if context.readDataFile('eea.faceted.inheritance.txt') is None:
        return
