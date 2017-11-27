import bob.io.base

import numpy
import bob.learn.linear
from bob.pad.base.algorithm import Algorithm

import logging
logger = logging.getLogger("bob.paper.taslp_2017")


class LDA (Algorithm):
  """Trains Logistical Regression classifier and projects testing data on it."""

  def __init__(self, normalize_features=True, mask=None, **kwargs):

    # call base class constructor registering that this tool performs everything.
    Algorithm.__init__(
        self,
        performs_projection=True,
        requires_projector_training=True,
        use_projected_features_for_enrollment=True,
    )
    self.machine = None
    self.normalize_features = normalize_features
    self.mask = mask

  def _check_feature(self, feature, machine=None):
    """Checks that the features are appropriate."""
    if not isinstance(feature, numpy.ndarray) or feature.ndim != 1 or (feature.dtype != numpy.float64):
      raise ValueError("The given feature is not appropriate", feature)

    index = 0
    if machine is not None and feature.shape[0] != machine.shape[index]:
      logger.warn("The given feature is expected to have %d elements, but it has %d" % (machine.shape[index], feature.shape[0]))
      return False
    return True

  def train_projector(self, training_features, projector_file):
    if len(training_features) < 2:
      raise ValueError("Training projector: features should contain two lists: real and attack!")

    # the format is specified in FileSelector.py:training_list() of bob.pad.base

    logger.info(" - Training: number of real features %d", len(training_features[0]))

    if isinstance(training_features[0][0][0], numpy.ndarray):
      logger.info(" - Training: each feature is a set of arrays")
      real_features = numpy.array([row if self._check_feature(row) else numpy.nan for feat in training_features[0] for row in feat], dtype=numpy.float64)
      #del training_features[0]
      print(len(training_features))
      attack_features = numpy.array([row if self._check_feature(row) else numpy.nan for feat in training_features[0] for row in feat], dtype=numpy.float64)
      #del training_features
    else:
      logger.info(" - Training: each feature is a single array")
      real_features = numpy.array([feat if self._check_feature(feat) else numpy.nan for feat in training_features[0]], dtype=numpy.float64)

      attack_features = numpy.array([feat if self._check_feature(feat) else numpy.nan for feat in training_features[1]], dtype=numpy.float64)

    # select only features component corresponding to self.mask values
    if self.mask is not None:
      real_features = real_features[:, self.mask]
      attack_features = attack_features[:, self.mask]

    logger.info("Real features shape: " + str(real_features.shape))
    logger.info("Attack features shape: " + str(attack_features.shape))

    # open file in which we will store the trained machine
    hdf5file = bob.io.base.HDF5File(projector_file, "w")

    from ..utils import norm

    mean = None
    std = None
    # normalize the features
    if self.normalize_features:
      mean, std = norm.calc_mean_std(real_features, attack_features, nonStdZero=True)
      real_features = norm.zeromean_unitvar_norm(real_features, mean, std)
      attack_features = norm.zeromean_unitvar_norm(attack_features, mean, std)

    # create Linear Discriminant Analysis Machine
    trainer = bob.learn.linear.FisherLDATrainer(use_pinv=False, strip_to_rank=True)

    # train the mchine using the provided training data
    data = [attack_features, real_features]

    logger.info("Training LDA machine...")
    [self.machine, self.variances] = trainer.train(data)
    logger.info("LDA machine trained.")

    # Check that scores for attacks are lower than for genuine access.
    # If it is not the case, multiply the weights by -1.
    y_real = self.machine(real_features).ravel()
    y_attack = self.machine(attack_features).ravel()
    eer_threshold = bob.measure.eer_threshold(y_attack, y_real)
    far, frr = bob.measure.farfrr(y_attack, y_real, eer_threshold)
    eer = (far + frr) / 2
    if (eer > 0.5):
     self.machine.weights = -self.machine.weights

    # if the features are normalized, save mean and std in LDA machine so that it can be used when projecting new data
    if self.normalize_features:
      if mean is not None and std is not None:
        self.machine.input_subtract = mean
        self.machine.input_divide = std

    hdf5file.cd('/')
    hdf5file.create_group('LDAProjector')
    hdf5file.cd('LDAProjector')
    self.machine.save(hdf5file)

  def load_projector(self, projector_file):
    hdf5file = bob.io.base.HDF5File(projector_file)

    # read LogRegr Machine model
    hdf5file.cd('/LDAProjector')
    self.machine = bob.learn.linear.Machine(hdf5file)

  def project_feature(self, feature):
    feature = numpy.asarray(feature, dtype=numpy.float64)
    if self.mask is not None:
      feature = feature[self.mask]

    if self._check_feature(feature, machine=self.machine):
      # Projects the data with LDA machine
      projection = self.machine(feature)
      return projection
    return numpy.zeros(1, dtype=numpy.float64)

  def project(self, feature):
    """project(feature) -> projected

    Projects the given feature into Fisher space.

    **Parameters:**

    feature : 1D :py:class:`numpy.ndarray`
      The 1D feature to be projected.

    **Returns:**

    projected : 1D :py:class:`numpy.ndarray`
      The ``feature`` projected into Fisher space.
    """

    if len(feature) > 0:
      if isinstance(feature[0], numpy.ndarray) or isinstance(feature[0], list):
        return [self.project_feature(feat) for feat in feature]
      else:
        return self.project_feature(feature)
    else:
      return numpy.zeros(1, dtype=numpy.float64)

  def score(self, toscore):
    """Returns the output of a classifier"""
    return toscore

  def score_for_multiple_projections(self, toscore):
    mean=0
    for sc in toscore:
      mean+=sc
    mean/=len(toscore)
    return mean


algorithm = LDA()
