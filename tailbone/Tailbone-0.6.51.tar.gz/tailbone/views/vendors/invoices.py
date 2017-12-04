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
Views for maintaining vendor invoices
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model, api
from rattail.vendors.invoices import iter_invoice_parsers, require_invoice_parser

import formalchemy

from tailbone.db import Session
from tailbone.views.batch import FileBatchMasterView2 as FileBatchMasterView


class VendorInvoicesView(FileBatchMasterView):
    """
    Master view for vendor invoice batches.
    """
    model_class = model.VendorInvoice
    model_row_class = model.VendorInvoiceRow
    default_handler_spec = 'rattail.batch.vendorinvoice:VendorInvoiceHandler'
    url_prefix = '/vendors/invoices'

    grid_columns = [
        'created',
        'created_by',
        'vendor',
        'filename',
        'executed',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_code',
        'shipped_cases',
        'shipped_units',
        'unit_cost',
        'status_code',
    ]

    def get_instance_title(self, batch):
        return unicode(batch.vendor)

    def configure_grid(self, g):
        super(VendorInvoicesView, self).configure_grid(g)
        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

    def configure_fieldset(self, fs):
        fs.purchase_order_number.set(label=self.handler.po_number_title)
        fs.purchase_order_number.set(validate=self.validate_po_number)
        fs.filename.set(label="Invoice File")

        fs.configure(
            include=[
                fs.vendor.readonly(),
                fs.filename,
                fs.parser_key,
                fs.purchase_order_number,
                fs.invoice_date.readonly(),
                fs.created,
                fs.created_by,
                fs.executed,
                fs.executed_by,
                ])

        if self.creating:
            parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)
            parser_options = [(p.display, p.key) for p in parsers]
            parser_options.insert(0, ("(please choose)", ''))
            fs.parser_key.set(label="File Type",
                              renderer=formalchemy.fields.SelectFieldRenderer,
                              options=parser_options)
            del fs.vendor
            del fs.invoice_date

        else:
            del fs.parser_key

    def validate_po_number(self, value, field):
        """
        Let the invoice handler in effect determine if the user-provided
        purchase order number is valid.
        """
        parser_key = field.parent.parser_key.value
        if not parser_key:
            raise formalchemy.ValidationError("Cannot validate PO number until File Type is chosen")
        parser = require_invoice_parser(parser_key)
        vendor = api.get_vendor(Session(), parser.vendor_key)
        try:
            self.handler.validate_po_number(value, vendor)
        except ValueError as error:
            raise formalchemy.ValidationError(unicode(error))

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorInvoicesView, self).get_batch_kwargs(batch)
        kwargs['parser_key'] = batch.parser_key
        return kwargs

    def init_batch(self, batch):
        parser = require_invoice_parser(batch.parser_key)
        vendor = api.get_vendor(Session(), parser.vendor_key)
        if not vendor:
            self.request.session.flash("No vendor setting found in database for key: {}".format(parser.vendor_key))
            return False
        batch.vendor = vendor
        return True

    def configure_row_grid(self, g):
        super(VendorInvoicesView, self).configure_row_grid(g)
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('shipped_cases', "Cases")
        g.set_label('shipped_units', "Units")

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_NOT_IN_DB,
                               row.STATUS_COST_NOT_IN_DB,
                               row.STATUS_NO_CASE_QUANTITY):
            return 'warning'
        if row.status_code in (row.STATUS_NOT_IN_PURCHASE,
                               row.STATUS_NOT_IN_INVOICE,
                               row.STATUS_DIFFERS_FROM_PURCHASE):
            return 'notice'


def includeme(config):
    VendorInvoicesView.defaults(config)
