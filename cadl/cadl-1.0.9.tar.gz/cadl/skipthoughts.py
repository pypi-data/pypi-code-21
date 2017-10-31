# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Input ops."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import tensorflow as tf

# A SentenceBatch is a pair of Tensors:
#  ids: Batch of input sentences represented as sequences of word ids: an int64
#    Tensor with shape [batch_size, padded_length].
#  mask: Boolean mask distinguishing real words (1) from padded words (0): an
#    int32 Tensor with shape [batch_size, padded_length].
SentenceBatch = collections.namedtuple("SentenceBatch", ("ids", "mask"))


class _HParams(object):
    """Wrapper for configuration parameters."""
    pass


def _model_config(input_file_pattern=None,
                 input_queue_capacity=640000,
                 num_input_reader_threads=1,
                 shuffle_input_data=True,
                 uniform_init_scale=0.1,
                 vocab_size=20000,
                 batch_size=128,
                 word_embedding_dim=620,
                 bidirectional_encoder=False,
                 encoder_dim=2400):
    """Creates a model configuration object.

  Args:
    input_file_pattern: File pattern of sharded TFRecord files containing
      tf.Example protobufs.
    input_queue_capacity: Number of examples to keep in the input queue.
    num_input_reader_threads: Number of threads for prefetching input
      tf.Examples.
    shuffle_input_data: Whether to shuffle the input data.
    uniform_init_scale: Scale of random uniform initializer.
    vocab_size: Number of unique words in the vocab.
    batch_size: Batch size (training and evaluation only).
    word_embedding_dim: Word embedding dimension.
    bidirectional_encoder: Whether to use a bidirectional or unidirectional
      encoder RNN.
    encoder_dim: Number of output dimensions of the sentence encoder.

  Returns:
    An object containing model configuration parameters.
  """
    config = _HParams()
    config.input_file_pattern = input_file_pattern
    config.input_queue_capacity = input_queue_capacity
    config.num_input_reader_threads = num_input_reader_threads
    config.shuffle_input_data = shuffle_input_data
    config.uniform_init_scale = uniform_init_scale
    config.vocab_size = vocab_size
    config.batch_size = batch_size
    config.word_embedding_dim = word_embedding_dim
    config.bidirectional_encoder = bidirectional_encoder
    config.encoder_dim = encoder_dim
    return config


def _training_config(learning_rate=0.0008,
                    learning_rate_decay_factor=0.5,
                    learning_rate_decay_steps=400000,
                    number_of_steps=500000,
                    clip_gradient_norm=5.0,
                    save_model_secs=600,
                    save_summaries_secs=600):
    """Creates a training configuration object.

  Args:
    learning_rate: Initial learning rate.
    learning_rate_decay_factor: If > 0, the learning rate decay factor.
    learning_rate_decay_steps: The number of steps before the learning rate
      decays by learning_rate_decay_factor.
    number_of_steps: The total number of training steps to run. Passing None
      will cause the training script to run indefinitely.
    clip_gradient_norm: If not None, then clip gradients to this value.
    save_model_secs: How often (in seconds) to save model checkpoints.
    save_summaries_secs: How often (in seconds) to save model summaries.

  Returns:
    An object containing training configuration parameters.

  Raises:
    ValueError: If learning_rate_decay_factor is set and
      learning_rate_decay_steps is unset.
  """
    if learning_rate_decay_factor and not learning_rate_decay_steps:
        raise ValueError(
            "learning_rate_decay_factor requires learning_rate_decay_steps.")

    config = _HParams()
    config.learning_rate = learning_rate
    config.learning_rate_decay_factor = learning_rate_decay_factor
    config.learning_rate_decay_steps = learning_rate_decay_steps
    config.number_of_steps = number_of_steps
    config.clip_gradient_norm = clip_gradient_norm
    config.save_model_secs = save_model_secs
    config.save_summaries_secs = save_summaries_secs
    return config


