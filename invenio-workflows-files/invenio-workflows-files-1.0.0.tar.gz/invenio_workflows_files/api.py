# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Version information for Invenio-Workflows-Files."""

from collections import OrderedDict

from flask import current_app
from invenio_files_rest.models import Bucket
from invenio_records_files.api import FileObject, FilesIterator
from invenio_workflows import WorkflowObject as _WorkflowObject

from .models import WorkflowsBuckets


class WorkflowFilesIterator(FilesIterator):
    """Iterator for files."""

    def __init__(self, workflow_object, bucket, file_cls=None):
        """Initialize iterator."""
        self._it = None
        self.record = workflow_object.data
        self.model = workflow_object
        self.file_cls = file_cls or FileObject
        self.bucket = bucket
        self.record.setdefault('_files', [])
        self.filesmap = OrderedDict([
            (f['key'], f) for f in self.record['_files']
        ])


class WorkflowObject(_WorkflowObject):
    """Define API for files manipulation using ``FilesMixin``."""

    files_iterator = WorkflowFilesIterator
    file_cls = FileObject

    def _create_bucket(self, location=None, storage_class=None):
        """Create file bucket for workflow object."""
        if location is None:
            location = current_app.config[
                'WORKFLOWS_DEFAULT_FILE_LOCATION_NAME'
            ]
        if storage_class is None:
            storage_class = current_app.config[
                'WORKFLOWS_DEFAULT_STORAGE_CLASS'
            ]
        bucket = Bucket.create(
            location=location,
            storage_class=storage_class
        )
        WorkflowsBuckets.create(workflow_object=self.model, bucket=bucket)
        return bucket

    @property
    def files(self):
        """Get files iterator."""
        workflows_bucket = WorkflowsBuckets.query.filter_by(
            workflow_object_id=self.id).first()

        if not workflows_bucket:
            bucket = self._create_bucket()
        else:
            bucket = workflows_bucket.bucket

        return self.files_iterator(self, bucket=bucket, file_cls=self.file_cls)
