import time
import itertools
import logging
import sys
import uuid
from  concurrent.futures import ThreadPoolExecutor

import networkx
import grpc

from . import cxmate_pb2
from . import cxmate_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ServiceServicer(cxmate_pb2_grpc.cxMateServiceServicer):
    """
    CyServiceServicer is an implementation of a grpc service definiton to process CX streams
    """

    def __init__(self, logger, process):
        """
        Construct a new 'CyServiceServicer' grpc service object

        :param process: A function that handles processing a call to the service
        """
        self.logger = logger
        self.process = process

    def StreamNetworks(self, input_stream, context):
        """
        A generator function called by grpc. Will catch all exceptions to protect
        the service

        :param element_iter: An iterator yielding CX protobuf objects
        :param context: A grpc context object with request metadata
        :returns: Must generate CX protobuf objects
        """
        id = str(uuid.uuid4())
        self.logger.info("StreamNetworks invoked for " + id)
        self.logger.info("processing parameters for " + id)
        params, input_stream = self.process_parameters(input_stream, id)
        self.logger.info("calling service handler for " + id)
        output_stream = self.process(params, input_stream)
        self.logger.info("iterating output stream for " + id)
        for element in output_stream:
            yield element

    def process_parameters(self, ele_iter, id):
        params = {}
        for ele in ele_iter:
            if ele.WhichOneof('element') == 'parameter':
                param = ele.parameter
                val = None
                val_type = param.WhichOneof('value')
                if val_type == 'numberValue':
                    val = param.numberValue
                elif val_type == 'booleanValue':
                    val = param.booleanValue
                elif val_type == 'integerValue':
                    val = param.integerValue
                else:
                    val = param.stringValue
                if param.name == 'request_id':
                    logging.info('request ' + id + ' has a tracing id of ' + val)
                params[param.name] = val
            else:
                return params, itertools.chain([ele], ele_iter)


class Adapter:
    """
    Static methods to convert popular network formats to and from CX stream iterators
    """
  
    @staticmethod
    def to_networkx(ele_iter):
        """
        Creates a list of networkx objects by read network elements from ele_iter

        :param ele_iter: A CX element generator
        :returns: A list of networkx objects
        """
        networks = []
        while ele_iter:
            network, ele_iter = Adapter.read_networkx(ele_iter)
            networks.append(network)
        return networks

    @staticmethod
    def read_networkx(ele_iter):
        network = networkx.Graph()
        attrs = []
        edges = {}
        for ele in ele_iter:
            if not 'label' in network.graph:
                network.graph['label'] = ele.label
            if ele.label != network.graph['label']:
                return network, itertools.chain([ele], ele_iter)
            ele_type = ele.WhichOneof('element')
            if ele_type == 'node':
                node = ele.node
                network.add_node(int(node.id), name=node.name)
            elif ele_type == 'edge':
                edge = ele.edge
                src, tgt = int(edge.sourceId), int(edge.targetId)
                edges[int(edge.id)] = (src, tgt)
                network.add_edge(src, tgt, id=int(edge.id), interaction=edge.interaction)
            elif ele_type == 'nodeAttribute':
                attr = ele.nodeAttribute
                network.add_node(attr.nodeId, **{attr.name: Adapter.parse_value(attr)})
            elif ele_type == 'edgeAttribute':
                attr = ele.edgeAttribute
                attrs.append(attr)
            elif ele_type == 'networkAttribute':
                attr = ele.networkAttribute
                network.graph[attr.name] = Adapter.parse_value(attr)
            for attr in attrs:
                source, target = edges[int(attr.edgeId)]
                network[source][target][attr.name] = Adapter.parse_value(attr)
        return network, None

    @staticmethod
    def parse_value(attr):
        value = attr.value
        if attr.type:
            if attr.type in ('boolean'):
                value = value.lower() in ('true')
            elif attr.type in ('double', 'float'):
                value = float(value)
            elif attr.type in ('integer', 'short', 'long'):
                value = int(value)
        return value

    @staticmethod
    def from_networkx(networks):
        """
        Creates a CX element generator from a list of networkx objects

        :param networks: A list of networkx objects
        :returns: A CX element generator
        """
        for networkx in networks:
            builder = NetworkElementBuilder(networkx.graph['label'])

            for nodeId, attrs in networkx.nodes(data=True):
                yield builder.Node(nodeId, attrs.get('name', ''))

                for k, v in attrs.items():
                    if k not in ('name'):
                        yield builder.NodeAttribute(nodeId, k, v)

            for sourceId, targetId, attrs in networkx.edges(data=True):
                yield builder.Edge(attrs['id'], sourceId, targetId, attrs.get('interaction', ''))

                for k, v in attrs.items():
                    if k not in ('interaction', 'id'):
                        yield builder.EdgeAttribute(attrs['id'], k, v)

            for key, value in networkx.graph.items():
                yield builder.NetworkAttribute(key, value)

    @staticmethod
    def to_JSON(ele_iter):
        pass

    @staticmethod
    def from_JSON(label, json):
        yield NetworkElementBuilder(label).Json(json)


