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

DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(DIR, ".."))

from modulemd import ModuleMetadata
from modulemd.profile import ModuleProfile
from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM

class TestConvenience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mmd = ModuleMetadata()

    def test_add_module_license(self):
        self.assertSetEqual(self.mmd.module_licenses, set())
        self.mmd.add_module_license("test")
        self.assertSetEqual(self.mmd.module_licenses, set(["test"]))

    def test_del_module_license(self):
        self.mmd.module_licenses = set(["test"])
        self.mmd.del_module_license("test")
        self.assertSetEqual(self.mmd.module_licenses, set())

    def test_clear_module_licenses(self):
        self.mmd.module_licenses = set(["test"])
        self.mmd.clear_module_licenses()
        self.assertSetEqual(self.mmd.module_licenses, set())

    def test_add_content_license(self):
        self.assertSetEqual(self.mmd.content_licenses, set())
        self.mmd.add_content_license("test")
        self.assertSetEqual(self.mmd.content_licenses, set(["test"]))

    def test_del_content_license(self):
        self.mmd.content_licenses = set(["test"])
        self.mmd.del_content_license("test")
        self.assertSetEqual(self.mmd.content_licenses, set())

    def test_clear_content_licenses(self):
        self.mmd.content_licenses = set(["test"])
        self.mmd.clear_content_licenses()
        self.assertSetEqual(self.mmd.content_licenses, set())

    def test_add_requires(self):
        self.assertDictEqual(self.mmd.requires, dict())
        self.mmd.add_requires("key", "value")
        self.assertDictEqual(self.mmd.requires, { "key" : "value" })

    def test_update_requires(self):
        self.assertDictEqual(self.mmd.requires, dict())
        self.mmd.update_requires("key", "value")
        self.assertDictEqual(self.mmd.requires, { "key" : "value" })
        self.mmd.update_requires("key", "newvalue")
        self.assertDictEqual(self.mmd.requires, { "key" : "newvalue" })

    def test_del_requires(self):
        self.mmd.requires = { "key" : "value" }
        self.mmd.del_requires("key")
        self.assertDictEqual(self.mmd.requires, dict())

    def test_clear_requires(self):
        self.mmd.requires = { "key" : "value" }
        self.mmd.clear_requires()
        self.assertDictEqual(self.mmd.requires, dict())

    def test_add_buildrequires(self):
        self.assertDictEqual(self.mmd.buildrequires, dict())
        self.mmd.add_buildrequires("key", "value")
        self.assertDictEqual(self.mmd.buildrequires, { "key" : "value" })

    def test_update_buildrequires(self):
        self.assertDictEqual(self.mmd.buildrequires, dict())
        self.mmd.update_buildrequires("key", "value")
        self.assertDictEqual(self.mmd.buildrequires, { "key" : "value" })
        self.mmd.update_buildrequires("key", "newvalue")
        self.assertDictEqual(self.mmd.buildrequires, { "key" : "newvalue" })

    def test_del_buildrequires(self):
        self.mmd.buildrequires = { "key" : "value" }
        self.mmd.del_buildrequires("key")
        self.assertDictEqual(self.mmd.buildrequires, dict())

    def test_clear_buildrequires(self):
        self.mmd.buildrequires = { "key" : "value" }
        self.mmd.clear_buildrequires()
        self.assertDictEqual(self.mmd.buildrequires, dict())

    def test_api_add_rpm(self):
        self.assertSetEqual(self.mmd.api.rpms, set())
        self.mmd.api.add_rpm("test")
        self.assertSetEqual(self.mmd.api.rpms, set(["test"]))

    def test_api_del_rpm(self):
        self.mmd.api.rpms = set(["test"])
        self.mmd.api.del_rpm("test")
        self.assertSetEqual(self.mmd.api.rpms, set())

    def test_api_clear_rpms(self):
        self.mmd.api.rpms = set(["test"])
        self.mmd.api.clear_rpms()
        self.assertSetEqual(self.mmd.api.rpms, set())

    def test_filter_add_rpm(self):
        self.assertSetEqual(self.mmd.filter.rpms, set())
        self.mmd.filter.add_rpm("test")
        self.assertSetEqual(self.mmd.filter.rpms, set(["test"]))

    def test_filter_del_rpm(self):
        self.mmd.filter.rpms = set(["test"])
        self.mmd.filter.del_rpm("test")
        self.assertSetEqual(self.mmd.filter.rpms, set())

    def test_filter_clear_rpms(self):
        self.mmd.filter.rpms = set(["test"])
        self.mmd.filter.clear_rpms()
        self.assertSetEqual(self.mmd.filter.rpms, set())

    def test_profile_add_rpm(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.assertSetEqual(self.mmd.profiles["test"].rpms, set())
        self.mmd.profiles["test"].add_rpm("test")
        self.assertSetEqual(self.mmd.profiles["test"].rpms, set(["test"]))

    def test_profile_del_rpm(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.mmd.profiles["test"].rpms = set(["test"])
        self.mmd.profiles["test"].del_rpm("test")
        self.assertSetEqual(self.mmd.profiles["test"].rpms, set())

    def test_profile_clear_rpms(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.mmd.profiles["test"].rpms = set(["test"])
        self.mmd.profiles["test"].clear_rpms()
        self.assertSetEqual(self.mmd.profiles["test"].rpms, set())

    def test_components_all(self):
        rpm = ModuleComponentRPM("rpm", "rationale")
        mod = ModuleComponentModule("mod", "rationale")
        self.mmd.components.rpms = { rpm.name : rpm }
        self.mmd.components.modules = { mod.name : mod }
        # XXX: It'd be nice if we could order these
        self.assertListEqual(self.mmd.components.all, [rpm, mod])

    def test_components_add_rpm(self):
        self.assertDictEqual(self.mmd.components.rpms, dict())
        self.mmd.components.add_rpm("rpm", "rationale", buildorder=1,
                repository="repository", ref="ref", cache="cache",
                arches=set(["a1", "a2"]), multilib=set(["m1", "m2"]))
        self.assertEqual(list(self.mmd.components.rpms.keys()), ["rpm"])
        self.assertIsInstance(self.mmd.components.rpms["rpm"],
                ModuleComponentRPM)
        self.assertEqual(self.mmd.components.rpms["rpm"].name, "rpm")
        self.assertEqual(self.mmd.components.rpms["rpm"].rationale, "rationale")
        self.assertEqual(self.mmd.components.rpms["rpm"].buildorder, 1)
        self.assertEqual(self.mmd.components.rpms["rpm"].repository, "repository")
        self.assertEqual(self.mmd.components.rpms["rpm"].ref, "ref")
        self.assertEqual(self.mmd.components.rpms["rpm"].cache, "cache")
        self.assertSetEqual(self.mmd.components.rpms["rpm"].arches,
                set(["a1", "a2"]))
        self.assertSetEqual(self.mmd.components.rpms["rpm"].multilib,
                set(["m1", "m2"]))

    def test_components_del_rpm(self):
        self.mmd.components.rpms = {
                "rpm" : ModuleComponentRPM("rpm", "rationale")
                }
        self.mmd.components.del_rpm("rpm")
        self.assertDictEqual(self.mmd.components.rpms, dict())

    def test_components_clear_rpms(self):
        self.mmd.components.rpms = {
                "rpm" : ModuleComponentRPM("rpm", "rationale")
                }
        self.mmd.components.clear_rpms()
        self.assertDictEqual(self.mmd.components.rpms, dict())

    def test_components_add_module(self):
        self.assertDictEqual(self.mmd.components.modules, dict())
        self.mmd.components.add_module("module", "rationale", buildorder=1,
                repository="repository", ref="ref")
        self.assertEqual(list(self.mmd.components.modules.keys()), ["module"])
        self.assertIsInstance(self.mmd.components.modules["module"],
                ModuleComponentModule)
        self.assertEqual(self.mmd.components.modules["module"].name, "module")
        self.assertEqual(self.mmd.components.modules["module"].rationale, "rationale")
        self.assertEqual(self.mmd.components.modules["module"].buildorder, 1)
        self.assertEqual(self.mmd.components.modules["module"].repository, "repository")
        self.assertEqual(self.mmd.components.modules["module"].ref, "ref")

    def test_components_del_module(self):
        self.mmd.components.modules = {
                "module" : ModuleComponentModule("module", "rationale")
                }
        self.mmd.components.del_module("module")
        self.assertDictEqual(self.mmd.components.modules, dict())

    def test_components_clear_modules(self):
        self.mmd.components.modules = {
                "module" : ModuleComponentModule("module", "rationale")
                }
        self.mmd.components.clear_modules()
        self.assertDictEqual(self.mmd.components.modules, dict())

    def test_artifacts_add_rpm(self):
        self.assertSetEqual(self.mmd.artifacts.rpms, set())
        self.mmd.artifacts.add_rpm("test")
        self.assertSetEqual(self.mmd.artifacts.rpms, set(["test"]))

    def test_artifacts_del_rpm(self):
        self.mmd.artifacts.rpms = set(["test"])
        self.mmd.artifacts.del_rpm("test")
        self.assertSetEqual(self.mmd.artifacts.rpms, set())

    def test_artifacts_clear_rpms(self):
        self.mmd.artifacts.rpms = set(["test"])
        self.mmd.artifacts.clear_rpms()
        self.assertSetEqual(self.mmd.artifacts.rpms, set())
