# -*- coding: utf-8 -*-
"""
@file
@brief Defines a competition.
"""
import numpy
import pandas
from io import StringIO
from .metrics import mse, sklearn_metric, roc_auc_score_macro, roc_auc_score_micro


class Competition:
    """
    Defines a competition.
    """

    def __init__(self, cpt_id, link, name, description, metric, datafile=None, expected_values=None):
        """
        @param      cpt_id              competition id
        @param      link                link to the page, something like ``/competition``
        @param      name                name of the competition
        @param      metric              metric or list of metrics, list of metrics to compute
        @param      description         description
        @param      datafile            data file
        @param      expected_values     expected values for each metric
        """
        self.link = link
        self.name = name
        self.cpt_id = cpt_id
        if isinstance(metric, str):
            metric = metric.split(',')
        if not isinstance(metric, list):
            metric = [metric]
        self.metrics = metric
        self.datafile = datafile
        self.description = description
        self.expected_values = self._load_values(expected_values)

    def _load_values(self, values):
        """
        Converts values into a list of list of values,
        one per metrics.
        """
        if isinstance(values, str):
            if '\n' in values:
                st = StringIO(values)
                res = pandas.read_csv(st)
            else:
                if self.datafile is None:
                    self.datafile = values
                res = pandas.read_csv(values)
        elif isinstance(values, list):
            if len(values) == 0:
                raise ValueError("values cannot be empty")
            if isinstance(values[0], dict):
                res = pandas.DataFrame(values, header=None, dtype=float)
            else:
                res = pandas.DataFrame(numpy.array(values), dtype=float)
                if res.shape[0] < res.shape[1]:
                    res = res.T.reset_index(drop=True)
            res.columns = ["exp%d" % i for i in range(res.shape[1])]
        elif isinstance(values, pandas.DataFrame):
            res = values
        else:
            raise TypeError(
                "Unexpected type for expected_values: {0}".format(type(values)))
        return res

    def evaluate(self, values):
        """
        Evaluates received values.

        @param      values      list of values
        @return                 dictionary {metric: res}
        """
        res = {}
        values = self._load_values(values)
        for met in self.metrics:
            res[met] = self.evaluate_metric(met, self.expected_values, values)
        return res

    def evaluate_metric(self, met, exp, val):
        """
        Evaluates a metric.

        @param      met     metric
        @param      exp     expected value
        @param      val     values
        @return             result
        """
        if met == "mse":
            return mse(exp, val)
        elif met == "roc_auc_score_micro":
            return roc_auc_score_micro(exp, val)
        elif met == "roc_auc_score_macro":
            return roc_auc_score_macro(exp, val)
        else:
            return sklearn_metric(met, exp, val)

    @property
    def metric(self):
        """
        Returns the metrics in a single string.
        """
        return ",".join(self.metrics)

    def to_dict(self):
        """
        Convert a competition into a dictionary.
        """
        s = StringIO()
        self.expected_values.to_csv(s, index=False)
        val = s.getvalue()
        return dict(cpt_id=self.cpt_id, link=self.link, name=self.name,
                    description=self.description, expected_values=val,
                    metric=",".join(self.metrics), datafile=self.datafile)

    @staticmethod
    def to_records(list_cpt):
        """
        Converts a list of competitions into a list of dictionaries.
        """
        res = []
        for cpt in list_cpt:
            for met in cpt.metrics:
                s = StringIO()
                cpt.expected_values.to_csv(s, index=False)
                val = s.getvalue()
                d = dict(link=cpt.link, cpt_name=cpt.name, metric=met,
                         description=cpt.description, expected_values=val)
                res.append(d)
        return res
