#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Sequana GUI. Can also be used for any snakemake pipeline"""
import sys
import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets as QW

from sequana.gui.ui_help import Ui_Help


helptxt = """
<div style="fontsize:12px">
<p>
<b>Sequanix</b> can be used to run Sequana NGS pipelines (see
<a href="http://sequana.readthedocs.io">Sequana.readthedocs.io</a> for details)
but also any Snakefile/configuration pairs
(see <a href="http://snakemake.readthedocs.io">snakemake.readthedocs.io</a>).
</p>
        <p>
        In both cases, a working directory must be set where the Snakefile
        and possibly a configuration file will be copied.
        </p>
        <p>The generic Snakefile must be executable meaning that users should
take care of dependencies. Sequana pipelines should work out of the box
(dependencies or Sequana pipelines being the same as <b>Sequanix</b>).</p>

        <h2>Sequana pipelines</h2>
        There are downloaded automatically with their config file from the
Sequana
        library. Here is a typical set of actions to run Sequana pipelines:

        <ol>
        <li> Select a pipeline</li>
        <li> Click on the Input tab and select one of this tab:</li>
            <ul>
           <li> directory: select all fastq.gz files</li>
           <li> samples: select a single-end or paired-end file(s)</li>
            </ul>
        <li> Select the working directory</li>
        </ol>

        <h2> Generic pipelines </h2>
        Similarly, if you have your own Snakefile (and config file)
        <ol>
        <li>Select a Snakefile </li>
        <li>Select a config file (optional)</li>
        <li> Select the working directory</li>
        </ol>

        <h2> Sequana pipeline dedicated help </help>
             %(pipelines)s
        </div>
"""


class HelpDialog(QW.QDialog):
    """todo"""
    def __init__(self, parent=None, pipelines=""):
        super().__init__(parent=parent)
        self.ui = Ui_Help()
        self.ui.setupUi(self)
        self.ui.textBrowser.setText(helptxt % {"pipelines": pipelines})
        self.ui.buttonBox.accepted.connect(self.close)

