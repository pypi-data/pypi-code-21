import time
from collections import defaultdict
from datetime import datetime

import numpy
from visdom import Visdom

from pyrsos.logger.plotting import plot_line


class Experiment(object):
    """
    Experiment class
    """

    def __init__(self, name, hparams):
        """

        Args:
            name (string): the name of the experiment
            hparams (object): the hypermarameters used for this experiment
        """
        self.name = name
        self.hparams = hparams
        self.metrics = defaultdict(Metric)

        self.timestamp_start = datetime.now()
        self.timestamp_update = datetime.now()
        self.last_update = time.time()

        self.viz = Visdom()

    def update_plots(self):
        for exp_name, metric in self.metrics.items():
            metric.update_plot()

    def add_metric(self, metric):
        """
        Add a metric to the experiment
        Args:
            metric (Metric): a metric object

        Returns:

        """
        metric.vic_context = self.viz
        self.metrics[metric.name] = metric


class Metric(object):
    """
    Metric hold the data of a value of the model that is being monitored

    A Metric object has to have a name,
    a vis_type which defines how it will be visualized
    and a dataset on which it will be attached to.
    """

    def __init__(self, name, vis_type, tags):
        """

        Args:
            name (str): the name of the metric
            vis_type (str): the visualization type
            tags (list): list of tags
        """
        self.name = name
        self.vis_type = vis_type
        self.tags = tags

        # a list that contains the values of the metric
        self._values = {tag: [] for tag in tags}

        # a helper list that contains the steps or times,
        # that each value was added to the Metric
        self._steps = {tag: [] for tag in tags}

        self.vic_context = None
        self._win = None

    def append(self, tag, value):
        """
        Add a value to the list of values of this metric
        Args:
            tag (str):
            value (int,float):

        Returns:

        """
        try:
            self._steps[tag].append(self._steps[tag][-1] + 1)
        except:
            self._steps[tag].append(1)

        self._values[tag].append(value)

    def update_plot(self):

        if self.vis_type == "line":
            plot_line(self.vic_context,
                      numpy.array([self._values[tag] for tag in self.tags]),
                      self.name, self.tags)
