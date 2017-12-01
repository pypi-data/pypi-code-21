"""
slick.py is a library for talking to slick (http://code.google.com/p/slickqa).

Copyright 2013 AccessData Group, LLC.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
__author__ = 'Jason Corbett'

from . import micromodels

class SlickQuery(micromodels.Model):
    """Base class for all query classes.  Query classes aren't used by slick, but are a way of documenting which
    query options are available for various endpoints."""

    def __init__(self):
        super(SlickQuery, self).__init__()


class ConfigurationQuery(SlickQuery):
    """Configuration Query options.  There are 3:
     * name: You can query for the configuration by Name.
     * configurationType: Although this is a string (on the server side as well), there are a few known configuration
       types: PROJECT, and ENVIRONMENT.  You probably won't query for PROJECT types, as they are automatically included
       in the project itself.
     * filename: This corresponds to the filename parameter of the configuration data type.  It is not directly used
       by the server for anything, but is an additional way to distinguish one configuration from another.
    """
    name = micromodels.StringField()
    configurationType = micromodels.StringField()
    filename = micromodels.StringField()

    def __init__(self, name=None, configurationType=None, filename=None):
        """Create a new configuration query, optionally specifying the parameters"""
        super(ConfigurationQuery, self).__init__()

        if name is not None:
            self.name = name
        if configurationType is not None:
            self.configurationType = configurationType
        if filename is not None:
            self.filename = filename

class SystemConfigurationQuery(SlickQuery):
    """
    Query for SystemConfigurations.  SystemConfigurations are different in that they are only an interface on the server
    and any java class can inherit and become a SystemConfiguration.  Because of this there is no specific model for
    SystemConfiguration.

    The query options are for a specific config-type or name.
    """
    configtype = micromodels.StringField('config-type')
    name = micromodels.StringField()

    def __init__(self, configtype = None, name = None):
        """Query for a system configuration.  You should specify a configuration type, otherwise you will get lots of
        different system configuration types back.
        """
        if configtype is not None:
            self.configtype = configtype
        if name is not None:
            self.name = name

class ResultQuery(SlickQuery):
    testrunid = micromodels.StringField()
    status = micromodels.StringField()
    excludestatus = micromodels.StringField()
    runstatus = micromodels.StringField()
    allfields = micromodels.BooleanField()

    def __init__(self, testrunid=None, status=None, excludestatus=None, runstatus=None, allfields=None):
        if testrunid is not None:
            self.testrunid = testrunid
        if status is not None:
            self.status = status
        if excludestatus is not None:
            self.excludestatus = excludestatus
        if runstatus is not None:
            self.runstatus = runstatus
        if allfields is not None:
            self.allfields = allfields

class TestcaseQuery(SlickQuery):
    projectid = micromodels.StringField()
    componentid = micromodels.StringField()
    automationKey = micromodels.StringField()
    automationId = micromodels.StringField()
    automationTool = micromodels.StringField()
    tag = micromodels.StringField()
    automated = micromodels.BooleanField()
    author = micromodels.StringField()
    namecontains = micromodels.StringField()
    name = micromodels.StringField()

    def __init__(self, projectid=None, componentid=None, automationKey=None, automationId=None, automationTool=None, tag=None, automated=None, author=None, namecontains=None, name=None):
        if projectid is not None:
            self.projectid = projectid
        if componentid is not None:
            self.componentid = componentid
        if automationKey is not None:
            self.automationKey = automationKey
        if automationId is not None:
            self.automationId = automationId
        if automationTool is not None:
            self.automationTool = automationTool
        if tag is not None:
            self.tag = tag
        if automated is not None:
            self.automated = automated
        if author is not None:
            self.author = author
        if namecontains is not None:
            self.namecontains = namecontains
        if name is not None:
            self.name = name

class TestrunGroupQuery(SlickQuery):
    createdafter = micromodels.DateTimeField(use_int=True)
    name = micromodels.StringField()

    def __init__(self, createdafter=None, name=None):
        if createdafter is not None:
            self.createdafter = createdafter
        if name is not None:
            self.name = name

class TestplanQuery(SlickQuery):
    projectid = micromodels.StringField()
    createdby = micromodels.StringField()

    def __init__(self, projectid, createdby=None):
        self.projectid = projectid
        if createdby is not None:
            self.createdby = createdby

class TestrunQuery(SlickQuery):
    projectid = micromodels.StringField()
    releaseid = micromodels.StringField()
    buildid = micromodels.StringField()
    createdafter = micromodels.DateTimeField(use_int=True)
    configid = micromodels.StringField()
    testplanid = micromodels.StringField()
    configName = micromodels.StringField()
    projectName = micromodels.StringField()
    releaseName = micromodels.StringField()
    buildName = micromodels.StringField()
    name = micromodels.StringField()
    limit = micromodels.IntegerField()

    def __init__(self, projectid=None, releaseid=None, buildid=None, createdafter=None, configid=None, testplanid=None,
                 configName=None, projectName=None, releaseName=None, buildName=None, name=None, limit=None):
        if projectid is not None:
            self.projectid = projectid
        if releaseid is not None:
            self.releaseid = releaseid
        if buildid is not None:
            self.buildid = buildid
        if createdafter is not None:
            self.createdafter = createdafter
        if configid is not None:
            self.configid = configid
        if testplanid is not None:
            self.testplanid = testplanid
        if configName is not None:
            self.configName = configName
        if projectName is not None:
            self.projectName = projectName
        if releaseName is not None:
            self.releaseName = releaseName
        if buildName is not None:
            self.buildName = buildName
        if name is not None:
            self.name = name
        if limit is not None:
            self.limit = limit

class HostStatusQuery(SlickQuery):
    """Query for a hosts status"""
    checkincutoff = micromodels.IntegerField()

    def __init__(self, checkincutoff=None):
        """You can query for all the host status within a time window between "now" and a number of minutes ago.  The
        default cut off is 5 minutes."""
        if checkincutoff is not None:
            self.checkincutoff = checkincutoff
