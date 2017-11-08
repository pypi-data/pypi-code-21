""" EEA Faceted Tool
"""
from Products.CMFCore.utils import ToolInit
from eea.faceted.tool.tool import FacetedTool

def initialize(context):
    """ initialize function called when used as a zope2 product """

    ToolInit('eea.faceted.tool',
             tools=(FacetedTool,),
             icon='tool.gif',
    ).initialize(context)
