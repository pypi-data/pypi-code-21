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

from . import micromodels


class Configuration(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    configurationType = micromodels.StringField()
    filename = micromodels.StringField()

    # Using BaseField for now as a way of holding a dictionary field
    configurationData = micromodels.BaseField()

    def create_reference(self):
        reference = ConfigurationReference()
        reference.configId = self.id
        reference.name = self.name
        if hasattr(self, 'filename'):
            reference.filename = self.filename
        return reference


class Link(micromodels.Model):
    name = micromodels.StringField()
    url = micromodels.StringField()


class StoredFile(micromodels.Model):
    id = micromodels.StringField()
    filename = micromodels.StringField()
    chunkSize = micromodels.IntegerField()
    uploadDate = micromodels.DateTimeField(use_int=True)
    mimetype = micromodels.StringField()
    md5 = micromodels.StringField()
    length = micromodels.IntegerField()


class ConfigurationReference(micromodels.Model):
    configId = micromodels.StringField()
    name = micromodels.StringField()
    filename = micromodels.StringField()


class ReloadStatus(micromodels.Model):
    systemName = micromodels.StringField()
    reloadTime = micromodels.DateTimeField(use_int=True)
    systemStatus = micromodels.StringField()


class Quote(micromodels.Model):
    id = micromodels.StringField()
    quote = micromodels.StringField()
    imageUrl = micromodels.StringField()
    attributed = micromodels.StringField()


class Build(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    built = micromodels.DateTimeField(use_int=True)
    description = micromodels.StringField()

    def create_reference(self):
        ref = BuildReference()
        ref.buildId = self.id
        ref.name = self.name
        return ref


class BuildReference(micromodels.Model):
    buildId = micromodels.StringField()
    name = micromodels.StringField()


class Release(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    target = micromodels.DateTimeField(use_int=True)
    defaultBuild = micromodels.StringField()
    builds = micromodels.ModelCollectionField(Build)
    status = micromodels.StringField()

    def create_reference(self):
        ref = ReleaseReference()
        ref.releaseId = self.id
        ref.name = self.name
        return ref


class ReleaseReference(micromodels.Model):
    releaseId = micromodels.StringField()
    name = micromodels.StringField()


class FeatureReference(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()


class Feature(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    description = micromodels.StringField()
    imgUrl = micromodels.StringField()
    img = micromodels.ModelField(StoredFile)

    def create_reference(self):
        ref = FeatureReference()
        ref.id = self.id
        ref.name = self.name
        return ref


class ComponentReference(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    code = micromodels.StringField()


class Component(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    description = micromodels.StringField()
    code = micromodels.StringField()
    features = micromodels.ModelCollectionField(Feature)

    def create_reference(self):
        ref = ComponentReference()
        ref.id = self.id
        ref.name = self.name
        if hasattr(self, 'code') and self.code is not None:
            ref.code = self.code
        return ref


class DataDrivenPropertyType(micromodels.Model):
    name = micromodels.StringField()
    requirement = micromodels.BooleanField()
    standardValues = micromodels.FieldCollectionField(micromodels.StringField)


class Project(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    description = micromodels.StringField()
    configuration = micromodels.ModelField(Configuration)
    defaultRelease = micromodels.StringField()
    releases = micromodels.ModelCollectionField(Release)
    inactiveReleases = micromodels.ModelCollectionField(Release)
    lastUpdated = micromodels.DateTimeField(use_int=True)
    tags = micromodels.FieldCollectionField(micromodels.StringField())
    attributes = micromodels.BaseField()
    automationTools = micromodels.FieldCollectionField(micromodels.StringField())
    components = micromodels.ModelCollectionField(Component)
    datadrivenProperties = micromodels.ModelCollectionField(DataDrivenPropertyType)

    def create_reference(self):
        reference = ProjectReference()
        reference.id = self.id
        reference.name = self.name
        return reference


class ProjectReference(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()


class ProductVersion(micromodels.Model):
    """This class represents a version of a product.  The only product included with slick for now is 'slick'"""
    productName = micromodels.StringField()
    versionString = micromodels.StringField()


class TestcaseQuery(micromodels.Model):
    queryDescription = micromodels.StringField()
    className = micromodels.StringField()

# TODO: define all the types of test case queries

class NamedTestCaseQuery(micromodels.Model):
    name = micromodels.StringField()
    query = micromodels.ModelField(TestcaseQuery)


class Step(micromodels.Model):
    name = micromodels.StringField()
    expectedResult = micromodels.StringField()


class TestcaseReference(micromodels.Model):
    testcaseId = micromodels.StringField()
    name = micromodels.StringField()
    automationId = micromodels.StringField()
    automationKey = micromodels.StringField()
    automationTool = micromodels.StringField()


class Testcase(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    purpose = micromodels.StringField()
    requirements = micromodels.StringField()
    steps = micromodels.ModelCollectionField(Step)
    author = micromodels.StringField()
    attributes = micromodels.BaseField()
    automated = micromodels.BooleanField()
    automationPriority = micromodels.IntegerField()
    automationTool = micromodels.StringField()
    automationConfiguration = micromodels.StringField()
    automationId = micromodels.StringField()
    automationKey = micromodels.StringField()
    stabilityRating = micromodels.IntegerField()
    tags = micromodels.FieldCollectionField(micromodels.StringField())
    project = micromodels.ModelField(ProjectReference)
    component = micromodels.ModelField(ComponentReference)
    dataDriven = micromodels.ModelCollectionField(DataDrivenPropertyType)
    deleted = micromodels.BooleanField()

    def create_reference(self):
        reference = TestcaseReference()
        reference.testcaseId = self.id
        reference.name = self.name
        if hasattr(self, 'automationId'):
            reference.automationId = self.automationId
        if hasattr(self, 'automationKey'):
            reference.automationKey = self.automationKey
        if hasattr(self, 'automationTool'):
            reference.automationTool = self.automationTool
        return reference


class Testplan(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    createdBy = micromodels.StringField()
    project = micromodels.ModelField(ProjectReference)
    sharedWith = micromodels.FieldCollectionField(micromodels.StringField())
    isprivate = micromodels.BooleanField()
    queries = micromodels.ModelCollectionField(NamedTestCaseQuery)


class ConfigurationOverride(micromodels.Model):
    key = micromodels.StringField()
    value = micromodels.StringField()
    isRequirement = micromodels.BooleanField()


class TestplanRunParameters(micromodels.Model):
    config = micromodels.ModelField(ConfigurationReference)
    runtimeOptions = micromodels.ModelField(ConfigurationReference)
    release = micromodels.ModelField(ReleaseReference)
    build = micromodels.ModelField(BuildReference)
    configurationOverride = micromodels.ModelCollectionField(ConfigurationOverride)


class ResultsByStatus(micromodels.Model):
    PASS = micromodels.IntegerField()
    FAIL = micromodels.IntegerField()
    BROKEN_TEST = micromodels.IntegerField()
    NOT_TESTED = micromodels.IntegerField()
    SKIPPED = micromodels.IntegerField()
    NO_RESULT = micromodels.IntegerField()
    CANCELLED = micromodels.IntegerField()
    PASSED_ON_RETRY = micromodels.IntegerField()


class TestrunSummary(micromodels.Model):
    totalTime = micromodels.IntegerField()
    resultsByStatus = micromodels.ModelField(ResultsByStatus)
    statusListOrdered = micromodels.FieldCollectionField(micromodels.StringField())
    total = micromodels.IntegerField()


class SlickUpdate(micromodels.Model):
    updateId = micromodels.StringField()
    description = micromodels.StringField()
    name = micromodels.StringField()
    needsApplying = micromodels.BooleanField()


class TestrunReference(micromodels.Model):
    testrunId = micromodels.StringField()
    name = micromodels.StringField()


class Testrun(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    testplanId = micromodels.StringField()
    testplan = micromodels.ModelField(Testplan)
    config = micromodels.ModelField(ConfigurationReference)
    runtimeOptions = micromodels.ModelField(ConfigurationReference)
    project = micromodels.ModelField(ProjectReference)
    dateCreated = micromodels.DateTimeField(use_int=True)
    runStarted = micromodels.DateTimeField(use_int=True)
    runFinshed = micromodels.DateTimeField(use_int=True)
    release = micromodels.ModelField(ReleaseReference)
    build = micromodels.ModelField(BuildReference)
    summary = micromodels.ModelField(TestrunSummary)
    files = micromodels.ModelCollectionField(StoredFile)
    links = micromodels.ModelCollectionField(Link)
    info = micromodels.StringField()
    state = micromodels.StringField()
    attributes = micromodels.BaseField()

    def create_reference(self):
        ref = TestrunReference()
        ref.testrunId = self.id
        ref.name = self.name
        return ref


class GroupType:
    PARALLEL = "PARALLEL"
    SERIAL = "SERIAL"

    def __init__(self):
        pass


class TestrunGroup(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    created = micromodels.DateTimeField(use_int=True)
    testruns = micromodels.ModelCollectionField(Testrun)
    groupType = micromodels.StringField()
    groupSummary = micromodels.ModelField(TestrunSummary)


class TestRunParameter(micromodels.Model):
    fulFilledRequirements = micromodels.BaseField()
    automationTool = micromodels.StringField()
    hostname = micromodels.StringField()


class ResultStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_TESTED = "NOT_TESTED"
    NO_RESULT = "NO_RESULT"
    BROKEN_TEST = "BROKEN_TEST"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    PASSED_ON_RETRY = "PASSED_ON_RETRY"

    def __init__(self):
        pass


class RunStatus:
    SCHEDULED = "SCHEDULED"
    TO_BE_RUN = "TO_BE_RUN"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"

    def __init__(self):
        pass


class LogEntry(micromodels.Model):
    entryTime = micromodels.DateTimeField(use_int=True)
    level = micromodels.StringField()
    loggerName = micromodels.StringField()
    message = micromodels.StringField()
    exceptionClassName = micromodels.StringField()
    exceptionMessage = micromodels.StringField()
    exceptionStackTrace = micromodels.FieldCollectionField(micromodels.StringField())


class UpdateRecord(micromodels.Model):
    id = micromodels.StringField()
    updateId = micromodels.StringField()
    logs = micromodels.ModelCollectionField(LogEntry)


class ResultReference(micromodels.Model):
    resultId = micromodels.StringField()
    status = micromodels.StringField()
    recorded = micromodels.DateTimeField(use_int=True)
    build = micromodels.ModelField(BuildReference)


class Result(micromodels.Model):
    id = micromodels.StringField()
    testrun = micromodels.ModelField(TestrunReference)
    config = micromodels.ModelField(ConfigurationReference)
    configurationOverride = micromodels.ModelCollectionField(ConfigurationOverride)
    testcase = micromodels.ModelField(TestcaseReference)
    recorded = micromodels.DateTimeField(use_int=True)
    started = micromodels.DateTimeField(use_int=True)
    finished = micromodels.DateTimeField(use_int=True)
    status = micromodels.StringField()
    runstatus = micromodels.StringField()
    reason = micromodels.StringField()
    attributes = micromodels.BaseField()
    files = micromodels.ModelCollectionField(StoredFile)
    links = micromodels.ModelCollectionField(Link)
    log = micromodels.ModelCollectionField(LogEntry)
    project = micromodels.ModelField(ProjectReference)
    component = micromodels.ModelField(ComponentReference)
    release = micromodels.ModelField(ReleaseReference)
    build = micromodels.ModelField(BuildReference)
    runlength = micromodels.IntegerField()
    history = micromodels.ModelCollectionField(ResultReference)
    hostname = micromodels.StringField()
    requirements = micromodels.FieldCollectionField(micromodels.StringField())


class HostStatus(micromodels.Model):
    hostname = micromodels.StringField()
    lastCheckIn = micromodels.DateTimeField(use_int=True)
    currentWork = micromodels.ModelField(Result)


class SystemConfiguration(micromodels.Model):
    """
    This model should be inherited by a sub model as each SystemConfiguration class will have different properties.
    The properties listed here are ones that are global to all SystemConfiguration instances (they are part of the
    java interface).
    """
    id = micromodels.StringField()
    configurationType = micromodels.StringField()
    name = micromodels.StringField()
    className = micromodels.StringField()


class AMQPSystemConfiguration(SystemConfiguration):
    """
    AMQP System Configurations.  The class name and configurationType should be fixed.
    """
    exchangeName = micromodels.StringField()
    hostname = micromodels.StringField()
    port = micromodels.IntegerField()
    username = micromodels.StringField()
    password = micromodels.StringField()
    virtualHost = micromodels.StringField()

    def __init__(self):
        super(AMQPSystemConfiguration, self).__init__()
        self.className = 'org.tcrun.slickij.api.data.AMQPSystemConfiguration'
        self.configurationType = 'amqp-system-configuration'


class EmailTemplateConfiguration(SystemConfiguration):
    """Configuration for email templates.  If the project reference is null, the template is considered global."""
    project = micromodels.ModelField(ProjectReference)
    subjectTemplate = micromodels.StringField()
    emailTemplate = micromodels.StringField()

    def __init__(self):
        super(EmailTemplateConfiguration, self).__init__()
        self.className = 'org.tcrun.slickij.api.data.EmailTemplateConfiguration'
        self.configurationType = 'email-template-configuration'


class EmailSystemConfiguration(SystemConfiguration):
    """Global Slick email configuration settings.  Things like smtp configuration and the sender email address are
    configured here."""

    smtpHostname = micromodels.StringField()
    smtpPort = micromodels.IntegerField()
    smtpUsername = micromodels.StringField()
    smtpPassword = micromodels.StringField()
    ssl = micromodels.BooleanField()
    enabled = micromodels.BooleanField()
    sender = micromodels.StringField()

    def __init__(self):
        super(EmailSystemConfiguration, self).__init__()
        self.className = 'org.tcrun.slickij.api.data.EmailSystemConfiguration'
        self.configurationType = 'email-system-configuration'
        self.configurationName = 'Global Email System Configuration'


class EmailOffSwitch(SystemConfiguration):
    """A way to turn off emails for particular parts of the product"""
    turnOffEmailsForType = micromodels.StringField()
    turnOffEmailsForId = micromodels.StringField()

    def __init__(self):
        super(EmailOffSwitch, self).__init__()
        self.className = 'org.tcrun.slickij.api.data.EmailOffSwitch'
        self.configurationType = 'email-off-switch'


class SubscriptionInfo(micromodels.Model):
    """Data representing an email subscription to events that happen on slick."""

    subscriptionType = micromodels.StringField()
    subscriptionValue = micromodels.StringField()
    onStart = micromodels.BooleanField()


class EmailSubscription(SystemConfiguration):
    """Email subscriptions have the email address as the name, and embed a list of subscription info models"""
    enabled = micromodels.BooleanField()
    subscriptions = micromodels.ModelCollectionField(SubscriptionInfo)

    def __init__(self):
        super(EmailSubscription, self).__init__()
        self.className = 'org.tcrun.slickij.api.data.EmailSubscription'
        self.configurationType = 'email-subscription'


class ComparisonTypes:
    EQUALS_IGNORE_CASE = "equals-ignore-case"
    EQUALS = "equals"
    CONTAINS = "contains"

    def __init__(self):
        pass


class MatchCriteria(micromodels.Model):
    """Match criteria for AutomaticTestrunGroup System Configuration.
    This describes a single match against a testrun."""
    propertyName = micromodels.StringField()
    propertyValue = micromodels.StringField()
    comparisonType = micromodels.StringField()


class AutomaticTestrunGroup(SystemConfiguration):
    enabled = micromodels.BooleanField()
    template = micromodels.StringField()
    groupType = micromodels.StringField()
    replaceSameBuild = micromodels.BooleanField()
    matchers = micromodels.ModelCollectionField(MatchCriteria)

    def __init__(self):
        super(AutomaticTestrunGroup, self).__init__()
        self.configurationType = 'auto-add-to-testrungroup'
        self.replaceSameBuild = True
