#!/usr/bin/env python

import sys
from os import path
from util import Color, get, merge, TMP_DIR, exit_error


################################
# Test Manager
################################
class TestManager(object):
    def __init__(self, conf):
        if not conf:
            conf = {}

        conf['output_dir'] = get(conf, 'output_dir', path.join(TMP_DIR))
        conf['env'] = get(conf, 'env', {})
        conf['before'] = get(conf, 'before', [])
        TestAction.validate(conf['before'])
        conf['after'] = get(conf, 'after', [])
        TestAction.validate(conf['after'])

        self.tests = self.load_tests(conf)

    def load_tests(self, conf):
        tests = {}

        for name, info in conf.iteritems():
            if name in ['output_dir', 'env', 'before', 'after']:
                continue

            info = merge(info, conf)
            tests[name] = Test(name, info)

        return tests

    def get_test(self, name):
        test = self.tests.get(name, None)
        if test:
            return test
        else:
            exit_error("Test '%s' was not found" % name)


################################################################
# Test
#
# NOTE: Scenarios won't necessarily run in order of given tags
# (Calabash goes through all feature files and their scenarios
# a executes those scenarios that match the tags)
################################################################
class Test:
    def __init__(self, name, conf):
        self.name = name
        self.output_dir = conf['output_dir']
        self.env = conf['env']

        self.run = get(conf, 'run', None)
        if not self.run:
            exit_error("Test '%s' is missing a 'run: ...'" % name)

        self.before = get(conf, 'before', [])
        TestAction.validate(self.before)
        self.after = get(conf, 'after', [])
        TestAction.validate(self.after)

    def get_env(self):
        return self.env

    def show(self, line_start=''):
        s = line_start + Color.LIGHT_GREEN + self.name + ":\n"
        # show run
        s += line_start + '  ' + self.run + Color.ENDC
        s = s.replace('@', Color.LIGHT_RED + '@' + Color.ENDC)
        s = s.replace('--tags', Color.YELLOW + '--tags')
        s = s.replace(',', Color.YELLOW + ',')
        # show actions
        if self.before:
            s += '\n'
            s += line_start + Color.YELLOW + '  before: ' + Color.ENDC + ', '.join(self.before) + Color.ENDC
        if self.after:
            s += '\n'
            s += line_start + Color.YELLOW + '  after: ' + Color.ENDC + ', '.join(self.after)
        # show ENV
        if self.env:
            s += '\n'
            s += line_start + Color.YELLOW + '  env: ' + Color.ENDC + str(self.env)

        return s


################################################################
# Action that can be run before or after a test
################################################################
class TestAction:
    DOWNLOAD = 'download'
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
    ALL = [DOWNLOAD, INSTALL, UNINSTALL]

    @classmethod
    def validate(cls, actions):
        for action in actions:
            if action not in cls.ALL:
                exit_error("Test action '%s' is not supported" % action)
