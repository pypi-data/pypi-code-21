# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Base views for maintaining batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import HTML

from tailbone import grids
from tailbone.views import MasterView2
from tailbone.views.batch import BatchMasterView, FileBatchMasterView
from tailbone.views.batch.core import MobileBatchStatusFilter


class BatchMasterView2(MasterView2, BatchMasterView):
    """
    Base class for all "batch master" views
    """

    grid_columns = [
        'id',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'complete',
        'executed',
        'executed_by',
    ]

    def configure_grid(self, g):
        super(BatchMasterView2, self).configure_grid(g)

        g.joiners['created_by'] = lambda q: q.join(model.User, model.User.uuid == self.model_class.created_by_uuid)
        g.joiners['executed_by'] = lambda q: q.outerjoin(model.User, model.User.uuid == self.model_class.executed_by_uuid)

        g.filters['executed'].default_active = True
        g.filters['executed'].default_verb = 'is_null'

        # TODO: not sure this todo is still relevant?
        # TODO: in some cases grid has no sorters yet..e.g. when building query for bulk-delete
        # if hasattr(g, 'sorters'):
        g.sorters['created_by'] = g.make_sorter(model.User.username)
        g.sorters['executed_by'] = g.make_sorter(model.User.username)

        g.default_sortkey = 'id'
        g.default_sortdir = 'desc'

        g.set_enum('status_code', self.model_class.STATUS)

        g.set_type('created', 'datetime')
        g.set_type('executed', 'datetime')

        g.set_renderer('id', self.render_batch_id)

        g.set_link('id')
        g.set_link('description')
        g.set_link('created')
        g.set_link('executed')

        g.set_label('id', "Batch ID")
        g.set_label('created_by', "Created by")
        g.set_label('rowcount', "Rows")
        g.set_label('status_code', "Status")
        g.set_label('executed_by', "Executed by")

    def render_batch_id(self, batch, column):
        return batch.id_str

    def configure_row_grid(self, g):
        super(BatchMasterView2, self).configure_row_grid(g)

        g.filters['status_code'].set_value_renderer(grids.filters.EnumValueRenderer(self.model_row_class.STATUS))

        g.default_sortkey = 'sequence'

        g.set_enum('status_code', self.model_row_class.STATUS)

        g.set_renderer('status_code', self.render_row_status)

        g.set_label('sequence', "Seq.")
        g.set_label('status_code', "Status")
        g.set_label('item_id', "Item ID")

    def render_row_status(self, row, column):
        code = row.status_code
        if code is None:
            return ""
        text = self.model_row_class.STATUS.get(code, six.text_type(code))
        if row.status_text:
            return HTML.tag('span', title=row.status_text, c=text)
        return text


class FileBatchMasterView2(BatchMasterView2, FileBatchMasterView):
    """
    Base class for all file-based "batch master" views
    """
