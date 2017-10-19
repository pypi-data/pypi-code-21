import fastr

IS_TEST = False


def create_network():
    network = fastr.Network('auto_prefix_test')

    const = network.create_constant(fastr.datatypes.Int, [1, 2, 3], id_='const')
    source = network.create_source(fastr.datatypes.Int, id_='source')

    node_m_p = network.create_node('AutoPrefixTest', id_='m_p')
    node_a_p = network.create_node('AutoPrefixTest', id_='a_p')
    node_m_n = network.create_node('AutoPrefixNegateTest', id_='m_n')
    node_a_n = network.create_node('AutoPrefixNegateTest', id_='a_n')

    sink_m_p = network.create_sink(fastr.datatypes.Int, id_='sink_m_p')
    sink_a_p = network.create_sink(fastr.datatypes.Int, id_='sink_a_p')
    sink_m_n = network.create_sink(fastr.datatypes.Int, id_='sink_m_n')
    sink_a_n = network.create_sink(fastr.datatypes.Int, id_='sink_a_n')

    for node in [node_m_p, node_a_p, node_m_n, node_a_n]:
        node.inputs['left_hand'] = source.output
        node.inputs['right_hand'] = const.output
        
    sink_m_p.input = node_m_p.outputs['multiplied']
    sink_m_n.input = node_m_n.outputs['multiplied']
    sink_a_n.input = node_a_n.outputs['added']
    sink_a_p.input = node_a_p.outputs['added']

    return network


def main():
    network = create_network()
    network.draw_network()
    network.dumpf('auto_prefix_test.json')

    network.execute(sourcedata={'source': [5]},
                    sinkdata={
                        'sink_a_n': 'vfs://tmp/results/auto_prefix/{node}_{sample_id}',
                        'sink_a_p': 'vfs://tmp/results/auto_prefix/{node}_{sample_id}',
                        'sink_m_p': 'vfs://tmp/results/auto_prefix/{node}_{sample_id}',
                        'sink_m_n': 'vfs://tmp/results/auto_prefix/{node}_{sample_id}'
                        }
                    )

if __name__ == '__main__':
    main()
