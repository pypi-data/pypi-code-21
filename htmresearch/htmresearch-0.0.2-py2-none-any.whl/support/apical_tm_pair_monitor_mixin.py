# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
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

"""
Apical Temporal Memory pair mixin that enables detailed monitoring of history.
"""

from collections import defaultdict

import copy

from prettytable import PrettyTable

from nupic.algorithms.monitor_mixin.metric import Metric
from nupic.algorithms.monitor_mixin.monitor_mixin_base import MonitorMixinBase
from nupic.algorithms.monitor_mixin.trace import (IndicesTrace, CountsTrace,
                                                BoolsTrace, StringsTrace)



class ApicalTMPairMonitorMixin(MonitorMixinBase):
  """
  Mixin for Apical TemporalMemory + pairs that stores a detailed history, for
  inspection and debugging.
  """

  def __init__(self, *args, **kwargs):
    super(ApicalTMPairMonitorMixin, self).__init__(*args, **kwargs)

    self._mmResetActive = True  # First iteration is always a reset


  def mmGetTraceActiveColumns(self):
    """
    @return (Trace) Trace of active columns
    """
    return self._mmTraces["activeColumns"]


  def mmGetTracePredictedCells(self):
    """
    @return (Trace) Trace of cells that were predicted for this timestep.
    """
    return self._mmTraces["predictedCells"]


  def mmGetTraceNumBasalSegments(self):
    """
    @return (Trace) Trace of # segments
    """
    return self._mmTraces["numBasalSegments"]


  def mmGetTraceNumBasalSynapses(self):
    """
    @return (Trace) Trace of # synapses
    """
    return self._mmTraces["numBasalSynapses"]


  def mmGetTraceNumApicalSegments(self):
    """
    @return (Trace) Trace of # segments
    """
    return self._mmTraces["numApicalSegments"]


  def mmGetTraceNumApicalSynapses(self):
    """
    @return (Trace) Trace of # synapses
    """
    return self._mmTraces["numApicalSynapses"]


  def mmGetTraceSequenceLabels(self):
    """
    @return (Trace) Trace of sequence labels
    """
    return self._mmTraces["sequenceLabels"]


  def mmGetTraceResets(self):
    """
    @return (Trace) Trace of resets
    """
    return self._mmTraces["resets"]


  def mmGetTracePredictedActiveCells(self):
    """
    @return (Trace) Trace of predicted => active cells
    """
    self._mmComputeTransitionTraces()
    return self._mmTraces["predictedActiveCells"]


  def mmGetTracePredictedInactiveCells(self):
    """
    @return (Trace) Trace of predicted => inactive cells
    """
    self._mmComputeTransitionTraces()
    return self._mmTraces["predictedInactiveCells"]


  def mmGetTracePredictedActiveColumns(self):
    """
    @return (Trace) Trace of predicted => active columns
    """
    self._mmComputeTransitionTraces()
    return self._mmTraces["predictedActiveColumns"]


  def mmGetTracePredictedInactiveColumns(self):
    """
    @return (Trace) Trace of predicted => inactive columns
    """
    self._mmComputeTransitionTraces()
    return self._mmTraces["predictedInactiveColumns"]


  def mmGetTraceUnpredictedActiveColumns(self):
    """
    @return (Trace) Trace of unpredicted => active columns
    """
    self._mmComputeTransitionTraces()
    return self._mmTraces["unpredictedActiveColumns"]


  def mmGetMetricFromTrace(self, trace):
    """
    Convenience method to compute a metric over an indices trace, excluding
    resets.

    @param (IndicesTrace) Trace of indices

    @return (Metric) Metric over trace excluding resets
    """
    return Metric.createFromTrace(trace.makeCountsTrace(),
                                  excludeResets=self.mmGetTraceResets())


  def mmGetMetricSequencesPredictedActiveCellsPerColumn(self):
    """
    Metric for number of predicted => active cells per column for each sequence

    @return (Metric) metric
    """
    self._mmComputeTransitionTraces()

    numCellsPerColumn = []

    for predictedActiveCells in (
        self._mmData["predictedActiveCellsForSequence"].values()):
      cellsForColumn = self.mapCellsToColumns(predictedActiveCells)
      numCellsPerColumn += [len(x) for x in cellsForColumn.values()]

    return Metric(self,
                  "# predicted => active cells per column for each sequence",
                  numCellsPerColumn)


  def mmGetMetricSequencesPredictedActiveCellsShared(self):
    """
    Metric for number of sequences each predicted => active cell appears in

    Note: This metric is flawed when it comes to high-order sequences.

    @return (Metric) metric
    """
    self._mmComputeTransitionTraces()

    numSequencesForCell = defaultdict(lambda: 0)

    for predictedActiveCells in (
          self._mmData["predictedActiveCellsForSequence"].values()):
      for cell in predictedActiveCells:
        numSequencesForCell[cell] += 1

    return Metric(self,
                  "# sequences each predicted => active cells appears in",
                  numSequencesForCell.values())


  def mmPrettyPrintConnections(self):
    """
    Pretty print the connections in the temporal memory.

    TODO: Use PrettyTable.

    @return (string) Pretty-printed text
    """
    text = ""

    text += ("Segments: (format => "
             "(#) [(source cell=permanence ...),       ...]\n")
    text += "------------------------------------\n"

    columns = range(self.numberOfColumns())

    for column in columns:
      cells = self.cellsForColumn(column)

      for cell in cells:
        segmentDict = dict()

        for seg in self.connections.segmentsForCell(cell):
          synapseList = []

          for synapse in self.connections.synapsesForSegment(seg):
            synapseData = self.connections.dataForSynapse(synapse)
            synapseList.append(
                (synapseData.presynapticCell, synapseData.permanence))

          synapseList.sort()
          synapseStringList = ["{0:3}={1:.2f}".format(sourceCell, permanence) for
                               sourceCell, permanence in synapseList]
          segmentDict[seg] = "({0})".format(" ".join(synapseStringList))

        text += ("Column {0:3} / Cell {1:3}:\t({2}) {3}\n".format(
          column, cell,
          len(segmentDict.values()),
          "[{0}]".format(",       ".join(segmentDict.values()))))

      if column < len(columns) - 1:  # not last
        text += "\n"

    text += "------------------------------------\n"

    return text


  def mmPrettyPrintSequenceCellRepresentations(self, sortby="Column"):
    """
    Pretty print the cell representations for sequences in the history.

    @param sortby (string) Column of table to sort by

    @return (string) Pretty-printed text
    """
    self._mmComputeTransitionTraces()
    table = PrettyTable(["Pattern", "Column", "predicted=>active cells"])

    for sequenceLabel, predictedActiveCells in (
          self._mmData["predictedActiveCellsForSequence"].iteritems()):
      cellsForColumn = self.mapCellsToColumns(predictedActiveCells)
      for column, cells in cellsForColumn.iteritems():
        table.add_row([sequenceLabel, column, list(cells)])

    return table.get_string(sortby=sortby).encode("utf-8")


  # ==============================
  # Helper methods
  # ==============================

  def _mmComputeTransitionTraces(self):
    """
    Computes the transition traces, if necessary.

    Transition traces are the following:

        predicted => active cells
        predicted => inactive cells
        predicted => active columns
        predicted => inactive columns
        unpredicted => active columns
    """
    if not self._mmTransitionTracesStale:
      return

    self._mmData["predictedActiveCellsForSequence"] = defaultdict(set)

    self._mmTraces["predictedActiveCells"] = IndicesTrace(self,
      "predicted => active cells (correct)")
    self._mmTraces["predictedInactiveCells"] = IndicesTrace(self,
      "predicted => inactive cells (extra)")
    self._mmTraces["predictedActiveColumns"] = IndicesTrace(self,
      "predicted => active columns (correct)")
    self._mmTraces["predictedInactiveColumns"] = IndicesTrace(self,
      "predicted => inactive columns (extra)")
    self._mmTraces["unpredictedActiveColumns"] = IndicesTrace(self,
      "unpredicted => active columns (bursting)")

    predictedCellsTrace = self._mmTraces["predictedCells"]

    for i, activeColumns in enumerate(self.mmGetTraceActiveColumns().data):
      predictedActiveCells = set()
      predictedInactiveCells = set()
      predictedActiveColumns = set()
      predictedInactiveColumns = set()

      for predictedCell in predictedCellsTrace.data[i]:
        predictedColumn = self.columnForCell(predictedCell)

        if predictedColumn  in activeColumns:
          predictedActiveCells.add(predictedCell)
          predictedActiveColumns.add(predictedColumn)

          sequenceLabel = self.mmGetTraceSequenceLabels().data[i]
          if sequenceLabel is not None:
            self._mmData["predictedActiveCellsForSequence"][sequenceLabel].add(
              predictedCell)
        else:
          predictedInactiveCells.add(predictedCell)
          predictedInactiveColumns.add(predictedColumn)

      unpredictedActiveColumns = set(activeColumns) - set(predictedActiveColumns)

      self._mmTraces["predictedActiveCells"].data.append(predictedActiveCells)
      self._mmTraces["predictedInactiveCells"].data.append(predictedInactiveCells)
      self._mmTraces["predictedActiveColumns"].data.append(predictedActiveColumns)
      self._mmTraces["predictedInactiveColumns"].data.append(
        predictedInactiveColumns)
      self._mmTraces["unpredictedActiveColumns"].data.append(
        unpredictedActiveColumns)

    self._mmTransitionTracesStale = False


  # ==============================
  # Overrides
  # ==============================
  def compute(self,
              activeColumns,
              basalInput=(),
              apicalInput=(),
              basalGrowthCandidates=None,
              apicalGrowthCandidates=None,
              learn=True,
              sequenceLabel=None):

    super(ApicalTMPairMonitorMixin, self).compute(
      activeColumns, basalInput, apicalInput, basalGrowthCandidates,
      apicalGrowthCandidates, learn)

    self._mmTraces["predictedCells"].data.append(
      set(self.getPredictedCells()))
    self._mmTraces["activeCells"].data.append(set(self.getActiveCells()))
    self._mmTraces["activeColumns"].data.append(activeColumns)
    self._mmTraces["numBasalSegments"].data.append(
      self.basalConnections.numSegments())
    self._mmTraces["numBasalSynapses"].data.append(
      self.basalConnections.numSynapses())
    self._mmTraces["numApicalSegments"].data.append(
      self.apicalConnections.numSegments())
    self._mmTraces["numApicalSynapses"].data.append(
      self.apicalConnections.numSynapses())
    self._mmTraces["sequenceLabels"].data.append(sequenceLabel)
    self._mmTraces["resets"].data.append(self._mmResetActive)
    self._mmResetActive = False

    self._mmTransitionTracesStale = True


  def reset(self):
    super(ApicalTMPairMonitorMixin, self).reset()

    self._mmResetActive = True


  def mmGetDefaultTraces(self, verbosity=1):
    traces = [
      self.mmGetTraceActiveColumns(),
      self.mmGetTracePredictedActiveColumns(),
      self.mmGetTracePredictedInactiveColumns(),
      self.mmGetTraceUnpredictedActiveColumns(),
      self.mmGetTracePredictedActiveCells(),
      self.mmGetTracePredictedInactiveCells()
    ]

    if verbosity == 1:
      traces = [trace.makeCountsTrace() for trace in traces]

    traces += [
      self.mmGetTraceNumBasalSegments(),
      self.mmGetTraceNumBasalSynapses(),
      self.mmGetTraceNumApicalSegments(),
      self.mmGetTraceNumApicalSynapses(),
    ]

    return traces + [self.mmGetTraceSequenceLabels()]


  def mmGetDefaultMetrics(self, verbosity=1):
    resetsTrace = self.mmGetTraceResets()
    return ([Metric.createFromTrace(trace, excludeResets=resetsTrace)
              for trace in self.mmGetDefaultTraces()[:-3]] +
            [Metric.createFromTrace(trace)
              for trace in self.mmGetDefaultTraces()[-3:-1]] +
            [self.mmGetMetricSequencesPredictedActiveCellsPerColumn(),
             self.mmGetMetricSequencesPredictedActiveCellsShared()])


  def mmClearHistory(self):
    super(ApicalTMPairMonitorMixin, self).mmClearHistory()

    self._mmTraces["activeColumns"] = IndicesTrace(self, "active columns")
    self._mmTraces["activeCells"] = IndicesTrace(self, "active cells")
    self._mmTraces["predictedCells"] = IndicesTrace(self, "predicted cells")
    self._mmTraces["numBasalSegments"] = CountsTrace(self, "# basal segments")
    self._mmTraces["numBasalSynapses"] = CountsTrace(self, "# basal synapses")
    self._mmTraces["numApicalSegments"] = CountsTrace(self, "# apical segments")
    self._mmTraces["numApicalSynapses"] = CountsTrace(self, "# apical synapses")
    self._mmTraces["sequenceLabels"] = StringsTrace(self, "sequence labels")
    self._mmTraces["resets"] = BoolsTrace(self, "resets")
    self._mmTransitionTracesStale = True


  def mmGetCellActivityPlot(self, title="", showReset=False,
                            resetShading=0.25, activityType="activeCells"):
    """
    Returns plot of the cell activity.

    @param title        (string)  an optional title for the figure

    @param showReset    (bool)    if true, the first set of cell activities
                                  after a reset will have a gray background

    @param resetShading (float)   if showReset is true, this float specifies the
                                  intensity of the reset background with 0.0
                                  being white and 1.0 being black

    @param activityType (string)  The type of cell activity to display. Valid
                                  types include "activeCells",
                                  "predictedCells", and "predictedActiveCells"

    @return (Plot) plot
    """
    if activityType == "predictedActiveCells":
      self._mmComputeTransitionTraces()

    cellTrace = copy.deepcopy(self._mmTraces[activityType].data)
    for i in xrange(len(cellTrace)):
      cellTrace[i] = self.getCellIndices(cellTrace[i])

    return self.mmGetCellTracePlot(cellTrace, self.numberOfCells(),
                                   activityType, title, showReset,
                                   resetShading)
