#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__version__ = "0.0.13"
__short_description__ = "A utility tool to help you build better sphinx documents"
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@me.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@me.com"
__github_username__ = "MacHu-GWU"

try:
    from .api_reference_doc import ApiReferenceDoc
    from .doctree import DocTree
except Exception as e:  # pragma: no cover
    print(e)
