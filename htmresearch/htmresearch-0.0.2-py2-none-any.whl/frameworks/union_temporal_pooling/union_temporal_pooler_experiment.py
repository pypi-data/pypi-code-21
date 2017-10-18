# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

import pprint
import time

import numpy

from nupic.algorithms.KNNClassifier import KNNClassifier
from htmresearch_core.experimental import ExtendedTemporalMemory
from nupic.bindings.math import GetNTAReal
from nupic.algorithms.monitor_mixin.monitor_mixin_base import MonitorMixinBase

from htmresearch.support.etm_monitor_mixin import (
     ExtendedTemporalMemoryMonitorMixin)
from htmresearch.support.union_temporal_pooler_monitor_mixin import (
     UnionTemporalPoolerMonitorMixin)

# from union_temporal_pooling.union_temporal_pooler_new import UnionTemporalPoolerNew as UnionTemporalPooler
# uncomment to use early version of union pooler
from htmresearch.algorithms.union_temporal_pooler import UnionTemporalPooler

class MonitoredFastExtendedTemporalMemory(ExtendedTemporalMemoryMonitorMixin,
                                          ExtendedTemporalMemory):
  pass


class MonitoredUnionTemporalPooler(UnionTemporalPoolerMonitorMixin, UnionTemporalPooler):
  pass



realDType = GetNTAReal()



