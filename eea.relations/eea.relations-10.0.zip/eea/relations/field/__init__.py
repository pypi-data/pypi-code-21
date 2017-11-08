""" Custom fields
"""
from Products.Archetypes.Registry import registerField
from eea.relations.field.referencefield import EEAReferenceField

def register():
    """ Register fields
    """
    registerField(
        EEAReferenceField,
        title="EEA Reference Field",
        description=("EEA Reference field that knows about is_required_for.")
    )
