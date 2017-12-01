import logging
import re
import sys
import time
from datetime import datetime
import types

import docutils.core

from .micromodels.fields import ModelCollectionField
from . import SlickConnection, SlickCommunicationError, Release, Build, BuildReference, Component, ComponentReference, \
    Project, Testplan, Testrun, Testcase, RunStatus, Result, ResultStatus, LogEntry, Configuration, TestrunGroup, \
    TestrunReference, Link


def add_log_entry(self, message, level='DEBUG', loggername='', exceptionclassname='', exceptionmessage='',
                  stacktrace=''):
    entry = LogEntry()
    entry.entryTime = int(round(time.time() * 1000))
    entry.message = str(message)
    entry.level = level
    entry.loggerName = loggername
    entry.exceptionClassName = exceptionclassname
    entry.exceptionMessage = exceptionmessage
    entry.exceptionStackTrace = stacktrace
    if not hasattr(self, 'log'):
        self.log = []
    self.log.append(entry)


def update_result(self):
    self.connection.results(self).update()


def update_testrun(self):
    if hasattr(self, 'summary'):
        del self.summary
    self.connection.testruns(self).update()


def add_file_to_result(self, filename, fileobj=None):
    slickfile = self.connection.files.upload_local_file(filename, fileobj)
    if not hasattr(self, 'files'):
        self.files = []
    self.files.append(slickfile)
    self.update()


def add_link_to_result(self, name, url):
    link = Link()
    link.name = name
    link.url = url
    if not hasattr(self, 'links'):
        self.links = []
    self.links.append(link)
    self.update()


def make_result_updatable(result, connection):
    result.connection = connection
    result.update = types.MethodType(update_result, result)
    result.add_file = types.MethodType(add_file_to_result, result)
    result.add_link = types.MethodType(add_link_to_result, result)
    result.add_log_entry = types.MethodType(add_log_entry, result)


def make_testrun_updatable(testrun, connection):
    testrun.connection = connection
    testrun.update = types.MethodType(update_testrun, testrun)
    testrun.add_file = types.MethodType(add_file_to_result, testrun)
    testrun.add_link = types.MethodType(add_link_to_result, testrun)


