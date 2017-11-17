"""
Functions for tweak MathJax

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.

THis code is copied from the rendernb checklet for Momotor <momotor.org>.
"""

import re
from nbformat import NotebookNode
from textwrap import dedent

__all__ = [
    'DEFAULT_MATHJAX_VERSION',
    'DEFAULT_MATHJAX_URL',
    'LOAD_MATHJAX_FUNCTION',
    'rewrite_mathjax',
]

DEFAULT_MATHJAX_VERSION = '2.7.1'
DEFAULT_MATHJAX_URL = ("https://cdnjs.cloudflare.com/ajax/libs/mathjax/{version}/MathJax.js?"
                       "config=TeX-AMS-MML_HTMLorMML-full,Safe")

LOAD_MATHJAX_FUNCTION = dedent("""\
    (function(src){
      if (!window.MathJax){
        window.MathJax = {
          tex2jax: {
            inlineMath: [ ['$![',']!$'] ],
            displayMath: [ ['$$![',']!$$'] ],
            processEscapes: true,
            processEnvironments: true
          },
          MathML: {
            extensions: ['content-mathml.js']
          },
          // Center justify equations in code and markdown cells. Elsewhere
          // we use CSS to left justify single line equations in code cells.
          displayAlign: 'center',
          "HTML-CSS": {
            availableFonts: [],
            imageFont: null,
            preferredFont: null,
            webFont: "STIX-Web",
            styles: {'.MathJax_Display': {"margin": 0}},
            linebreaks: { automatic: true }
          }
        };
    
        var tag = document.createElement('script');
        tag.src = src;
        tag.type = "text/javascript";
    
        document.head.appendChild(tag);
      }
      else {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
      }
    })
    """)

MATHJAX_REPLACE = (
    (re.compile(r'(?<!\$)\$(?!\$)(?!!)([^$]+?)\$(?!\$)'), r'$![\1]!$'),
    (re.compile(r'\\\((.+?)\\\)'), r'$![\1]!$'),
    (re.compile(r'(?<!\$)\${2}(?!\$)(?!!)([^$]+?)\${2}(?!\$)'), r'$$![\1]!$$'),
    (re.compile(r'\\\[(.+?)\\]'), r'$$![\1]!$$'),
)


def rewrite(source: str) -> str:
    for regexp, repl in MATHJAX_REPLACE:
        source = regexp.sub(repl, source)

    return source


def rewrite_mathjax(notebook: NotebookNode) -> bool:
    """Test notebook for MathJax formatting, replacing it with safer versions:
    * The inline $...$ and \(...\) tags become $![...]!$
    * The full line $$...$$ and \[...\] tags become $$![...]!$$

    .. note:: **Modifies**: ``notebook``

    :param notebook: notebook to rewrite
    :return: whether any replacements were made
    """
    detected = False

    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            source = cell.source
            if source:
                rewritten = rewrite(source)
                if source != rewritten:
                    cell.source = rewritten
                    detected = True

    return detected


def get_mathjax_script(version: str=DEFAULT_MATHJAX_VERSION, src: str=DEFAULT_MATHJAX_URL) -> str:
    """

    :param version: MathJax version
    :param src: MathJax URL
    :return: JavaScript MathJax function
    """
    if not src:
        src = DEFAULT_MATHJAX_URL

    return LOAD_MATHJAX_FUNCTION + '("{}")'.format(src.format(version=version))
