"""
Functions for rendering

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.

Parts of this code are reworked from the rendernb checklet for Momotor <momotor.org>.
"""

from nbformat import NotebookNode
from typing import Any, Dict
from nbconvert import HTMLExporter
from .inline_attachments import InlineAttachmentsPreprocessor
from textwrap import dedent

ADDITIONAL_STYLES = dedent("""\
    div.inner_cell, div.output_subarea {
      flex: 1 auto !important;
    }
    """)

HTML_FRAME = dedent("""\
    <html>
    <head>
    <style>
    {css}
    </style>
    <script>
    {javascript}
    </script>
    </head>
    <body>
    {body}
    </body>
    </html>
    """)


def render_nb(notebook: NotebookNode) -> Dict[str, Any]:
    """Render notebook as html.

    :param notebook: notebook to render
    :return: html
    """
    resources = {}

    iapp = InlineAttachmentsPreprocessor()
    notebook, resources = iapp.preprocess(notebook, resources)

    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'

    body, resources = html_exporter.from_notebook_node(notebook)

    properties = {
        'body': body,
        'css': '',
        'javascript': ''
    }

    return HTML_FRAME.format(**properties)