class SlickQA(object):
    def __init__(self, url, project_name, release_name, build_name, test_plan=None, test_run=None,
                 environment_name=None, test_run_group_name=None):
        self.logger = logging.getLogger('slick-reporter.Slick')
        self.slickcon = None
        self.is_connected = False
        self.project = None
        self.environment = environment_name
        self.component = None
        self.componentref = None
        self.testplan = test_plan
        self.releaseref = None
        self.release = release_name
        self.build = build_name
        self.buildref = None
        self.testrun = test_run
        self.testrunref = None
        self.testrun_group = test_run_group_name
        self.logqueue = []

        self.init_connection(url)
        if self.is_connected:
            self.logger.debug("Initializing Slick...")
            self.init_project(project_name)
            self.init_release()
            self.init_build()
            self.init_testplan()
            self.init_environment()
            self.init_testrun()
            self.init_testrungroup()
            # TODO: if you have a list of test cases, add results for each with notrun status

    def init_connection(self, url):
        try:
            self.logger.debug("Checking connection to server...")
            self.slickcon = SlickConnection(url)
            successful = self.verify_connection()
            if not successful:
                raise SlickCommunicationError(
                    "Unable to verify connection to {} by trying to access the version api".format(
                        self.slickcon.getUrl()))
            self.is_connected = True
        except SlickCommunicationError as se:
            self.logger.error(se.message)

    def verify_connection(self):
        version = self.slickcon.version.findOne()
        if version:
            self.logger.debug("Successfully connected. Using version {}".format(version))
            return True
        self.logger.debug("Unable to connect. No version available.")
        return False

    def init_project(self, project, create=True):
        self.logger.debug("Looking for project by name '{}'.".format(project))
        try:
            self.project = self.slickcon.projects.findByName(project)
        except SlickCommunicationError as err:
            self.logger.error("Error communicating with slick: {}".format(err.args[0]))
        if self.project is None and create:
            self.logger.error("Unable to find project with name '{}', creating...".format(self.project))
            self.project = Project()
            self.project.name = project
            self.project = self.slickcon.projects(self.project).create()

        assert isinstance(self.project, Project)
        self.logger.info("Using project with name '{}' and id: {}.".format(self.project.name, self.project.id))

    def init_release(self):
        release_name = self.release
        self.logger.debug("Looking for release '{}' in project '{}'".format(release_name, self.project.name))
        if not hasattr(self.project, 'releases'):
            self.project.releases = []
        for release in self.project.releases:
            assert isinstance(release, Release)
            if release.name == release_name:
                self.logger.info("Found Release '{}' with id '{}' in Project '{}'.".format(release.name, release.id,
                                                                                           self.project.id))
                self.release = release
                self.releaseref = release.create_reference()
                break
        else:
            self.logger.info("Adding release {} to project {}.".format(release_name, self.project.name))
            release = Release()
            release.name = release_name
            self.release = self.slickcon.projects(self.project).releases(release).create()
            assert isinstance(self.release, Release)
            self.project = self.slickcon.projects(self.project).get()
            self.releaseref = self.release.create_reference()
            self.logger.info("Using newly created release '{}' with id '{}' in Project '{}'.".format(self.release.name,
                                                                                                     self.release.id,
                                                                                                     self.project.name))

    def init_build(self):
        build_number = self.build
        if not hasattr(self.release, 'builds'):
            self.release.builds = []
        for build in self.release.builds:
            if build.name == build_number:
                self.logger.debug("Found build with name '{}' and id '{}' on release '{}'".format(build.name, build.id,
                                                                                                  self.release.name))
                self.buildref = build.create_reference()
                break
        else:
            self.logger.info("Adding build {} to release {}.".format(build_number, self.release.name))
            build = Build()
            build.name = build_number
            build.built = datetime.now()
            self.buildref = (
                self.slickcon.projects(self.project).releases(self.release).builds(build).create()).create_reference()
            assert isinstance(self.buildref, BuildReference)
            self.logger.info("Using newly created build '{}' with id '{}' in Release '{}' in Project '{}'.".format(
                self.buildref.name, self.buildref.buildId, self.release.name, self.project.name))

    def get_component(self, component_name):
        self.logger.debug(
            "Looking for component with name '{}' in project '{}'".format(component_name, self.project.name))
        for comp in self.project.components:
            if comp.name == component_name:
                assert isinstance(comp, Component)
                self.logger.info(
                    "Found component with name '{}' and id '{}' in project '{}'.".format(comp.name, comp.id,
                                                                                         self.project.name))
                self.component = comp
                self.componentref = self.component.create_reference()
                assert isinstance(self.componentref, ComponentReference)
                return self.component

    def create_component(self, component_name):
        self.logger.info("Adding component {} to project {}.".format(component_name, self.project.name))
        component = Component()
        component.name = component_name
        component.code = component_name.replace(" ", "-")
        self.component = self.slickcon.projects(self.project).components(component).create()
        self.project.components.append(self.component)
        self.componentref = self.component.create_reference()
        self.logger.info("Using newly created component '{}' with id '{}' in project '{}'.".format(
            self.component.name, self.component.id, self.project.name))
        return self.component

    def init_testplan(self):
        if self.testplan:
            testplan_name = self.testplan
            testplan = self.slickcon.testplans.findOne(projectid=self.project.id, name=testplan_name)
            if testplan is None:
                self.logger.debug("Creating testplan with name '{}' connected to project '{}'.".format(testplan_name,
                                                                                                       self.project.name))
                testplan = Testplan()
                testplan.name = testplan_name
                testplan.project = self.project.create_reference()
                testplan.isprivate = False
                testplan.createdBy = "slickqa-python"
                testplan = self.slickcon.testplans(testplan).create()
                self.logger.info("Using newly create testplan '{}' with id '{}'.".format(testplan.name, testplan.id))
            else:
                self.logger.info(
                    "Found (and using) existing testplan '{}' with id '{}'.".format(testplan.name, testplan.id))
            self.testplan = testplan
        else:
            self.logger.warn("No testplan specified for the testrun.")

    def init_environment(self):
        if self.environment is not None:
            env = self.slickcon.configurations.findOne(name=self.environment, configurationType="ENVIRONMENT")
            if env is None:
                env = Configuration()
                env.name = self.environment
                env.configurationType = "ENVIRONMENT"
                env = self.slickcon.configurations(env).create()
            self.environment = env

    def init_testrun(self):
        testrun = Testrun()
        if self.testrun is not None:
            testrun.name = self.testrun
        else:
            if self.testplan is not None:
                testrun.name = self.testplan.name
            else:
                testrun.name = 'Tests run from slick-python'
        if self.testplan is not None:
            testrun.testplanId = self.testplan.id
        testrun.project = self.project.create_reference()
        testrun.release = self.releaseref
        testrun.build = self.buildref
        testrun.state = RunStatus.RUNNING
        testrun.runStarted = int(round(time.time() * 1000))
        if self.environment is not None and isinstance(self.environment, Configuration):
            testrun.config = self.environment.create_reference()

        self.logger.debug("Creating testrun with name {}.".format(testrun.name))
        self.testrun = self.slickcon.testruns(testrun).create()
        make_testrun_updatable(self.testrun, self.slickcon)

    def init_testrungroup(self):
        if self.testrun_group is not None:
            trg = self.slickcon.testrungroups.findOne(name=self.testrun_group)
            if trg is None:
                trg = TestrunGroup()
                trg.name = self.testrun_group
                trg.testruns = []
                trg.created = datetime.now()
                trg = self.slickcon.testrungroups(trg).create()
            self.testrun_group = self.slickcon.testrungroups(trg).add_testrun(self.testrun)

    def add_log_entry(self, message, level='DEBUG', loggername='', exceptionclassname='', exceptionmessage='',
                      stacktrace=''):
        entry = LogEntry()
        entry.entryTime = int(round(time.time() * 1000))
        entry.message = message
        entry.level = level
        entry.loggerName = loggername
        entry.exceptionClassName = exceptionclassname
        entry.exceptionMessage = exceptionmessage
        entry.exceptionStackTrace = stacktrace
        self.logqueue.append(entry)

    def finish_testrun(self):
        assert isinstance(self.testrun, Testrun)
        testrun = Testrun()
        if self.testrun.name:
            testrun.name = self.testrun.name
        else:
            testrun.name = 'Tests run from slick-python'
        testrun.id = self.testrun.id
        testrun.runFinished = int(round(time.time() * 1000))
        testrun.state = RunStatus.FINISHED
        self.logger.debug("Finishing testrun named {}, with id {}.".format(testrun.name, testrun.id))
        self.slickcon.testruns(testrun).update()

    # TODO: need to add logs, files, etc. to a result

    def file_result(self, name, status=ResultStatus.FAIL, reason=None, runlength=0, testdata=None,
                    runstatus=RunStatus.FINISHED, attributes=None, requires=None):
        test = None
        if testdata is not None:
            assert isinstance(testdata, Testcase)
            if testdata.automationId:
                test = self.slickcon.testcases.findOne(projectid=self.project.id, automationId=testdata.automationId)
            if test is None and hasattr(testdata, 'automationKey') and testdata.automationKey is not None:
                test = self.slickcon.testcases.findOne(projectid=self.project.id, automationKey=testdata.automationId)
        if test is None:
            test = self.slickcon.testcases.findOne(projectid=self.project.id, name=name)
        if test is None:
            self.logger.debug("Creating testcase with name '{}' on project '{}'.".format(name, self.project.name))
            test = Testcase()
            if testdata is not None:
                test = testdata
            test.name = name
            test.project = self.project.create_reference()
            test = self.slickcon.testcases(test).create()
            self.logger.info(
                "Using newly created testcase with name '{}' and id '{}' for result.".format(name, test.id))
        else:
            if testdata is not None:
                # update the test with the data passed in
                assert isinstance(test, Testcase)
                testdata.id = test.id
                testdata.name = name
                testdata.project = self.project.create_reference()
                test = self.slickcon.testcases(testdata).update()
            self.logger.info("Found testcase with name '{}' and id '{}' for result.".format(test.name, test.id))
        result = Result()
        result.testrun = self.testrun.create_reference()
        result.testcase = test.create_reference()
        result.project = self.project.create_reference()
        result.release = self.releaseref
        result.build = self.buildref
        if self.component is not None:
            result.component = self.componentref
        if len(self.logqueue) > 0:
            result.log = []
            result.log.extend(self.logqueue)
            self.logqueue[:] = []
        result.reason = reason
        result.runlength = runlength
        result.end = int(round(time.time() * 1000))
        result.started = result.end - result.runlength
        result.status = status
        result.runstatus = runstatus
        if attributes is not None:
            result.attributes = attributes
        if requires is not None:
            result.requirements = requires
        self.logger.debug("Filing result of '{}' for test with name '{}'".format(result.status, result.testcase.name))
        result = self.slickcon.results(result).create()
        self.logger.info("Filed result of '{}' for test '{}', result id: {}".format(result.status, result.testcase.name,
                                                                                    result.id))
        make_result_updatable(result, self.slickcon)
        return result


