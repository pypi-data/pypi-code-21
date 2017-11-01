# coding: utf-8
"""Jupyter QuantLab Launcher"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from notebook.notebookapp import NotebookApp
from traitlets import Unicode

from .handlers import add_handlers, QuantLabConfig


class QuantLabLauncherApp(NotebookApp):

    default_url = Unicode('/quatlab',
        help="The default URL to redirect to from `/`")

    quantlab_config = QuantLabConfig()

    def start(self):
        add_handlers(self.web_app, self.quantlab_config)
        NotebookApp.start(self)


main = QuantLabLauncherApp.launch_instance
