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
from fastr.core.node import Node, SourceNode, SinkNode, ConstantNode
from fastr.utils.dicteq import diffobj_str


class TestNode():

    def setup(self):
        self.source_network = fastr.Network('source_network')
        self.addint = fastr.Node(fastr.toollist['AddInt'], 'testnode_addint', parent=self.source_network)
        self.sum = fastr.Node(fastr.toollist['Sum'], 'testnode_addimages', parent=self.source_network)
        self.source_node = fastr.SourceNode('Int', 'source', parent=self.source_network)
        self.source_node2 = fastr.SourceNode('Int', 'source2', parent=self.source_network)
        self.sink_node = fastr.SinkNode('Int', 'sink', parent=self.source_network)
        self.sink_node2 = fastr.SinkNode('Int', 'sink2', parent=self.source_network)
        self.constant_node = fastr.ConstantNode('Int', [42], 'constant', parent=self.source_network)
        self.constant_node2 = fastr.ConstantNode('Int', [42], 'constant2', parent=self.source_network)

        fastr.log.info('Target network')
        self.target_network = fastr.Network('target_network')
        fastr.log.info('Created')

    def test_node_eq_operator(self):
        nt.eq_(self.addint, self.addint)
        nt.eq_(self.sum, self.sum)
        nt.ok_(self.addint != self.sum)
        nt.ok_(self.sum != self.addint)

    def test_sourcenode_eq_operator(self):
        nt.eq_(self.source_node, self.source_node)
        nt.eq_(self.source_node2, self.source_node2)
        nt.ok_(self.source_node != self.source_node2)
        nt.ok_(self.source_node2 != self.source_node)

    def test_constantnode_eq_operator(self):
        nt.eq_(self.constant_node, self.constant_node)
        nt.eq_(self.constant_node2, self.constant_node2)
        nt.ok_(self.constant_node != self.constant_node2)
        nt.ok_(self.constant_node2 != self.constant_node)

    def test_sinknode_eq_operator(self):
        nt.eq_(self.sink_node, self.sink_node)
        nt.eq_(self.sink_node2, self.sink_node2)
        nt.ok_(self.sink_node != self.sink_node2)
        nt.ok_(self.sink_node2 != self.sink_node)

    def test_node_getstate_setstate(self):
        #  Dump state and rebuild in a clean object
        addint_state = self.addint.__getstate__()
        addint_state['parent'] = self.target_network
        addint_rebuilt = Node.__new__(Node)
        addint_rebuilt.__setstate__(addint_state)
        nt.eq_(self.addint, addint_rebuilt, msg=diffobj_str(self.addint, addint_rebuilt))

        #  Dump state and rebuild in a clean object
        addimages_state = self.sum.__getstate__()
        addimages_state['parent'] = self.target_network
        addimages_rebuilt = Node.__new__(Node)
        addimages_rebuilt.__setstate__(addimages_state)
        nt.eq_(self.sum, addimages_rebuilt, msg=diffobj_str(self.sum, addimages_rebuilt))

    def test_node_serializing(self):
        addint_json = self.addint.dumps()
        addimages_json = self.sum.dumps()
        addint_rebuilt = Node.loads(addint_json, network=self.target_network)
        addimages_rebuilt = Node.loads(addimages_json, network=self.target_network)
        nt.eq_(self.addint, addint_rebuilt, msg=diffobj_str(self.addint, addint_rebuilt))
        nt.eq_(self.sum, addimages_rebuilt, msg=diffobj_str(self.sum, addimages_rebuilt))
        nt.ok_(self.sum != addint_rebuilt)
        nt.ok_(self.addint != addimages_rebuilt)
        nt.ok_(addint_rebuilt != addimages_rebuilt)

    def test_source_node_serializing(self):
        source_json = self.source_node.dumps()
        fastr.log.info('JSON: {}'.format(source_json))
        source_rebuilt = SourceNode.loads(source_json, network=self.target_network)
        nt.eq_(self.source_node, source_rebuilt, msg=diffobj_str(self.source_node, source_rebuilt))

    def test_sink_node_serializing(self):
        sink_json = self.sink_node.dumps()
        fastr.log.info('JSON: {}'.format(sink_json))
        sink_rebuilt = SinkNode.loads(sink_json, network=self.target_network)
        nt.eq_(self.sink_node, sink_rebuilt, msg=diffobj_str(self.sink_node, sink_rebuilt))

    def test_constant_node_serializing(self):
        constant_json = self.constant_node.dumps()
        fastr.log.info('JSON: {}'.format(constant_json))
        constant_rebuilt = ConstantNode.loads(constant_json, network=self.target_network)
        nt.eq_(self.constant_node, constant_rebuilt, msg=diffobj_str(self.constant_node, constant_rebuilt))
