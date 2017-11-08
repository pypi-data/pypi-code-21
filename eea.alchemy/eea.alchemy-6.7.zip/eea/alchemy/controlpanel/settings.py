""" Control Panel
"""
from zope.component import queryUtility
from zope.interface import implements
from zope.formlib import form
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from eea.alchemy.controlpanel.interfaces import _
from plone.app.controlpanel.form import ControlPanelForm
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

class ControlPanel(ControlPanelForm):
    """ Diffbot API
    """
    form_fields = form.FormFields(IAlchemySettings)
    label = _(u"Alchemy Settings")
    description = _(u"Alchemy settings")
    form_name = _(u"Alchemy settings")

class ControlPanelAdapter(SchemaAdapterBase):
    """ Form adapter
    """
    implements(IAlchemySettings)

    def __init__(self, context):
        super(ControlPanelAdapter, self).__init__(context)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            self._settings = queryUtility(
                IRegistry).forInterface(IAlchemySettings, False)
        return self._settings

    @property
    def token(self):
        """ Get token
        """
        name = u"token"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @token.setter
    def token(self, value):
        """ Set token
        """
        self.settings.token = value

    @property
    def autoTagging(self):
        """ Enable auto-tagging
        """
        name = u"autoTagging"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoTagging.setter
    def autoTagging(self, value):
        """ Enable / disable auto-tagging
        """
        self.settings.autoTagging = value

    @property
    def modalDisplay(self):
        """ Enable auto-tagging
        """
        name = u"modalDisplay"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @modalDisplay.setter
    def modalDisplay(self, value):
        """ Enable / disable auto-tagging
        """
        self.settings.modalDisplay = value


    @property
    def autoTaggingFirstOnly(self):
        """ Auto-tagging only the first occurence
        """
        name = u"autoTaggingFirstOnly"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoTaggingFirstOnly.setter
    def autoTaggingFirstOnly(self, value):
        """ Auto-tagging only the first occurence
        """
        self.settings.autoTaggingFirstOnly = value

    @property
    def autoTaggingTable(self):
        """ Fields and links
        """
        name = u"autoTaggingTable"
        mapping = getattr(self.settings, name, {})
        return mapping.items()

    @autoTaggingTable.setter
    def autoTaggingTable(self, value):
        """ Update autoTaggingTable
        """
        self.settings.autoTaggingTable = dict(value)

    @property
    def autoTaggingBlackList(self):
        """ Blacklist
        """
        name = u"autoTaggingBlackList"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoTaggingBlackList.setter
    def autoTaggingBlackList(self, value):
        """ Update blacklist
        """
        self.settings.autoTaggingBlackList = value

    @property
    def autoTaggingDelimiter(self):
        """ Blacklist
        """
        name = u"autoTaggingDelimiter"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoTaggingDelimiter.setter
    def autoTaggingDelimiter(self, value):
        """ Update blacklist
        """
        self.settings.autoTaggingDelimiter = value

    @property
    def autoRelations(self):
        """ Enable auto-relations
        """
        name = u"autoRelations"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoRelations.setter
    def autoRelations(self, value):
        """ Enable / disable auto-relations
        """
        self.settings.autoRelations = value

    @property
    def autoRelationsFields(self):
        """ Fields
        """
        name = u"autoRelationsFields"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @autoRelationsFields.setter
    def autoRelationsFields(self, value):
        """ Update autoRelationsFields
        """
        self.settings.autoRelationsFields = value

    @property
    def onlyExistingKeywords(self):
        """ Only discover existing keywords
        """
        name = u"onlyExistingKeywords"
        return getattr(self.settings, name, IAlchemySettings[name].default)

    @onlyExistingKeywords.setter
    def onlyExistingKeywords(self, value):
        """ Enable / disable onlyExistingKeywords
        """
        self.settings.onlyExistingKeywords = value
