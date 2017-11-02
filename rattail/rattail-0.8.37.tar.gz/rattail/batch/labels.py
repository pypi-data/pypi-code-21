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
Handler for label batches
"""

from __future__ import unicode_literals, absolute_import

import csv
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail import enum
from rattail.db import model, api
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.util import progress_loop
from rattail.time import make_utc
from rattail.config import parse_bool


log = logging.getLogger(__name__)


class LabelBatchHandler(BatchHandler):
    """
    Handler for Print Labels batches.
    """
    batch_model_class = model.LabelBatch

    def setup(self, batch, progress=None):
        self.now = make_utc()

    setup_populate = setup
    setup_refresh = setup

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make a new batch, with initial rows if applicable.
        """
        self.skip_first_line = parse_bool(kwargs.pop('skip_first_line', False))
        self.calc_check_digit = kwargs.pop('calc_check_digit', False)
        if self.calc_check_digit != 'upc':
            self.calc_check_digit = parse_bool(self.calc_check_digit)
        return super(LabelBatchHandler, self).make_batch(session, progress, **kwargs)

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from handheld batch, etc.
        """
        assert batch.handheld_batch or batch.filename or batch.products
        session = orm.object_session(batch)
        self.label_profile = self.get_label_profile(session)
        assert self.label_profile
        self.setup_populate(batch, progress=progress)

        def append(item, i):
            row = model.LabelBatchRow()
            row.label_code = self.label_profile.code
            row.label_profile = self.label_profile
            with session.no_autoflush:
                if isinstance(item, model.Product):
                    row.product = item
                    row.upc = row.product.upc
                    row.label_quantity = 1
                else: # item is handheld batch row
                    row.upc = item.upc
                    row.product = item.product
                    row.label_quantity = item.units or 1
                    # copy these in case product is null
                    row.brand_name = item.brand_name
                    row.description = item.description
                    row.size = item.size
                batch.add_row(row)
            self.refresh_row(row)

        if batch.handheld_batch:
            data = batch.handheld_batch.active_rows()
        elif batch.filename:
            data = self.read_products_from_file(batch, progress=progress)
        elif batch.products:
            data = batch.products

        assert progress_loop(append, data, progress,
                             message="Adding initial rows to batch")

    def read_products_from_file(self, batch, progress=None):
        """
        Returns list of Product objects based on lookup from CSV file data.

        # TODO: should this actually happen here? vs refresh and just mark product not found?
        """
        path = batch.filepath(self.config)
        with open(path, 'rb') as f:
            if self.skip_first_line:
                f.readline()
            reader = csv.reader(f)
            data = list(reader)

        products = []
        session = orm.object_session(batch)

        def append(entry, i):
            upc = entry[0].strip()
            if upc:
                upc = GPC(upc, calc_check_digit=self.calc_check_digit)
                product = api.get_product_by_upc(session, upc)
                if product:
                    products.append(product)
                else:
                    log.warning("product not found: {}".format(upc))

        if self.progress_loop(append, data, progress,
                              message="Reading data from CSV file"):
            return products

    def get_label_profile(self, session):
        code = self.config.get('rattail.batch', 'labels.default_code')
        if code:
            return session.query(model.LabelProfile)\
                          .filter(model.LabelProfile.code == code)\
                          .one()
        else:
            return session.query(model.LabelProfile)\
                          .order_by(model.LabelProfile.ordinal)\
                          .first()

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        if not row.product and row.upc:
            session = orm.object_session(row)
            row.product = api.get_product_by_upc(session, row.upc)
        if not row.product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        product = row.product
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None
        category = product.category
        row.category_code = category.code if category else None
        row.category_name = category.name if category else None
        regular_price = product.regular_price
        row.regular_price = regular_price.price if regular_price else None
        row.pack_quantity = regular_price.pack_multiple if regular_price else None
        row.pack_price = regular_price.pack_price if regular_price else None
        sale_price = product.current_price
        if sale_price:
            if (sale_price.type == enum.PRICE_TYPE_SALE and
                sale_price.starts and sale_price.starts <= self.now and
                sale_price.ends and sale_price.ends >= self.now):
                pass            # this is what we want
            else:
                sale_price = None
        row.sale_price = sale_price.price if sale_price else None
        row.sale_start = sale_price.starts if sale_price else None
        row.sale_stop = sale_price.ends if sale_price else None
        cost = product.cost
        vendor = cost.vendor if cost else None
        row.vendor_id = vendor.id if vendor else None
        row.vendor_name = vendor.name if vendor else None
        row.vendor_item_code = cost.code if cost else None
        row.case_quantity = cost.case_size if cost else None
        if row.regular_price:
            row.status_code = row.STATUS_OK
        else:
            row.status_code = row.STATUS_REGULAR_PRICE_UNKNOWN

    def execute(self, batch, progress=None, **kwargs):
        """
        Print some labels!
        """
        return self.print_labels(batch, progress)

    def print_labels(self, batch, progress=None):
        """
        Print all labels for the given batch.
        """
        profiles = {}

        def organize(row, i):
            profile = row.label_profile
            if profile.uuid not in profiles:
                profiles[profile.uuid] = profile
                profile.labels = []
            profile.labels.append((row.product, row.label_quantity))

        # filter out removed rows, and maybe inactive product rows
        rows = [row for row in batch.data_rows if not row.removed]
        if self.config.getbool('rattail.batch', 'labels.exclude_inactive_products', default=False):
            rows = [row for row in rows if row.status_code != row.STATUS_PRODUCT_APPEARS_INACTIVE]

        if not progress_loop(organize, rows, progress,
                             message="Organizing labels by type"):
            return False # user canceled

        # okay now print for real
        # TODO: this is compatible with legacy code but will re-read all needed
        # product data from master table instead of levaraging batch rows
        for profile in profiles.itervalues():
            printer = profile.get_printer(self.config)
            printer.print_labels(profile.labels, progress=progress)

        return True
