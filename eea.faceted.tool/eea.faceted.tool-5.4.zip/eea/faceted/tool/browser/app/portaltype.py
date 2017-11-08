""" Portal type forms
"""
from z3c.form import form, field
from z3c.form import button

from zope.container.interfaces import INameChooser
from eea.faceted.tool.config import EEAMessageFactory as _
from eea.faceted.tool.interfaces import IPortalType
from eea.faceted.tool.storage.portaltype import PortalType


class AddPage(form.AddForm):
    """ Add page
    """
    fields = field.Fields(IPortalType)

    def create(self, data):
        """ Create
        """
        name = INameChooser(
            self.context).chooseName(data.get('title', ''), None)
        ob = PortalType(id=name)
        form.applyChanges(self, ob, data)
        return ob

    def add(self, obj):
        """ Add
        """
        name = obj.getId()
        self.context[name] = obj
        self._finished_add = True
        return obj

    def nextURL(self):
        """ Next
        """
        return "./@@view"


class EditPage(form.EditForm):
    """ Edit page
    """
    fields = field.Fields(IPortalType)

    def nextURL(self):
        """ Next
        """
        return "../@@view"

    @button.buttonAndHandler(_(u"label_apply", default=u"Apply"),
                             name='apply')
    def handleApply(self, action):
        """ Apply button
        """
        super(EditPage, self).handleApply(self, action)
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        """ Cancel button
        """
        self.request.response.redirect(self.nextURL())
        return ''
