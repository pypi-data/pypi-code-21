import unittest
import random

import networkx
from service import Adapter, NetworkElementBuilder

class TestNetworkxAdapter(unittest.TestCase):

    def testFromValue(self):
        builder = NetworkElementBuilder('test')
        typ, value = builder.from_value(1)
        self.assertEqual(typ, 'integer')
        self.assertEqual(value, '1')

        typ, value = builder.from_value(False)
        self.assertEqual(typ, 'boolean')
        self.assertEqual(value, 'False')

        typ, value = builder.from_value(1.5)
        self.assertEqual(typ, 'float')
        self.assertEqual(value, '1.5')

        typ, value = builder.from_value('H')
        self.assertEqual(typ, 'string')
        self.assertEqual(value, 'H')

        typ, value = builder.from_value({1: 2})
        self.assertEqual(typ, 'string')
        self.assertEqual(value, '{1: 2}')

    def test_from_networkx(self):
        net, edgeList = create_mock_networkx(num_nodes=100, num_edges=50)
        net.graph['desc'] = 'example'
        nodeCount = 0
        edgeCount = 0
        for aspect in Adapter.from_networkx([net]):
            which = aspect.WhichOneof('element')
            if which == 'node':
                nodeCount += 1
                node = aspect.node
                self.assertEqual(net.node[node.id]['name'], node.name)
            elif which == 'edge':
                edgeCount += 1
                edge = aspect.edge
                self.assertEqual(edge.id, net[edge.sourceId][edge.targetId]['id'])
            elif which == 'nodeAttribute':
                attr = aspect.nodeAttribute
                self.assertEqual(net[attr.nodeId][attr.name], attr.value)
            elif which == 'edgeAttribute':
                attr = aspect.edgeAttribute
                a, b = edgeList[attr.edgeId]
                self.assertEqual(str(net[a][b]['value']), attr.value)
            elif which == 'networkAttribute':
                attr = aspect.networkAttribute
                self.assertEqual(net.graph[attr.name], attr.value)
            else:
                print("UNTESTED %s" % aspect)
        self.assertEqual(nodeCount, len(net))
        self.assertEqual(edgeCount, net.size())

    def testToNetworkX(self):
        net, edgeList = create_mock_networkx(num_nodes=100, num_edges=50,
                data={'keyStr': 'value',
                'keyInt': 1,
                'keyFloat': 1.2,
                'keyBool': True})

        stream = Adapter.from_networkx([net])
        net_res_list = Adapter.to_networkx(stream)
        compare_networkx(net, net_res_list[0])
        self.assertEqual(net.graph, net_res_list[0].graph)

    def testUnusualAttributeType(self):
        net, edgeList = create_mock_networkx(num_nodes=100, num_edges=50, data={'keyDict': {1: 2}})
        stream = Adapter.from_networkx([net])
        net_res_list = Adapter.to_networkx(stream)
        compare_networkx(net, net_res_list[0])
        # autoconvert to string for unrecognized value types
        self.assertEqual(str(net.graph['keyDict']), net_res_list[0].graph['keyDict'])

    def testLargeNetwork(self):
        net, edgeList = create_mock_networkx(num_nodes=10000, num_edges=5000)
        stream = Adapter.from_networkx([net])
        net_res_list = Adapter.to_networkx(stream)
        compare_networkx(net, net_res_list[0])

    def testMultipleNetworks(self):
        nets = [create_mock_networkx('net1')[0], create_mock_networkx('net2')[0]]
        streams = Adapter.from_networkx(nets)
        res_nets = Adapter.to_networkx(streams)
        compare_networkx(nets[0], res_nets[0])
        compare_networkx(nets[1], res_nets[1])

def compare_networkx(net1, net2):
    for a, b in net1.edges():
        val = net2.edge[a][b]['value']
        assert val == net1.edge[a][b]['value'], "Edge attribute incorrect. %s != %s" % (val, net1.edge[a][b]['value'])
    for ID, attrs in net1.nodes(data=True):
        assert attrs['name'] == net2.node[ID]['name'], "Node name incorrect. %s != %s" % (attr['name'], net2.node[ID]['name'])
    net1_graph = {k: (v if type(v) in (float, str, int, bool) else str(v)) for k, v in net1.graph.items()}
    assert net1_graph == net2.graph, "Network attributes do not match. %s != %s" % (net1.graph, net2.graph)
    return True

def create_mock_networkx(label='network_label', num_nodes=100, num_edges=100, data={}):
    edgeList = {}
    n = networkx.Graph()
    n.graph['label'] = label
    for n_id in range(num_nodes):
        n.add_node(n_id, name=hex(n_id))
    ID = num_nodes
    for e_id in range(num_edges):
        n1 = random.randint(0, num_nodes-1)
        n2 = random.randint(0, num_nodes-2)
        val = random.choice([1, 1.5, 'a', True])
        edgeList[ID] = (n1, n2)
        n.add_edge(n1, n2, id=ID, value=val)
        ID += 1
    for k, v in data.items():
        n.graph[k] = v
    return n, edgeList

if __name__ == '__main__':
    unittest.main()
