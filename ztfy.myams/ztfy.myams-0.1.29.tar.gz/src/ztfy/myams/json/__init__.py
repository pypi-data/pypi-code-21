#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.language.session.interfaces import ILanguageSession

# import local interfaces

# import Zope3 packages

# import local packages
from z3c.jsonrpc.publisher import MethodPublisher


class I18nMethodsPublisher(MethodPublisher):
    """I18n methods publisher"""

    def setUserLanguage(self, lang):
        if lang:
            ILanguageSession(self.request).setLanguage(lang)
