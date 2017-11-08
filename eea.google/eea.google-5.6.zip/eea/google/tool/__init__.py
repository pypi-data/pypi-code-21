""" tool package """

from Products.CMFCore.utils import ToolInit
from eea.google.tool.google import GoogleTool


def initialize(context):
    """ initialize function called when used as a zope2 product """

    ToolInit('eea.google',
             tools=(GoogleTool,),
             icon='icon.gif',
    ).initialize(context)
