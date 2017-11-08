""" JSON adapters
"""
from zope.interface import implements
from eea.geotags.json.interfaces import IJsonProviderSearchMutator
from eea.geotags.vocabularies.interfaces import IGeoCountriesMapping


class JSONProviderSearchMutator(object):
    """ Abstract adapter to mutate JSONProvider search results
    """
    implements(IJsonProviderSearchMutator)

    def __init__(self, context):
        self.context = context

    def __call__(self, template):
        """ Return a dict of geonames search results
        """
        return template


class EEAJSONProviderSearchMutator(object):
    """ Abstract adapter to mutate JSONProvider search results
    """
    implements(IJsonProviderSearchMutator)

    def __init__(self, context):
        self.context = context
        self.country_mapping = IGeoCountriesMapping(context)()

    def __call__(self, template):
        """ Return a dict of geonames search with mutated results
        """
        features = template.get('features')
        is_matchable = hasattr(self.country_mapping, 'get')
        if features and is_matchable:
            for entry in features:
                match = self.country_mapping.get(
                    entry['properties'].get('title'))

                # check also description for country matching as some matches
                # might be triggered while checking for description
                if not match:
                    match = self.country_mapping.get(
                        entry['properties'].get('description'))

                if match:
                    title = match.title
                    entry['properties']['title'] = title
                    entry['properties']['description'] = title
                    entry['properties']['other']['countryName'] = title
                    entry['properties']['other']['name'] = title
        return template
