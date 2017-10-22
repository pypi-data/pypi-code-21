#!/usr/bin/python
# -*- coding: utf-8 -*-

# downloader.py file is part of slpkg.

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
import tarfile
import subprocess

from slpkg.messages import Msg
from slpkg.slack.slack_version import slack_ver
from slpkg.__metadata__ import MetaData as _meta_


class Download(object):
    """Downloader manager. Slpkg use wget by default but support
    curl, aria2 and httpie
    """
    def __init__(self, path, url, repo):
        self.path = path
        self.url = url
        self.repo = repo
        self.file_name = ""
        self.meta = _meta_
        self.msg = Msg()
        self.dir_prefix = ""
        self.downder = self.meta.downder
        self.downder_options = self.meta.downder_options

    def start(self):
        """Download files using wget or other downloader.
        Optional curl, aria2c and httpie
        """
        dwn_count = 1
        self._directory_prefix()
        for dwn in self.url:
            # get file name from url and fix passing char '+'
            self.file_name = dwn.split("/")[-1].replace("%2B", "+")

            if dwn.startswith("file:///"):
                source_dir = dwn[7:-7].replace(slack_ver(), "")
                self._make_tarfile(self.file_name, source_dir)

            self._check_certificate()
            print("\n[{0}/{1}][ {2}Download{3} ] --> {4}\n".format(
                dwn_count, len(self.url), self.meta.color["GREEN"],
                self.meta.color["ENDC"],
                self.file_name))
            if self.downder in ["wget", "aria2c"]:
                subprocess.call("{0} {1} {2}{3} {4}".format(
                                self.downder, self.downder_options,
                                self.dir_prefix, self.path, dwn),
                                shell=True)
            elif self.downder in ["curl", "http"]:
                subprocess.call("{0} {1} {2}{3} {4}".format(
                                self.downder, self.downder_options,
                                self.path, self.file_name, dwn), shell=True)
            self._check_if_downloaded()
            dwn_count += 1

    def _make_tarfile(self, output_filename, source_dir):
        """Create .tar.gz file
        """
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    def _directory_prefix(self):
        """Downloader options for specific directory
        """
        if self.downder == "wget":
            self.dir_prefix = "--directory-prefix="
        elif self.downder == "aria2c":
            self.dir_prefix = "--dir="

    def _check_if_downloaded(self):
        """Check if file downloaded
        """
        if not os.path.isfile(self.path + self.file_name):
            print("")
            self.msg.template(78)
            print("| Download '{0}' file [ {1}FAILED{2} ]".format(
                self.file_name, self.meta.color["RED"],
                self.meta.color["ENDC"]))
            self.msg.template(78)
            print("")
            if not self.msg.answer() in ["y", "Y"]:
                raise SystemExit()

    def _check_certificate(self):
        """Check for certificates options for wget
        """
        if (self.file_name.startswith("jdk-") and self.repo == "sbo" and
                self.downder == "wget"):
            certificate = (' --no-check-certificate --header="Cookie: '
                           'oraclelicense=accept-securebackup-cookie"')
            self.msg.template(78)
            print("| '{0}' need to go ahead downloading".format(
                certificate[:23].strip()))
            self.msg.template(78)
            print("")
            self.downder_options += certificate
            if not self.msg.answer() in ["y", "Y"]:
                raise SystemExit()
