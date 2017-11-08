""" EEA Relations
"""
def initialize(context):
    """ Zope 2 """
    from eea.relations import validators
    validators.register()

    from eea.relations import field
    field.register()

    from eea.relations import widget
    widget.register()

    from eea.relations import content
    content.initialize(context)
