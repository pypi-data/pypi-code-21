### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
import re

# import Zope3 interfaces

# import local interfaces
from ztfy.appskin.interfaces import IApplicationBase
from ztfy.i18n.interfaces import II18nAttributesAware
from ztfy.i18n.interfaces.content import II18nBaseContent
from ztfy.security.interfaces import ILocalRoleManager
from ztfy.skin.interfaces import ISkinnable, ICustomBackOfficeInfoTarget

# import Zope3 packages
from zope.interface import Interface, Invalid, invariant
from zope.schema import Bool, List, Choice, Int, TextLine

# import local packages
from ztfy.file.schema import FileField, ImageField
from ztfy.i18n.schema import I18nTextLine, I18nHTML
from ztfy.security.schema import PrincipalList
from ztfy.utils.schema import TextLineListField

from ztfy.sendit import _


EMAIL_REGEX = re.compile("[^@]+@[^@]+\.[^@]+")


def checkPassword(password):
    """Check validity of a given password"""
    nbmaj = 0
    nbmin = 0
    nbn = 0
    nbo = 0
    for car in password:
        if ord(car) in range(ord('A'), ord('Z') + 1):
            nbmaj += 1
        elif ord(car) in range(ord('a'), ord('z') + 1):
            nbmin += 1
        elif ord(car) in range(ord('0'), ord('9') + 1):
            nbn += 1
        else:
            nbo += 1
    if [nbmin, nbmaj, nbn, nbo].count(0) > 1:
        raise Invalid(_("Your password must contain at least three of these kinds of characters: "
                        "lowercase letters, uppercase letters, numbers and special characters"))


#
# Custom exceptions classes
#

class FilterException(Exception):
    """Filter exclusion exception"""


#
# Sendit application interfaces
#

class ISenditApplicationInfo(II18nBaseContent):
    """Sendit application info"""


class ISenditApplicationSecurityInfo(Interface):
    """Sendit application security info"""

    administrators = PrincipalList(title=_("System administrators"),
                                   description=_("List of principals allowed to configure the whole application, "
                                                 "including system settings and utilities"),
                                   required=False)

    managers = PrincipalList(title=_("Application managers"),
                             description=_("List of principals which can manage application settings"),
                             required=False)

    open_registration = Bool(title=_("Open registration"),
                             description=_("If 'Yes', registration will be opened to external users"),
                             required=True,
                             default=False)

    confirmation_delay = Int(title=_("Confirmation delay"),
                             description=_("Number of days after which unconfirmed registration "
                                           "requests will be deleted"),
                             required=True,
                             default=7)

    internal_auth_plugins = List(title=_("Internal authenticators"),
                                 description=_("List of authentication plug-ins managing internal users.\n "
                                               "Profiles of internal users are automatically activated."),
                                 value_type=Choice(vocabulary='AuthenticatorPlugins'),
                                 default=[])

    external_auth_plugin = Choice(title=_("External authenticator"),
                                  description=_("Authenticator plug-in in which external users will be defined"),
                                  vocabulary='AuthenticatorPlugins',
                                  required=True,
                                  default=None)

    single_auth_plugins = List(title=_("Personal authentication plug-ins"),
                               description=_("List of authentication plug-ins which provide individual principals "
                                             "(instead of others which provide groups)"),
                               required=False,
                               value_type=Choice(vocabulary='AuthenticatorPlugins'))

    filtering_plugins = List(title=_("Packets filtering plug-ins"),
                             description=_("Selected plug-ins will be used to filter packets"),
                             required=False,
                             value_type=Choice(vocabulary='ZTFY Sendit filters'))

    trusted_redirects = Bool(title=_("Trusted redirects?"),
                             description=_("You can activate this option when your server is hosted behind an "
                                           "application firewall not using the same protocol (HTTP / HTTPS)"),
                             required=True,
                             default=False)


