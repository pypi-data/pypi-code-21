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
Views for handheld batches
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail import enum
from rattail.db import model
from rattail.util import OrderedDict

import formalchemy as fa
import formencode as fe
from webhelpers2.html import tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views.batch import FileBatchMasterView2 as FileBatchMasterView


ACTION_OPTIONS = OrderedDict([
    ('make_label_batch', "Make a new Label Batch"),
    ('make_inventory_batch', "Make a new Inventory Batch"),
])


class ExecutionOptions(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    action = fe.validators.OneOf(ACTION_OPTIONS)


class InventoryBatchFieldRenderer(fa.FieldRenderer):
    """
    Renderer for handheld batch's "inventory batch" field.
    """

    def render_readonly(self, **kwargs):
        batch = self.raw_value
        if batch:
            return tags.link_to(
                batch.id_str,
                self.request.route_url('batch.inventory.view', uuid=batch.uuid))
        return ''



class HandheldBatchView(FileBatchMasterView):
    """
    Master view for handheld batches.
    """
    model_class = model.HandheldBatch
    default_handler_spec = 'rattail.batch.handheld:HandheldBatchHandler'
    model_title_plural = "Handheld Batches"
    route_prefix = 'batch.handheld'
    url_prefix = '/batch/handheld'
    execution_options_schema = ExecutionOptions
    editable = False

    model_row_class = model.HandheldBatchRow
    rows_creatable = False
    rows_editable = True

    grid_columns = [
        'id',
        'device_type',
        'device_name',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'cases',
        'units',
        'status_code',
    ]

    def configure_grid(self, g):
        super(HandheldBatchView, self).configure_grid(g)
        device_types = OrderedDict(sorted(self.enum.HANDHELD_DEVICE_TYPE.items(),
                                          key=lambda item: item[1]))
        g.set_enum('device_type', device_types)

    def grid_extra_class(self, batch, i):
        if batch.status_code is not None and batch.status_code != batch.STATUS_OK:
            return 'notice'

    def _preconfigure_fieldset(self, fs):
        super(HandheldBatchView, self)._preconfigure_fieldset(fs)
        device_types = OrderedDict(sorted(self.enum.HANDHELD_DEVICE_TYPE.items(),
                                          key=lambda item: item[1]))
        fs.device_type.set(renderer=forms.renderers.EnumFieldRenderer(device_types))

    def configure_fieldset(self, fs):
        if self.creating:
            fs.configure(
                include=[
                    fs.filename,
                    fs.device_type,
                    fs.device_name,
                ])

        else:
            fs.configure(
                include=[
                    fs.id,
                    fs.device_type,
                    fs.device_name,
                    fs.filename,
                    fs.created,
                    fs.created_by,
                    fs.rowcount,
                    fs.status_code,
                    fs.executed,
                    fs.executed_by,
                ])

        if self.viewing and fs.model.inventory_batch:
            fs.append(fa.Field('inventory_batch', value=fs.model.inventory_batch, renderer=InventoryBatchFieldRenderer))

    def get_batch_kwargs(self, batch):
        kwargs = super(HandheldBatchView, self).get_batch_kwargs(batch)
        kwargs['device_type'] = batch.device_type
        kwargs['device_name'] = batch.device_name
        return kwargs

    def configure_row_grid(self, g):
        super(HandheldBatchView, self).configure_row_grid(g)
        g.set_type('cases', 'quantity')
        g.set_type('units', 'quantity')
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'

    def _preconfigure_row_fieldset(self, fs):
        super(HandheldBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(readonly=True, label="UPC", renderer=forms.renderers.GPCFieldRenderer,
                   attrs={'link': lambda r: self.request.route_url('products.view', uuid=r.product_uuid)})
        fs.brand_name.set(readonly=True)
        fs.description.set(readonly=True)
        fs.size.set(readonly=True)

    def configure_row_fieldset(self, fs):
        fs.configure(
            include=[
                fs.sequence,
                fs.upc,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.status_code,
                fs.cases,
                fs.units,
            ])

    def get_exec_options_kwargs(self, **kwargs):
        kwargs['ACTION_OPTIONS'] = list(ACTION_OPTIONS.iteritems())
        return kwargs

    def get_execute_success_url(self, batch, result, **kwargs):
        if kwargs['action'] == 'make_inventory_batch':
            return self.request.route_url('batch.inventory.view', uuid=result.uuid)
        elif kwargs['action'] == 'make_label_batch':
            return self.request.route_url('labels.batch.view', uuid=result.uuid)
        return super(HandheldBatchView, self).get_execute_success_url(batch)

    def get_execute_results_success_url(self, result, **kwargs):
        batch = result
        return self.get_execute_success_url(batch, result, **kwargs)


def includeme(config):
    HandheldBatchView.defaults(config)
