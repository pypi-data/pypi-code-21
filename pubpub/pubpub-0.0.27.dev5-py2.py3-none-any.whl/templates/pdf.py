import io, os, nbformat
from jinja2 import DictLoader, Template, FileSystemLoader
from nbconvert import HTMLExporter
from pystache import render

from .base import Template
from .latex import LatexExporter
from scss import Compiler
from ..resources import data_dir
from ..utils import get_working_directory, preserve_cwd, execute_in_virtualenv


class PDFTemplate(Template):
  def process(self):
    """Convert the notebook into pdf"""
    self.bundle.prepare()

    latex_filename = self.bundle.complete_latex_filename()

    # LatexExporter(self.bundle).process()
    output_pdf = self.run_to_pdf(
        self.bundle,
        latex_filename,
    )

    return output_pdf

  @preserve_cwd
  def run_to_pdf(self, bundle, processed_file):
    basename = os.path.basename(processed_file).split(".")[0]
    args = [
        "pdflatex", "-output-directory=/tmp", "-synctex=1",
        "-interaction=nonstopmode",
        "\"%s\"" % processed_file, "&&", "mv", basename + ".pdf",
        self.bundle.output
    ]

    os.chdir(self.bundle.working_directory)
    return execute_in_virtualenv(args, self.bundle.virtualenv_name)
