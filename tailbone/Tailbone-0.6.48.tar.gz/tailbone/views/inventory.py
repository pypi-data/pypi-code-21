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
Views for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import re

import six

from rattail import pod
from rattail.db import model, api
from rattail.time import localtime
from rattail.gpc import GPC
from rattail.util import pretty_quantity

import formalchemy as fa
import formencode as fe

from tailbone import forms
from tailbone.views.batch import BatchMasterView2 as BatchMasterView


class InventoryBatchView(BatchMasterView):
    """
    Master view for inventory batches.
    """
    model_class = model.InventoryBatch
    model_title_plural = "Inventory Batches"
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'batch.inventory'
    url_prefix = '/batch/inventory'
    index_title = "Inventory"
    creatable = False
    mobile_creatable = True
    mobile_rows_creatable = True

    grid_columns = [
        'id',
        'created',
        'created_by',
        'description',
        'mode',
        'rowcount',
        'total_cost',
        'executed',
        'executed_by',
    ]

    model_row_class = model.InventoryBatchRow
    rows_editable = True

    row_grid_columns = [
        'sequence',
        'upc',
        'item_id',
        'brand_name',
        'description',
        'size',
        'previous_units_on_hand',
        'cases',
        'units',
        'unit_cost',
        'total_cost',
        'status_code',
    ]

    def configure_grid(self, g):
        super(InventoryBatchView, self).configure_grid(g)
        g.set_enum('mode', self.enum.INVENTORY_MODE)
        g.set_type('total_cost', 'currency')
        g.set_label('mode', "Count Mode")

    def render_mobile_listitem(self, batch, i):
        return "({}) {} rows - {}, {}".format(
            batch.id_str,
            "?" if batch.rowcount is None else batch.rowcount,
            batch.created_by,
            localtime(self.request.rattail_config, batch.created, from_utc=True).strftime('%Y-%m-%d'))

    def editable_instance(self, batch):
        return True

    def mutable_batch(self, batch):
        return not batch.executed and not batch.complete and batch.mode != self.enum.INVENTORY_MODE_ZERO_ALL

    def allow_worksheet(self, batch):
        return self.mutable_batch(batch)

    def _preconfigure_fieldset(self, fs):
        super(InventoryBatchView, self)._preconfigure_fieldset(fs)
        permission_prefix = self.get_permission_prefix()

        modes = dict(self.enum.INVENTORY_MODE)
        if not self.request.has_perm('{}.create.replace'.format(permission_prefix)):
            if hasattr(self.enum, 'INVENTORY_MODE_REPLACE'):
                modes.pop(self.enum.INVENTORY_MODE_REPLACE, None)
            if hasattr(self.enum, 'INVENTORY_MODE_REPLACE_ADJUST'):
                modes.pop(self.enum.INVENTORY_MODE_REPLACE_ADJUST, None)
        if not self.request.has_perm('{}.create.zero'.format(permission_prefix)):
            if hasattr(self.enum, 'INVENTORY_MODE_ZERO_ALL'):
                modes.pop(self.enum.INVENTORY_MODE_ZERO_ALL, None)

        fs.mode.set(renderer=forms.renderers.EnumFieldRenderer(modes),
                    label="Count Mode", required=True, attrs={'auto-enhance': 'true'})
        # if len(modes) == 1:
        #     fs.mode.set(readonly=True)

        fs.total_cost.set(readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)
        fs.append(fa.Field('handheld_batches', renderer=forms.renderers.HandheldBatchesFieldRenderer, readonly=True,
                           value=lambda b: b._handhelds))

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.description,
                fs.created,
                fs.created_by,
                fs.handheld_batches,
                fs.mode,
                fs.reason_code,
                fs.rowcount,
                fs.complete,
                fs.executed,
                fs.executed_by,
            ])
        if not self.creating:
            fs.mode.set(readonly=True)
            fs.reason_code.set(readonly=True)

    def row_editable(self, row):
        return self.mutable_batch(row.batch)

    def row_deletable(self, row):
        return self.mutable_batch(row.batch)

    def save_edit_row_form(self, form):
        row = form.fieldset.model
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).save_edit_row_form(form)

    def delete_row(self):
        row = self.Session.query(model.InventoryBatchRow).get(self.request.matchdict['uuid'])
        if not row:
            raise self.notfound()
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).delete_row()

    def configure_mobile_fieldset(self, fs):
        fs.configure(include=[
            fs.mode,
            fs.reason_code,
            fs.rowcount,
            fs.complete,
            fs.executed,
            fs.executed_by,
        ])
        batch = fs.model
        if self.creating:
            del fs.rowcount
        if not batch.executed:
            del [fs.executed, fs.executed_by]
            if not batch.complete:
                del fs.complete
        else:
            del fs.complete

    # TODO: this view can create new rows, with only a GET query.  that should
    # probably be changed to require POST; for now we just require the "create
    # batch row" perm and call it good..
    def mobile_row_from_upc(self):
        """
        Locate and/or create a row within the batch, according to the given
        product UPC, then redirect to the row view page.
        """
        batch = self.get_instance()
        row = None
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if upc:

            # try to locate general product by UPC; add to batch either way
            provided = GPC(upc, calc_check_digit=False)
            checked = GPC(upc, calc_check_digit='upc')
            product = api.get_product_by_upc(self.Session(), provided)
            if not product:
                product = api.get_product_by_upc(self.Session(), checked)
            row = model.InventoryBatchRow()
            if product:
                row.product = product
                row.upc = product.upc
            else:
                row.upc = provided # TODO: why not 'checked' instead? how to choose?
                row.description = "(unknown product)"
            self.handler.add_row(batch, row)

        self.Session.flush()
        return self.redirect(self.mobile_row_route_url('view', uuid=row.uuid))

    def template_kwargs_view_row(self, **kwargs):
        row = kwargs['instance']
        kwargs['product_image_url'] = pod.get_image_url(self.rattail_config, row.upc)
        return kwargs

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(InventoryBatchView, self).get_batch_kwargs(batch, mobile=False)
        kwargs['mode'] = batch.mode
        kwargs['complete'] = False
        kwargs['reason_code'] = batch.reason_code
        return kwargs

    def get_mobile_row_data(self, batch):
        # we want newest on top, for inventory batch rows
        return self.get_row_data(batch)\
                   .order_by(self.model_row_class.sequence.desc())

    # TODO: ugh, the hackiness.  needs a refactor fo sho
    def mobile_view_row(self):
        """
        Mobile view for inventory batch rows.  Note that this also handles
        updating a row...ugh.
        """
        self.viewing = True
        row = self.get_row_instance()
        parent = self.get_parent(row)
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'product_image_url': pod.get_image_url(self.rattail_config, row.upc),
            'form': form,
        }

        if self.request.has_perm('{}.edit'.format(self.get_row_permission_prefix())):
            update_form = forms.SimpleForm(self.request, schema=InventoryForm)
            if update_form.validate():
                row = update_form.data['row']
                cases = update_form.data['cases']
                units = update_form.data['units']
                if cases:
                    row.cases = cases
                    row.units = None
                elif units:
                    row.cases = None
                    row.units = units
                self.handler.refresh_row(row)
                return self.redirect(self.request.route_url('mobile.{}.view'.format(self.get_route_prefix()), uuid=row.batch_uuid))

        return self.render_to_response('view_row', context, mobile=True)

    def get_row_instance_title(self, row):
        if row.upc:
            return row.upc.pretty()
        if row.item_id:
            return row.item_id
        return "row {}".format(row.sequence)

    def configure_row_grid(self, g):
        super(InventoryBatchView, self).configure_row_grid(g)

        g.set_type('previous_units_on_hand', 'quantity')
        g.set_type('cases', 'quantity')
        g.set_type('units', 'quantity')
        g.set_type('unit_cost', 'currency')
        g.set_type('total_cost', 'currency')

        # TODO: i guess row grids don't support this properly yet?
        # g.set_link('upc')
        # g.set_link('item_id')
        # g.set_link('description')

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('status_code', "Status")
        g.set_label('previous_units_on_hand', "Prev. On Hand")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'

    def render_mobile_row_listitem(self, row, i):
        description = row.product.full_description if row.product else row.description
        unit_uom = 'LB' if row.product and row.product.weighed else 'EA'
        qty = "{} {}".format(pretty_quantity(row.cases or row.units), 'CS' if row.cases else unit_uom)
        return "({}) {} - {}".format(row.upc.pretty(), description, qty)

    def _preconfigure_row_fieldset(self, fs):
        super(InventoryBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(readonly=True, label="UPC", renderer=forms.renderers.GPCFieldRenderer,
                   attrs={'link': lambda r: self.request.route_url('products.view', uuid=r.product_uuid)})
        fs.item_id.set(readonly=True)
        fs.brand_name.set(readonly=True)
        fs.description.set(readonly=True)
        fs.size.set(readonly=True)
        fs.previous_units_on_hand.set(label="Prev. On Hand")
        fs.cases.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.unit_cost.set(readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)
        fs.total_cost.set(readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_fieldset(self, fs):
        fs.configure(
            include=[
                fs.sequence,
                fs.upc,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.status_code,
                fs.previous_units_on_hand,
                fs.cases,
                fs.units,
                fs.unit_cost,
                fs.total_cost,
            ])

    @classmethod
    def defaults(cls, config):
        cls._batch_defaults(config)
        cls._defaults(config)
        cls._inventory_defaults(config)

    @classmethod
    def _inventory_defaults(cls, config):
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # mobile - make new row from UPC
        config.add_route('mobile.{}.row_from_upc'.format(route_prefix), '/mobile{}/{{{}}}/row-from-upc'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_row_from_upc', route_name='mobile.{}.row_from_upc'.format(route_prefix),
                        permission='{}.create_row'.format(permission_prefix))

        # extra perms for creating batches per "mode"
        config.add_tailbone_permission(permission_prefix, '{}.create.replace'.format(permission_prefix),
                                       "Create new {} with 'replace' mode".format(model_title))
        config.add_tailbone_permission(permission_prefix, '{}.create.zero'.format(permission_prefix),
                                       "Create new {} with 'zero' mode".format(model_title))


class ValidBatchRow(forms.validators.ModelValidator):
    model_class = model.InventoryBatchRow

    def _to_python(self, value, state):
        row = super(ValidBatchRow, self)._to_python(value, state)
        if row.batch.executed:
            raise fe.Invalid("Batch has already been executed", value, state)
        return row


class InventoryForm(forms.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    row = ValidBatchRow()
    cases = fe.validators.Number()
    units = fe.validators.Number()


def includeme(config):
    InventoryBatchView.defaults(config)
