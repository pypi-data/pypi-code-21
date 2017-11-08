""" Widget
"""
from Products.Archetypes.Registry import registerWidget
from eea.geotags.widget.location import GeotagsWidget

registerWidget(GeotagsWidget,
    title='Geotags Widget',
    description='Geotags widget',
    used_for=(
        'eea.geotags.field.GeotagsStringField',
        'eea.geotags.field.GeotagsLinesField',
    )
)
