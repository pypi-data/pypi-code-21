""" Controller
"""
import json
from zope.component import queryAdapter
from zope.component.hooks import getSite
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from Products.Five.browser import BrowserView

class View(BrowserView):
    """ Alchemy View Controller
    """
    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            site = getSite()
            self._settings = queryAdapter(site, IAlchemySettings)
        return self._settings

    def tags(self, **kwargs):
        """ Get tags
        """
        search = {}
        delimiter = self.settings.autoTaggingDelimiter
        if delimiter and delimiter != u' ':
            delimiter = delimiter.strip()

        if getattr(self.context, 'getField', None):
            table = self.settings.autoTaggingTable
            for name, link in table:
                field = self.context.getField(name)
                if not field:
                    continue
                value = field.getAccessor(self.context)()

                if not value:
                    continue

                if isinstance(value, (str, unicode)):
                    if delimiter:
                        for val in value.split(delimiter):
                            search[val.strip()] = link
                    else:
                        search[value] = link
                elif isinstance(value, (list, tuple, set)):
                    for val in value:
                        if not val:
                            continue
                        search[val] = link

        return {
            'enabled': self.settings.autoTagging,
            'blacklist': self.settings.autoTaggingBlackList,
            'firstOnly': self.settings.autoTaggingFirstOnly,
            'search': search
        }

    def tags_json(self, **kwargs):
        """ Return self.tags as JSON
        """
        return json.dumps(self.tags(**kwargs))
