"""This module contains components used to build up analyses.

To add a component to an analysis, you use :any:`Analysis.create_card` method::

    h = HtmlBlock('This will render on a Card in an Analysis')
    analysis.create_card(h)

Or the :any:`Analysis.create_html_card` convenience methods::

    vl = VariableLink(datasource=self._data_source, variable_name=self._variables[0])
    analysis.create_html_card("Target variable is: {0}".format(analysis.html_ref(vl)))

"""

from .base import _Component
from .model_fit_by_row_plot import ModelFitByRowPlot
from .model import Model
from .model_fit_separation_plot import ModelFitSeparationPlot
from .model_evaluator import ModelEvaluator
from .distribution_plot import DistributionPlot
from .box_plot import BoxPlot
from .double_histogram_plot import DoubleHistogramPlot
from .scatter_plot import ScatterPlot
from .binned_mean_plot import BinnedMeanPlot
from .by_row_plot import ByRowPlot
from .custom_plot import CustomPlot
from .model_summary import ModelSummary
from .text_block import TextBlock
from .html_block import HtmlBlock
from .titled_layout import TitledLayout
from .magnitude_bar import MagnitudeBar
from .variable_link import VariableLink
from .search_link import SearchLink
from .search_builder_link import SearchBuilderLink
from .download_file import DownloadFile
from .tabbed_layout import TabbedLayout
from .dropdown_layout import DropdownLayout
from .layout import Layout
from .modal import Modal
from .modal_link import ModalLink
from .tooltip import Tooltip
from .table_builder import TableBuilder
from .formatted_text import FormattedText
from .image import Image
from .most_frequent_variables_plot import MostFrequentVariablesPlot
from .threshold_selection_plot import ThresholdSelectionPlot
from .model_terms_plot import ModelTermsPlot

__all__ = [
    '_Component',
    'ModelFitByRowPlot',
    'Model',
    'ModelFitSeparationPlot',
    'ModelEvaluator',
    'DistributionPlot',
    'BoxPlot',
    'DoubleHistogramPlot',
    'ScatterPlot',
    'BinnedMeanPlot',
    'ByRowPlot',
    'CustomPlot',
    'ModelSummary',
    'TextBlock',
    'HtmlBlock',
    'TitledLayout',
    'MagnitudeBar',
    'VariableLink',
    'SearchLink',
    'SearchBuilderLink',
    'DownloadFile',
    'TabbedLayout',
    'DropdownLayout',
    'Layout',
    'Modal',
    'ModalLink',
    'Tooltip',
    'TableBuilder',
    'FormattedText',
    'Image',
    'MostFrequentVariablesPlot',
    'ThresholdSelectionPlot',
    'ModelTermsPlot'
]
