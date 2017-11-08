""" Content rules handlers
"""
from plone.app.contentrules.handlers import execute

def inline_comment(event):
    """ Execute inline comment
    """
    execute(event.object, event)
