#!/usr/bin/env python

# docutils GLEP support
# Copyright (c) 2017 Gentoo Foundation
# Placed in public domain
# based on PEP code by:
#
# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 1.1 $
# Date: $Date: 2004/07/20 18:23:59 $
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing HTML from GLEP
(Python Enhancement Proposal) documents.
"""

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


def main():
    description = ('Generates (X)HTML from reStructuredText-format GLEP files.  '
                   + default_description)

    publish_cmdline(reader_name='docutils_glep',
                    writer_name='docutils_glep',
                    description=description)

if __name__ == '__main__':
    main()
