# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

import nose.tools as nt

import fastr
from fastr.core.tool import Tool
from fastr.utils.dicteq import diffdict
from fastr.core.version import Version
from fastr.utils.dicteq import diffobj_str


class TestTool():

    def setup(self):
        self.addint = fastr.toollist['AddInt']
        self.addimages = fastr.toollist['Sum']
        self.addint_copy = copy.deepcopy(self.addint)
        self.addimages_copy = copy.deepcopy(self.addimages)

    def test_tool_eq_operator(self):
        nt.eq_(self.addint, self.addint, msg=diffobj_str(self.addint, self.addint))
        nt.eq_(self.addint, self.addint_copy, msg=diffobj_str(self.addint, self.addint_copy))
        nt.eq_(self.addimages, self.addimages_copy, msg=diffobj_str(self.addimages, self.addimages_copy))
        assert self.addint != self.addimages
        assert self.addint_copy != self.addimages

    def test_tool_getstate_setstate(self):
        #  Dump state and rebuild in a clean object
        addint_state = self.addint.__getstate__()
        addint_rebuilt = Tool.__new__(Tool)
        addint_rebuilt.__setstate__(addint_state)
        nt.eq_(self.addint, addint_rebuilt)

        #  Dump state and rebuild in a clean object
        addimages_state = self.addimages.__getstate__()
        addimages_rebuilt = Tool.__new__(Tool)
        addimages_rebuilt.__setstate__(addimages_state)
        nt.eq_(self.addimages, addimages_rebuilt)

    def test_tool_serializing(self):
        addint_json = self.addint.dumps()
        addint_rebuilt = Tool.loads(addint_json)
        nt.eq_(self.addint, addint_rebuilt, msg='Differences:\n{}'.format('\n'.join(diffdict(self.addint.__dict__, addint_rebuilt.__dict__))))

    def test_toolversions(self):
        toolname = 'Source'
        tool = fastr.toollist[toolname]
        version = Version("1.0")
        nt.eq_(fastr.toollist.toolversions(tool)[0], version)
        nt.eq_(fastr.toollist.toolversions(toolname)[0], version)
        nt.eq_(len(fastr.toollist.toolversions(toolname)), 1, msg="Excpected number of versions for tool {} is 1 not {}.".format(toolname, len(fastr.toollist.toolversions(toolname))))
        # Maybe a unique id should be used here, but I think it very unlikely that this toolname will be encountered.
        nt.eq_(fastr.toollist.toolversions('097G)(A&*BD)(A7vA)(F67vAD)F967vAF-67vAD)F(86vAFD096vAF)97v'), None)
        assert isinstance(fastr.toollist.toolversions(tool), list), "%r is not of list type" % fastr.toollist.toolversions(tool)
