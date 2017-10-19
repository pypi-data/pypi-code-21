import fastr

IS_TEST = True


def create_macro_network():
    # Create Network
    network = fastr.Network('add_ints_macro')

    # Create first source
    input_ = network.create_source(fastr.typelist['Int'], id_='input')

    # Create calculation nodes
    addint1 = network.create_node(fastr.toollist['AddInt'], id_='addint1', stepid='add')
    addint2 = network.create_node(fastr.toollist['AddInt'], id_='addint2', stepid='add')

    # Link network
    addint1.inputs['left_hand'] = input_.output
    addint1.inputs['right_hand'] = 10,
    addint2.inputs['left_hand'] = addint1.outputs['result']
    addint2.inputs['right_hand'] = 100,

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['Int'], id_='macro_sink')

    # Link the addint node to the sink
    sink.inputs['input'] = addint2.outputs['result']

    return network


def create_super_macro_node():
    network = fastr.Network('macro_container')
    # Create Outputs

    input_value = network.create_source(fastr.typelist['Int'], id_='input_value')
    # Create Macro Networks

    macro_network_1 = create_macro_network()
    macro_network_2 = create_macro_network()
    add_multiple_ints_node_1 = network.create_macro(macro_network_1, id_='node_add_multiple_ints_1')
    add_multiple_ints_node_2 = network.create_macro(macro_network_2, id_='node_add_multiple_ints_2')
    # Create Sink

    output_value = network.create_sink(fastr.typelist['Int'], id_='output_value')
    # Create Links

    add_multiple_ints_node_1.inputs['input'] = input_value.output
    add_multiple_ints_node_2.inputs['input'] = add_multiple_ints_node_1.outputs['macro_sink']
    output_value.inputs['input'] = add_multiple_ints_node_2.outputs['macro_sink']

    return network


def create_network():
    macro_network = create_super_macro_node()

    # Create Network
    test_network = fastr.Network('macro_top_level')

    # Create data source
    input_ = test_network.create_source(fastr.typelist['Int'], id_='source', stepid='source')

    # Create MacroNode
    add_multiple_ints_node = test_network.create_macro(macro_network, id_='node_add_ints')

    # Create sink
    sink = test_network.create_sink(fastr.typelist['Int'], id_='sink')

    # Adjust constants(non required inputs) in macro network
    #  add_multiple_ints_node.inputs['const_addint1_value2__add_multiple_ints_1'] = 1234, #input.output
    # Link the network
    add_multiple_ints_node.inputs['input_value'] = input_.output
    sink.inputs['input'] = add_multiple_ints_node.outputs['output_value']

    return test_network


def source_data(network):
    return {'source': [1, 'vfslist://example_data/add_ints/values']}


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Validate and execute network
    if network.is_valid():
        network.draw_network(name=network.id, img_format='svg', expand_macro=True, draw_dimension=True)
        network.execute(source_data(network), sink_data(network))
    else:
        print("Network was not valid")


if __name__ == '__main__':
    main()
