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

"""Module metadata manipulation library.

A python library for manipulation of the proposed module metadata format.

Example usage:

.. code:: python

    import modulemd
    mmd = modulemd.ModuleMetadata()
    mmd.load("metadata.yaml")
    mmd.add_module_license("ISC")
    mmd.components.clear_rpms()
    mmd.components.add_rpm("example", "with reason", multilib=["x86_64"])
    mmd.dump("out.yaml")
"""

import sys
import datetime
import dateutil.parser
import yaml

if sys.version_info > (3,):
    long = int

from modulemd.api import ModuleAPI
from modulemd.artifacts import ModuleArtifacts
from modulemd.buildopts import ModuleBuildopts
from modulemd.buildopts.rpms import ModuleBuildoptsRPMs
from modulemd.components import ModuleComponents
from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM
from modulemd.filter import ModuleFilter
from modulemd.profile import ModuleProfile

supported_mdversions = ( 1, )

def load_all(f):
    """Loads a metadata file containing multiple modulemd documents
    into a list of ModuleMetadata instances.

    :param str f: File name to load
    """
    with open(f, "r") as infile:
        data = infile.read()
    return loads_all(data)

def loads_all(s):
    """Loads multiple modulemd documents from a YAML multidocument
    string.

    :param str s: String containing multiple YAML documents.
    """
    l = list()
    for doc in yaml.safe_load_all(s):
        m = ModuleMetadata()
        m.loadd(doc)
        l.append(m)
    return l

def dump_all(f, l):
    """Dumps a list of ModuleMetadata instances into a file.

    :param str f: Output filename
    :param list l: List of ModuleMetadata instances
    """
    with open(f, "w") as outfile:
        outfile.write(dumps_all(l))

def dumps_all(l):
    """Dumps a list of ModuleMetadata instance into a YAML multidocument
    string.

    :param list l: List of ModuleMetadata instances
    """
    return yaml.dump_all([x.dumpd() for x in l], explicit_start=True)

