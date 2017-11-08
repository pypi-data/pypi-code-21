""" Fields
"""
from Products.Archetypes.Registry import registerField
from eea.forms.fields.ManagementPlanField import ManagementPlanField

def register():
    """ Register custom fields
    """
    registerField(ManagementPlanField, title=u'Management Plan Field')
