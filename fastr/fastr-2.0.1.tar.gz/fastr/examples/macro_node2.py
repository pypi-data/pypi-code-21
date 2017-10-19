import fastr


def create_macro_network():
    # Create Network
    network = fastr.Network('add_ints_macro')
    # Create first source
    input_1 = network.create_source(fastr.typelist['Int'], id_='macro_input_1')
    input_2 = network.create_source(fastr.typelist['Int'], id_='macro_input_2')

    # Create calculation nodes
    addint1 = network.create_node(fastr.toollist['AddInt'], id_='addint1')

    # Link network
    addint1.inputs['left_hand'] = input_1.output
    addint1.inputs['right_hand'] = input_2.output
    addint1.inputs['right_hand'].input_group = 'other'

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['Int'], id_='macro_sink')

    # Link the addint node to the sink
    sink.inputs['input'] = addint1.outputs['result']

    return network


def create_network():
    macro_network = create_macro_network()

    # Create Network
    network = fastr.Network('macro_node_2')

    # Extra Node
    add = network.create_node(fastr.toollist['AddInt'], id_='addint')

    # Create data source
    input_1 = network.create_source(fastr.typelist['Int'], id_='source_1')
    input_2 = network.create_source(fastr.typelist['Int'], id_='source_2')
    input_3 = network.create_source(fastr.typelist['Int'], id_='source_3')

    # Create MacroNode
    add_multiple_ints_node = network.create_macro(macro_network, id_='node_add_multiple_ints_1')

    # Sum some stuff
    sum = network.create_node(fastr.toollist['Sum'], id_='sum')

    # Create sink
    sink = network.create_sink(fastr.typelist['Int'], id_='sink')

    # Adjust constants(non required inputs) in macro network
    #  add_multiple_ints_node.inputs['const_addint1_value2__add_multiple_ints_1'] = 1234, #input.output
    # Link the network
    add.inputs['left_hand'] = input_1.output
    add.inputs['right_hand'] = input_2.output
    add.inputs['right_hand'].input_group = 'right'

    add_multiple_ints_node.inputs['macro_input_1'] = add.outputs['result']
    add_multiple_ints_node.inputs['macro_input_2'] = input_3.output

    link = sum.inputs['values'] << add_multiple_ints_node.outputs['macro_sink']
    link.collapse = 1

    sink.inputs['input'] = sum.outputs['result']

    return network


def source_data(network):
    return {
        'source_1': [1, 2],
        'source_2': [4, 5, 6],
        'source_3': [7, 8, 9, 10],
    }


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Validate and execute network
    if network.is_valid():
        network.draw_network(name=network.id, img_format='svg', draw_dimension=True)
        network.execute(source_data(network), sink_data(network))
    else:
        print("Network was not valid")


if __name__ == '__main__':
    main()
