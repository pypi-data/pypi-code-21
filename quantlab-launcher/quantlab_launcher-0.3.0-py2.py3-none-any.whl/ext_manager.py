"""ContentsManager for extra file extensions."""

# Copyright (c) Quant Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os

from notebook.services.contents.manager import ContentsManager

class ExtContentsManager(ContentsManager):

    def new_untitled(self, path='', type='', ext=''):
        """Create a new untitled file or directory in path

        path must be a directory

        File extension can be specified.

        Use `new` to create files with a fully specified path (including filename).
        """
        path = path.strip('/')
        if not self.dir_exists(path):
            raise HTTPError(404, 'No such directory: %s' % path)

        model = {}
        if type:
            model['type'] = type

        if ext == '.ipynb':
            model.setdefault('type', 'notebook')
        else:
            model.setdefault('type', 'file')

        insert = ''
        if model['type'] == 'directory':
            untitled = self.untitled_directory
            insert = ' '
        elif model['type'] == 'notebook':
            untitled = self.untitled_notebook
            ext = '.ipynb'
        elif model['type'] == 'file':
            untitled = self.untitled_file
        elif model['type'] == 'spreadsheet':
            untitled = self.untitled_file
        elif model['type'] == 'calendar':
            untitled = self.untitled_file
        elif model['type'] == 'highcharts':
            untitled = self.untitled_file
        else:
            raise HTTPError(400, "Unexpected model type: %r" % model['type'])

        name = self.increment_filename(untitled + ext, path, insert=insert)
        path = u'{0}/{1}'.format(path, name)
        return self.new(model, path)
