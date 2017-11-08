""" Custom validators
"""
from Products.validation.config import validation
from eea.relations.validators.contenttype import ContentType
from eea.relations.validators.required import Required

def register():
    """ Register validators
    """
    validation.register(ContentType('eea.relations.contenttype'))
    validation.register(Required('eea.relations.required'))
