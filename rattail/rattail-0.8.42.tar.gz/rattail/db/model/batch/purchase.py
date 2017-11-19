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
Models for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import (Base, uuid_column, BatchMixin, BatchRowMixin,
                              PurchaseBase, PurchaseItemBase, PurchaseCreditBase,
                              Purchase, PurchaseItem)
from rattail.util import pretty_quantity


class PurchaseBatch(BatchMixin, PurchaseBase, Base):
    """
    Hopefully generic batch used for entering new purchases into the system, etc.?
    """
    batch_key = 'purchase'
    __tablename__ = 'purchase_batch'
    __batchrow_class__ = 'PurchaseBatchRow'
    model_title = "Purchasing Batch"
    model_title_plural = "Purchasing Batches"

    @declared_attr
    def __table_args__(cls):
        return cls.__batch_table_args__() + cls.__purchase_table_args__() + (
            sa.ForeignKeyConstraint(['purchase_uuid'], ['purchase.uuid'], name='purchase_batch_fk_purchase'),
        )

    STATUS_OK                   = 1
    STATUS_UNKNOWN_PRODUCT      = 2

    STATUS = {
        STATUS_OK:              "ok",
        STATUS_UNKNOWN_PRODUCT: "has unknown product(s)",
    }

    purchase_uuid = sa.Column(sa.String(length=32), nullable=True)

    purchase = orm.relationship(
        Purchase,
        doc="""
        Reference to the purchase with which the batch is associated.  May be
        null, e.g. in the case of a "new purchase" batch.
        """,
        backref=orm.backref(
            'batches',
            order_by='PurchaseBatch.id',
            doc="""
            List of batches associated with the purchase.
            """))

    mode = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric "mode" for the purchase batch, to indicate new/receiving etc.
    """)


class PurchaseBatchRow(BatchRowMixin, PurchaseItemBase, Base):
    """
    Row of data within a purchase batch.
    """
    __tablename__ = 'purchase_batch_row'
    __batch_class__ = PurchaseBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__batchrow_table_args__() + cls.__purchaseitem_table_args__() + (
            sa.ForeignKeyConstraint(['item_uuid'], ['purchase_item.uuid'], name='purchase_batch_row_fk_item'),
        )

    STATUS_OK                           = 1
    STATUS_PRODUCT_NOT_FOUND            = 2
    STATUS_COST_NOT_FOUND               = 3
    STATUS_CASE_QUANTITY_UNKNOWN        = 4
    STATUS_INCOMPLETE                   = 5
    STATUS_ORDERED_RECEIVED_DIFFER      = 6

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        STATUS_COST_NOT_FOUND           : "product found but not cost",
        STATUS_CASE_QUANTITY_UNKNOWN    : "case quantity not known",
        STATUS_INCOMPLETE               : "incomplete",
        STATUS_ORDERED_RECEIVED_DIFFER  : "ordered / received differ",
    }

    item_uuid = sa.Column(sa.String(length=32), nullable=True)

    item = orm.relationship(
        PurchaseItem,
        doc="""
        Reference to the purchase item with which the batch row is associated.
        May be null, e.g. in the case of a "new purchase" batch.
        """)


class PurchaseBatchCredit(PurchaseCreditBase, Base):
    """
    Represents a working copy of purchase credit tied to a batch row.
    """
    __tablename__ = 'purchase_batch_credit'

    @declared_attr
    def __table_args__(cls):
        return cls.__purchasecredit_table_args__() + (
            sa.ForeignKeyConstraint(['row_uuid'], ['purchase_batch_row.uuid'], name='purchase_batch_credit_fk_row'),
        )

    uuid = uuid_column()

    row_uuid = sa.Column(sa.String(length=32), nullable=True)

    row = orm.relationship(
        PurchaseBatchRow,
        doc="""
        Reference to the batch row with which the credit is associated.
        """,
        backref=orm.backref(
            'credits',
            doc="""
            List of :class:`PurchaseBatchCredit` instances for the row.
            """))

    def __unicode__(self):
        if self.cases_shorted is not None and self.units_shorted is not None:
            qty = "{} cases, {} units".format(
                pretty_quantity(self.cases_shorted),
                pretty_quantity(self.units_shorted))
        elif self.cases_shorted is not None:
            qty = "{} cases".format(pretty_quantity(self.cases_shorted))
        elif self.units_shorted is not None:
            qty = "{} units".format(pretty_quantity(self.units_shorted))
        else:
            qty = "??"
        qty += " {}".format(self.credit_type)
        if self.credit_type == 'expired' and self.expiration_date:
            qty += " ({})".format(self.expiration_date)
        if self.credit_type == 'mispick' and self.mispick_product:
            qty += " ({})".format(self.mispick_product)
        if self.invoice_total:
            return "{} = ${:0.2f}".format(qty, self.invoice_total)
        return qty
