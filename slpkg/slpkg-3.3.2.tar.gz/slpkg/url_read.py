#!/usr/bin/python
# -*- coding: utf-8 -*-

# url_read.py file is part of slpkg.

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
import urllib2

from slpkg.__metadata__ import MetaData as _meta_


class URL(object):
    """Urls reading class
    """
    def __init__(self, link):
        self.link = link
        self.meta = _meta_

    def reading(self):
        """Open url and read
        """
        try:
            # testing proxy
            proxies = {}
            try:
                proxies["http_proxy"] = os.environ['http_proxy']
            except KeyError:
                pass
            try:
                proxies["https_proxy"] = os.environ['https_proxy']
            except KeyError:
                pass

            if len(proxies) != 0:
                proxy = urllib2.ProxyHandler(proxies)
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener)

            # end testing
            f = urllib2.urlopen(self.link)
            return f.read()
        except (urllib2.URLError, ValueError):
            print("\n{0}Can't read file '{1}'{2}".format(
                self.meta.color["RED"], self.link.split("/")[-1],
                self.meta.color["ENDC"]))
            return " "
