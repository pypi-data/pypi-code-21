#!/usr/bin/python
# -*- coding: utf-8 -*-

# queue.py file is part of slpkg.

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
from collections import OrderedDict

from slpkg.utils import Utils
from slpkg.downloader import Download
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.compressed import SBoLink
from slpkg.sbo.search import sbo_search_pkg
from slpkg.sbo.slack_find import slack_package


class QueuePkgs(object):
    """Manage SBo packages, add or remove for building or
    installation
    """
    def __init__(self):
        queue_file = [
            "# In this file you can create a list of\n",
            "# packages you want to build or install.\n",
            "#\n"
        ]
        self.meta = _meta_
        self.quit = False
        self.queue = self.meta.lib_path + "queue/"
        self.queue_list = self.queue + "queue_list"
        self._SOURCES = self.meta.SBo_SOURCES
        if not os.path.exists(self.meta.lib_path):
            os.mkdir(self.meta.lib_path)
        if not os.path.exists(self.queue):
            os.mkdir(self.queue)
        if not os.path.isfile(self.queue_list):
            with open(self.queue_list, "w") as queue:
                for line in queue_file:
                    queue.write(line)
                queue.close()
        self.queued = Utils().read_file(self.queue_list)

    def packages(self):
        """Return queue list from /var/lib/queue/queue_list
        file.
        """
        queue_list = []
        for read in self.queued.splitlines():
            read = read.lstrip()
            if not read.startswith("#"):
                queue_list.append(read.replace("\n", ""))
        return queue_list

    def listed(self):
        """Print packages from queue
        """
        print("\nPackages in queue:\n")
        for pkg in self.packages():
            if pkg:
                print("{0}{1}{2}".format(self.meta.color["GREEN"], pkg,
                                         self.meta.color["ENDC"]))
                self.quit = True
        if self.quit:
            print("")   # new line at exit

    def add(self, pkgs):
        """Add packages in queue if not exist
        """
        queue_list = self.packages()
        pkgs = list(OrderedDict.fromkeys(pkgs))
        print("\nAdd packages in queue:\n")
        with open(self.queue_list, "a") as queue:
            for pkg in pkgs:
                find = sbo_search_pkg(pkg)
                if pkg not in queue_list and find is not None:
                    print("{0}{1}{2}".format(self.meta.color["GREEN"], pkg,
                                             self.meta.color["ENDC"]))
                    queue.write(pkg + "\n")
                    self.quit = True
                else:
                    print("{0}{1}{2}".format(self.meta.color["RED"], pkg,
                                             self.meta.color["ENDC"]))
                    self.quit = True
            queue.close()
        if self.quit:
            print("")   # new line at exit

    def remove(self, pkgs):
        """Remove packages from queue
        """
        print("\nRemove packages from queue:\n")
        with open(self.queue_list, "w") as queue:
            for line in self.queued.splitlines():
                if line not in pkgs:
                    queue.write(line + "\n")
                else:
                    print("{0}{1}{2}".format(self.meta.color["RED"], line,
                                             self.meta.color["ENDC"]))
                    self.quit = True
            queue.close()
        if self.quit:
            print("")   # new line at exit

    def build(self):
        """Build packages from queue
        """
        packages = self.packages()
        if packages:
            for pkg in packages:
                if not os.path.exists(self.meta.build_path):
                    os.mkdir(self.meta.build_path)
                if not os.path.exists(self._SOURCES):
                    os.mkdir(self._SOURCES)
                sbo_url = sbo_search_pkg(pkg)
                sbo_dwn = SBoLink(sbo_url).tar_gz()
                source_dwn = SBoGrep(pkg).source().split()
                sources = []
                os.chdir(self.meta.build_path)
                script = sbo_dwn.split("/")[-1]
                Download(self.meta.build_path, sbo_dwn.split(),
                         repo="sbo").start()
                for src in source_dwn:
                    Download(self._SOURCES, src.split(), repo="sbo").start()
                    sources.append(src.split("/")[-1])
                BuildPackage(script, sources, self.meta.build_path,
                             auto=False).build()
        else:
            print("\nPackages not found in the queue for building\n")
            raise SystemExit(1)

    def install(self):
        """Install packages from queue
        """
        packages = self.packages()
        if packages:
            print("")   # new line at start
            for pkg in packages:
                ver = SBoGrep(pkg).version()
                prgnam = "{0}-{1}".format(pkg, ver)
                if find_package(prgnam, self.meta.output):
                    binary = slack_package(prgnam)
                    PackageManager(binary).upgrade(flag="--install-new")
                else:
                    print("\nPackage {0} not found in the {1} for "
                          "installation\n".format(prgnam, self.meta.output))
        else:
            print("\nPackages not found in the queue for installation\n")
            raise SystemExit(1)