def _setup_learning_rate(config, global_step):
  """Sets up the learning rate with optional exponential decay.

  Args:
    config: Object containing learning rate configuration parameters.
    global_step: Tensor; the global step.

  Returns:
    learning_rate: Tensor; the learning rate with exponential decay.
  """
  if config.learning_rate_decay_factor > 0:
    learning_rate = tf.train.exponential_decay(
        learning_rate=float(config.learning_rate),
        global_step=global_step,
        decay_steps=config.learning_rate_decay_steps,
        decay_rate=config.learning_rate_decay_factor,
        staircase=False)
  else:
    learning_rate = tf.constant(config.learning_rate)
  return learning_rate


def parse_example_batch(serialized):
    """Parses a batch of tf.Example protos.

  Args:
    serialized: A 1-D string Tensor; a batch of serialized tf.Example protos.
  Returns:
    encode: A SentenceBatch of encode sentences.
    decode_pre: A SentenceBatch of "previous" sentences to decode.
    decode_post: A SentenceBatch of "post" sentences to decode.
  """
    features = tf.parse_example(
        serialized,
        features={
            "encode": tf.VarLenFeature(dtype=tf.int64),
            "decode_pre": tf.VarLenFeature(dtype=tf.int64),
            "decode_post": tf.VarLenFeature(dtype=tf.int64),
        })

    def _sparse_to_batch(sparse):
        ids = tf.sparse_tensor_to_dense(sparse)  # Padding with zeroes.
        mask = tf.sparse_to_dense(sparse.indices, sparse.dense_shape,
                                  tf.ones_like(sparse.values, dtype=tf.int32))
        return SentenceBatch(ids=ids, mask=mask)

    output_names = ("encode", "decode_pre", "decode_post")
    return tuple(_sparse_to_batch(features[x]) for x in output_names)


def prefetch_input_data(reader,
                        file_pattern,
                        shuffle,
                        capacity,
                        num_reader_threads=1):
    """Prefetches string values from disk into an input queue.

  Args:
    reader: Instance of tf.ReaderBase.
    file_pattern: Comma-separated list of file patterns (e.g.
        "/tmp/train_data-?????-of-00100", where '?' acts as a wildcard that
        matches any character).
    shuffle: Boolean; whether to randomly shuffle the input data.
    capacity: Queue capacity (number of records).
    num_reader_threads: Number of reader threads feeding into the queue.

  Returns:
    A Queue containing prefetched string values.
  """
    data_files = []
    for pattern in file_pattern.split(","):
        data_files.extend(tf.gfile.Glob(pattern))
    if not data_files:
        tf.logging.fatal("Found no input files matching %s", file_pattern)
    else:
        tf.logging.info("Prefetching values from %d files matching %s",
                        len(data_files), file_pattern)

    filename_queue = tf.train.string_input_producer(
        data_files, shuffle=shuffle, capacity=16, name="filename_queue")

    if shuffle:
        min_after_dequeue = int(0.6 * capacity)
        values_queue = tf.RandomShuffleQueue(
            capacity=capacity,
            min_after_dequeue=min_after_dequeue,
            dtypes=[tf.string],
            shapes=[[]],
            name="random_input_queue")
    else:
        values_queue = tf.FIFOQueue(
            capacity=capacity,
            dtypes=[tf.string],
            shapes=[[]],
            name="fifo_input_queue")

    enqueue_ops = []
    for _ in range(num_reader_threads):
        _, value = reader.read(filename_queue)
        enqueue_ops.append(values_queue.enqueue([value]))
    tf.train.queue_runner.add_queue_runner(
        tf.train.queue_runner.QueueRunner(values_queue, enqueue_ops))
    tf.summary.scalar(
        "queue/%s/fraction_of_%d_full" % (values_queue.name, capacity),
        tf.cast(values_queue.size(), tf.float32) * (1.0 / capacity))

    return values_queue


_layer_norm = tf.contrib.layers.layer_norm


