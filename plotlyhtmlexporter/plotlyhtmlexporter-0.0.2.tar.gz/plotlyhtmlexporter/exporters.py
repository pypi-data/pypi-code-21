from nbconvert.exporters.html import HTMLExporter
from traitlets import List

from .preprocessors import PlotlySanitizeHTML


class PlotlyHTMLExporter(HTMLExporter):

    preprocessors = List(
        config=True,
        default_value=[PlotlySanitizeHTML, ],
        help="Preprocessor to recognize and trust Plotly Output",
    )
