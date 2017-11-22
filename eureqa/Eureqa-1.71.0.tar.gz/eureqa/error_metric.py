# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class ErrorMetrics(object):
    """
    Stores the value of the error of an expression as compared to a model
    by a variety of different types of error-evaluation methods.

    :param float mean_absolute_error: Mean Absolute Error
    :param float mean_absolute_percentage_error: Mean Absolute Percentage Error
    :param float r2_goodness_of_fit: R^2 Goodness of Fit
    :param float correlation_coefficient: Correlation Coefficient
    :param float maximum_absolute_error: Maximum Absolute Error
    :param float signed_difference_between_lhs_and_rhs: Signed Difference Between LHS and RHS
    :param float area_under_roc_error: Area Under ROC Curve
    :param float log_loss_error: Log Loss Error
    :param float rank_correlation_1_minus_r: Rank Correlation
    :param float mean_square_error: Mean Squared Error
    :param float mean_squared_error_auc_hybrid: Mean Squared Error for Classification
    :param float mean_absolute_percentage_error: Mean Absolute Percentage Error

    :var float mean_absolute_error: Mean Absolute Error
    :var float mean_absolute_percentage_error: Mean Absolute Percentage Error
    :var float r2_goodness_of_fit: R^2 Goodness of Fit
    :var float correlation_coefficient: Correlation Coefficient
    :var float maximum_absolute_error: Maximum Absolute Error
    :var float signed_difference_between_lhs_and_rhs: Signed Difference Between LHS and RHS
    :var float area_under_roc_error: Area Under ROC Curve
    :var float log_loss_error: Log Loss Error
    :var float rank_correlation_1_minus_r: Rank Correlation
    :var float mean_square_error: Mean Squared Error
    :var float mean_squared_error_auc_hybrid: Mean Squared Error for Classification
    :var float mean_absolute_percentage_error: Mean Absolute Percentage Error
    """

    def __init__(self,
                 mean_absolute_error = None,
                 r2_goodness_of_fit = None,
                 correlation_coefficient = None,
                 maximum_absolute_error = None,
                 signed_difference_between_lhs_and_rhs = None,
                 area_under_roc_error = None,
                 log_loss_error = None,
                 rank_correlation_1_minus_r = None,
                 mean_square_error = None,
                 mean_squared_error_auc_hybrid = None,
                 mean_absolute_percentage_error = None,
                 _body = None):
        """ ErrorMetrics init """

        self.mean_absolute_error = mean_absolute_error
        self.mean_absolute_percentage_error = mean_absolute_percentage_error
        self.r2_goodness_of_fit = r2_goodness_of_fit
        self.correlation_coefficient = correlation_coefficient
        self.maximum_absolute_error = maximum_absolute_error
        self.signed_difference_between_lhs_and_rhs = signed_difference_between_lhs_and_rhs
        self.area_under_roc_error = area_under_roc_error
        self.log_loss_error = log_loss_error
        self.rank_correlation_1_minus_r = rank_correlation_1_minus_r
        self.mean_square_error = mean_square_error
        self.mean_squared_error_auc_hybrid = mean_squared_error_auc_hybrid
        self._series_id_value = None
        if _body is not None:
            self._from_json(_body)

    _metric_map = {
        'Mean Absolute Error': 'mean_absolute_error',
        'Mean Absolute Percentage Error': 'mean_absolute_percentage_error',
        'Mean Squared Error': 'mean_square_error',
        'R^2 Goodness of Fit': 'r2_goodness_of_fit',
        'Correlation Coefficient': 'correlation_coefficient',
        'Maximum Absolute Error': 'maximum_absolute_error',
        'Mean Logarithm Squared Error': '_mean_logarithm_squared_error',
        'Median Absolute Error': '_median_error',
        'Interquartile Mean Absolute Error': '_interquartile_mean_absolute_error',
        'Signed Difference Between LHS and RHS': 'signed_difference_between_lhs_and_rhs',
        'Implicit Derivative Error': '_implicit_derivative_error',
        'AIC Squared Error': '_squared_error_aic',
        'AIC Absolute Error': '_absolute_error_aic',
        'Area Under ROC Curve': 'area_under_roc_error',
        'Log Loss Error': 'log_loss_error',
        'Hinge Loss Error': '_hinge_loss_error',
        'Rank Correlation': 'rank_correlation_1_minus_r',
        'Slope Absolute Error': '_slope_absolute_error',
        'Mean Squared Error for Classification': 'mean_squared_error_auc_hybrid',
        'Maximum Classification Accuracy': '_maximum_classification_accuracy'
    }

    @property
    def series_id_value(self):
        return self._series_id_value

    def _from_json(self, json):
        self._body = json
        self._series_id_value = json.get('series_id_value')
        self._model = json.get('model')
        for elt in json['metrics']:
            setattr(self, self._metric_map[elt['metric_name']], elt['metric_value'])

    def _to_json(self):
        metrics = []
        for longname, slug in self._metric_map.iteritems():
            if hasattr(self, slug):
                metrics.append({'metric_name': longname, 'metric_value': getattr(self, slug)})
        return { 'metrics':         metrics,
                 'series_id_value': self.series_id_value}

"""Available error metrics:"""


def mean_absolute_error():
    """Mean Absolute Error error metric"""

    return 'Mean Absolute Error'

def mean_absolute_percentage_error():
    """Mean Absolute Percentage Error error metric"""

    return 'Mean Absolute Percentage Error'

def r2_goodness_of_fit():
    """R^2 Goodness of Fit error metric"""

    return 'R^2 Goodness of Fit'

def correlation_coefficient():
    """Correlation Coefficient error metric"""

    return 'Correlation Coefficient'

def maximum_absolute_error():
    """Maximum Absolute Error error metric"""

    return 'Maximum Absolute Error'

def _mean_logarithm_squared_error():
    """Mean Logarithm Squared Error error metric"""

    return 'Mean Logarithm Squared Error'

def _median_error():
    """Median Absolute Error error metric"""

    return 'Median Absolute Error'

def _interquartile_mean_absolute_error():
    """Interquartile Mean Absolute Error error metric"""

    return 'Interquartile Mean Absolute Error'

def signed_difference_between_lhs_and_rhs():
    """Signed Difference Between LHS and RHS error metric"""

    return 'Signed Difference Between LHS and RHS'

def _implicit_derivative_error():
    """Implicit Derivative Error error metric"""

    return 'Implicit Derivative Error'

def _squared_error_aic():
    """AIC Squared Error error metric"""

    return 'AIC Squared Error'

def _absolute_error_aic():
    """AIC Absolute Error error metric"""

    return 'AIC Absolute Error'

def area_under_roc_error():
    """Area Under ROC Curve error metric"""

    return 'Area Under ROC Curve'

def log_loss_error():
    """Log Loss Error error metric"""

    return 'Log Loss Error'

def _hinge_loss_error():
    """Hinge Loss Error error metric"""

    return 'Hinge Loss Error'

def rank_correlation_1_minus_r():
    """Rank Correlation error metric"""

    return 'Rank Correlation'

def _slope_absolute_error():
    """Slope Absolute Error error metric"""

    return 'Slope Absolute Error'

def mean_square_error():
    """Mean Squared Error error metric"""

    return 'Mean Squared Error'

def mean_squared_error_auc_hybrid():
    """Mean Squared Error for Classification error metric"""

    return 'Mean Squared Error for Classification'

def _maximum_classification_accuracy():
    """Maximum Classification Accuracy error metric"""

    return 'Maximum Classification Accuracy'
