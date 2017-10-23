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

from modulemd import ModuleMetadata
from modulemd import supported_mdversions
from modulemd.profile import ModuleProfile
from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM

class TestBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m = ModuleMetadata()
        m.name = "name"
        m.stream = "stream"
        m.version = 1
        m.context = "context"
        m.arch = "arch"
        m.summary = "summary"
        m.description = "description"
        m.eol = datetime.date(2077, 10, 23)
        m.module_licenses = set(["module1", "module2", "module3"])
        m.content_licenses = set(["content1", "content2", "content3"])
        m.xmd = { "key" : "value" }
        m.buildrequires = {
                "br1" : "br1stream",
                "br2" : "br2stream",
                "br3" : "br3stream"
                }
        m.requires = {
                "r1" : "r1stream",
                "r2" : "r2stream",
                "r3" : "r3stream"
                }
        m.community = "community"
        m.documentation = "documentation"
        m.tracker = "tracker"
        profile = ModuleProfile()
        profile.description = "description"
        profile.rpms = set(["prof1", "prof2", "prof3"])
        m.profiles = { "profile" : profile }
        m.api.rpms = set(["api1", "api2", "api3"])
        m.filter.rpms = set(["filter1", "filter2", "filter3"])
        rpm = ModuleComponentRPM("rpm", "rationale",
                buildorder=1,
                repository="repository",
                ref="ref",
                cache="cache",
                arches=set(["arch1", "arch2", "arch3"]),
                multilib=set(["multi1", "multi2", "multi3"])
                )
        m.components.rpms = { "rpm" : rpm }
        mod = ModuleComponentModule("mod", "rationale",
                buildorder=2,
                repository="repository",
                ref="ref",
                )
        m.components.modules = { "mod" : mod }
        m.artifacts.rpms = set(["art1", "art2", "art3"])
        m.buildopts.rpms.macros = "%test 1"
        cls.mmd = m

    def test_mdversion(self):
        self.assertIn(self.mmd.mdversion, supported_mdversions)

    def test_name(self):
        self.assertEqual(self.mmd.name, "name")

    def test_stream(self):
        self.assertEqual(self.mmd.stream, "stream")

    def test_version(self):
        self.assertEqual(self.mmd.version, 1)

    def test_context(self):
        self.assertEqual(self.mmd.context, "context")

    def test_arch(self):
        self.assertEqual(self.mmd.arch, "arch")

    def test_summary(self):
        self.assertEqual(self.mmd.summary, "summary")

    def test_description(self):
        self.assertEqual(self.mmd.description, "description")

    def test_eol(self):
        self.assertEqual(self.mmd.eol, datetime.date(2077, 10, 23))

    def test_module_licenses(self):
        self.assertSetEqual(
                self.mmd.module_licenses,
                set(["module1", "module2", "module3"])
                )

    def test_content_licenses(self):
        self.assertSetEqual(
                self.mmd.content_licenses,
                set(["content1", "content2", "content3"])
                )

    def test_xmd(self):
        self.assertDictEqual(self.mmd.xmd, { "key" : "value" })

    def test_buildrequires(self):
        self.assertDictEqual(
                self.mmd.buildrequires,
                {
                    "br1" : "br1stream",
                    "br2" : "br2stream",
                    "br3" : "br3stream"
                }
                )

    def test_requires(self):
        self.assertDictEqual(
                self.mmd.requires,
                {
                    "r1" : "r1stream",
                    "r2" : "r2stream",
                    "r3" : "r3stream"
                }
                )

    def test_community(self):
        self.assertEqual(self.mmd.community, "community")

    def test_documentation(self):
        self.assertEqual(self.mmd.documentation, "documentation")

    def test_tracker(self):
        self.assertEqual(self.mmd.tracker, "tracker")

    def test_profiles(self):
        self.assertEqual(list(self.mmd.profiles.keys()), ["profile"])
        self.assertEqual(
                self.mmd.profiles["profile"].description,
                "description"
                )
        self.assertSetEqual(
                self.mmd.profiles["profile"].rpms,
                set(["prof1", "prof2", "prof3"])
                )

    def test_api(self):
        self.assertSetEqual(
                self.mmd.api.rpms,
                set(["api1", "api2", "api3"])
                )

    def test_filter(self):
        self.assertSetEqual(
                self.mmd.filter.rpms,
                set(["filter1", "filter2", "filter3"])
                )

    def test_rpms(self):
        self.assertEqual(list(self.mmd.components.rpms.keys()), ["rpm"])
        rpm = self.mmd.components.rpms["rpm"]
        self.assertEqual(rpm.name, "rpm")
        self.assertEqual(rpm.rationale, "rationale")
        self.assertEqual(rpm.buildorder, 1)
        self.assertEqual(rpm.repository, "repository")
        self.assertEqual(rpm.ref, "ref")
        self.assertEqual(rpm.cache, "cache")
        self.assertSetEqual(rpm.arches, set(["arch1", "arch2", "arch3"]))
        self.assertSetEqual(rpm.multilib, set(["multi1", "multi2", "multi3"]))

    def test_modules(self):
        self.assertEqual(list(self.mmd.components.modules.keys()), ["mod"])
        mod = self.mmd.components.modules["mod"]
        self.assertEqual(mod.name, "mod")
        self.assertEqual(mod.rationale, "rationale")
        self.assertEqual(mod.buildorder, 2)
        self.assertEqual(mod.repository, "repository")
        self.assertEqual(mod.ref, "ref")

    def test_artifacts(self):
        self.assertSetEqual(
                self.mmd.artifacts.rpms,
                set(["art1", "art2", "art3"])
                )

    def test_buildopts_rpms(self):
        self.assertEqual(self.mmd.buildopts.rpms.macros,
                "%test 1")
