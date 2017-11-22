# jupyter nbconvert --to PDF --Exporter.preprocessors=[\"grader.Grader\"] IT105\ Assignment\ #1.ipynb 
# depends on: py 3.6, nbconvert, jupyter_client, ipykernel
import os
import re
import sys
import nbformat

from nbconvert import PDFExporter
from nbconvert.preprocessors import Preprocessor
from nbconvert.preprocessors import ExecutePreprocessor

class Grader(ExecutePreprocessor):
    def __init__(self, **kwargs):
        defaults = {
            'timeout': 10, 
            'kernel_name': 'python3', 
            'allow_errors': True,
            'raise_on_iopub_timeout': True,
            'interrupt_on_timeout': True,
            'shutdown_kernel': 'immediate'
        }

        defaults.update(kwargs)
        super().__init__(**defaults)

        self.grader = None
        self.annotations = {}
        self.pattern = re.compile('^#\s*([^\n]+)')

    def preprocess_cell(self, cell, resources, cell_index):
        self.position = cell_index
        cell, resources = super().preprocess_cell(cell, resources, cell_index)

        if self.grader and cell.cell_type == 'code':
            print("Grading " + self.grader + " ...", file=sys.stderr)
            getattr(self, self.grader)(cell)

        elif cell.cell_type == 'markdown':
            match = self.pattern.match(cell.source)

            if match:
                title = match.group(1).strip()
                words = [x.lower() for x in re.split('\W+', title)]
                function = '_'.join(words)

                if hasattr(self, function):
                    self.grader = function
                    return cell, resources
                else:
                    print("No grading function for '" + title + "' (" + function + ")", file=sys.stderr)
        
        self.grader = None
        return cell, resources

    def preprocess(self, nb, resources):
        nb, resources = super().preprocess(nb, resources)

        for position, annotations in self.annotations.items():
            for annotation in annotations:
                nb['cells'].insert(
                    position + 1,
                    nbformat.v4.new_markdown_cell(
                        source="> **" + annotation + "**"
                    )
                )  

        return nb, resources

    def annotate(self, string):
        self.annotations[self.position] = self.annotations.get(self.position,[])
        self.annotations[self.position].append(string)