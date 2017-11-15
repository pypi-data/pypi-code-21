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
"""Implementation of the mkzopeinstance script.

This creates a new instances of the Zope server instance home.  An
'instance home' contains two things:

- application server configuration and data

- server process control scripts and data
"""

from __future__ import print_function

import optparse
import os
import shutil
import sys
from xml.sax.saxutils import quoteattr as xml_quoteattr

import zope.app.server
from zope.password import password
from zope.app.applicationcontrol import zopeversion


def main(argv=None, from_checkout=False):
    """Top-level script function to create a new Zope instance."""
    if argv is None:
        argv = sys.argv
    try:
        options = parse_args(argv, from_checkout)
    except SystemExit as e:
        if e.code:
            return 2
        else:
            return 0
    app = Application(options)
    try:
        return app.process()
    except KeyboardInterrupt:
        return 1
    except SystemExit as e:
        return e.code


class Application(object):

    def __init__(self, options):
        self.options = options
        self.need_blank_line = False

    def read_input_line(self, prompt):
        # The tests replace this to make sure the right things happen.
        if not self.options.interactive:
            print('Error: Tried to ask for user input in'
                  ' non-interactive mode.', file=sys.stderr)
            sys.exit(1)
        return raw_input(prompt)

    def read_password(self, prompt):
        # The tests replace this to make sure the right things happen.
        if not self.options.interactive:
            print('Error: Tried to ask for user input in'
                  ' non-interactive mode.', file=sys.stderr)
            sys.exit(1)
        import getpass
        try:
            return getpass.getpass(prompt)
        except KeyboardInterrupt:
            # The cursor was left on the same line as the prompt,
            # which we don't like.  Print a blank line.
            print()
            raise

    def process(self):
        options = self.options

        # make sure we can find the skeleton
        if not os.path.isdir(options.skeleton):
            print("skeleton directory", options.skeleton, file=sys.stderr)
            print("does not exist or is not a directory", file=sys.stderr)
            return 1

        # create the destination
        if not options.destination:
            options.destination = self.get_skeltarget()
        options.destination = os.path.abspath(options.destination)
        if not os.path.exists(options.destination):
            try:
                os.mkdir(options.destination)
            except OSError as e:
                print("could not create instance home:", e, file=sys.stderr)
                return 1
        elif not os.path.isdir(options.destination):
            print(options.destination, "is not a directory", file=sys.stderr)
            print("(instance homes cannot be created in non-directories)",
                  file=sys.stderr)
            return 1

        if not options.username:
            options.username = self.get_username()

        (options.password_manager,
            password_manager) = self.get_password_manager()

        if not options.password:
            options.password = self.get_password()

        options.password = password_manager.encodePassword(options.password)
        if not isinstance(options.password, str):
            options.password = options.password.decode()

        # now create the instance!
        self.copy_skeleton()
        if options.add_package_includes:
            # need to copy ZCML differently since it's not in the skeleton:
            import __main__
            swhome = os.path.dirname(
                os.path.dirname(os.path.realpath(__main__.__file__)))
            shutil.copy2(os.path.join(swhome, "securitypolicy.zcml"),
                         os.path.join(options.destination, "etc"))
        return 0

    def get_skeltarget(self):
        self.print_message(SKELTARGET_MESSAGE)
        self.need_blank_line = True
        while 1:
            skeltarget = self.read_input_line("Directory: ").strip()
            if skeltarget == '':
                print('You must specify a directory', file=sys.stderr)
                continue
            return os.path.expanduser(skeltarget)

    def get_username(self):
        self.print_message(USERNAME_MESSAGE)
        self.need_blank_line = True
        while 1:
            username = self.read_input_line("Username: ").strip()
            if not username:
                print("You must specify an administrative user", file=sys.stderr)
                continue
            return username

    def get_password(self):
        self.print_message(PASSWORD_MESSAGE)
        while 1:
            password = self.read_password("Password: ")
            if not password:
                print("Password may not be empty", file=sys.stderr)
                continue
            if password != password.strip() or password.split() != [password]:
                print("Password may not contain spaces", file=sys.stderr)
                continue
            break
        again = self.read_password("Verify password: ")
        if again != password:
            print("Password not verified!", file=sys.stderr)
            sys.exit(1)
        return password

    def get_password_manager(self):
        if not self.options.password_manager and not self.options.interactive:
            self.options.password_manager = password.managers[0][0]

        if self.options.password_manager:
            for name, manager in password.managers:
                if name == self.options.password_manager:
                    return (name, manager)
            print("Unknown password manager!", file=sys.stderr)
            sys.exit(1)

        self.print_message(PASSWORD_MANAGER_MESSAGE)
        for i, (name, manager) in enumerate(password.managers):
            print("% i. %s" % (i + 1, name))
        print()
        self.need_blank_line = True
        while 1:
            password_manager = self.read_input_line(
                "Password Manager Number [1]: ")
            if not password_manager:
                index = 0
                break
            elif password_manager.isdigit():
                index = int(password_manager)
                if index > 0 and index <= len(password.managers):
                    index -= 1
                    break
            print("You must select a password manager", file=sys.stderr)
        print("%r password manager selected" % password.managers[index][0])
        return password.managers[index]

    def print_message(self, message):
        if self.need_blank_line:
            print()
            self.need_blank_line = False
        print(message)

    def copy_skeleton(self):
        options = self.options
        # TODO we should be able to compute the script
        script = os.path.abspath(sys.argv[0])
        zope_home = os.path.dirname(os.path.dirname(script))
        zope_init = os.path.dirname(os.path.dirname(
            os.path.abspath(zope.app.server.__file__)))
        software_home = os.path.dirname(os.path.dirname(zope_init))
        self.replacements = [
            ("<<USERNAME>>", options.username),
            ("<<USERNAME-XMLATTR>>", xml_quoteattr(options.username)),
            ("<<PASSWORD>>", options.password),
            ("<<PASSWORD-XMLATTR>>", xml_quoteattr(options.password)),
            ("<<PASSWORD_MANAGER>>", options.password_manager),
            ("<<PYTHON>>", sys.executable),
            ("<<INSTANCE_HOME>>", options.destination),
            ("<<ZOPE_HOME>>", zope_home),
            ("<<SOFTWARE_HOME>>", software_home),
            ]
        self.copytree(self.options.skeleton, self.options.destination)
        if options.zserver:
            self.copytree(
                os.path.join(os.path.dirname(zope.app.server.__file__),
                             'zopeskel'),
                self.options.destination,
                )


    def copytree(self, src, dst):
        # Similar to shutil.copytree(), but doesn't care about
        # symlinks, doesn't collect errors, and uses self.copyfile()
        # instead of shutil.copy2().
        assert os.path.isdir(dst), dst
        names = os.listdir(src)
        if ".svn" in names:
            names.remove(".svn")
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                if not os.path.exists(dstname):
                    os.mkdir(dstname)
                self.copytree(srcname, dstname)
            else:
                self.copyfile(srcname, dstname)
            # There shouldn't be any need to deal with devices, sockets etc.

    def copyfile(self, src, dst):
        if dst.endswith(".in"):
            dst = dst[:-3]
            text = open(src, "rU").read()
            # perform replacements
            for var, string in self.replacements:
                text = text.replace(var, string)

            # If the file exists, keep the old file.  This is a
            # hopefully temporary hack to get around distutils
            # stripping the permissions on the server skeletin files.
            # We reuse the original default files, which have the
            # right permissions.
            old = os.path.exists(dst)
            if old:
                f = open(dst, "r+")
                f.truncate(0)
            else:
                f = open(dst, "w")

            f.write(text)
            f.close()

            if not old:
                shutil.copymode(src, dst)
                shutil.copystat(src, dst)
        else:
            shutil.copy2(src, dst)

