""" Popups
"""
import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.component import queryForwardRelations

logger = logging.getLogger('eea.relations.browser.popup')

class Popup(BrowserView):
    """ Widget popup helper
    """
    _relations = []
    _field = ''
    _uids = ()

    @property
    def field(self):
        """ Field
        """
        return self._field

    @property
    def uids(self):
        """ UIDs
        """
        return self._uids

    @property
    def relations(self):
        """ Relations
        """
        if self._relations:
            return self._relations
        self._relations = queryForwardRelations(self.context)
        return self._relations

    def tabs(self):
        """ Return popup tabs
        """
        rtool = getToolByName(self.context, 'portal_relations')
        rtoolObjects = rtool.objectIds()
        for relation in self.relations:
            nto = relation.getField('to').getAccessor(relation)()
            if nto not in rtoolObjects:
                continue

            required = relation.getField('required').getAccessor(relation)()
            required_for = relation.getField(
                'required_for').getAccessor(relation)()
            yield rtool[nto], required, bool(required_for)

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        field = kwargs.get('field', '')
        if field:
            self._field = field

        # Uids
        uids = kwargs.get('uids', ())
        self._uids = uids

        return self.index()

class BaseView(BrowserView):
    """ Base view for selected item
    """
    _field = ''
    _mode = 'view'
    _uids = ()

    @property
    def field(self):
        """ Field
        """
        return self._field

    @property
    def mode(self):
        """ Mode
        """
        return self._mode

    @property
    def uids(self):
        """ UIDs
        """
        return self._uids

    def setup(self, **kwargs):
        """ Setup view
        """
        if self.request:
            kwargs.update(self.request.form)

        # jQuery >= 1.4 adds type to params keys
        # $.param({ a: [2,3,4] }) // "a[]=2&a[]=3&a[]=4"
        # Let's fix this
        kwargs = dict((key.replace('[]', ''), val)
                      for key, val in kwargs.items())

        # Set mode
        mode = kwargs.pop('mode', 'view')
        self._mode = mode

        # Set field
        field = kwargs.pop('field', '')
        self._field = field

        # Set uids
        uids = kwargs.pop('uids', ())
        if not isinstance(uids, (list, tuple)):
            uids = uids,
        self._uids = [uid for uid in uids if uid]

        self.kwargs = kwargs


class PopupSelectedItems(BaseView):
    """ Widget popup selected items helper
    """
    @property
    def items(self):
        """ Return selected items
        """
        if not self.uids:
            return

        ctool = getToolByName(self.context, 'portal_catalog')
        for uid in self.uids:
            if not uid:
                continue
            brains = ctool(UID=uid)
            for brain in brains:
                yield brain.getObject()

    def __call__(self, **kwargs):
        """ Render
        """
        self.setup(**kwargs)
        return self.index()

class PopupSelectedItem(BaseView):
    """ Display an item
    """
    def __call__(self, **kwargs):
        self.setup(**kwargs)
        return self.index()