class LayerNormGRUCell(tf.contrib.rnn.RNNCell):
    """GRU cell with layer normalization.

  The layer normalization implementation is based on:

    https://arxiv.org/abs/1607.06450.

  "Layer Normalization"
  Jimmy Lei Ba, Jamie Ryan Kiros, Geoffrey E. Hinton
  """

    def __init__(self,
                 num_units,
                 w_initializer,
                 u_initializer,
                 b_initializer,
                 activation=tf.nn.tanh):
        """Initializes the cell.

    Args:
      num_units: Number of cell units.
      w_initializer: Initializer for the "W" (input) parameter matrices.
      u_initializer: Initializer for the "U" (recurrent) parameter matrices.
      b_initializer: Initializer for the "b" (bias) parameter vectors.
      activation: Cell activation function.
    """
        self._num_units = num_units
        self._w_initializer = w_initializer
        self._u_initializer = u_initializer
        self._b_initializer = b_initializer
        self._activation = activation

    @property
    def state_size(self):
        return self._num_units

    @property
    def output_size(self):
        return self._num_units

    def _w_h_initializer(self):
        """Returns an initializer for the "W_h" parameter matrix.

    See equation (23) in the paper. The "W_h" parameter matrix is the
    concatenation of two parameter submatrices. The matrix returned is
    [U_z, U_r].

    Returns:
      A Tensor with shape [num_units, 2 * num_units] as described above.
    """

        def _initializer(shape, dtype=tf.float32, partition_info=None):
            num_units = self._num_units
            assert shape == [num_units, 2 * num_units]
            u_z = self._u_initializer([num_units, num_units], dtype,
                                      partition_info)
            u_r = self._u_initializer([num_units, num_units], dtype,
                                      partition_info)
            return tf.concat([u_z, u_r], 1)

        return _initializer

    def _w_x_initializer(self, input_dim):
        """Returns an initializer for the "W_x" parameter matrix.

    See equation (23) in the paper. The "W_x" parameter matrix is the
    concatenation of two parameter submatrices. The matrix returned is
    [W_z, W_r].

    Args:
      input_dim: The dimension of the cell inputs.

    Returns:
      A Tensor with shape [input_dim, 2 * num_units] as described above.
    """

        def _initializer(shape, dtype=tf.float32, partition_info=None):
            num_units = self._num_units
            assert shape == [input_dim, 2 * num_units]
            w_z = self._w_initializer([input_dim, num_units], dtype,
                                      partition_info)
            w_r = self._w_initializer([input_dim, num_units], dtype,
                                      partition_info)
            return tf.concat([w_z, w_r], 1)

        return _initializer

    def __call__(self, inputs, state, scope=None):
        """GRU cell with layer normalization."""
        input_dim = inputs.get_shape().as_list()[1]
        num_units = self._num_units

        with tf.variable_scope(scope or "gru_cell"):
            with tf.variable_scope("gates"):
                w_h = tf.get_variable(
                    "w_h", [num_units, 2 * num_units],
                    initializer=self._w_h_initializer())
                w_x = tf.get_variable(
                    "w_x", [input_dim, 2 * num_units],
                    initializer=self._w_x_initializer(input_dim))
                z_and_r = (
                    _layer_norm(tf.matmul(state, w_h), scope="layer_norm/w_h") +
                    _layer_norm(tf.matmul(inputs, w_x), scope="layer_norm/w_x"))
                z, r = tf.split(tf.sigmoid(z_and_r), 2, 1)
            with tf.variable_scope("candidate"):
                w = tf.get_variable(
                    "w", [input_dim, num_units],
                    initializer=self._w_initializer)
                u = tf.get_variable(
                    "u", [num_units, num_units],
                    initializer=self._u_initializer)
                h_hat = (
                    r * _layer_norm(tf.matmul(state, u), scope="layer_norm/u") +
                    _layer_norm(tf.matmul(inputs, w), scope="layer_norm/w"))
            new_h = (1 - z) * state + z * self._activation(h_hat)
        return new_h, new_h


def random_orthonormal_initializer(shape, dtype=tf.float32,
                                   partition_info=None):  # pylint: disable=unused-argument
    """Variable initializer that produces a random orthonormal matrix."""
    if len(shape) != 2 or shape[0] != shape[1]:
        raise ValueError("Expecting square shape, got %s" % shape)
    _, u, _ = tf.svd(tf.random_normal(shape, dtype=dtype), full_matrices=True)
    return u


