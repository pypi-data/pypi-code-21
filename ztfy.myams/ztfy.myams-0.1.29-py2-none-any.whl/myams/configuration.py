#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
import pkg_resources
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces
from zope.annotation.interfaces import IAnnotations
from ztfy.myams.interfaces import IMyAMSApplication
from ztfy.myams.interfaces.configuration import IMyAMSStaticConfiguration, IMyAMSConfigurationTarget, IMyAMSConfiguration

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.location.location import locate
from zope.schema.fieldproperty import FieldProperty
from ztfy.extfile.blob import BlobImage, BlobFile
from ztfy.file.property import FileProperty

# import local packages
from ztfy.mail.adapter import getPrincipalAddress
from ztfy.utils.request import queryRequest
from ztfy.utils.traversing import getParent


class MyAMSStaticConfiguration(object):
    """MyAMS static configuration"""

    implements(IMyAMSStaticConfiguration)

    application_package = 'ztfy.myams'
    application_name = u'MyAMS'
    inner_package = None
    inner_package_name = None

    version_location = u'menus'

    include_top_links = True
    include_site_search = True
    include_mobile_search = True
    include_user_activity = True
    include_user_shortcuts = True
    include_logout_button = True
    include_minify_button = True
    include_flags = True
    include_menus = True
    include_ribbon = True
    include_reload_button = True
    body_css_class = u''

    @property
    def version(self):
        result = pkg_resources.get_distribution(self.application_package).version
        if self.inner_package:
            result += ' (%s v%s)' % (self.inner_package_name,
                                     pkg_resources.get_distribution(self.inner_package).version)
        return result


class MyAMSConfiguration(Persistent, Contained):
    """MyAMS user configuration"""

    implements(IMyAMSConfiguration)

    title = FieldProperty(IMyAMSConfiguration['title'])
    description = FieldProperty(IMyAMSConfiguration['description'])
    author = FieldProperty(IMyAMSConfiguration['author'])
    icon = FileProperty(IMyAMSConfiguration['icon'], klass=BlobImage, img_klass=BlobImage)
    logo = FileProperty(IMyAMSConfiguration['logo'], klass=BlobImage, img_klass=BlobImage)
    logo_title = FieldProperty(IMyAMSConfiguration['logo_title'])
    custom_css = FileProperty(IMyAMSConfiguration['custom_css'], klass=BlobFile)
    custom_js = FileProperty(IMyAMSConfiguration['custom_js'], klass=BlobFile)
    google_analytics_key = FieldProperty(IMyAMSConfiguration['google_analytics_key'])
    uservoice_api_key = FieldProperty(IMyAMSConfiguration['uservoice_api_key'])
    login_header_info = FieldProperty(IMyAMSConfiguration['login_header_info'])
    login_footer_info = FieldProperty(IMyAMSConfiguration['login_footer_info'])

    @property
    def static_configuration(self):
        application = getParent(self, IMyAMSApplication)
        if application is not None:
            return queryUtility(IMyAMSStaticConfiguration, name=application.configuration_name)

    def getUserEmail(self):
        request = queryRequest()
        if request is None:
            return None
        address = getPrincipalAddress(request.principal)
        if not address:
            return None
        return address[0][1]


MYAMS_CONFIGURATION_KEY = 'ztfy.myams.configuration'


@adapter(IMyAMSConfigurationTarget)
@implementer(IMyAMSConfiguration)
def MyAMSConfigurationFactory(context):
    """MyAMS configuration factory"""
    annotations = IAnnotations(context)
    configuration = annotations.get(MYAMS_CONFIGURATION_KEY)
    if configuration is None:
        configuration = annotations[MYAMS_CONFIGURATION_KEY] = MyAMSConfiguration()
        locate(configuration, context, '++configuration++')
    return configuration
