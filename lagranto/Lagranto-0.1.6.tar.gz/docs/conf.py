# -*- coding: utf-8 -*-
#

import os
import sys
from unittest.mock import Mock

# path to the modules
sys.path.insert(0, os.path.abspath('../'))


on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    MOCK_MODULES = ['numpy', 'netCDF4', 'shapely', 'fiona',
                    'cartopy', 'numpy.ma', 'mpl_toolkits.basemap',
                    'pyproj', 'matplotlib.collections',
                    'matplotlib.colors', 'matplotlib.pyplot',
                    'cartopy.mpl', 'cartopy.mpl.geoaxes']

    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# -- General configuration ------------------------------------------------

# sphinx extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

# The suffix(es) of source filenames.
source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Lagranto'
copyright = u'2017, Nicolas Piaget'
author = u'Nicolas Piaget'


# The short X.Y version.
version = '0.1'
# The full version, including alpha/beta/rc tags.
release = '0.1'

# excluded directories for source files
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# HTML and HTML Help pages theme
html_theme = 'alabaster'


html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
}

html_search_language = 'en'

# Output file base name for HTML help builder.
htmlhelp_basename = 'LagrantoDoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  (master_doc, 'LagrantoDoc.tex', u'Lagranto Documentation',
   u'Nicolas Piaget', 'manual'),
]
