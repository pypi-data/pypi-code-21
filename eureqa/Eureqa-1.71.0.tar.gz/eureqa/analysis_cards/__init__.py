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

from analysis_card import AnalysisCard
from distribution_plot_card import DistributionPlotCard
from model_card import ModelCard
from model_summary_card import ModelSummaryCard
from text_card import TextCard
from model_fit_by_row_plot_card import ModelFitByRowPlotCard
from model_fit_separation_plot_card import ModelFitSeparationPlotCard
from model_evaluator_card import ModelEvaluatorCard
from box_plot_card import BoxPlotCard
from double_histogram_plot_card import DoubleHistogramPlotCard
from scatter_plot_card import ScatterPlotCard
from binned_mean_plot_card import BinnedMeanPlotCard
from by_row_plot_card import ByRowPlotCard
from plot import Plot
from custom_plot_card import CustomPlotCard
from html_card import HtmlCard

import warnings
warnings.warn("The 'eureqa.analysis_cards' API is deprecated.  Please use the new 'eureqa.analysis.components' API.",
              DeprecationWarning)

__all__ = ['AnalysisCard',
           'DistributionPlotCard',
           'ModelCard',
           'ModelSummaryCard',
           'TextCard',
           'HtmlCard',
           'ModelFitByRowPlotCard',
           'ModelFitSeparationPlotCard',
           'ModelEvaluatorCard',
           'BoxPlotCard',
           'DoubleHistogramPlotCard',
           'ScatterPlotCard',
           'BinnedMeanPlotCard',
           'ByRowPlotCard',
           'Plot',
           'CustomPlotCard'
           ]
