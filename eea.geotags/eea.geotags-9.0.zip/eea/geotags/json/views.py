""" geotags JSON related views
"""

import json
from Products.Five.browser import BrowserView
from eea.geotags.vocabularies.interfaces import IGeoCountriesMapping


class CountryMappings(BrowserView):
    """ Geotags country mappings view
    """
    def __init__(self, context, request):
        self.request = request
        self.context = context

    def __call__(self, *args, **kwargs):
        """
        :return: json dict of country mappings
        :rtype: dict
        """
        res = {}
        vocab = IGeoCountriesMapping(self.context)()
        for i in vocab:
            res[i] = vocab[i].title
        return json.dumps(res)
