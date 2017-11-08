""" JSON Interfaces
"""
from zope.interface import Interface

class IJsonProvider(Interface):
    """ Get a JSON from external webservice and return it following the
        geojson specifications. See http://geojson.org
    """

    def groups(**kwargs):
        """ Country groups (e.g continents)
        """

    def biogroups(**kwargs):
        """ Biogeographical regions
        """

    def countries(group=None, continentCode='EU', **kwargs):
        """ Countries in group and continent
        """

    def nuts(country=None, **kwargs):
        """ Primary administrative divisions of a country
        """

    def cities(country=None, adminCode1=None, **kwargs):
        """ Cities filtered by country and/or primary administrative division
        """

    def natural_features(country=None, adminCode1=None, **kwargs):
        """ Natural features filtered by country and/or primary
            administrative division
        """

    def search(**kwargs):
        """ Free search
        """


class IJsonProviderSearchMutator(Interface):
    """ Adapter to mutate JsonProvider searches
    """
    def __call__(**kwargs):
        """ Return a dict with modified search results
        """
