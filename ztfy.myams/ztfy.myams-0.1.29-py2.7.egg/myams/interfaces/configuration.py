#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import Text, TextLine, Bool, Choice

# import local packages
from ztfy.file.schema import ImageField, FileField

from ztfy.myams import _


MYAMS_CONFIGURATION_NAME_KEY = 'ztfy.myams.configuration.name'


class IMyAMSStaticConfiguration(Interface):
    """MyAMS static configuration"""

    application_package = TextLine(title=_("Main application package"),
                                   description=_("This package is used to get application version"),
                                   required=False)

    application_name = TextLine(title=_("Main application name"),
                                description=_("This name is used to display application version"),
                                required=False)

    inner_package = TextLine(title=_("Inner package"),
                             description=_("This is another important package displayed in application version"),
                             required=False)

    inner_package_name = TextLine(title=_("Inner package name"),
                                  description=_("Package name used to display application version"),
                                  required=False)

    version = Attribute(_("Application version"))

    version_location = Choice(title=_("Version location"),
                              required=False,
                              values=(u'menus', u'shortcuts'),
                              default=u'menus')

    include_top_links = Bool(title=_("Include top links?"),
                             default=True,
                             required=True)

    include_site_search = Bool(title=_("Include site search?"),
                               default=True,
                               required=True)

    include_mobile_search = Bool(title=_("Include mobile search?"),
                                 default=True,
                                 required=True)

    include_user_activity = Bool(title=_("Include user dropdown window?"),
                                 default=True,
                                 required=True)

    include_user_shortcuts = Bool(title=_("Include user shortcuts?"),
                                  default=True,
                                  required=True)

    include_logout_button = Bool(title=_("Include logout button?"),
                                 default=True,
                                 required=True)

    include_minify_button = Bool(title=_("Include minify button?"),
                                 default=True,
                                 required=True)

    include_flags = Bool(title=_("Include flags menu?"),
                         default=True,
                         required=True)

    include_menus = Bool(title=_("Include main menus?"),
                         default=True,
                         required=True)

    include_ribbon = Bool(title=_("Include ribbon?"),
                          default=True,
                          required=True)

    include_reload_button = Bool(title=_("Include reload button?"),
                                 default=True,
                                 required=True)

    body_css_class = TextLine(title=_("Body HTML tag CSS class"),
                              required=False)


class IMyAMSConfiguration(Interface):
    """MyAMS application global configuration"""

    title = TextLine(title=_("Title"),
                     description=_("Application title displayed in title bar"),
                     required=False)

    description = TextLine(title=_("Description"),
                           description=_("Main application description"),
                           required=False)

    author = TextLine(title=_("Author"),
                      description=_("Public author name"),
                      required=False)

    icon = ImageField(title=_("Favorites icon"),
                      description=_("Please provide a transparent image of 32x32 pixels..."),
                      required=False)

    logo = ImageField(title=_("Logo"),
                      description=_("Please provide a transparent image in PNG format..."),
                      required=False)

    logo_title = TextLine(title=_("Logo title"),
                          description=_("This text will be used as logo alternate text"),
                          required=False)

    custom_css = FileField(title=_("Custom CSS file"),
                           required=False)

    custom_js = FileField(title=_("Custom javascript file"),
                          required=False)

    google_analytics_key = TextLine(title=_("Google Analytics key"),
                                    required=False)

    uservoice_api_key = TextLine(title=_("UserVoice API key"),
                                 description=_("This is the name of UserVoice javascript file"),
                                 required=False)

    login_header_info = Text(title=_("Login page header info"),
                             description=_("This text will be displayed in login page header. "
                                           "You can use reStructuredText syntax."),
                             required=False)

    login_footer_info = Text(title=_("Login page footer info"),
                             description=_("This text will be displayed in login page footer. "
                                           "You can use reStructuredText syntax."),
                             required=False)

    static_configuration = Attribute(_("Application static configuration utility"))

    def getUserEmail(self):
        """Get current user email address"""


class IMyAMSConfigurationTarget(Interface):
    """MyAMS configuration marker interface"""