class ISenditApplicationMailingInfo(II18nAttributesAware):
    """Sendit application mailing info"""

    enable_notifications = Bool(title=_("Enable mail notifications?"),
                                description=_("If 'no', mail notifications will be disabled"),
                                required=True,
                                default=False)

    mailer_name = Choice(title=_("SMTP utility mailer"),
                         description=_("Mail delivery utility used to send mails"),
                         required=False,
                         vocabulary='ZTFY mail deliveries')

    @invariant
    def checkMailer(self):
        if self.enable_notifications and not self.mailer_name:
            raise Invalid(_("Notifications can't be enabled without mailer utility"))

    mail_service_owner = I18nTextLine(title=_("Service owner name"),
                                      description=_("Name of the entity providing this files sharing service"),
                                      required=True)

    mail_service_name = I18nTextLine(title=_("Service name"),
                                     description=_("This name will be the name of the service given in registration "
                                                   "and notification messages"),
                                     required=True)

    mail_sender_name = TextLine(title=_("Mails sender name"),
                                description=_("This name will be used for messages send by the application"),
                                required=True)

    mail_sender_address = TextLine(title=_("Mails sender address"),
                                   description=_("This address will be used for messages send by the application"),
                                   constraint=EMAIL_REGEX.match,
                                   required=True)

    mail_subject_header = I18nTextLine(title=_("Mails subject header prefix"),
                                       description=_("This header will be placed in front of each message send by "
                                                     "the application"),
                                       required=False)

    mail_signature = I18nHTML(title=_("Mails signature"),
                              description=_("This text will be placed in bottom of each message send by the "
                                            "application"),
                              required=False)


class ISenditApplicationQuotaInfo(Interface):
    """Sendit application quota info"""

    default_quota_size = Int(title=_("Default quota size"),
                             description=_("Default user quota size is given in megabytes"),
                             required=True,
                             default=1024)

    default_max_documents = Int(title=_("Default maximum documents count"),
                                description=_("Default maximum number of documents uploadable in a single packet"),
                                required=True,
                                default=10)


class ISenditApplicationFiltersInfo(Interface):
    """Sendit application filters info"""

    excluded_domains = TextLineListField(title=_("Excluded domains"),
                                         description=_("Target addresses from these domains will be globally excluded"),
                                         required=False)

    excluded_addresses = TextLineListField(title=_("Excluded addresses"),
                                           description=_("Target addresses matching these regular expressions will be "
                                                         "excluded. Don't forget to protect points with an antislash!"),
                                           required=False)

    excluded_principals = PrincipalList(title=_("Excluded principals"),
                                        description=_("Any individual or group principal present in this list will be "
                                                      "excluded"),
                                        required=False)

    def checkAddressFilters(self, address):
        """Check if given input matches any exclusion filter"""

    def checkPrincipalsFilters(self, principal):
        """Check if given principal matches any exclusion filter"""


class ISenditApplication(IApplicationBase, ISenditApplicationInfo, ISenditApplicationSecurityInfo,
                         ISenditApplicationMailingInfo, ISenditApplicationQuotaInfo, ISenditApplicationFiltersInfo,
                         ISkinnable, ILocalRoleManager, ICustomBackOfficeInfoTarget):
    """Sendit application interface"""


class ISenditApplicationBackInfo(Interface):
    """Sendit application back-office presentation options"""

    custom_css = FileField(title=_("Custom CSS"),
                           description=_("You can provide a custom CSS for your back-office"),
                           required=False)

    custom_banner = ImageField(title=_("Custom banner"),
                               description=_("You can provide a custom image file which will be displayed on top of "
                                             "back-office pages"),
                               required=False)

    custom_logo = ImageField(title=_("Custom logo"),
                             description=_("You can provide a custom image file which will be displayed on top of "
                                           "left column"),
                             required=False)

    custom_icon = ImageField(title=_("Custom icon"),
                             description=_("You can provide a custom image file to be used as back-office favorite "
                                           "icon"),
                             required=False)
