
def device_name(device_type, device_id):
    return '/{t}:{i}'.format(t=device_type, i=device_id)


def refined_tensor_or_graph_name(tensor_or_graph):
    import tensorflow as tf
    if isinstance(tensor_or_graph, tf.Tensor):
        return tensor_or_graph.name.replace(':', '_')
    return tensor_or_graph.name
