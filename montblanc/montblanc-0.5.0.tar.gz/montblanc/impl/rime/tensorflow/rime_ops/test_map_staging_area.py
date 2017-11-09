import tensorflow as tf
from tensorflow.python.ops import data_flow_ops

with tf.Graph().as_default() as G:
    i = tf.constant(1, dtype=tf.int64)
    j = tf.constant(2.0, dtype=tf.float64)

    msa = data_flow_ops.MapStagingArea([tf.int64, tf.float64], names=["i", "j"], ordered=True)

    key, data = msa.get(i)

    put = msa.put(i, {"i":i, "j":j})
    G.finalize()

from pprint import pprint
pprint(G.as_graph_def())

with tf.Session(graph=G) as S:
    #_, (key, data) = S.run([get, put])
    print S.run([data,put])
