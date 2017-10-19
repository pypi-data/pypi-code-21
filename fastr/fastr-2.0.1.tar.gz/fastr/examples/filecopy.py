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


IS_TEST = True

def create_network():
    # Import the faster environment and set it up
    import fastr
    # Create a new network
    network = fastr.Network(id_='file_copy')

    # Create a source node in the network
    source1 = network.create_source(fastr.typelist['TxtFile'], id_='source')

    # Create a new node in the network using toollist
    node = network.create_node(fastr.toollist['PassThroughAuto'], id_="copy")

    # Create a link between the source output and an input of the addint node
    node.inputs['input_file'] = source1.output

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['TxtFile'], id_='sink')

    # Link the addint node to the sink
    sink.input = node.outputs['output_file']

    return network


def source_data(network):
    return {'source': ['vfs://example_data/hello.txt']}


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw_network()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
