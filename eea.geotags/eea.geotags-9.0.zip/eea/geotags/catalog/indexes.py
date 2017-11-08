""" Custom zCatalog indexes
"""
import json
from copy import deepcopy
from zope.interface import Interface
from zope.component import queryAdapter
from eea.geotags.interfaces import IGeoTags
from plone.indexer.decorator import indexer

@indexer(Interface)
def geotags(obj, **kwargs):
    """ Index for eea.geotags annotations
    """
    geo = queryAdapter(obj, IGeoTags)
    if not geo:
        raise AttributeError

    tags = deepcopy(geo.tags)
    features = tags.get('features', [])
    if not features:
        return ""

    # Do some cleanup in order not to polute zCatalog with unnecesary data
    for feature in features:
        feature.get('properties', {}).pop('other', {})
    return json.dumps(tags)
