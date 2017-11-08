""" EEA Geotags interfaces
"""
# Vocabulary adapters
from eea.geotags.vocabularies.interfaces import IGeoGroups
from eea.geotags.vocabularies.interfaces import IBioGroups
from eea.geotags.vocabularies.interfaces import IGeoCountries
from eea.geotags.json.interfaces import IJsonProvider

# GeoTags storage
from eea.geotags.storage.interfaces import IGeoTaggable
from eea.geotags.storage.interfaces import IGeoTagged
from eea.geotags.storage.interfaces import IGeoTags

__all__ = [IGeoGroups.__name__,
           IBioGroups.__name__,
           IGeoCountries.__name__,
           IJsonProvider.__name__,
           IGeoTaggable.__name__,
           IGeoTagged.__name__,
           IGeoTags.__name__]
