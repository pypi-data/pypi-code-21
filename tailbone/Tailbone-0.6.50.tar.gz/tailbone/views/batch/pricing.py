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
Views for pricing batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.views.batch import BatchMasterView2 as BatchMasterView


class PricingBatchView(BatchMasterView):
    """
    Master view for pricing batches.
    """
    model_class = model.PricingBatch
    model_row_class = model.PricingBatchRow
    default_handler_spec = 'rattail.batch.pricing:PricingBatchHandler'
    model_title_plural = "Pricing Batches"
    route_prefix = 'batch.pricing'
    url_prefix = '/batches/pricing'
    creatable = False
    bulk_deletable = True
    rows_editable = True
    rows_bulk_deletable = True

    grid_columns = [
        'id',
        'description',
        'created',
        'created_by',
        'rowcount',
        # 'status_code',
        # 'complete',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'discounted_unit_cost',
        'old_price',
        'new_price',
        'price_margin',
        'price_diff',
        'status_code',
    ]

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.description,
                fs.min_diff_threshold,
                fs.notes,
                fs.created,
                fs.created_by,
                fs.executed,
                fs.executed_by,
            ])

    def configure_row_grid(self, g):
        super(PricingBatchView, self).configure_row_grid(g)

        g.set_type('old_price', 'currency')
        g.set_type('new_price', 'currency')
        g.set_type('price_diff', 'currency')

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('regular_unit_cost', "Reg. Cost")
        g.set_label('price_margin', "Margin")
        g.set_label('price_markup', "Markup")
        g.set_label('price_diff', "Diff")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_CANNOT_CALCULATE_PRICE:
            return 'warning'
        if row.status_code in (row.STATUS_PRICE_INCREASE, row.STATUS_PRICE_DECREASE):
            return 'notice'

    def _preconfigure_row_fieldset(self, fs):
        super(PricingBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(label="UPC")
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer)
        fs.old_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.new_price.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.price_diff.set(renderer=forms.renderers.CurrencyFieldRenderer)

    def configure_row_fieldset(self, fs):
        fs.configure(
            include=[
                fs.sequence,
                fs.product,
                fs.upc,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.department_number,
                fs.department_name,
                fs.vendor,
                fs.regular_unit_cost,
                fs.discounted_unit_cost,
                fs.old_price,
                fs.new_price,
                fs.price_diff,
                fs.price_margin,
                fs.price_markup,
                fs.status_code,
                fs.status_text,
            ])


def includeme(config):
    PricingBatchView.defaults(config)
