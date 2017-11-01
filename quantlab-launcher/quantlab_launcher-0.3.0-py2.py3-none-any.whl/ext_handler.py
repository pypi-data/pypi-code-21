"""Tornado handlers for extra file extensions."""

# Copyright (c) Quant Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os
from tornado import gen, web

from notebook.services.contents.handlers import ContentsHandler

from .ext_manager import ExtContentsManager

class FileExtHandler(ContentsHandler):

    @property
    def contents_manager(self):
        return ExtContentsManager()
