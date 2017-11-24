# -*- coding: utf-8 -*-
import os
from tensorflow.python.estimator import export as export_lib

from tensorflow.python.keras._impl.keras.estimator import (
    estimator_lib,
    model_fn_lib,
    ops,
    _clone_and_build_model,
    metrics_module,
    random_seed,
    training_util,
    models,
    saver_lib,
    session,
    logging,
    K
)

from tensorflow.python.saved_model import signature_constants

_DEFAULT_SERVING_KEY = signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY


def _create_keras_model_fn(keras_model, custom_objects=None):
  """Creates model_fn for keras Estimator.

  Args:
    keras_model: an instance of compiled keras model.
    custom_objects: Dictionary for custom objects.

  Returns:
    The model_fn for a keras Estimator.
  """

  def model_fn(features, labels, mode):
    """model_fn for keras Estimator."""
    model = _clone_and_build_model(mode, keras_model, custom_objects, features,
                                   labels)
    # Get inputs to EstimatorSpec
    predictions = dict(zip(model.output_names, model.outputs))

    loss = None
    train_op = None
    eval_metric_ops = None

    # Set loss and metric only during train and evaluate.
    if mode is not model_fn_lib.ModeKeys.PREDICT:
      model._make_train_function()  # pylint: disable=protected-access
      loss = model.total_loss

      if model.metrics:
        eval_metric_ops = {}
        # When each metric maps to an output
        if isinstance(model.metrics, dict):
          for i, output_name in enumerate(model.metrics.keys()):
            metric_name = model.metrics[output_name]
            if callable(metric_name):
              metric_name = metric_name.__name__
            # When some outputs use the same metric
            if list(model.metrics.values()).count(metric_name) > 1:
              metric_name += '_' + output_name
            eval_metric_ops[metric_name] = metrics_module.mean(
                model.metrics_tensors[i - len(model.metrics)])
        else:
          for i, metric_name in enumerate(model.metrics):
            if callable(metric_name):
              metric_name = metric_name.__name__
            eval_metric_ops[metric_name] = metrics_module.mean(
                model.metrics_tensors[i])

    # Set train_op only during train.
    if mode is model_fn_lib.ModeKeys.TRAIN:
      train_op = model.train_function.updates_op

    return model_fn_lib.EstimatorSpec(
        mode=mode,
        predictions=predictions,
        loss=loss,
        train_op=train_op,
        eval_metric_ops=eval_metric_ops,
        export_outputs={
            _DEFAULT_SERVING_KEY: export_lib.export_output.PredictOutput(predictions)
        })

  return model_fn


def _save_first_checkpoint(keras_model, estimator, custom_objects,
                           keras_weights):
  """Save first checkpoint for the keras Estimator.

  Args:
    keras_model: an instance of compiled keras model.
    estimator: keras estimator.
    custom_objects: Dictionary for custom objects.
    keras_weights: A flat list of Numpy arrays for weights of given keras_model.

  Returns:
    The model_fn for a keras Estimator.
  """
  with ops.Graph().as_default() as g, g.device(estimator._device_fn):
    random_seed.set_random_seed(estimator.config.tf_random_seed)
    training_util.create_global_step()
    model = _clone_and_build_model(model_fn_lib.ModeKeys.TRAIN, keras_model,
                                   custom_objects)

    if isinstance(model, models.Sequential):
      model = model.model
    # Load weights and save to checkpoint if there is no checkpoint
    latest_path = saver_lib.latest_checkpoint(estimator.model_dir)
    if not latest_path:
      with session.Session() as sess:
        model.set_weights(keras_weights)
        # Make update ops and initialize all variables.
        if not model.train_function:
          # pylint: disable=protected-access
          model._make_train_function()
          K._initialize_variables(sess)
          # pylint: enable=protected-access
        saver = saver_lib.Saver()
        saver.save(sess, os.path.join(estimator.model_dir, 'keras_model.ckpt'))


def model_to_estimator(keras_model=None,
                       keras_model_path=None,
                       custom_objects=None,
                       model_dir=None,
                       config=None):
  """Constructs an `Estimator` instance from given keras model.

  Args:
    keras_model: Keras model in memory.
    keras_model_path: Directory to a keras model on disk.
    custom_objects: Dictionary for custom objects.
    model_dir: Directory to save Estimator model parameters, graph and etc.
    config: Configuration object.

  Returns:
    An Estimator from given keras model.

  Raises:
    ValueError: if neither keras_model nor keras_model_path was given.
    ValueError: if both keras_model and keras_model_path was given.
    ValueError: if the keras_model_path is a GCS URI.
    ValueError: if keras_model has not been compiled.
  """
  if (not keras_model) and (not keras_model_path):
    raise ValueError(
        'Either keras_model or keras_model_path needs to be provided.')
  if keras_model and keras_model_path:
    raise ValueError(
        'Please specity either keras_model or keras_model_path but not both.')

  if not keras_model:
    if keras_model_path.startswith(
        'gs://') or 'storage.googleapis.com' in keras_model_path:
      raise ValueError(
          '%s is not a local path. Please copy the model locally first.' %
          keras_model_path)
    logging.info('Loading models from %s', keras_model_path)
    keras_model = models.load_model(keras_model_path)
  else:
    logging.info('Using the Keras model from memory.')
    keras_model = keras_model

  if not hasattr(keras_model, 'optimizer'):
    raise ValueError(
        'Given keras model has not been compiled yet. Please compile first '
        'before creating the estimator.')

  keras_weights = keras_model.get_weights()
  keras_model_fn = _create_keras_model_fn(keras_model, custom_objects)
  est = estimator_lib.Estimator(
      keras_model_fn, model_dir=model_dir, config=config)
  # TODO(yifeif): move checkpoint initialization to scaffold.init_fn
  _save_first_checkpoint(keras_model, est, custom_objects, keras_weights)
  return est
