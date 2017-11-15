##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests for the implementation of the mkzopeinstance script.
"""

import os
import shutil
import tempfile
import unittest

from zope.app.server import mkzopeinstance
from zope.app.server.tests import capture_output


class ArgumentParsingTestCase(unittest.TestCase):
    """Ensure the command line is properly converted to an options
    object.
    """

    def parse_args(self, args, stdout=None, stderr=None):
        argv = ["foo/bar.py"] + args
        with capture_output(stdout, stderr):
            options = mkzopeinstance.parse_args(argv)
        self.assertEqual(options.program, "bar.py")
        self.assert_(options.version)
        return options

    def test_no_arguments(self):
        self.parse_args([])

    def test_version_long(self):
        self.check_stdout_content(["--version"])

    def test_help_long(self):
        self.check_stdout_content(["--help"])

    def test_help_short(self):
        self.check_stdout_content(["-h"])

    def check_stdout_content(self, args):
        with self.assertRaises(SystemExit) as cm:
            with capture_output() as (stdout, stderr):
                self.parse_args(args, stdout, stderr)
        self.assertEqual(cm.exception.code, 0)
        self.assertNotEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")

    def test_without_destination(self):
        options = self.parse_args([])
        self.assertEqual(options.destination, None)

    def test_destination_long(self):
        options = self.parse_args(["--dir", "some/dir"])
        self.assertEqual(options.destination, "some/dir")

    def test_destination_short(self):
        options = self.parse_args(["-d", "some/dir"])
        self.assertEqual(options.destination, "some/dir")

    def test_without_skeleton(self):
        # make sure we get *some* skeleton directory by default
        # there's no claim that it exists
        options = self.parse_args([])
        self.assertNotEqual(options.skeleton, None)

    def test_with_skeleton_long(self):
        options = self.parse_args(["--skelsrc", "some/dir"])
        self.assertEqual(options.skeleton, "some/dir")
        self.failIf(options.add_package_includes)

    def test_with_skeleton_short(self):
        options = self.parse_args(["-s", "some/dir"])
        self.assertEqual(options.skeleton, "some/dir")
        self.failIf(options.add_package_includes)

    def test_without_username(self):
        options = self.parse_args([])
        self.assertEqual(options.username, None)
        self.assertEqual(options.password, None)

    def test_username_without_password_long(self):
        options = self.parse_args(["--user", "User"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, None)

    def test_username_without_password_short(self):
        options = self.parse_args(["-u", "User"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, None)

    def test_username_with_password_long(self):
        options = self.parse_args(["--user", "User:Pass"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, "Pass")

    def test_username_with_password_short(self):
        options = self.parse_args(["-u", "User:Pass"])
        self.assertEqual(options.username, "User")
        self.assertEqual(options.password, "Pass")

    def test_without_password_manager(self):
        options = self.parse_args([])
        self.assertEqual(options.password_manager, None)

    def test_password_manager_short(self):
        options = self.parse_args(["-m", "Manager"])
        self.assertEqual(options.password_manager, "Manager")

    def test_password_manager_long(self):
        options = self.parse_args(["--password-manager", "Manager"])
        self.assertEqual(options.password_manager, "Manager")

    def test_junk_positional_arg(self):
        with self.assertRaises(SystemExit) as cm:
            self.parse_args(["junk"])
        self.assertNotEqual(cm.exception.code, 0)


class InputCollectionTestCase(unittest.TestCase):

    def setUp(self):
        super(InputCollectionTestCase, self).setUp()
        self.tmpdir = tempfile.mkdtemp(prefix="test-mkzopeinstance-")
        self.skeleton = os.path.join(self.tmpdir, "skel")
        self.instance = os.path.join(self.tmpdir, "inst")
        os.mkdir(self.skeleton)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        super(InputCollectionTestCase, self).tearDown()

    def createOptions(self):
        options = Options()
        options.skeleton = self.skeleton
        options.interactive = True
        return options

    def test_get_skeltarget(self):
        options = self.createOptions()
        input = ["  ", " foo "]
        app = ControlledInputApplication(options, input)
        with capture_output() as (stdout, stderr):
            skel = app.get_skeltarget()
        self.assertEqual(skel, "foo")
        self.assertEqual(input, [])
        self.assert_(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_process_creates_destination(self):
        options = self.createOptions()
        input = [self.instance]
        app = ControlledInputApplication(options, input)
        with capture_output() as (stdout, stderr):
            self.assertEqual(app.process(), 0)
        self.assert_(os.path.isdir(self.instance))
        self.assertEqual(input, [])
        self.failUnless(app.all_input_consumed())

    def test_zserver_support(self):
        # test the zserver option.  We should get zserver versions of
        # runzope, zopectl, debugzope and zope.conf.  Any of these
        # that we provide in put skeleton should be overritten.

        # privide a dummy runzope
        os.mkdir(os.path.join(self.skeleton, 'bin'))
        f = open(os.path.join(self.skeleton, 'bin', 'runzope.in'), 'w')
        f.write('runzope')
        f.close()

        options = self.createOptions()
        options.destination = self.instance
        options.interactive = False
        options.zserver = True
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            self.assertEqual(app.process(), 0)
        self.assert_(
            'from zope.app.server.main import main' in
            open(os.path.join(self.instance, 'bin', 'runzope')).read()
            )
        self.assert_(
            'from zope.app.server.main import debug' in
            open(os.path.join(self.instance, 'bin', 'debugzope')).read()
            )
        self.assert_(os.path.exists(
            os.path.join(self.instance, 'etc', 'zope.conf')
            ))

    def test_process_aborts_on_file_destination(self):
        options = self.createOptions()
        options.destination = self.instance
        open(self.instance, "w").close()
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            self.assertEqual(app.process(), 1)
        self.assert_(stderr.getvalue())

    def test_process_aborts_on_failed_destination_creation(self):
        options = self.createOptions()
        options.destination = os.path.join(self.instance, "foo")
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            self.assertEqual(app.process(), 1)
        self.assert_(stderr.getvalue())

    def test_get_username(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["myuser"])
        with capture_output() as (stdout, stderr):
            usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failIf(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_username_strips_whitespace(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["  myuser\t"])
        with capture_output() as (stdout, stderr):
            usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failIf(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_username_ignores_empty_names(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["", "  ", "\t", "myuser"])
        with capture_output() as (stdout, stderr):
            usr = app.get_username()
        self.assertEqual(usr, "myuser")
        self.failUnless(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_manager(self):
        options = self.createOptions()
        options.password_manager = None
        app = ControlledInputApplication(options, ["1"])
        with capture_output() as (stdout, stderr):
            name, pwm = app.get_password_manager()
        self.assertEqual(name, "Plain Text")
        self.assertEqual(pwm.encodePassword("foo").decode(), "foo")
        self.failIf(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_wrong_password_manager(self):
        options = self.createOptions()
        options.password_manager = "Unknown"
        app = ControlledInputApplication(options, [])
        with self.assertRaises(SystemExit) as cm:
            with capture_output() as (stdout, stderr):
                app.get_password_manager()
        self.assertEqual(cm.exception.code, 1)
        self.failUnless(stderr.getvalue())
        self.failIf(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["foo", "foo"])
        with capture_output() as (stdout, stderr):
            pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failIf(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_not_verified(self):
        options = self.createOptions()
        app = ControlledInputApplication(options, ["foo", "bar"])
        with self.assertRaises(SystemExit) as cm:
            with capture_output() as (stdout, stderr):
                app.get_password()
        self.assertEqual(cm.exception.code, 1)
        self.failUnless(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_empty(self):
        # Make sure the empty password is ignored.
        options = self.createOptions()
        app = ControlledInputApplication(options, ["", "foo", "foo"])
        with capture_output() as (stdout, stderr):
            pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failUnless(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_get_password_disallows_whitespace(self):
        # Any password that contains spaces is disallowed.
        options = self.createOptions()
        app = ControlledInputApplication(options, [" ", "\t", "a b",
                                                   " a", "b ", "foo", "foo"])
        with capture_output() as (stdout, stderr):
            pw = app.get_password()
        self.assertEqual(pw, "foo")
        self.failUnless(stderr.getvalue())
        self.failUnless(stdout.getvalue())
        self.failUnless(app.all_input_consumed())

    def test_can_rewrite_existing_instance(self):
        # Fill out the skeleton a little so we test more cases:
        os.mkdir(os.path.join(self.skeleton, "etc"))
        f = open(os.path.join(self.skeleton, "etc", "README.txt"), "w")
        f.write("Configuration goes here.\n")
        f.close()

        # Create an instance home:
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            rc = app.process()
        self.assertEqual(rc, 0)
        self.failUnless(app.all_input_consumed())
        self.failUnless(os.path.exists(os.path.join(self.instance, "etc")))

        # Make sure we can do it again:
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            rc = app.process()
        self.assertEqual(rc, 0)
        self.failUnless(app.all_input_consumed())
        self.failUnless(os.path.exists(os.path.join(self.instance, "etc")))

    def test_zope_namespace_package_doesnt_affect_software_home(self):
        # Make sure that a zope namespace package in a different
        # location won't affect SOFTWARE_HOME

        # let's mess with zope's __file__
        import zope
        old_path = getattr(zope, '__file__', None)
        zope.__file__ = os.path.join(
            *'and now for something completely different'.split())

        # place a test file into the skeleton dir that'll be expanded
        # to SOFTWARE_HOME by mkzopeinstance
        with open(os.path.join(self.skeleton, 'test.in'), 'w') as f:
            f.write('<<SOFTWARE_HOME>>')

        # run mkzopeinstance
        options = self.createOptions()
        options.destination = self.instance
        app = ControlledInputApplication(options, [])
        with capture_output() as (stdout, stderr):
            app.process()

        # check for the expected output: mkzopeinstance should take
        # zope.app.server as an anchor for determining SOFTWARE_HOME
        import zope.app.server
        expected = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(zope.app.server.__file__))))
        with open(os.path.join(self.instance, 'test')) as f:
            self.assertEqual(f.read(), expected)

        # cleanup the fake 'zope' module
        if old_path is None:
            del zope.__file__
        else:  # pragma: no cover
            zope.__file__ = old_path


class ControlledInputApplication(mkzopeinstance.Application):

    def __init__(self, options, input_lines):
        mkzopeinstance.Application.__init__(self, options)
        self.__input = input_lines

    def read_input_line(self, prompt):
        return self.__input.pop(0)

    read_password = read_input_line

    def all_input_consumed(self):
        return not self.__input


class Options(object):

    username = "[test-username]"
    password_manager = "Plain Text"
    password = "[test-password]"
    destination = None
    version = "[test-version]"
    program = "[test-program]"
    add_package_includes = False
    zserver = False
