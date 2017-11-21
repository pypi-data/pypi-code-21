self.kappa = mx.sym.Variable(name="%skappa" % prefix, shape=(1, 1, self.heads, 1))

# (batch*heads, queries_max_length, depth_per_head)
contexts = dot_attention(queries, keys, values, lengths, dropout=self.dropout, bias=bias)

# (batch, heads, queries_max_length, depth_per_head)
#contexts = mx.sym.reshape(data=contexts, shape=(-4, -1, self.heads, queries_max_length, 0))

# (batch, queries_max_length, heads, depth_per_head)
#contexts = mx.sym.transpose(contexts, axes=(0, 2, 1, 3))

# (batch, queries_max_length, heads, depth * self.heads)
# contexts = mx.sym.FullyConnected(data=contexts,
#                                  weight=self.w_h2o,
#                                  bias=self.b_h2o,
#                                  num_hidden=self.depth * self.heads,
#                                  flatten=False)

# (batch, queries_max_length, heads, depth * self.heads)
# contexts = mx.sym.broadcast_mul(lhs=contexts, rhs=self.kappa)

# heads * (batch, queries_max_length, heads, depth)
# contexts = mx.sym.split(data=contexts, num_outputs=heads, axis=3)
# return list(contexts)



# what we really need to do is to return lists. Mostly because layer normalization and residual connections need to be done right