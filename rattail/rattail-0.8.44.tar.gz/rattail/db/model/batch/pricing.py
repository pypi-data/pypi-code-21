# -*- coding: utf-8 -*-
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
Data model for pricing batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, BatchMixin, ProductBatchRowMixin, Vendor


class PricingBatch(BatchMixin, Base):
    """
    Primary data model for pricing batches.
    """
    __tablename__ = 'batch_pricing'
    __batchrow_class__ = 'PricingBatchRow'
    batch_key = 'pricing'
    model_title = "Pricing Batch"

    min_diff_threshold = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)

    calculate_for_manual = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    Flag indicating whether prices should be calculated for products which are
    manually priced under normal circumstances.
    """)


class PricingBatchRow(ProductBatchRowMixin, Base):
    """
    Row of data within a pricing batch.
    """
    __tablename__ = 'batch_pricing_row'
    __batch_class__ = PricingBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='batch_pricing_row_fk_vendor'),
        )

    STATUS_PRICE_UNCHANGED              = 1
    STATUS_PRICE_INCREASE               = 2
    STATUS_PRICE_DECREASE               = 3
    STATUS_PRODUCT_NOT_FOUND            = 4
    STATUS_PRODUCT_MANUALLY_PRICED      = 5
    STATUS_CANNOT_CALCULATE_PRICE       = 6
    STATUS_PRICE_INCREASE_MINOR         = 7
    STATUS_PRICE_DECREASE_MINOR         = 8

    STATUS = {
        STATUS_PRICE_UNCHANGED          : "price not changed",
        STATUS_PRICE_INCREASE           : "price increase",
        STATUS_PRICE_INCREASE_MINOR     : "price increase (minor)",
        STATUS_PRICE_DECREASE           : "price drop",
        STATUS_PRICE_DECREASE_MINOR     : "price drop (minor)",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        STATUS_PRODUCT_MANUALLY_PRICED  : "product is priced manually",
        STATUS_CANNOT_CALCULATE_PRICE   : "cannot calculate price",
    }

    vendor_uuid = sa.Column(sa.String(length=32), nullable=True)
    vendor = orm.relationship(Vendor)

    regular_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True)
    discounted_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True)

    old_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)
    price_margin = sa.Column(sa.Numeric(precision=5, scale=3), nullable=True)
    price_markup = sa.Column(sa.Numeric(precision=4, scale=2), nullable=True)
    new_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)
    price_diff = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True)

    manually_priced = sa.Column(sa.Boolean(), nullable=True, doc="""
    Optional flag to indicate whether the product is manually priced, under
    normal circumstances.
    """)
