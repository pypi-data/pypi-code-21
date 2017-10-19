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

import nose.tools as nt

import fastr
from fastr.core.network import Network
from fastr.utils.dicteq import diffobj_str


class TestNetwork():

    def setup(self):
        self.populated_network = fastr.Network('populated_network')

        self.source_node1 = fastr.SourceNode('Int', 'source', parent=self.populated_network)
        self.constant_node = fastr.ConstantNode('Int', (42, 7, 1337), 'constant', parent=self.populated_network)

        self.addint = fastr.Node(fastr.toollist['AddInt'], 'testnode_addint', parent=self.populated_network)
        self.div_link = self.populated_network.create_link(self.constant_node.output,
                                                           self.addint.inputs['left_hand'])
        self.div_link.expand = True
        self.addint.inputs['right_hand'] = self.source_node1.output

        self.sink_node = fastr.SinkNode('Int', 'sink', self.populated_network)
        self.sink_node.inputs['input'] = self.addint.outputs['result']

        self.empty_network = fastr.Network('empty_network')

    def test_network_eq_operator(self):
        nt.eq_(self.populated_network, self.populated_network)
        nt.eq_(self.empty_network, self.empty_network)
        nt.ok_(self.populated_network != self.empty_network)

    def test_network_getstate_setstate(self):
        #  Dump state and rebuild in a clean object
        empty_state = self.empty_network.__getstate__()
        empty_rebuilt = Network.__new__(Network)
        empty_rebuilt.__setstate__(empty_state)
        nt.eq_(self.empty_network, empty_rebuilt, msg=diffobj_str(self.empty_network, empty_rebuilt))

        #  Dump state and rebuild in a clean object
        populated_state = self.populated_network.__getstate__()
        populated_rebuilt = Network.__new__(Network)
        populated_rebuilt.__setstate__(populated_state)
        nt.eq_(self.populated_network, populated_rebuilt, msg=diffobj_str(self.populated_network, populated_rebuilt))

    def test_network_serializing(self):
        empty_json = self.empty_network.dumps()
        empty_rebuilt = Network.loads(empty_json)
        nt.eq_(self.empty_network, empty_rebuilt, msg=diffobj_str(self.empty_network, empty_rebuilt))

        populated_json = self.populated_network.dumps()
        populated_rebuilt = Network.loads(populated_json)
        nt.eq_(self.populated_network, populated_rebuilt, msg=diffobj_str(self.populated_network, populated_rebuilt))

        nt.ok_(populated_rebuilt, empty_rebuilt)
        nt.ok_(self.empty_network != populated_rebuilt)
        nt.ok_(self.populated_network != empty_rebuilt)


