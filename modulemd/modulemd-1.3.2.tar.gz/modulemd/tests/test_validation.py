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
from modulemd import supported_mdversions
from modulemd.profile import ModuleProfile
from modulemd.components.base import ModuleComponentBase
from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM

class TestValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mmd = ModuleMetadata()

    def test_mdversion_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "mdversion", "")

    def test_mdversion_value(self):
        self.assertRaises(ValueError, setattr, self.mmd, "mdversion", -1)

    def test_name_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "name", 0)

    def test_stream_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "stream", 0)

    def test_version_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "version", "")

    def test_version_value(self):
        self.assertRaises(ValueError, setattr, self.mmd, "version", -1)

    def test_context_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "context", 0)

    def test_arch_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "arch", 0)

    def test_summary_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "summary", 0)

    def test_description_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "description", 0)

    def test_eol_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "eol", 0)

    def test_module_license_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "module_licenses", 0)

    def test_module_license_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd, "module_licenses",
                set([1, 2, 3]))

    def test_content_license_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "content_licenses", 0)

    def test_content_license_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd, "content_licenses",
                set([1, 2, 3]))

    def test_xmd_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "xmd", 0)

    def test_buildrequires_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "buildrequires", 0)

    def test_buildrequires_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd, "buildrequires",
                { "key" : 0 } )
        self.assertRaises(TypeError, setattr, self.mmd, "buildrequires",
                { 0 : "value" } )
        self.assertRaises(TypeError, setattr, self.mmd, "buildrequires",
                { 0 : 0 } )

    def test_requires_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "requires", 0)

    def test_requires_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd, "requires",
                { "key" : 0 } )
        self.assertRaises(TypeError, setattr, self.mmd, "requires",
                { 0 : "value" } )
        self.assertRaises(TypeError, setattr, self.mmd, "requires",
                { 0 : 0 } )

    def test_community_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "community", 0)

    def test_documentation_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "documentation", 0)

    def test_tracker_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "tracker", 0)

    def test_profiles_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "profiles", 0)

    def test_profiles_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd, "profiles",
                { "key" : 0 } )
        self.assertRaises(TypeError, setattr, self.mmd, "profiles",
                { 0 : ModuleProfile() } )
        self.assertRaises(TypeError, setattr, self.mmd, "profiles",
                { 0 : 0 } )

    def test_profile_description_type(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.assertRaises(TypeError, setattr, self.mmd.profiles["test"],
                "description", 0)

    def test_profile_rpms_type(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.assertRaises(TypeError, setattr, self.mmd.profiles["test"],
                "rpms", 0)

    def test_profile_rpms_type_deep(self):
        self.mmd.profiles = { "test" : ModuleProfile() }
        self.assertRaises(TypeError, setattr, self.mmd.profiles["test"],
                "rpms", set([1, 2, 3]))

    def test_api_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "api", 0)

    def test_api_rpms_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.api, "rpms", 0)

    def test_api_rpms_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd.api, "rpms",
                set([1, 2, 3]))

    def test_filter_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "filter", 0)

    def test_filter_rpms_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.filter, "rpms", 0)

    def test_filter_rpms_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd.filter, "rpms",
                set([1, 2, 3]))

    def test_components_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "components", 0)

    def test_components_rpms_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.components, "rpms", 0)

    def test_components_rpms_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd.components, "rpms",
                { "key" : 0 } )
        self.assertRaises(TypeError, setattr, self.mmd.components, "rpms",
                { 0 : ModuleComponentRPM("name", "rationale") } )
        self.assertRaises(TypeError, setattr, self.mmd.components, "rpms",
                { 0 : 0 } )

    def test_components_modules_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.components, "modules", 0)

    def test_components_modules_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd.components, "modules",
                { "key" : 0 } )
        self.assertRaises(TypeError, setattr, self.mmd.components, "modules",
                { 0 : ModuleComponentModule("name", "rationale") } )
        self.assertRaises(TypeError, setattr, self.mmd.components, "rpms",
                { 0 : 0 } )

    def test_component_base_name_type(self):
        c = ModuleComponentBase("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "name", 0)

    def test_component_base_rationale_type(self):
        c = ModuleComponentBase("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "rationale", 0)

    def test_component_base_buildorder_type(self):
        c = ModuleComponentBase("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "buildorder", "")

    def test_component_rpm_name_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "name", 0)

    def test_component_rpm_rationale_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "rationale", 0)

    def test_component_rpm_buildorder_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "buildorder", "")

    def test_component_rpm_repository_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "repository", 0)

    def test_component_rpm_ref_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "ref", 0)

    def test_component_rpm_cache_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "cache", 0)

    def test_component_rpm_arches_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "arches", 0)

    def test_component_rpm_arches_type_deep(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "arches", set([1, 2, 3]))

    def test_component_rpm_multilib_type(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "multilib", 0)

    def test_component_rpm_multilib_type_deep(self):
        c = ModuleComponentRPM("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "multilib", set([1, 2, 3]))

    def test_component_module_name_type(self):
        c = ModuleComponentModule("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "name", 0)

    def test_component_module_rationale_type(self):
        c = ModuleComponentModule("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "rationale", 0)

    def test_component_module_buildorder_type(self):
        c = ModuleComponentModule("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "buildorder", "")

    def test_component_module_repository_type(self):
        c = ModuleComponentModule("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "repository", 0)

    def test_component_module_ref_type(self):
        c = ModuleComponentModule("name", "rationale")
        self.assertRaises(TypeError, setattr, c, "ref", 0)

    def test_artifacts_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "artifacts", 0)

    def test_artifacts_rpms_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.artifacts, "rpms", 0)

    def test_artifacts_rpms_type_deep(self):
        self.assertRaises(TypeError, setattr, self.mmd.artifacts, "rpms",
                set([1, 2, 3]))

    def test_buildopts_type(self):
        self.assertRaises(TypeError, setattr, self.mmd, "buildopts", 0);

    def test_buildopts_rpms_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.buildopts, "rpms", 0);

    def test_buildopts_rpms_macros_type(self):
        self.assertRaises(TypeError, setattr, self.mmd.buildopts.rpms,
                "macros", 0);
