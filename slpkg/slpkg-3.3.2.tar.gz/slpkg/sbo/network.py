#!/usr/bin/python
# -*- coding: utf-8 -*-

# network.py file is part of slpkg.

# Copyright 2014-2017 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import pydoc

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.dialog_box import DialogUtil
from slpkg.security import pkg_security
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from slpkg.sbo.read import ReadSBo
from slpkg.sbo.remove import delete
from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.sbo_arch import SBoArch
from slpkg.sbo.compressed import SBoLink
from slpkg.sbo.search import sbo_search_pkg
from slpkg.sbo.slack_find import slack_package

from slpkg.slack.slack_version import slack_ver


class SBoNetwork(object):
    """View SBo site in terminal and also read, build or
    install packages
    """
    def __init__(self, name, flag):
        self.name = name
        self.flag = flag
        self.meta = _meta_
        self.msg = Msg()
        self.arch = SBoArch().get()
        self.comp_tar = ".tar.gz"
        self.choice = ""
        self.FAULT = ""
        self.green = self.meta.color["GREEN"]
        self.red = self.meta.color["RED"]
        self.yellow = self.meta.color["YELLOW"]
        self.cyan = self.meta.color["CYAN"]
        self.grey = self.meta.color["GREY"]
        self.endc = self.meta.color["ENDC"]
        self.build_folder = self.meta.build_path
        self._SOURCES = self.meta.SBo_SOURCES
        self.msg.reading()
        self.data = SBoGrep(name="").names()
        self.case_insensitive()
        if "--checklist" in self.flag:
            self.with_checklist()
        grep = SBoGrep(self.name)
        self.sbo_files = grep.files()
        self.blacklist = BlackList().packages(pkgs=self.data, repo="sbo")
        self.sbo_url = sbo_search_pkg(self.name)
        if self.sbo_url:
            self.sbo_desc = grep.description()[len(self.name) + 2:-1]
            self.source_dwn = grep.source().split()
            self.sbo_req = grep.requires()
            self.sbo_dwn = SBoLink(self.sbo_url).tar_gz()
            self.sbo_version = grep.version()
            self.dwn_srcs = self.sbo_dwn.split() + self.source_dwn
        if "--checklist" not in self.flag or not self.sbo_url and self.name:
            self.msg.done()

    def view(self):
        """View SlackBuild package, read or install them
        from slackbuilds.org
        """
        if self.sbo_url and self.name not in self.blacklist:
            self.prgnam = ("{0}-{1}".format(self.name, self.sbo_version))
            self.view_sbo()
            while True:
                self.read_choice()
                choice = {
                    "r": self.choice_README,
                    "R": self.choice_README,
                    "s": self.choice_SlackBuild,
                    "S": self.choice_SlackBuild,
                    "f": self.choice_info,
                    "F": self.choice_info,
                    "o": self.choice_doinst,
                    "O": self.choice_doinst,
                    "d": self.choice_download,
                    "D": self.choice_download,
                    "download": self.choice_download,
                    "b": self.choice_build,
                    "B": self.choice_build,
                    "build": self.choice_build,
                    "i": self.choice_install,
                    "I": self.choice_install,
                    "install": self.choice_install,
                    "c": self.choice_clear_screen,
                    "C": self.choice_clear_screen,
                    "clear": self.choice_clear_screen,
                    "q": self.choice_quit,
                    "quit": self.choice_quit,
                    "Q": self.choice_quit
                }
                try:
                    choice[self.choice]()
                except KeyError:
                    pass
        else:
            self.msg.pkg_not_found("\n", self.name, "Can't view", "\n")
            raise SystemExit(1)

    def case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase
        """
        if "--case-ins" in self.flag:
            data_dict = Utils().case_sensitive(self.data)
            for key, value in data_dict.iteritems():
                if key == self.name.lower():
                    self.name = value

    def read_choice(self):
        """Return choice
        """
        commands = {
            "r": "README",
            "R": "README",
            "s": "{0}.SlackBuild".format(self.name),
            "S": "{0}.SlackBuild".format(self.name),
            "f": "{0}.info".format(self.name),
            "F": "{0}.info".format(self.name),
            "o": "doinst.sh",
            "O": "doinst.sh",
            "d": "download",
            "D": "download",
            "download": "download",
            "b": "build",
            "B": "build",
            "build": "build",
            "i": "install",
            "I": "install",
            "install": "install",
            "c": "clear",
            "C": "clear",
            "clear": "clear",
            "q": "quit",
            "quit": "quit",
            "Q": "quit"
        }
        try:
            message = "  Choose an option > "
            self.choice = raw_input("{0}{1}{2}".format(self.grey, message,
                                                       self.endc))
        except EOFError:
            print("")
            raise SystemExit()
        try:
            sys.stdout.write("{0}\x1b[1A{1}{2}{3}\n".format(
                " " * len(message), self.cyan, commands[self.choice],
                self.endc))
            sys.stdout.flush()
        except KeyError:
            pass

    def choice_README(self):
        """View README file
        """
        README = ReadSBo(self.sbo_url).readme("README")
        fill = self.fill_pager(README)
        self.pager(README + fill)

    def choice_SlackBuild(self):
        """View .SlackBuild file
        """
        SlackBuild = ReadSBo(self.sbo_url).slackbuild(self.name, ".SlackBuild")
        fill = self.fill_pager(SlackBuild)
        self.pager(SlackBuild + fill)

    def choice_info(self):
        """View .info file
        """
        info = ReadSBo(self.sbo_url).info(self.name, ".info")
        fill = self.fill_pager(info)
        self.pager(info + fill)

    def choice_doinst(self):
        """View doinst.sh file
        """
        if "doinst.sh" in self.sbo_files.split():
            doinst_sh = ReadSBo(self.sbo_url).doinst("doinst.sh")
            fill = self.fill_pager(doinst_sh)
            self.pager(doinst_sh + fill)

    def choice_download(self):
        """Download script.tar.gz and sources
        """
        Download(path="", url=self.dwn_srcs, repo="sbo").start()
        raise SystemExit()

    def choice_build(self):
        """Build package
        """
        self.build()
        delete(self.build_folder)
        raise SystemExit()

    def choice_install(self):
        """Download, build and install package
        """
        pkg_security([self.name])
        if not find_package(self.prgnam, self.meta.pkg_path):
            self.build()
            self.install()
            delete(self.build_folder)
            raise SystemExit()
        else:
            self.msg.template(78)
            self.msg.pkg_found(self.prgnam)
            self.msg.template(78)
            raise SystemExit()

    def choice_clear_screen(self):
        """Clear screen
        """
        os.system("clear")
        self.view()

    def choice_quit(self):
        """Quit from choices
        """
        raise SystemExit()

    def view_sbo(self):
        """View slackbuild.org
        """
        sbo_url = self.sbo_url.replace("/slackbuilds/", "/repository/")
        br1, br2, fix_sp = "", "", " "
        if self.meta.use_colors in ["off", "OFF"]:
            br1 = "("
            br2 = ")"
            fix_sp = ""
        print("")   # new line at start
        self.msg.template(78)
        print("| {0}{1}SlackBuilds Repository{2}".format(" " * 28, self.grey,
                                                         self.endc))
        self.msg.template(78)
        print("| {0} > {1} > {2}{3}{4}".format(slack_ver(),
                                               sbo_url.split("/")[-3].title(),
                                               self.cyan, self.name, self.endc))
        self.msg.template(78)
        print("| {0}Package url{1}: {2}".format(self.green, self.endc, sbo_url))
        self.msg.template(78)
        print("| {0}Description: {1}{2}".format(self.green,
                                                self.endc, self.sbo_desc))
        print("| {0}SlackBuild: {1}{2}".format(self.green, self.endc,
                                               self.sbo_dwn.split("/")[-1]))
        print("| {0}Sources: {1}{2}".format(
            self.green, self.endc,
            (", ".join([src.split("/")[-1] for src in self.source_dwn]))))
        print("| {0}Requirements: {1}{2}".format(self.yellow,
                                                 self.endc,
                                                 ", ".join(self.sbo_req)))
        self.msg.template(78)
        print("| {0}R{1}{2}EADME               View the README file".format(
            self.red, self.endc, br2))
        print("| {0}S{1}{2}lackBuild           View the .SlackBuild "
              "file".format(self.red, self.endc, br2))
        print("| In{0}{1}f{2}{3}o{4}                View the .info "
              "file".format(br1, self.red, self.endc, br2, fix_sp))
        if "doinst.sh" in self.sbo_files.split():
            print("| D{0}{1}o{2}{3}inst.sh{4}           View the doinst.sh "
                  "file".format(br1, self.red, self.endc, br2, fix_sp))
        print("| {0}D{1}{2}ownload             Download this package".format(
            self.red, self.endc, br2))
        print("| {0}B{1}{2}uild                Download and build".format(
            self.red, self.endc, br2))
        print("| {0}I{1}{2}nstall              Download/Build/Install".format(
            self.red, self.endc, br2))
        print("| {0}C{1}{2}lear                Clear screen".format(self.red,
                                                                    self.endc,
                                                                    br2))
        print("| {0}Q{1}{2}uit                 Quit".format(self.red,
                                                            self.endc, br2))

        self.msg.template(78)

    def with_checklist(self):
        """Using dialog and checklist option
        """
        data = []
        if self.name == "ALL":
            data = self.data
        else:
            for name in self.data:
                if self.name in name:
                    data.append(name)
        if data:
            text = "Press 'spacebar' to choose SlackBuild for view"
            title = " SlackBuilds.org "
            backtitle = "{0} {1}".format(_meta_.__all__, _meta_.__version__)
            status = False
            pkg = DialogUtil(data, text, title, backtitle, status).checklist()
            if pkg and len(pkg) > 1:
                print("\nslpkg: Error: Choose only one package")
                raise SystemExit()
            if pkg is None:
                raise SystemExit()
            self.name = "".join(pkg)
            os.system("clear")

    def pager(self, text):
        """Read text
        """
        pydoc.pager(text)

    def fill_pager(self, page):
        """Fix pager spaces
        """
        tty_size = os.popen("stty size", "r").read().split()
        rows = int(tty_size[0]) - 1
        lines = sum(1 for line in page.splitlines())
        diff = rows - lines
        fill = "\n" * diff
        if diff > 0:
            return fill
        else:
            return ""

    def error_uns(self):
        """Check if package supported by arch
        before proceed to install
        """
        self.FAULT = ""
        UNST = ["UNSUPPORTED", "UNTESTED"]
        if "".join(self.source_dwn) in UNST:
            self.FAULT = "".join(self.source_dwn)

    def build(self):
        """Only build and create Slackware package
        """
        pkg_security([self.name])
        self.error_uns()
        if self.FAULT:
            print("")
            self.msg.template(78)
            print("| Package {0} {1} {2} {3}".format(self.prgnam, self.red,
                                                     self.FAULT, self.endc))
            self.msg.template(78)
        else:
            sources = []
            if not os.path.exists(self.meta.build_path):
                os.makedirs(self.meta.build_path)
            if not os.path.exists(self._SOURCES):
                os.makedirs(self._SOURCES)
            os.chdir(self.meta.build_path)
            Download(self.meta.build_path, self.sbo_dwn.split(),
                     repo="sbo").start()
            Download(self._SOURCES, self.source_dwn, repo="sbo").start()
            script = self.sbo_dwn.split("/")[-1]
            for src in self.source_dwn:
                sources.append(src.split("/")[-1])
            BuildPackage(script, sources, self.meta.build_path,
                         auto=False).build()
            slack_package(self.prgnam)  # check if build

    def install(self):
        """Install SBo package found in /tmp directory.
        """
        binary = slack_package(self.prgnam)
        print("[ {0}Installing{1} ] --> {2}".format(self.green, self.endc,
                                                    self.name))
        PackageManager(binary).upgrade(flag="--install-new")
