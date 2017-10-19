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
    network = fastr.Network(id_='expand2')

    # Create a source node in the network
    source = network.create_source(fastr.typelist['Int'], id_='source')

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['Int'], id_='sink')

    # Link the addint node to the sink
    link = network.create_link(source.output, sink.input)
    link.expand = True

    return network


def source_data(network):
    return {
        'source': {
            'sample_a': (1, 2, 3, 4),
            'sample_b': (5, 6, 8),
            'sample_c': (9, 11),
        }
    }


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw_network()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
