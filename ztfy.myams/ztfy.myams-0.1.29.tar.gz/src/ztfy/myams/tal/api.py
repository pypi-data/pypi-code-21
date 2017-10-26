#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.json.interfaces import IJSONWriter
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.myams.interfaces import IMyAMSApplication, IObjectData
from ztfy.myams.interfaces.configuration import IMyAMSConfiguration, IMyAMSStaticConfiguration, \
    MYAMS_CONFIGURATION_NAME_KEY
from ztfy.myams.tal.interfaces import IMyAMSTalesAPI

# import Zope3 packages
from zope.component import getUtility, queryUtility
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.utils.request import getRequestData
from ztfy.utils.traversing import getParent


class MyAMSTalesAdapter(object):
    """myams: TALES adapter"""

    implements(IMyAMSTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def data(self):
        data = IObjectData(self.context, None)
        if (data is not None) and data.object_data:
            writer = getUtility(IJSONWriter)
            return writer.write(data.object_data)

    @property
    def application(self):
        return getParent(self.context, IMyAMSApplication)

    def configuration(self):
        application = self.application
        if application is not None:
            return IMyAMSConfiguration(application, None)

    def static_configuration(self):
        configuration_name = getRequestData(MYAMS_CONFIGURATION_NAME_KEY, self.request)
        if configuration_name:
            configuration = queryUtility(IMyAMSStaticConfiguration, name=configuration_name)
            if configuration is not None:
                return configuration
        configuration = self.configuration()
        if configuration is not None:
            return configuration.static_configuration

    def resources(self):
        application = getParent(self.context, IMyAMSApplication)
        if application is not None:
            for resource in application.resources:
                removeSecurityProxy(resource).need()
