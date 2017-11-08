""" Field
"""
from Products.Archetypes.Registry import registerField
from eea.geotags.field.location import GeotagsStringField, GeotagsLinesField

registerField(
    GeotagsStringField,
    title="Geotags String Field",
    description=("Geotags string field.")
)

registerField(
    GeotagsLinesField,
    title="Geotags Lines Field",
    description=("Geotags lines field.")
)
