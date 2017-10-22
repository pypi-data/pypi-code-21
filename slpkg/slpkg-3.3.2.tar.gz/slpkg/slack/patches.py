#!/usr/bin/python
# -*- coding: utf-8 -*-

# patches.py file is part of slpkg.

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
import shutil
import subprocess

from slpkg.init import Update
from slpkg.utils import Utils
from slpkg.sizes import units
from slpkg.messages import Msg
from slpkg.url_read import URL
from slpkg.toolbar import status
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.remove import delete_package
from slpkg.grep_md5 import pkg_checksum
from slpkg.dialog_box import DialogUtil
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager
from slpkg.pkg.installed import GetFromInstalled

from slpkg.binary.greps import repo_data

from slpkg.slack.mirrors import mirrors
from slpkg.slack.slack_version import slack_ver


class Patches(object):
    """Upgrade distribution from official Slackware mirrors
    """
    def __init__(self, skip, flag):
        self.skip = skip
        self.flag = flag
        self.meta = _meta_
        self.msg = Msg()
        self.version = self.meta.slack_rel
        self.patch_path = self.meta.slpkg_tmp_patches
        self.pkg_for_upgrade = []
        self.dwn_links = []
        self.upgrade_all = []
        self.count_added = 0
        self.count_upg = 0
        self.upgraded = []
        self.installed = []
        self.comp_sum = []
        self.uncomp_sum = []
        self.utils = Utils()
        self.msg.checking()
        if self.version == "stable":
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT",
                                            "patches/")).reading()
        else:
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT", "")).reading()

    def start(self):
        """
        Install new patches from official Slackware mirrors
        """
        self.store()
        self.msg.done()
        if self.upgrade_all:
            if "--checklist" in self.flag:
                self.dialog_checklist()
            print("\nThese packages need upgrading:\n")
            self.msg.template(78)
            print("{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
                "| Package", " " * 17,
                "New Version", " " * 8,
                "Arch", " " * 4,
                "Build", " " * 2,
                "Repos", " " * 10,
                "Size"))
            self.msg.template(78)
            print("Upgrading:")
            self.views()
            unit, size = units(self.comp_sum, self.uncomp_sum)
            print("\nInstalling summary")
            print("=" * 79)
            print("{0}Total {1} {2} will be upgraded and {3} will be "
                  "installed.".format(self.meta.color["GREY"],
                                      self.count_upg,
                                      self.msg.pkg(self.upgrade_all),
                                      self.count_added))
            print("Need to get {0} {1} of archives.".format(size[0],
                                                            unit[0]))
            print("After this process, {0} {1} of additional disk space "
                  "will be used.{2}".format(size[1], unit[1],
                                            self.meta.color["ENDC"]))
            print("")
            if self.msg.answer() in ["y", "Y"]:
                Download(self.patch_path, self.dwn_links,
                         repo="slack").start()
                self.upgrade_all = self.utils.check_downloaded(
                    self.patch_path, self.upgrade_all)
                self.upgrade()
                self.kernel()
                if self.meta.slackpkg_log in ["on", "ON"]:
                    self.slackpkg_update()
                self.msg.reference(self.installed, self.upgraded)
                delete_package(self.patch_path, self.upgrade_all)
                self.update_lists()
        else:
            slack_arch = ""
            if self.meta.arch == "x86_64":
                slack_arch = "64"
            print("\nSlackware{0} '{1}' v{2} distribution is up to "
                  "date\n".format(slack_arch, self.version, slack_ver()))

    def store(self):
        """
        Store and return packages for upgrading
        """
        data = repo_data(self.PACKAGES_TXT, "slack", self.flag)
        black = BlackList().packages(pkgs=data[0], repo="slack")
        for name, loc, comp, uncomp in zip(data[0], data[1], data[2], data[3]):
            status(0.0003)
            repo_pkg_name = split_package(name)[0]
            if (not os.path.isfile(self.meta.pkg_path + name[:-4]) and
                    repo_pkg_name not in black and
                    repo_pkg_name not in self.skip):
                self.dwn_links.append("{0}{1}/{2}".format(mirrors("", ""),
                                                          loc, name))
                self.comp_sum.append(comp)
                self.uncomp_sum.append(uncomp)
                self.upgrade_all.append(name)
                self.count_upg += 1
                if not find_package(repo_pkg_name + self.meta.sp,
                                    self.meta.pkg_path):
                    self.count_added += 1
                    self.count_upg -= 1
        return self.count_upg

    def dialog_checklist(self):
        """Create checklist to choose packages for upgrade
        """
        data = []
        for upg in self.upgrade_all:
            data.append(upg[:-4])
        text = "Press 'spacebar' to unchoose packages from upgrade"
        title = " Upgrade "
        backtitle = "{0} {1}".format(self.meta.__all__,
                                     self.meta.__version__)
        status = True
        pkgs = DialogUtil(data, text, title, backtitle,
                          status).checklist()
        index = 0
        for pkg, comp, uncomp in zip(self.upgrade_all, self.comp_sum,
                                     self.uncomp_sum):
            if pkg[:-4] not in pkgs:
                self.dwn_links.pop(index)
                self.upgrade_all.pop(index)
                self.comp_sum.pop(index)
                self.uncomp_sum.pop(index)
                self.count_upg -= 1
                del comp, uncomp
                index -= 1
            index += 1
        if not self.upgrade_all:
            raise SystemExit()

    def views(self):
        """
        Views packages
        """
        for upg, size in sorted(zip(self.upgrade_all, self.comp_sum)):
            pkg_repo = split_package(upg[:-4])
            color = self.meta.color["RED"]
            pkg_inst = GetFromInstalled(pkg_repo[0]).name()
            if pkg_repo[0] == pkg_inst:
                color = self.meta.color["YELLOW"]
            ver = GetFromInstalled(pkg_repo[0]).version()
            print("  {0}{1}{2}{3} {4}{5} {6}{7}{8}{9}{10}{11:>12}{12}".format(
                color, pkg_repo[0] + ver, self.meta.color["ENDC"],
                " " * (23-len(pkg_repo[0] + ver)), pkg_repo[1],
                " " * (18-len(pkg_repo[1])), pkg_repo[2],
                " " * (8-len(pkg_repo[2])), pkg_repo[3],
                " " * (7-len(pkg_repo[3])), "Slack",
                size, " K")).rstrip()

    def upgrade(self):
        """
        Upgrade packages
        """
        for pkg in self.upgrade_all:
            check_md5(pkg_checksum(pkg, "slack_patches"), self.patch_path + pkg)
            pkg_ver = "{0}-{1}".format(split_package(pkg)[0],
                                       split_package(pkg)[1])
            if find_package(split_package(pkg)[0] + self.meta.sp,
                            self.meta.pkg_path):
                print("[ {0}upgrading{1} ] --> {2}".format(
                    self.meta.color["YELLOW"], self.meta.color["ENDC"],
                    pkg[:-4]))
                PackageManager((self.patch_path + pkg).split()).upgrade(
                    "--install-new")
                self.upgraded.append(pkg_ver)
            else:
                print("[ {0}installing{1} ] --> {2}".format(
                    self.meta.color["GREEN"], self.meta.color["ENDC"],
                    pkg[:-4]))
                PackageManager((self.patch_path + pkg).split()).upgrade(
                    "--install-new")
                self.installed.append(pkg_ver)

    def kernel(self):
        """
        Check if kernel upgraded if true
        then reinstall "lilo"
        """
        for core in self.upgrade_all:
            if "kernel" in core:
                if self.meta.default_answer in ["y", "Y"]:
                    answer = self.meta.default_answer
                else:
                    print("")
                    self.msg.template(78)
                    print("| {0}*** HIGHLY recommended reinstall 'LILO' "
                          "***{1}".format(self.meta.color["RED"],
                                          self.meta.color["ENDC"]))
                    self.msg.template(78)
                    try:
                        answer = raw_input("\nThe kernel has been upgraded, "
                                           "reinstall `LILO` [y/N]? ")
                    except EOFError:
                        print("")
                        raise SystemExit()
                if answer in ["y", "Y"]:
                    subprocess.call("lilo", shell=True)
                    break

    def slackpkg_update(self):
        """This replace slackpkg ChangeLog.txt file with new
        from Slackware official mirrors after update distribution.
        """
        NEW_ChangeLog_txt = URL(mirrors("ChangeLog.txt", "")).reading()
        if os.path.isfile(self.meta.slackpkg_lib_path + "ChangeLog.txt.old"):
            os.remove(self.meta.slackpkg_lib_path + "ChangeLog.txt.old")
        if os.path.isfile(self.meta.slackpkg_lib_path + "ChangeLog.txt"):
            shutil.copy2(self.meta.slackpkg_lib_path + "ChangeLog.txt",
                         self.meta.slackpkg_lib_path + "ChangeLog.txt.old")
            os.remove(self.meta.slackpkg_lib_path + "ChangeLog.txt")
        with open(self.meta.slackpkg_lib_path + "ChangeLog.txt", "w") as log:
            log.write(NEW_ChangeLog_txt)
            log.close()

    def update_lists(self):
        """Update packages list and ChangeLog.txt file after
        upgrade distribution
        """
        print("{0}Update package lists ?{1}".format(self.meta.color["GREEN"],
                                                    self.meta.color["ENDC"]))
        print("=" * 79)
        if self.msg.answer() in ["y", "Y"]:
            Update().repository(["slack"])
