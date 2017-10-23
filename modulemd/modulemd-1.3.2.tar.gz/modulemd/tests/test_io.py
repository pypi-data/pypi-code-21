#/usr/bin/python3
# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>

import unittest

import os
import sys
import datetime

DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(DIR, ".."))

from modulemd import ModuleMetadata, dump_all, load_all

class TestIO(unittest.TestCase):
    maxDiff = None  # display diff when a test fails

    @classmethod
    def setUpClass(cls):
        cls.mmd = ModuleMetadata()

    def test_load_spec(self):
        self.mmd.load("spec.yaml")
        self.assertEqual(self.mmd.mdversion, 1)
        self.assertEqual(self.mmd.name, "foo")
        self.assertEqual(self.mmd.stream, "stream-name")
        self.assertEqual(self.mmd.version, 20160927144203)
        self.assertEqual(self.mmd.context, "c0ffee43")
        self.assertEqual(self.mmd.arch, "x86_64")
        self.assertEqual(self.mmd.summary, "An example module")
        self.assertEqual(self.mmd.description, "A module for the demonstration of the metadata format. Also, the obligatory lorem ipsum dolor sit amet goes right here.")
        self.assertEqual(self.mmd.eol, datetime.date(2077, 10, 23))
        self.assertSetEqual(self.mmd.module_licenses, set(["MIT"]))
        self.assertSetEqual(self.mmd.content_licenses,
                set(["Beerware", "GPLv2+", "zlib"]))
        self.assertEqual(self.mmd.xmd, {'some_key': 'some_data'})
        self.assertDictEqual(self.mmd.buildrequires,
                {
                    "platform" : "and-its-stream-name",
                    "extra-build-env" : "and-its-stream-name-too"
                })
        self.assertDictEqual(self.mmd.requires,
                {
                    "platform" : "and-its-stream-name"
                })
        self.assertEqual(self.mmd.community, "http://www.example.com/")
        self.assertEqual(self.mmd.documentation, "http://www.example.com/")
        self.assertEqual(self.mmd.tracker, "http://www.example.com/")
        self.assertSetEqual(set(self.mmd.profiles.keys()),
                set(["default", "minimal", "container", "buildroot",
                    "srpm-buildroot"]))
        self.assertSetEqual(self.mmd.profiles["default"].rpms,
                set(["bar", "bar-extras", "baz"]))
        self.assertEqual(self.mmd.profiles["minimal"].description,
                "Minimal profile installing only the bar package.")
        self.assertSetEqual(self.mmd.profiles["minimal"].rpms,
                set(["bar"]))
        self.assertSetEqual(self.mmd.api.rpms,
                set(["bar", "bar-extras", "bar-devel", "baz", "xxx"]))
        self.assertSetEqual(self.mmd.filter.rpms,
                set(["baz-nonfoo"]))
        self.assertSetEqual(set(self.mmd.components.rpms.keys()),
                set(["bar", "baz", "xxx", "xyz"]))
        self.assertEqual(self.mmd.components.rpms["bar"].rationale,
                "We need this to demonstrate stuff.")
        self.assertEqual(self.mmd.components.rpms["bar"].repository,
                "https://pagure.io/bar.git")
        self.assertEqual(self.mmd.components.rpms["bar"].ref,
                "26ca0c0")
        self.assertEqual(self.mmd.components.rpms["bar"].cache,
                "https://example.com/cache")
        self.assertEqual(self.mmd.components.rpms["baz"].rationale,
                "This one is here to demonstrate other stuff.")
        self.assertEqual(self.mmd.components.rpms["xxx"].rationale,
                "xxx demonstrates arches and multilib.")
        self.assertSetEqual(self.mmd.components.rpms["xxx"].arches,
                set(["i686", "x86_64"]))
        self.assertSetEqual(self.mmd.components.rpms["xxx"].multilib,
                set(["x86_64"]))
        self.assertEqual(self.mmd.components.rpms["xyz"].rationale,
                "xyz is a bundled dependency of xxx.")
        self.assertEqual(self.mmd.components.rpms["xyz"].buildorder,
                10)
        self.assertSetEqual(set(self.mmd.components.modules),
                set(["includedmodule"]))
        self.assertEqual(self.mmd.components.modules["includedmodule"].rationale,
                "Included in the stack, just because.")
        self.assertEqual(self.mmd.components.modules["includedmodule"].repository,
                "https://pagure.io/includedmodule.git")
        self.assertEqual(self.mmd.components.modules["includedmodule"].ref,
                "somecoolbranchname")
        self.assertEqual(self.mmd.components.modules["includedmodule"].buildorder,
                100)
        self.assertSetEqual(self.mmd.artifacts.rpms,
                set(["bar-0:1.23-1.module_deadbeef.x86_64",
                     "bar-devel-0:1.23-1.module_deadbeef.x86_64",
                     "bar-extras-0:1.23-1.module_deadbeef.x86_64",
                     "baz-0:42-42.module_deadbeef.x86_64",
                     "xxx-0:1-1.module_deadbeef.x86_64",
                     "xxx-0:1-1.module_deadbeef.i686",
                     "xyz-0:1-1.module_deadbeef.x86_64"]))
        self.assertEqual(self.mmd.buildopts.rpms.macros,
                "%demomacro 1\n%demomacro2 %{demomacro}23\n")

    def test_reload(self):
        self.mmd.load("spec.yaml")
        first = repr(self.mmd)
        self.mmd.dump("testdump.yaml")
        self.mmd = ModuleMetadata()
        self.mmd.load("testdump.yaml")
        second = repr(self.mmd)
        # fails on python 3:
        # http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
        self.assertEqual(first, second)
        os.remove("testdump.yaml")

    def test_reload_all(self):
        a = ModuleMetadata()
        b = ModuleMetadata()
        a.name = 'a'
        b.name = 'b'
        arepr = repr(a)
        brepr = repr(b)
        dump_all("testdumpall.yaml", [a, b])
        a, b = load_all("testdumpall.yaml")
        self.assertEqual(arepr, repr(a))
        self.assertEqual(brepr, repr(b))
        os.remove("testdumpall.yaml")