SKELTARGET_MESSAGE = """\
Please choose a directory in which you'd like to install Zope
'instance home' files such as database files, configuration files,
etc.
"""

USERNAME_MESSAGE = """\
Please choose a username for the initial administrator account.
This is required to allow Zope's management interface to be used.
"""

PASSWORD_MESSAGE = """\
Please provide a password for the initial administrator account.
"""

PASSWORD_MANAGER_MESSAGE = """\
Please select a password manager which will be used for encode the password of
the initial administrator account.
"""


def parse_args(argv, from_checkout=False):
    """Parse the command line, returning an object representing the input."""
    path, prog = os.path.split(os.path.realpath(argv[0]))
    version = "%prog for " + zopeversion.ZopeVersionUtility.getZopeVersion()
    p = optparse.OptionParser(prog=prog,
                              usage="%prog [options]",
                              version=version)
    p.add_option("-d", "--dir", dest="destination", metavar="DIR",
                 help="the dir in which the instance home should be created")
    p.add_option("-s", "--skelsrc", dest="skeleton", metavar="DIR",
                 help="template skeleton directory")
    p.add_option("-m", "--password-manager",
                 dest="password_manager", metavar="NAME",
                 help=("set the name of the password manager"
                       " to be used for encode the password"))
    p.add_option("-u", "--user", dest="username", metavar="USER:PASSWORD",
                 help="set the user name and password of the initial user")
    p.add_option("--non-interactive", dest="interactive", action="store_false",
                 default=True, help="do no interactive prompting")
    p.add_option("--zserver", dest="zserver", action="store_true",
                 help="""\
Use the older ZServer network server rather than the default Twisted
server.  The Twisted integration with Zope is experimental and not
recommended for use in production sites.  We do encourage it's
use in development or in sites that can stand a little uncertianty, so
that we can gain more experience with it.
""",
                 )


    options, args = p.parse_args(argv[1:])
    if options.skeleton is None:
        options.add_package_includes = from_checkout
        basedir = os.path.dirname(path)
        # no assurance that this exists!
        options.skeleton = os.path.join(basedir, "zopeskel")
    else:
        options.add_package_includes = False
    options.program = prog
    options.version = version
    if args:
        p.error("too many arguments")
    options.password = None
    if options.username and ":" in options.username:
        options.username, options.password = options.username.split(":", 1)
    return options
