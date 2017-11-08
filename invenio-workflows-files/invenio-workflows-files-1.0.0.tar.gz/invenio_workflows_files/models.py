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

"""Models for Invenio-Workflows-Files."""

from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_workflows.models import WorkflowObjectModel
from sqlalchemy_utils.types import UUIDType


class WorkflowsBuckets(db.Model):
    """Relationship between WorkflowObject and Buckets."""

    __tablename__ = 'workflows_buckets'

    workflow_object_id = db.Column(
        db.Integer,
        db.ForeignKey(
            WorkflowObjectModel.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        primary_key=True,
        nullable=False,
    )

    bucket_id = db.Column(
        UUIDType,
        db.ForeignKey(
            Bucket.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        primary_key=True,
        nullable=False,
    )

    bucket = db.relationship(Bucket)
    workflow_object = db.relationship(WorkflowObjectModel)

    @classmethod
    def create(cls, workflow_object, bucket):
        """Create a new WorkflowsBuckets and adds it to the session."""
        rb = cls(workflow_object=workflow_object, bucket=bucket)
        db.session.add(rb)
        return rb


__all__ = ('WorkflowsBuckets',)
