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
Handler for pricing batches
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler


class PricingBatchHandler(BatchHandler):
    """
    Handler for pricing batches.
    """
    batch_model_class = model.PricingBatch

    def populate(self, batch, progress=None):
        """
        Batch row data comes from product query.
        """
        assert batch.products
        session = orm.object_session(batch)

        def append(item, i):
            row = model.PricingBatchRow()
            row.product = item
            row.upc = row.product.upc
            self.add_row(batch, row)

        assert self.progress_loop(append, batch.products, progress,
                                  message="Adding initial rows to batch")

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        product = row.product
        assert product

        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None

        cost = product.cost
        row.vendor = cost.vendor if cost else None
        row.regular_unit_cost = cost.unit_cost if cost else None

        price = product.regular_price
        row.old_price = price.price if price else None

    def set_status_per_diff(self, row):
        """
        Set the row's status code according to its price diff
        """
        threshold = row.batch.min_diff_threshold
        minor = bool(threshold) and abs(row.price_diff) < threshold
        if row.price_diff > 0:
            if minor:
                row.status_code = row.STATUS_PRICE_INCREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_INCREASE
        elif row.price_diff < 0:
            if minor:
                row.status_code = row.STATUS_PRICE_DECREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_DECREASE
        else:
            row.status_code = row.STATUS_PRICE_UNCHANGED