class UnionTemporalPoolerExperiment(object):
  """
  This class defines a Temporal Memory-Union Temporal Pooler network and provides methods
  to run the network on data sequences.
  """


  DEFAULT_TEMPORAL_MEMORY_PARAMS = {"columnCount": 1024,
                                    "cellsPerColumn": 8,
                                    "activationThreshold": 20,
                                    "initialPermanence": 0.5,
                                    "connectedPermanence": 0.6,
                                    "minThreshold": 20,
                                    "sampleSize": 30,
                                    "permanenceIncrement": 0.10,
                                    "permanenceDecrement": 0.02,
                                    "seed": 42,
                                    "learnOnOneCell": False}


  DEFAULT_UNION_POOLER_PARAMS = {# Spatial Pooler Params
                                 # inputDimensions set to TM cell count
                                 # potentialRadius set to TM cell count
                                 "columnDimensions": [1024],
                                 "numActiveColumnsPerInhArea": 20,
                                 "stimulusThreshold": 0,
                                 "synPermInactiveDec": 0.01,
                                 "synPermActiveInc": 0.1,
                                 "synPermConnected": 0.1,
                                 "potentialPct": 0.5,
                                 "globalInhibition": True,
                                 "localAreaDensity": -1,
                                 "minPctOverlapDutyCycle": 0.001,
                                 "dutyCyclePeriod": 1000,
                                 "boostStrength": 10.0,
                                 "seed": 42,
                                 "spVerbosity": 0,
                                 "wrapAround": True,

                                 # Union Temporal Pooler Params
                                 "activeOverlapWeight": 1.0,
                                 "predictedActiveOverlapWeight": 10.0,
                                 "maxUnionActivity": 0.20,
                                 "exciteFunctionType": 'Fixed',
                                 "decayFunctionType": 'NoDecay'}

  DEFAULT_CLASSIFIER_PARAMS = {"k": 1,
                               "distanceMethod": "rawOverlap",
                               "distThreshold": 0}



  def __init__(self, tmOverrides=None, upOverrides=None,
               classifierOverrides=None, seed=42, consoleVerbosity=0):
    print "Initializing Temporal Memory..."
    params = dict(self.DEFAULT_TEMPORAL_MEMORY_PARAMS)
    params.update(tmOverrides or {})
    params["seed"] = seed
    print "params: "
    print params
    self.tm = MonitoredFastExtendedTemporalMemory(mmName="TM", **params)

    print "Initializing Union Temporal Pooler..."
    start = time.time()
    params = dict(self.DEFAULT_UNION_POOLER_PARAMS)
    params.update(upOverrides or {})
    params["inputDimensions"] = [self.tm.numberOfCells()]
    params["potentialRadius"] = self.tm.numberOfCells()
    params["seed"] = seed
    self.up = MonitoredUnionTemporalPooler(mmName="UP", **params)
    elapsed = int(time.time() - start)
    print "Total time: {0:2} seconds.".format(elapsed)

    print "Initializing KNN Classifier..."
    params = dict(self.DEFAULT_CLASSIFIER_PARAMS)
    params.update(classifierOverrides or {})
    self.classifier = KNNClassifier(**params)


  def runNetworkOnSequences(self, inputSequences, inputCategories, tmLearn=True,
                            upLearn=None, classifierLearn=False, verbosity=0,
                            progressInterval=None):
    """
    Runs Union Temporal Pooler network on specified sequence.

    @param inputSequences           One or more sequences of input patterns.
                                    Each should be terminated with None.

    @param inputCategories          A sequence of category representations
                                    for each element in inputSequences
                                    Each should be terminated with None.

    @param tmLearn:   (bool)        Temporal Memory learning mode
    @param upLearn:   (None, bool)  Union Temporal Pooler learning mode. If None,
                                    Union Temporal Pooler will not be run.
    @param classifierLearn: (bool)  Classifier learning mode

    @param progressInterval: (int)  Interval of console progress updates
                                    in terms of timesteps.
    """

    currentTime = time.time()
    for i in xrange(len(inputSequences)):
      sensorPattern = inputSequences[i]
      inputCategory = inputCategories[i]

      self.runNetworkOnPattern(sensorPattern,
                               tmLearn=tmLearn,
                               upLearn=upLearn,
                               sequenceLabel=inputCategory)

      if classifierLearn and sensorPattern is not None:
        unionSDR = self.up.getUnionSDR()
        upCellCount = self.up.getColumnDimensions()
        self.classifier.learn(unionSDR, inputCategory, isSparse=upCellCount)
        if verbosity > 1:
          pprint.pprint("{0} is category {1}".format(unionSDR, inputCategory))

      if progressInterval is not None and i > 0 and i % progressInterval == 0:
        elapsed = (time.time() - currentTime) / 60.0
        print ("Ran {0} / {1} elements of sequence in "
               "{2:0.2f} minutes.".format(i, len(inputSequences), elapsed))
        currentTime = time.time()
        print MonitorMixinBase.mmPrettyPrintMetrics(
          self.tm.mmGetDefaultMetrics())

    if verbosity >= 2:
      traces = self.tm.mmGetDefaultTraces(verbosity=verbosity)
      print MonitorMixinBase.mmPrettyPrintTraces(traces,
                                                 breakOnResets=
                                                 self.tm.mmGetTraceResets())

      if upLearn is not None:
        traces = self.up.mmGetDefaultTraces(verbosity=verbosity)
        print MonitorMixinBase.mmPrettyPrintTraces(traces,
                                                   breakOnResets=
                                                   self.up.mmGetTraceResets())
      print


  def runNetworkOnPattern(self, sensorPattern, tmLearn=True, upLearn=None,
                          sequenceLabel=None):
    if sensorPattern is None:
      self.tm.reset()
      self.up.reset()
    else:
      self.tm.compute(sensorPattern,
                      learn=tmLearn,
                      sequenceLabel=sequenceLabel)

      if upLearn is not None:
        activeCells, predActiveCells, burstingCols, = self.getUnionTemporalPoolerInput()
        self.up.compute(activeCells,
                        predActiveCells,
                        learn=upLearn,
                        sequenceLabel=sequenceLabel)


  def getUnionTemporalPoolerInput(self):
    """
    Gets the Union Temporal Pooler input from the Temporal Memory
    """
    activeCells = numpy.zeros(self.tm.numberOfCells()).astype(realDType)
    activeCells[list(self.tm.activeCellsIndices())] = 1

    predictedActiveCells = numpy.zeros(self.tm.numberOfCells()).astype(
      realDType)
    predictedActiveCells[list(self.tm.predictedActiveCellsIndices())] = 1

    burstingColumns = numpy.zeros(self.tm.numberOfColumns()).astype(realDType)
    burstingColumns[list(self.tm.unpredictedActiveColumns)] = 1

    return activeCells, predictedActiveCells, burstingColumns


  def getBurstingColumnsStats(self):
    """
    Gets statistics on the Temporal Memory's bursting columns. Used as a metric
    of Temporal Memory's learning performance.
    :return: mean, standard deviation, and max of Temporal Memory's bursting
    columns over time
    """
    traceData = self.tm.mmGetTraceUnpredictedActiveColumns().data
    resetData = self.tm.mmGetTraceResets().data
    countTrace = []
    for x in xrange(len(traceData)):
      if not resetData[x]:
        countTrace.append(len(traceData[x]))

    mean = numpy.mean(countTrace)
    stdDev = numpy.std(countTrace)
    maximum = max(countTrace)
    return mean, stdDev, maximum