class DocStringMetaData(object):
    def __init__(self, func):
        if hasattr(func, '__doc__') and func.__doc__ is not None:
            dom = docutils.core.publish_doctree(func.__doc__).asdom()
            if dom is not None and dom.firstChild is not None and dom.firstChild.nodeName == 'document':
                document = dom.firstChild
                if document.hasChildNodes() and document.firstChild.nodeName == 'paragraph':
                    self.name = document.firstChild.firstChild.nodeValue
                    if len(document.childNodes) > 1:
                        for node in document.childNodes[1:]:
                            self.process_node(node)
                else:
                    self.name = self.get_name_from_function_name(func)
                    for node in document.childNodes:
                        self.process_node(node)
        else:
            self.name = self.get_name_from_function_name(func)

    def get_name_from_function_name(self, func):
        if hasattr(func, '__name__') and func.__name__ is not None and func.__name__ != "":
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', func.__name__)
            s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            return re.sub(r'_', ' ', re.sub(r'_?[tT]est$', '', re.sub(r'^[Tt]est_?', '', s2))).capitalize()

    def process_node(self, node):
        if node.nodeName == 'block_quote':
            for child_node in node.childNodes:
                self.process_node(child_node)
        if node.nodeName == 'field_list':
            for child_node in node.childNodes:
                self.process_node(child_node)
        if node.nodeName == 'paragraph':
            if hasattr(self, 'purpose'):
                self.purpose = self.purpose + '\n\n' + node.firstChild.nodeValue
            else:
                self.purpose = node.firstChild.nodeValue
        if node.nodeName == 'field':
            if node.firstChild.firstChild.nodeValue == 'expectedResults' and \
                    node.childNodes[1].firstChild.nodeName == 'enumerated_list':
                self.expectedResults = []
                for list_item in node.childNodes[1].firstChild.childNodes:
                    self.expectedResults.append(list_item.firstChild.firstChild.nodeValue)
            elif node.firstChild.firstChild.nodeValue == 'steps' and \
                    node.childNodes[1].firstChild.nodeName == 'enumerated_list':
                self.steps = []
                for list_item in node.childNodes[1].firstChild.childNodes:
                    self.steps.append(list_item.firstChild.firstChild.nodeValue)
            elif node.firstChild.firstChild.nodeValue == 'tags':
                setattr(self, node.firstChild.firstChild.nodeValue,
                        node.childNodes[1].firstChild.firstChild.nodeValue.split(", "))
            else:
                try:
                    setattr(self, node.firstChild.firstChild.nodeValue,
                            node.childNodes[1].firstChild.firstChild.nodeValue)
                except:
                    sys.stderr.write("Problem parsing comment for test: {}".format(self.name))
