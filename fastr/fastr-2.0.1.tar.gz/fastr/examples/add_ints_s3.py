#!/usr/bin/env python

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

IS_TEST = False


def create_network():
    # Import the faster environment and set it up
    import fastr
    # Create a new network
    network = fastr.Network(id_='add_ints')

    # Create a source node in the network
    source1 = network.create_source(fastr.typelist['Int'], id_='source')

    # Create a new node in the network using toollist
    node = network.create_node(fastr.toollist['AddInt'], id_="add")

    # Create a link between the source output and an input of the addint node
    node.inputs['left_hand'] = source1.output

    # Create a constant node and link it to the value2 input of the addint node
    node.inputs['right_hand'] = [10]

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['Int'], id_='sink')

    # Link the addint node to the sink
    sink.input = node.outputs['result']

    return network


def source_data(network):
    return {'source': [1, 's3list://localhost@addints.localhost:9000/values']}


def sink_data(network):
    return {'sink': 's3://localhost@addints.localhost:9000/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw_network()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
