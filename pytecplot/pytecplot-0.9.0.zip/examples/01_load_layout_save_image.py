import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import tecplot

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.lay')

tecplot.load_layout(infile)
tecplot.export.save_png('layout_example.png', 600, supersample=3)
