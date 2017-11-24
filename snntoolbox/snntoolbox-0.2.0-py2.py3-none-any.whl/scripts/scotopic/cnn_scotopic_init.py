# coding=utf-8

"""Initialize scotopic CNN."""


def cnn_scotopic_init(net, config):

    net = net_insert_bnorm(net)
    net = net_adapt(net, config)

    return net


def net_adapt(net, config):

    adapt_layer = config.getboolean('sp', 'adapt_layer')
    if adapt_layer == 'first':
        # only adapt the first layer
        net.layers[0] = adapt_conv(net.layers[0])
    elif adapt_layer == 'all':
        # adapt all layers
        for l in range(len(net.layers)):
            if net.layers[l].type == 'conv':
                net.layers[l] = adapt_conv(net.layers[l])
    elif adapt_layer == 'wb-first':
        # adapt the first layer, both weight and bias
        # batch normalization should take care of the scaling and offset
        net.layers[0] = adapt_bnorm(net.layers[0])
    elif adapt_layer == 'wb-all':
        # adapt all layers
        for l in range(len(net.layers)):
            if net.layers[l].type == 'conv':
                net.layers[l] = adapt_bnorm(net.layers[l])
    return net

#
# def adapt_conv(l):
#
#     l.PPPArray = sp.PPPArray
#     ppp_N = length((l.PPPArray))
#     nout = matcompat.size((l.weights.cell[1]), 2.)
#     l.type = 'custom'
#     l.original_type = 'conv'
#     l.forward = lambda a, res1, res2, testMode: vl_timed_conv('forward', res1, np.array([]), a)
#     l.backward = lambda a, res1, res2: vl_timed_conv('backward', res1, (res2.dzdx), a)
#     l.weights.cell[1] = np.zeros(ppp_N, nout, 'single')
#     l.opts = cellarray([])
#
#     return [l]
#
#
# def adapt_bnorm(l):
#
#     # Local Variables: a, res1, ppp_N, PPPArray, res2, weightDecay, sp, l, weights, original_type, forward, backward, type, nout, testMode
#     # Function calls: length, adaptBnorm, ones, zeros, vl_timed_Bnorm, size
#     l.PPPArray = sp.PPPArray
#     ppp_N = length((l.PPPArray))
#     nout = matcompat.size((l.weights.cell[0]), 1.)
#     l.type = 'custom'
#     l.original_type = 'bnorm'
#     l.forward = lambda a, res1, res2, testMode: vl_timed_Bnorm('forward', res1, np.array([]), a, testMode)
#     l.backward = lambda a, res1, res2: vl_timed_Bnorm('backward', res1, (res2.dzdx), a)
#     l.weights.cell[0] = np.ones(nout, ppp_N, 'single')
#     l.weights.cell[1] = np.zeros(nout, ppp_N, 'single')
#     l.weights.cell[2] = np.zeros(nout, 2., ppp_N, 'single')
#     l.weightDecay = np.array(np.hstack((0., 0., 0.)))
#
#     return [l]
#
#
# def net_insert_bnorm(net):
#
#     # Local Variables: insertLayers, net, l, k
#     # Function calls: length, isfield, insertBnorm, net_insertBNorm, cat
#     insertLayers = np.array([])
#     for l in np.arange(1., (length((net.layers)))+1):
#         if isfield((net.layers.cell[int(l)-1]), 'weights'):
#             insertLayers = cat(2., insertLayers, l)
#
#
#
#     k = 0.
#     for l in insertLayers:
#         net = insertBnorm(net, (l+k))
#         k = k+1.
#
#     return [net]
#
#
# def insert_bnorm(net, l):
#
#     # Local Variables: layers, ndim, layer, l, learningRate, biases, weights, net
#     # Function calls: horzcat, struct, isfield, insertBnorm, ones, zeros, size
#     #% --------------------------------------------------------------------
#     #% disable bias of the conv layer below (it will be modeled by BNorm)
#     net.layers.cell[int(l)-1].weights.cell[1,:][] = 0.
#     net.layers.cell[int(l)-1].learningRate[1] = 0.
#     ndim = matcompat.size((net.layers.cell[int(l)-1].weights.cell[0]), 4.)
#     layer = struct('type', 'bnorm', 'weights', cellarray(np.hstack((cellarray(np.hstack((np.ones(ndim, 1., 'single'), np.zeros(ndim, 1., 'single'))))))), 'learningRate', np.array(np.hstack((1., 1., 0.05))), 'weightDecay', np.array(np.hstack((0., 0.))))
#     net.layers.cell[int(l)-1].biases = np.array([])
#     net.layers = horzcat((net.layers[0:l]), layer, (net.layers[int(l+1.)-1:]))
#     return [net]