class SkipThoughtsModel(object):
    """Skip-thoughts model."""

    def __init__(self, config, mode="train", input_reader=None):
        """Basic setup. The actual TensorFlow graph is constructed in build().

    Args:
      config: Object containing configuration parameters.
      mode: "train", "eval" or "encode".
      input_reader: Subclass of tf.ReaderBase for reading the input serialized
        tf.Example protocol buffers. Defaults to TFRecordReader.

    Raises:
      ValueError: If mode is invalid.
    """
        if mode not in ["train", "eval", "encode"]:
            raise ValueError("Unrecognized mode: %s" % mode)

        self.config = config
        self.mode = mode
        self.reader = input_reader if input_reader else tf.TFRecordReader()

        # Initializer used for non-recurrent weights.
        self.uniform_initializer = tf.random_uniform_initializer(
            minval=-self.config.uniform_init_scale,
            maxval=self.config.uniform_init_scale)

        # Input sentences represented as sequences of word ids. "encode" is the
        # source sentence, "decode_pre" is the previous sentence and "decode_post"
        # is the next sentence.
        # Each is an int64 Tensor with  shape [batch_size, padded_length].
        self.encode_ids = None
        self.decode_pre_ids = None
        self.decode_post_ids = None

        # Boolean masks distinguishing real words (1) from padded words (0).
        # Each is an int32 Tensor with shape [batch_size, padded_length].
        self.encode_mask = None
        self.decode_pre_mask = None
        self.decode_post_mask = None

        # Input sentences represented as sequences of word embeddings.
        # Each is a float32 Tensor with shape [batch_size, padded_length, emb_dim].
        self.encode_emb = None
        self.decode_pre_emb = None
        self.decode_post_emb = None

        # The output from the sentence encoder.
        # A float32 Tensor with shape [batch_size, num_gru_units].
        self.thought_vectors = None

        # The cross entropy losses and corresponding weights of the decoders. Used
        # for evaluation.
        self.target_cross_entropy_losses = []
        self.target_cross_entropy_loss_weights = []

        # The total loss to optimize.
        self.total_loss = None

    def build_inputs(self):
        """Builds the ops for reading input data.

    Outputs:
      self.encode_ids
      self.decode_pre_ids
      self.decode_post_ids
      self.encode_mask
      self.decode_pre_mask
      self.decode_post_mask
    """
        if self.mode == "encode":
            # Word embeddings are fed from an external vocabulary which has possibly
            # been expanded (see vocabulary_expansion.py).
            encode_ids = None
            decode_pre_ids = None
            decode_post_ids = None
            encode_mask = tf.placeholder(
                tf.int8, (None, None), name="encode_mask")
            decode_pre_mask = None
            decode_post_mask = None
        else:
            # Prefetch serialized tf.Example protos.
            input_queue = prefetch_input_data(
                self.reader,
                self.config.input_file_pattern,
                shuffle=self.config.shuffle_input_data,
                capacity=self.config.input_queue_capacity,
                num_reader_threads=self.config.num_input_reader_threads)

            # Deserialize a batch.
            serialized = input_queue.dequeue_many(self.config.batch_size)
            encode, decode_pre, decode_post = parse_example_batch(serialized)

            encode_ids = encode.ids
            decode_pre_ids = decode_pre.ids
            decode_post_ids = decode_post.ids

            encode_mask = encode.mask
            decode_pre_mask = decode_pre.mask
            decode_post_mask = decode_post.mask

        self.encode_ids = encode_ids
        self.decode_pre_ids = decode_pre_ids
        self.decode_post_ids = decode_post_ids

        self.encode_mask = encode_mask
        self.decode_pre_mask = decode_pre_mask
        self.decode_post_mask = decode_post_mask

    def build_word_embeddings(self):
        """Builds the word embeddings.

    Inputs:
      self.encode_ids
      self.decode_pre_ids
      self.decode_post_ids

    Outputs:
      self.encode_emb
      self.decode_pre_emb
      self.decode_post_emb
    """
        if self.mode == "encode":
            # Word embeddings are fed from an external vocabulary which has possibly
            # been expanded (see vocabulary_expansion.py).
            encode_emb = tf.placeholder(tf.float32, (
                None, None, self.config.word_embedding_dim), "encode_emb")
            # No sequences to decode.
            decode_pre_emb = None
            decode_post_emb = None
        else:
            word_emb = tf.get_variable(
                name="word_embedding",
                shape=[self.config.vocab_size, self.config.word_embedding_dim],
                initializer=self.uniform_initializer)

            encode_emb = tf.nn.embedding_lookup(word_emb, self.encode_ids)
            decode_pre_emb = tf.nn.embedding_lookup(word_emb,
                                                    self.decode_pre_ids)
            decode_post_emb = tf.nn.embedding_lookup(word_emb,
                                                     self.decode_post_ids)

        self.encode_emb = encode_emb
        self.decode_pre_emb = decode_pre_emb
        self.decode_post_emb = decode_post_emb

    def _initialize_gru_cell(self, num_units):
        """Initializes a GRU cell.

    The Variables of the GRU cell are initialized in a way that exactly matches
    the skip-thoughts paper: recurrent weights are initialized from random
    orthonormal matrices and non-recurrent weights are initialized from random
    uniform matrices.

    Args:
      num_units: Number of output units.

    Returns:
      cell: An instance of RNNCell with variable initializers that match the
        skip-thoughts paper.
    """
        return LayerNormGRUCell(
            num_units,
            w_initializer=self.uniform_initializer,
            u_initializer=random_orthonormal_initializer,
            b_initializer=tf.constant_initializer(0.0))

    def build_encoder(self):
        """Builds the sentence encoder.

    Inputs:
      self.encode_emb
      self.encode_mask

    Outputs:
      self.thought_vectors

    Raises:
      ValueError: if config.bidirectional_encoder is True and config.encoder_dim
        is odd.
    """
        with tf.variable_scope("encoder") as scope:
            length = tf.to_int32(
                tf.reduce_sum(self.encode_mask, 1), name="length")

            if self.config.bidirectional_encoder:
                if self.config.encoder_dim % 2:
                    raise ValueError(
                        "encoder_dim must be even when using a bidirectional encoder."
                    )
                num_units = self.config.encoder_dim // 2
                cell_fw = self._initialize_gru_cell(
                    num_units)  # Forward encoder
                cell_bw = self._initialize_gru_cell(
                    num_units)  # Backward encoder
                _, states = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw,
                    cell_bw=cell_bw,
                    inputs=self.encode_emb,
                    sequence_length=length,
                    dtype=tf.float32,
                    scope=scope)
                thought_vectors = tf.concat(states, 1, name="thought_vectors")
            else:
                cell = self._initialize_gru_cell(self.config.encoder_dim)
                _, state = tf.nn.dynamic_rnn(
                    cell=cell,
                    inputs=self.encode_emb,
                    sequence_length=length,
                    dtype=tf.float32,
                    scope=scope)
                # Use an identity operation to name the Tensor in the Graph.
                thought_vectors = tf.identity(state, name="thought_vectors")

        self.thought_vectors = thought_vectors

    def _build_decoder(self, name, embeddings, targets, mask, initial_state,
                       reuse_logits):
        """Builds a sentence decoder.

    Args:
      name: Decoder name.
      embeddings: Batch of sentences to decode; a float32 Tensor with shape
        [batch_size, padded_length, emb_dim].
      targets: Batch of target word ids; an int64 Tensor with shape
        [batch_size, padded_length].
      mask: A 0/1 Tensor with shape [batch_size, padded_length].
      initial_state: Initial state of the GRU. A float32 Tensor with shape
        [batch_size, num_gru_cells].
      reuse_logits: Whether to reuse the logits weights.
    """
        # Decoder RNN.
        cell = self._initialize_gru_cell(self.config.encoder_dim)
        with tf.variable_scope(name) as scope:
            # Add a padding word at the start of each sentence (to correspond to the
            # prediction of the first word) and remove the last word.
            decoder_input = tf.pad(
                embeddings[:, :-1, :], [[0, 0], [1, 0], [0, 0]], name="input")
            length = tf.reduce_sum(mask, 1, name="length")
            decoder_output, _ = tf.nn.dynamic_rnn(
                cell=cell,
                inputs=decoder_input,
                sequence_length=length,
                initial_state=initial_state,
                scope=scope)

        # Stack batch vertically.
        decoder_output = tf.reshape(decoder_output,
                                    [-1, self.config.encoder_dim])
        targets = tf.reshape(targets, [-1])
        weights = tf.to_float(tf.reshape(mask, [-1]))

        # Logits.
        with tf.variable_scope("logits", reuse=reuse_logits) as scope:
            logits = tf.contrib.layers.fully_connected(
                inputs=decoder_output,
                num_outputs=self.config.vocab_size,
                activation_fn=None,
                weights_initializer=self.uniform_initializer,
                scope=scope)

        losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=targets, logits=logits)
        batch_loss = tf.reduce_sum(losses * weights)
        tf.losses.add_loss(batch_loss)

        tf.summary.scalar("losses/" + name, batch_loss)

        self.target_cross_entropy_losses.append(losses)
        self.target_cross_entropy_loss_weights.append(weights)

    def build_decoders(self):
        """Builds the sentence decoders.

    Inputs:
      self.decode_pre_emb
      self.decode_post_emb
      self.decode_pre_ids
      self.decode_post_ids
      self.decode_pre_mask
      self.decode_post_mask
      self.thought_vectors

    Outputs:
      self.target_cross_entropy_losses
      self.target_cross_entropy_loss_weights
    """
        if self.mode != "encode":
            # Pre-sentence decoder.
            self._build_decoder("decoder_pre", self.decode_pre_emb,
                                self.decode_pre_ids, self.decode_pre_mask,
                                self.thought_vectors, False)

            # Post-sentence decoder. Logits weights are reused.
            self._build_decoder("decoder_post", self.decode_post_emb,
                                self.decode_post_ids, self.decode_post_mask,
                                self.thought_vectors, True)

    def build_loss(self):
        """Builds the loss Tensor.

    Outputs:
      self.total_loss
    """
        if self.mode != "encode":
            total_loss = tf.losses.get_total_loss()
            tf.summary.scalar("losses/total", total_loss)

            self.total_loss = total_loss

    def build_global_step(self):
        """Builds the global step Tensor.

    Outputs:
      self.global_step
    """
        self.global_step = tf.contrib.framework.create_global_step()

    def build(self):
        """Creates all ops for training, evaluation or encoding."""
        self.build_inputs()
        self.build_word_embeddings()
        self.build_encoder()
        self.build_decoders()
        self.build_loss()
        self.build_global_step()


