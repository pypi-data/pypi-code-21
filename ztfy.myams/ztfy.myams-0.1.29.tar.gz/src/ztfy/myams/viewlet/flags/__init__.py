#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.language.negotiator.interfaces import INegotiatorManager
from zope.i18n.interfaces import INegotiator

# import local interfaces

# import Zope3 packages
from zope.component import adapts, queryUtility
from zope.i18n import translate
from zope.interface import Interface

# import local packages
from ztfy.baseskin.viewlet import ContentProviderBase
from ztfy.myams.layer import MyAMSLayer


class FlagsContentProvider(ContentProviderBase):
    """Flags content provider"""

    adapts(Interface, MyAMSLayer, Interface)

    @property
    def langs(self):
        manager = queryUtility(INegotiatorManager)
        if manager is not None:
            return manager.offeredLanguages
        return ()

    def getLabel(self, lang):
        try:
            from ztfy.i18n.languages import BASE_LANGUAGES
        except ImportError:
            return lang
        else:
            return translate(BASE_LANGUAGES.get(lang), context=self.request)

    @property
    def current(self):
        manager = queryUtility(INegotiatorManager)
        negotiator = queryUtility(INegotiator)
        if (manager is not None) and (negotiator is not None):
            return negotiator.getLanguage(manager.offeredLanguages, self.request)
        return None