class NetworkElementBuilder():
    """
    Factory class for declaring the network element from networkx attributes
    """

    def __init__(self, label):
        self.label = label

    def Json(self, json):
        ele = self.new_element()
        ele.json = json
        return ele

    def Node(self, nodeId, name):
        ele = self.new_element()
        node = ele.node
        node.id = nodeId
        node.name = name
        return ele

    def Edge(self, edgeId, sourceId, targetId, interaction):
        ele = self.new_element()
        edge = ele.edge
        edge.id = edgeId
        edge.sourceId = sourceId
        edge.targetId = targetId
        edge.interaction = interaction
        return ele

    def NodeAttribute(self, nodeId, key, value):
        ele = self.new_element()
        nodeAttr = ele.nodeAttribute
        nodeAttr.nodeId = nodeId
        typ, value = self.from_value(value)
        nodeAttr.type = typ
        nodeAttr.name = key
        nodeAttr.value = value
        return ele

    def EdgeAttribute(self, edgeId, key, value):
        ele = self.new_element()
        edgeAttr = ele.edgeAttribute
        edgeAttr.edgeId = edgeId
        typ, value = self.from_value(value)
        edgeAttr.type = typ
        edgeAttr.name = key
        edgeAttr.value = value
        return ele

    def NetworkAttribute(self, key, value):
        ele = self.new_element()
        networkAttr = ele.networkAttribute
        networkAttr.name = key
        typ, value = self.from_value(value)
        networkAttr.type = typ
        networkAttr.value = value
        return ele

    def new_element(self):
        ele = cxmate_pb2.NetworkElement()
        ele.label = self.label
        return ele

    def from_value(self, value):
        if isinstance(value, bool):
            return 'boolean', str(value)
        elif isinstance(value, float):
            return 'float', str(value)
        elif isinstance(value, int):
            return 'integer', str(value)
        return 'string', str(value)


class Service:
    """
    A cxMate service
    """

    def process(self, input_stream):
        """
        Process handles a single cxMate request.

        :param input_stream: A stream iterator yielding CX protobuf objects
        :returns: A stream iterator yielding CX protobuf objects
        """
        raise NotImplementedError

    def run(self, listen_on = '0.0.0.0:8080', max_workers=10):
        """
        Run starts the service and then waits for a keyboard interupt

        :param str listen_on: The tcp address the service should listen on, 0.0.0.0:8080 by default
        :param int max_workers: The number of worker threads serving the service, 10 by default
        :returns: none
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        server = grpc.server(ThreadPoolExecutor(max_workers=max_workers))
        servicer = ServiceServicer(logger, self.process)
        cxmate_pb2_grpc.add_cxMateServiceServicer_to_server(servicer, server)
        server.add_insecure_port(listen_on)
        logger.info("starting service on " + listen_on)
        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            logging.error("service stopped")
            server.stop(0)