def train():
    FLAGS = tf.flags.FLAGS

    tf.flags.DEFINE_string("input_file_pattern", None,
                           "File pattern of sharded TFRecord files containing "
                           "tf.Example protos.")
    tf.flags.DEFINE_string("train_dir", None,
                           "Directory for saving and loading checkpoints.")

    tf.logging.set_verbosity(tf.logging.INFO)

    if not FLAGS.input_file_pattern:
        raise ValueError("--input_file_pattern is required.")
    if not FLAGS.train_dir:
        raise ValueError("--train_dir is required.")

    model_config = _model_config(
        input_file_pattern=FLAGS.input_file_pattern)
    training_config = _training_config()

    tf.logging.info("Building training graph.")
    g = tf.Graph()
    with g.as_default():
        model = SkipThoughtsModel(
            model_config, mode="train")
        model.build()

        learning_rate = _setup_learning_rate(training_config, model.global_step)
        optimizer = tf.train.AdamOptimizer(learning_rate)

        train_tensor = tf.contrib.slim.learning.create_train_op(
            total_loss=model.total_loss,
            optimizer=optimizer,
            global_step=model.global_step,
            clip_gradient_norm=training_config.clip_gradient_norm)

        saver = tf.train.Saver()

    tf.contrib.slim.learning.train(
        train_op=train_tensor,
        logdir=FLAGS.train_dir,
        graph=g,
        global_step=model.global_step,
        number_of_steps=training_config.number_of_steps,
        save_summaries_secs=training_config.save_summaries_secs,
        saver=saver,
        save_interval_secs=training_config.save_model_secs)
