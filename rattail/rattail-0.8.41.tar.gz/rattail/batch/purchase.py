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
Handler for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.batch import BatchHandler
from rattail.time import make_utc


class PurchaseBatchHandler(BatchHandler):
    """
    Handler for purchase order batches.
    """
    batch_model_class = model.PurchaseBatch

    # set this to True for handler to skip various "case" logic
    ignore_cases = False

    def should_populate(self, batch):
        # TODO: this probably should change soon, for now this works..
        return batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

    def populate(self, batch, progress=None):
        assert batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

        def append(item, i):
            row = model.PurchaseBatchRow()
            row.item = item
            row.product = item.product
            row.cases_ordered = item.cases_ordered
            row.units_ordered = item.units_ordered
            row.cases_received = item.cases_received
            row.units_received = item.units_received
            row.po_unit_cost = item.po_unit_cost
            row.po_total = item.po_total
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
                row.invoice_unit_cost = item.invoice_unit_cost
                row.invoice_total = item.invoice_total
            batch.add_row(row)
            self.refresh_row(row)

        assert self.progress_loop(append, batch.purchase.items, progress,
                                  message="Adding initial rows to batch")

    def refresh(self, batch, progress=None):
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            batch.po_total = 0
        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            batch.invoice_total = 0
        return super(PurchaseBatchHandler, self).refresh(batch, progress=progress)

    def refresh_batch_status(self, batch):
        if any([not row.product_uuid for row in batch.active_rows()]):
            batch.status_code = batch.STATUS_UNKNOWN_PRODUCT
        else:
            batch.status_code = batch.STATUS_OK

    def refresh_row(self, row, initial=False):
        """
        Refreshing a row will A) assume that ``row.product`` is already set to
        a valid product, and B) update various other fields on the row
        (description, size, etc.)  to reflect the current product data.  It
        also will adjust the batch PO total per the row PO total.
        """
        batch = row.batch
        product = row.product
        if not product:
            if row.upc:
                session = orm.object_session(row)
                product = api.get_product_by_upc(session, row.upc)
            if not product:
                # TODO: should we do more stuff here..?
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return
            row.product = product

        cost = row.product.cost_for_vendor(batch.vendor) or row.product.cost
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        if product.department:
            row.department_number = product.department.number
            row.department_name = product.department.name
        else:
            row.department_number = None
            row.department_name = None
        row.vendor_code = cost.code if cost else None
        new_case_quantity = cost.case_size if cost else None
        if new_case_quantity:
            row.case_quantity = new_case_quantity

        self.refresh_totals(row, cost, initial)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.status_code = row.STATUS_OK

        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            if (row.cases_received is None and row.units_received is None and
                row.cases_damaged is None and row.units_damaged is None and
                row.cases_expired is None and row.units_expired is None and
                row.cases_mispick is None and row.units_mispick is None):
                row.status_code = row.STATUS_INCOMPLETE
            else:
                if self.get_units_ordered(row) != self.get_units_accounted_for(row):
                    row.status_code = row.STATUS_ORDERED_RECEIVED_DIFFER
                else:
                    row.status_code = row.STATUS_OK

    def refresh_totals(self, row, cost, initial):
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.po_unit_cost = self.get_unit_cost(row.product, batch.vendor)
            if row.po_unit_cost:
                row.po_total = row.po_unit_cost * self.get_units_ordered(row)
                batch.po_total = (batch.po_total or 0) + row.po_total
            else:
                row.po_total = None

        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            row.invoice_unit_cost = (cost.unit_cost if cost else None) or row.po_unit_cost
            if row.invoice_unit_cost:
                row.invoice_total = row.invoice_unit_cost * self.get_units_accounted_for(row)
                batch.invoice_total = (batch.invoice_total or 0) + row.invoice_total
            else:
                row.invoice_total = None

    def get_unit_cost(self, product, vendor):
        """
        Must return the PO unit cost for the given product, from the given vendor.
        """
        cost = product.cost_for_vendor(vendor) or product.cost
        if cost:
            return cost.unit_cost

    def get_units_ordered(self, row):
        return (row.units_ordered or 0) + (row.case_quantity or 1) * (row.cases_ordered or 0)

    def get_units_received(self, row):
        return (row.units_received or 0) + row.case_quantity * (row.cases_received or 0)

    def get_units_shipped(self, row):
        units_damaged = (row.units_damaged or 0) + row.case_quantity * (row.cases_damaged or 0)
        units_expired = (row.units_expired or 0) + row.case_quantity * (row.cases_expired or 0)
        return self.get_units_received(row) + units_damaged + units_expired

    def get_units_accounted_for(self, row):
        units_mispick = (row.units_mispick or 0) + row.case_quantity * (row.cases_mispick or 0)
        return self.get_units_shipped(row) + units_mispick

    def update_order_counts(self, purchase, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                inventory.on_order = (inventory.on_order or 0) + (item.units_ordered or 0) + (
                    (item.cases_ordered or 0) * (item.case_quantity or 1))

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def execute(self, batch, user, progress=None):
        """
        Default behavior for executing a purchase batch will create a new
        purchase, by invoking :meth:`make_purchase()`.
        """
        session = orm.object_session(batch)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            purchase = self.make_purchase(batch, user, progress=progress)
            self.update_order_counts(purchase, progress=progress)
            return purchase

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            with session.no_autoflush:
                return self.receive_purchase(batch, progress=progress)

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            # TODO: finish this...
            # with session.no_autoflush:
            #     return self.cost_purchase(batch, progress=progress)
            purchase = batch.purchase
            purchase.invoice_date = batch.invoice_date
            purchase.status = self.enum.PURCHASE_STATUS_COSTED
            return purchase

        assert False

    def make_credits(self, batch, progress=None):
        session = orm.object_session(batch)
        mapper = orm.class_mapper(model.PurchaseBatchCredit)

        def copy(row, i):
            for batch_credit in row.credits:
                credit = model.PurchaseCredit()
                for prop in mapper.iterate_properties:
                    if isinstance(prop, orm.ColumnProperty) and hasattr(credit, prop.key):
                        setattr(credit, prop.key, getattr(batch_credit, prop.key))
                credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                session.add(credit)

        return self.progress_loop(copy, batch.active_rows(), progress,
                                  message="Creating purchase credits")

    def make_purchase(self, batch, user, progress=None):
        """
        Effectively clones the given batch, creating a new Purchase in the
        Rattail system.
        """
        session = orm.object_session(batch)
        purchase = model.Purchase()

        # TODO: should be smarter and only copy certain fields here
        skip_fields = [
            'date_received',
        ]
        for prop in orm.object_mapper(batch).iterate_properties:
            if prop.key in skip_fields:
                continue
            if hasattr(purchase, prop.key):
                setattr(purchase, prop.key, getattr(batch, prop.key))

        def clone(row, i):
            item = model.PurchaseItem()
            # TODO: should be smarter and only copy certain fields here
            for prop in orm.object_mapper(row).iterate_properties:
                if hasattr(item, prop.key):
                    setattr(item, prop.key, getattr(row, prop.key))
            purchase.items.append(item)

        assert self.progress_loop(clone, batch.active_rows(), progress,
                                  message="Creating purchase items")

        purchase.created = make_utc()
        purchase.created_by = user
        purchase.status = self.enum.PURCHASE_STATUS_ORDERED
        session.add(purchase)
        batch.purchase = purchase
        return purchase

    def receive_purchase(self, batch, progress=None):
        """
        Update the purchase for the given batch, to indicate received status.
        """
        session = orm.object_session(batch)
        purchase = batch.purchase
        if not purchase:
            batch.purchase = purchase = model.Purchase()

            # TODO: should be smarter and only copy certain fields here
            skip_fields = [
                'date_received',
            ]
            for prop in orm.object_mapper(batch).iterate_properties:
                if prop.key in skip_fields:
                    continue
                if hasattr(purchase, prop.key):
                    setattr(purchase, prop.key, getattr(batch, prop.key))

        purchase.invoice_number = batch.invoice_number
        purchase.invoice_date = batch.invoice_date
        purchase.invoice_total = batch.invoice_total
        purchase.date_received = batch.date_received

        # determine which fields we'll copy when creating new purchase item
        copy_fields = []
        for prop in orm.class_mapper(model.PurchaseItem).iterate_properties:
            if hasattr(model.PurchaseBatchRow, prop.key):
                copy_fields.append(prop.key)

        def update(row, i):
            item = row.item
            if not item:
                row.item = item = model.PurchaseItem()
                for field in copy_fields:
                    setattr(item, field, getattr(row, field))
                purchase.items.append(item)

            item.cases_received = row.cases_received
            item.units_received = row.units_received
            item.cases_damaged = row.cases_damaged
            item.units_damaged = row.units_damaged
            item.cases_expired = row.cases_expired
            item.units_expired = row.units_expired
            item.invoice_line_number = row.invoice_line_number
            item.invoice_case_cost = row.invoice_case_cost
            item.invoice_unit_cost = row.invoice_unit_cost
            item.invoice_total = row.invoice_total

        with session.no_autoflush:
            assert self.progress_loop(update, batch.active_rows(), progress,
                                      message="Updating purchase line items")

        purchase.status = self.enum.PURCHASE_STATUS_RECEIVED
        return purchase