class ModuleMetadata(object):
    """Class representing the whole module."""

    REPODATA_FILENAME = "modulemd"

    def __init__(self):
        """Creates a new ModuleMetadata instance."""
        self.mdversion = max(supported_mdversions)
        self.name = ""
        self.stream = ""
        self.version = 0
        self.context = ""
        self.arch = ""
        self.summary = ""
        self.description = ""
        self.eol = None
        self.module_licenses = set()
        self.content_licenses = set()
        self.buildrequires = dict()
        self.requires = dict()
        self.community = ""
        self.documentation = ""
        self.tracker = ""
        self.xmd = dict()
        self.profiles = dict()
        self.api = ModuleAPI()
        self.filter = ModuleFilter()
        self.buildopts = ModuleBuildopts()
        self.components = ModuleComponents()
        self.artifacts = ModuleArtifacts()

    def __repr__(self):
        return ("<ModuleMetadata: "
                "mdversion: {0}, "
                "name: {1}, "
                "stream: {2}, "
                "version: {3}, "
                "context: {4}, "
                "arch: {5}, "
                "summary: {6}, "
                "description: {7}, "
                "eol: {8}, "
                "module_licenses: {9}, "
                "content_licenses: {10}, "
                "buildrequires: {11}, "
                "requires: {12}, "
                "community: {13}, "
                "documentation: {14}, "
                "tracker: {15}, "
                "xmd: {16}, "
                "profiles: {17}, "
                "api: {18}, "
                "filter: {19}, "
                "components: {20}, "
                "artifacts: {21}>").format(
                        repr(self.mdversion),
                        repr(self.name),
                        repr(self.stream),
                        repr(self.version),
                        repr(self.context),
                        repr(self.arch),
                        repr(self.summary),
                        repr(self.description),
                        repr(self.eol),
                        repr(sorted(self.module_licenses)),
                        repr(sorted(self.content_licenses)),
                        repr(sorted(self.buildrequires)),
                        repr(sorted(self.requires)),
                        repr(self.community),
                        repr(self.documentation),
                        repr(self.tracker),
                        repr(sorted(self.xmd)),
                        repr(sorted(self.profiles)),
                        repr(self.api),
                        repr(self.filter),
                        repr(self.components),
                        repr(self.artifacts)
                )

    def load(self, f):
        """Loads a metadata file into the instance.

        :param str f: File name to load
        """
        with open(f, "r") as infile:
            data = infile.read()
        self.loads(data)

    def loads(self, s):
        """Loads metadata from a string.

        :param str s: Raw metadata in YAML
        """
        yamld = yaml.safe_load(s)
        self.loadd(yamld)

    def loadd(self, d):
        """Loads metadata from a dictionary.

        :param dict d: YAML metadata parsed into a dict
        :raises ValueError: If the metadata is invalid or unsupported.
        """
        # header
        if "document" not in d or d["document"] != "modulemd":
            raise ValueError("The supplied data isn't a valid modulemd document")
        if "version" not in d:
            raise ValueError("Document version is required")
        if d["version"] not in supported_mdversions:
            raise ValueError("The supplied metadata version isn't supported")
        self.mdversion = d["version"]
        if "data" not in d or not isinstance(d["data"], dict):
            raise ValueError("Data section missing or mangled")
        # data
        data = d["data"]
        if "name" in data:
            self.name = str(data["name"])
        if "stream" in data:
            self.stream = str(data["stream"])
        if "version" in data:
            self.version = int(data["version"])
        if "context" in data:
            self.context = str(data["context"])
        if "arch" in data:
            self.arch = str(data["arch"])
        if "summary" in data:
            self.summary = str(data["summary"])
        if "description" in data:
            self.description = str(data["description"])
        if "eol" in data:
            try:
                self.eol = dateutil.parser.parse(str(data["eol"])).date()
            except:
                self.eol = None
        if ("license" in data
                and isinstance(data["license"], dict)
                and "module" in data["license"]
                and data["license"]["module"]):
            self.module_licenses = set(data["license"]["module"])
        if ("license" in data
                and isinstance(data["license"], dict)
                and "content" in data["license"]):
            self.content_licenses = set(data["license"]["content"])
        if ("dependencies" in data
                and isinstance(data["dependencies"], dict)):
            if ("buildrequires" in data["dependencies"]
                    and isinstance(data["dependencies"]["buildrequires"], dict)):
                for n, s in data["dependencies"]["buildrequires"].items():
                    self.add_buildrequires(str(n), str(s))
            if ("requires" in data["dependencies"]
                    and isinstance(data["dependencies"]["requires"], dict)):
                for n, s in data["dependencies"]["requires"].items():
                    self.add_requires(str(n), str(s))
        if "references" in data and data["references"]:
            if "community" in data["references"]:
                self.community = data["references"]["community"]
            if "documentation" in data["references"]:
                self.documentation = data["references"]["documentation"]
            if "tracker" in data["references"]:
                self.tracker = data["references"]["tracker"]
        if "xmd" in data:
            self.xmd = data["xmd"]
        if ("profiles" in data
                and isinstance(data["profiles"], dict)):
            for profile in data["profiles"].keys():
                self.profiles[profile] = ModuleProfile()
                if "description" in data["profiles"][profile]:
                    self.profiles[profile].description = \
                        str(data["profiles"][profile]["description"])
                if "rpms" in data["profiles"][profile]:
                    self.profiles[profile].rpms = \
                        set(data["profiles"][profile]["rpms"])
        if ("api" in data
                and isinstance(data["api"], dict)):
            self.api = ModuleAPI()
            if ("rpms" in data["api"]
                    and isinstance(data["api"]["rpms"],list)):
                self.api.rpms = set(data["api"]["rpms"])
        if ("filter" in data
                and isinstance(data["filter"], dict)):
            self.filter = ModuleFilter()
            if ("rpms" in data["filter"]
                    and isinstance(data["filter"]["rpms"],list)):
                self.filter.rpms = set(data["filter"]["rpms"])
        if ("buildopts" in data
                and isinstance(data["buildopts"], dict)):
            self.buildopts = ModuleBuildopts()
            if ("rpms" in data["buildopts"]
                    and isinstance(data["buildopts"]["rpms"], dict)):
                self.buildopts.rpms = ModuleBuildoptsRPMs()
                if ("macros" in data["buildopts"]["rpms"]
                        and isinstance(data["buildopts"]["rpms"]["macros"], str)):
                    self.buildopts.rpms.macros = data["buildopts"]["rpms"]["macros"]
        if ("components" in data
                and isinstance(data["components"], dict)):
            self.components = ModuleComponents()
            if "rpms" in data["components"]:
                for p, e in data["components"]["rpms"].items():
                    extras = dict()
                    extras["rationale"] = e["rationale"]
                    if "buildorder" in e:
                        extras["buildorder"] = int(e["buildorder"])
                    if "repository" in e:
                        extras["repository"] = str(e["repository"])
                    if "cache" in e:
                        extras["cache"] = str(e["cache"])
                    if "ref" in e:
                        extras["ref"] = str(e["ref"])
                    if ("arches" in e
                            and isinstance(e["arches"], list)):
                        extras["arches"] = set(str(x) for x in e["arches"])
                    if ("multilib" in e
                            and isinstance(e["multilib"], list)):
                        extras["multilib"] = set(str(x) for x in e["multilib"])
                    self.components.add_rpm(p, **extras)
            if "modules" in data["components"]:
                for p, e in data["components"]["modules"].items():
                    extras = dict()
                    extras["rationale"] = e["rationale"]
                    if "buildorder" in e:
                        extras["buildorder"] = int(e["buildorder"])
                    if "repository" in e:
                        extras["repository"] = str(e["repository"])
                    if "ref" in e:
                        extras["ref"] = str(e["ref"])
                    self.components.add_module(p, **extras)
        if ("artifacts" in data
                and isinstance(data["artifacts"], dict)):
            self.artifacts = ModuleArtifacts()
            if ("rpms" in data["artifacts"]
                    and isinstance(data["artifacts"]["rpms"],list)):
                self.artifacts.rpms = set(data["artifacts"]["rpms"])

    def dump(self, f):
        """Dumps the metadata into the supplied file.

        :param str f: File name of the destination
        """
        data = self.dumps()
        with open(f, "w") as outfile:
            outfile.write(data)

    def dumpd(self):
        """Dumps the metadata into a dictionary.

        :rtype: dict
        """
        doc = dict()
        # header
        doc["document"] = "modulemd"
        doc["version"] = self.mdversion
        # data
        d = dict()
        if self.name:
            d["name"] = self.name
        if self.stream:
            d["stream"] = self.stream
        if self.version:
            d["version"] = self.version
        if self.context:
            d["context"] = self.context
        if self.arch:
            d["arch"] = self.arch
        d["summary"] = self.summary
        d["description"] = self.description
        if self.eol:
            d["eol"] = str(self.eol)
        d["license"] = dict()
        d["license"]["module"] = sorted(list(self.module_licenses))
        if self.content_licenses:
            d["license"]["content"] = sorted(list(self.content_licenses))
        if self.buildrequires or self.requires:
            d["dependencies"] = dict()
            if self.buildrequires:
                d["dependencies"]["buildrequires"] = self.buildrequires
            if self.requires:
                d["dependencies"]["requires"] = self.requires
        if self.community or self.documentation or self.tracker:
            d["references"] = dict()
            if self.community:
                d["references"]["community"] = self.community
            if self.documentation:
                d["references"]["documentation"] = self.documentation
            if self.tracker:
                d["references"]["tracker"] = self.tracker
        if self.xmd:
            d["xmd"] = self.xmd
        if self.profiles:
            d["profiles"] = dict()
            for profile in self.profiles.keys():
                if self.profiles[profile].description:
                    if profile not in d["profiles"]:
                        d["profiles"][profile] = dict()
                    d["profiles"][profile]["description"] = \
                        str(self.profiles[profile].description)
                if self.profiles[profile].rpms:
                    if profile not in d["profiles"]:
                        d["profiles"][profile] = dict()
                    d["profiles"][profile]["rpms"] = \
                        sorted(list(self.profiles[profile].rpms))
        if self.api:
            d["api"] = dict()
            if self.api.rpms:
                d["api"]["rpms"] = sorted(list(self.api.rpms))
        if self.filter:
            d["filter"] = dict()
            if self.filter.rpms:
                d["filter"]["rpms"] = sorted(list(self.filter.rpms))
        if self.buildopts:
            d["buildopts"] = dict()
            if self.buildopts.rpms:
                d["buildopts"]["rpms"] = dict()
                if self.buildopts.rpms.macros:
                    d["buildopts"]["rpms"]["macros"] = \
                            self.buildopts.rpms.macros
        if self.components:
            d["components"] = dict()
            if self.components.rpms:
                d["components"]["rpms"] = dict()
                for p in self.components.rpms.values():
                    extra = dict()
                    extra["rationale"] = p.rationale
                    if p.buildorder:
                        extra["buildorder"] = p.buildorder
                    if p.repository:
                        extra["repository"] = p.repository
                    if p.ref:
                        extra["ref"] = p.ref
                    if p.cache:
                        extra["cache"] = p.cache
                    if p.arches:
                        extra["arches"] = sorted(list(p.arches))
                    if p.multilib:
                        extra["multilib"] = sorted(list(p.multilib))
                    d["components"]["rpms"][p.name] = extra
            if self.components.modules:
                d["components"]["modules"] = dict()
                for p in self.components.modules.values():
                    extra = dict()
                    extra["rationale"] = p.rationale
                    if p.buildorder:
                        extra["buildorder"] = p.buildorder
                    if p.repository:
                        extra["repository"] = p.repository
                    if p.ref:
                        extra["ref"] = p.ref
                    d["components"]["modules"][p.name] = extra
        if self.artifacts:
            d["artifacts"] = dict()
            if self.artifacts.rpms:
                d["artifacts"]["rpms"] = sorted(list(self.artifacts.rpms))
        doc["data"] = d
        return doc

    def dumps(self):
        """Dumps the metadata into a string.

        :rtype: str
        """
        return yaml.safe_dump(self.dumpd(), default_flow_style=False)

    @property
    def mdversion(self):
        """An int property representing the metadata format version used.

        This is automatically set to the highest supported version for
        new objects or set by the loaded document.  This value can be
        changed to one of the supported_mdversions to alter the output
        format.
        """
        return self._mdversion

    @mdversion.setter
    def mdversion(self, i):
        if not isinstance(i, (int, long)):
            raise TypeError("mdversion: data type not supported")
        if i not in supported_mdversions:
            raise ValueError("mdversion: document version not supported")
        self._mdversion = int(i)

    @property
    def name(self):
        """A string property representing the name of the module."""
        return self._name

    @name.setter
    def name(self, s):
        if not isinstance(s, str):
            raise TypeError("name: data type not supported")
        self._name = s

    @property
    def stream(self):
        """A string property representing the stream name of the module."""
        return self._stream

    @stream.setter
    def stream(self, s):
        if not isinstance(s, str):
            raise TypeError("stream: data type not supported")
        self._stream = str(s)

    @property
    def version(self):
        """An integer property representing the version of the module."""
        return self._version

    @version.setter
    def version(self, i):
        if not isinstance(i, (int, long)):
            raise TypeError("version: data type not supported")
        if i < 0:
            raise ValueError("version: version cannot be negative")
        self._version = i

    @property
    def context(self):
        """A string property representing the context flag of the module."""
        return self._context

    @context.setter
    def context(self, s):
        if not isinstance(s, str):
            raise TypeError("context: data type not supported")
        self._context = s

    @property
    def arch(self):
        """A string property representing the module artifacts' hardware
        architecture compatibility.
        """
        return self._arch

    @arch.setter
    def arch(self, s):
        if not isinstance(s, str):
            raise TypeError("arch: data type not supported")
        self._arch = s

    @property
    def summary(self):
        """A string property representing a short summary of the module."""
        return self._summary

    @summary.setter
    def summary(self, s):
        if not isinstance(s, str):
            raise TypeError("summary: data type not supported")
        self._summary = s

    @property
    def description(self):
        """A string property representing a detailed description of the
        module."""
        return self._description

    @description.setter
    def description(self, s):
        if not isinstance(s, str):
            raise TypeError("description: data type not supported")
        self._description = s

    @property
    def eol(self):
        """A datetime.date property representing the module's EOL date.
        May be None if no EOL is defined."""
        return self._eol

    @eol.setter
    def eol(self, o):
        if not isinstance(o, datetime.date) and o is not None:
            raise TypeError("eol: data type not supported")
        self._eol = o

    @property
    def module_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module itself."""
        return self._module_licenses

    @module_licenses.setter
    def module_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("module_licenses: data type not supported")
        for s in ss:
            if not isinstance(s, str):
                raise TypeError("module_licenses: data type not supported")
        self._module_licenses = ss

    def add_module_license(self, s):
        """Adds a module license to the set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("add_module_license: data type not supported")
        self._module_licenses.add(s)

    def del_module_license(self, s):
        """Removes the supplied license from the module licenses set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("del_module_license: data type not supported")
        self._module_licenses.discard(s)

    def clear_module_licenses(self):
        """Clears the module licenses set."""
        self._module_licenses.clear()

    @property
    def content_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module contents."""
        return self._content_licenses

    @content_licenses.setter
    def content_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("content_licenses: data type not supported")
        for s in ss:
            if not isinstance(s, str):
                raise TypeError("content_licenses: data type not supported")
        self._content_licenses = ss

    def add_content_license(self, s):
        """Adds a content license to the set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("add_content_license: data type not supported")
        self._content_licenses.add(s)

    def del_content_license(self, s):
        """Removes the supplied license from the content licenses set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("del_content_license: data type not supported")
        self._content_licenses.discard(s)

    def clear_content_licenses(self):
        """Clears the content licenses set."""
        self._content_licenses.clear()

    @property
    def requires(self):
        """A dictionary property representing the required dependencies of
        the module.

        Keys are the required module names (strings), values are their
        required stream names (also strings).
        """
        return self._requires

    @requires.setter
    def requires(self, d):
        if not isinstance(d, dict):
            raise TypeError("requires: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("requires: data type not supported")
        self._requires = d

    def add_requires(self, n, v):
        """Adds a required module dependency.

        :param str n: Required module name
        :param str v: Required module stream name
        """
        if not isinstance(n, str) or not isinstance(v, str):
            raise TypeError("add_requires: data type not supported")
        self._requires[n] = v

    update_requires = add_requires

    def del_requires(self, n):
        """Deletes the dependency on the supplied module.

        :param str n: Required module name
        """
        if not isinstance(n, str):
            raise TypeError("del_requires: data type not supported")
        if n in self._requires:
            del self._requires[n]

    def clear_requires(self):
        """Removes all required runtime dependencies."""
        self._requires.clear()

    @property
    def buildrequires(self):
        """A dictionary property representing the required build dependencies
        of the module.

        Keys are the required module names (strings), values are their
        required stream names (also strings).
        """
        return self._buildrequires

    @buildrequires.setter
    def buildrequires(self, d):
        if not isinstance(d, dict):
            raise TypeError("buildrequires: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("buildrequires: data type not supported")
        self._buildrequires = d

    def add_buildrequires(self, n, v):
        """Adds a module build dependency.

        :param str n: Required module name
        :param str v: Required module stream name
        """
        if not isinstance(n, str) or not isinstance(v, str):
            raise TypeError("add_buildrequires: data type not supported")
        self._buildrequires[n] = v

    update_buildrequires = add_buildrequires

    def del_buildrequires(self, n):
        """Deletes the build dependency on the supplied module.

        :param str n: Required module name
        """
        if not isinstance(n, str):
            raise TypeError("del_buildrequires: data type not supported")
        if n in self._buildrequires:
            del self._buildrequires[n]

    def clear_buildrequires(self):
        """Removes all build dependencies."""
        self._buildrequires.clear()

    @property
    def community(self):
        """A string property representing a link to the upstream community
        for this module.
        """
        return self._community

    @community.setter
    def community(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("community: data type not supported")
        self._community = s

    @property
    def documentation(self):
        """A string property representing a link to the upstream
        documentation for this module.
        """
        return self._documentation

    @documentation.setter
    def documentation(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("documentation: data type not supported")
        self._documentation = s

    @property
    def tracker(self):
        """A string property representing a link to the upstream bug tracker
        for this module.
        """
        return self._tracker

    @tracker.setter
    def tracker(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("tracker: data type not supported")
        self._tracker = s

    @property
    def xmd(self):
        """A dictionary property containing user-defined data."""
        return self._xmd

    @xmd.setter
    def xmd(self, d):
        if not isinstance(d, dict):
            raise TypeError("xmd: data type not supported")
        self._xmd = d

    @property
    def profiles(self):
        """A dictionary property representing the module profiles."""
        return self._profiles

    @profiles.setter
    def profiles(self, d):
        if not isinstance(d, dict):
            raise TypeError("profiles: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, ModuleProfile):
                raise TypeError("profiles: data type not supported")
        self._profiles = d

    @property
    def api(self):
        """A ModuleAPI instance representing the module's public API."""
        return self._api

    @api.setter
    def api(self, o):
        if not isinstance(o, ModuleAPI):
            raise TypeError("api: data type not supported")
        self._api = o

    @property
    def filter(self):
        """A ModuleFilter instance representing the module's filter."""
        return self._filter

    @filter.setter
    def filter(self, o):
        if not isinstance(o, ModuleFilter):
            raise TypeError("filter: data type not supported")
        self._filter = o

    @property
    def buildopts(self):
        """A ModuleBuildopts instance representing the additional
        module components build options.
        """
        return self._buildopts

    @buildopts.setter
    def buildopts(self, o):
        if not isinstance(o, ModuleBuildopts):
            raise TypeError("buildopts: data type not supported")
        self._buildopts = o

    @property
    def components(self):
        """A ModuleComponents instance property representing the components
        defining the module.
        """
        return self._components

    @components.setter
    def components(self, o):
        if not isinstance(o, ModuleComponents):
            raise TypeError("components: data type not supported")
        self._components = o

    @property
    def artifacts(self):
        """A ModuleArtifacts instance representing the module's artifacts."""
        return self._artifacts

    @artifacts.setter
    def artifacts(self, o):
        if not isinstance(o, ModuleArtifacts):
            raise TypeError("artifacts: data type not supported")
        self._artifacts = o
