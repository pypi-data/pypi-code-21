# -*- coding: utf-8 -*-

# import sys, os

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'ZSPARQLMethod'
copyright = u'2011, Eau de Web'

from Products.ZSPARQLMethod import __version__ as version
release = version

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'ZSPARQLMethoddoc'
