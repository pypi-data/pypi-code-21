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
Views for "true" purchase orders
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import formalchemy as fa
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView


class BatchesFieldRenderer(fa.FieldRenderer):

    def render_readonly(self, **kwargs):
        batches = self.raw_value
        if not batches:
            return ''

        enum = self.request.rattail_config.get_enum()

        routes = {
            enum.PURCHASE_BATCH_MODE_ORDERING: 'ordering.view',
            enum.PURCHASE_BATCH_MODE_RECEIVING: 'receiving.view',
        }

        def render(batch):
            if batch.executed:
                actor = batch.executed_by
                pending = ''
            else:
                actor = batch.created_by
                pending = ' (pending)'
            display = '{} ({} by {}){}'.format(batch.id_str,
                                               enum.PURCHASE_BATCH_MODE[batch.mode],
                                               actor, pending)
            return tags.link_to(display, self.request.route_url(routes[batch.mode], uuid=batch.uuid))

        items = [HTML.tag('li', c=render(batch)) for batch in batches]
        return HTML.tag('ul', c=items)


class PurchaseView(MasterView):
    """
    Master view for purchase orders.
    """
    model_class = model.Purchase
    creatable = False
    editable = False

    has_rows = True
    model_row_class = model.PurchaseItem
    row_model_title = 'Purchase Item'

    grid_columns = [
        'store',
        'vendor',
        'department',
        'buyer',
        'date_ordered',
        'date_received',
        'invoice_number',
        'status',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'item_id',
        'brand_name',
        'description',
        'size',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'po_total',
        'invoice_total',
    ]

    def get_instance_title(self, purchase):
        if purchase.status >= self.enum.PURCHASE_STATUS_COSTED:
            if purchase.invoice_date:
                return "{} (invoiced {})".format(purchase.vendor, purchase.invoice_date.strftime('%Y-%m-%d'))
            if purchase.date_received:
                return "{} (invoiced {})".format(purchase.vendor, purchase.date_received.strftime('%Y-%m-%d'))
            return "{} (invoiced)".format(purchase.vendor)
        elif purchase.status >= self.enum.PURCHASE_STATUS_RECEIVED:
            if purchase.date_received:
                return "{} (received {})".format(purchase.vendor, purchase.date_received.strftime('%Y-%m-%d'))
            return "{} (received)".format(purchase.vendor)
        elif purchase.status >= self.enum.PURCHASE_STATUS_ORDERED:
            if purchase.date_ordered:
                return "{} (ordered {})".format(purchase.vendor, purchase.date_ordered.strftime('%Y-%m-%d'))
            return "{} (ordered)".format(purchase.vendor)
        return unicode(purchase)

    def configure_grid(self, g):
        super(PurchaseView, self).configure_grid(g)

        g.joiners['store'] = lambda q: q.join(model.Store)
        g.filters['store'] = g.make_filter('store', model.Store.name)
        g.sorters['store'] = g.make_sorter(model.Store.name)

        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.joiners['department'] = lambda q: q.join(model.Department)
        g.filters['department'] = g.make_filter('department', model.Department.name)
        g.sorters['department'] = g.make_sorter(model.Department.name)

        g.joiners['buyer'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['buyer'] = g.make_filter('buyer', model.Person.display_name,
                                           default_active=True, default_verb='contains')
        g.sorters['buyer'] = g.make_sorter(model.Person.display_name)

        g.filters['date_ordered'].label = "Ordered"
        g.filters['date_ordered'].default_active = True
        g.filters['date_ordered'].default_verb = 'equal'

        g.default_sortkey = 'date_ordered'
        g.default_sortdir = 'desc'

        g.set_enum('status', self.enum.PURCHASE_STATUS)

        g.set_label('date_ordered', "Ordered")
        g.set_label('date_received', "Received")
        g.set_label('invoice_number', "Invoice No.")

    def _preconfigure_fieldset(self, fs):
        fs.store.set(renderer=forms.renderers.StoreFieldRenderer)
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer)
        fs.department.set(renderer=forms.renderers.DepartmentFieldRenderer)
        fs.status.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.PURCHASE_STATUS),
                      readonly=True)
        fs.po_number.set(label="PO Number")
        fs.po_total.set(label="PO Total", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.batches.set(renderer=BatchesFieldRenderer)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.store,
                fs.vendor,
                fs.department,
                fs.status,
                fs.buyer,
                fs.date_ordered,
                fs.date_received,
                fs.po_number,
                fs.po_total,
                fs.invoice_date,
                fs.invoice_number,
                fs.invoice_total,
                fs.created,
                fs.created_by,
                fs.batches,
            ])
        if self.viewing:
            purchase = fs.model
            if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
                del fs.date_received
                del fs.invoice_number
                del fs.invoice_total

    def delete_instance(self, purchase):
        """
        Delete all batches for the purchase, then delete the purchase.
        """
        for batch in list(purchase.batches):
            self.Session.delete(batch)
        self.Session.flush()
        self.Session.delete(purchase)
        self.Session.flush()

    def get_parent(self, item):
        return item.purchase

    def get_row_data(self, purchase):
        return Session.query(model.PurchaseItem)\
                      .filter(model.PurchaseItem.purchase == purchase)

    def configure_row_grid(self, g):
        super(PurchaseView, self).configure_row_grid(g)

        g.default_sortkey = 'sequence'

        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('cases_received', 'quantity')
        g.set_type('units_received', 'quantity')
        g.set_type('po_total', 'currency')
        g.set_type('invoice_total', 'currency')

        g.set_label('sequence', "Seq")
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('cases_ordered', "Cases Ord.")
        g.set_label('units_ordered', "Units Ord.")
        g.set_label('cases_received', "Cases Rec.")
        g.set_label('units_received', "Units Rec.")
        g.set_label('po_total', "Total")
        g.set_label('invoice_total', "Total")

        purchase = self.get_instance()
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            g.hide_column('cases_received')
            g.hide_column('units_received')
            g.hide_column('invoice_total')
        elif purchase.status in (self.enum.PURCHASE_STATUS_RECEIVED,
                                 self.enum.PURCHASE_STATUS_COSTED):
            g.hide_column('po_total')

    def _preconfigure_row_fieldset(self, fs):
        fs.vendor_code.set(label="Vendor Item Code")
        fs.upc.set(label="UPC")
        fs.po_unit_cost.set(label="PO Unit Cost", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.po_total.set(label="PO Total", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_unit_cost.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.append(fa.Field('department', value=lambda i: '{} {}'.format(i.department_number, i.department_name)))

    def configure_row_fieldset(self, fs):

        fs.configure(
            include=[
                fs.sequence,
                fs.vendor_code,
                fs.upc,
                fs.product,
                fs.department,
                fs.case_quantity,
                fs.cases_ordered,
                fs.units_ordered,
                fs.cases_received,
                fs.units_received,
                fs.cases_damaged,
                fs.units_damaged,
                fs.cases_expired,
                fs.units_expired,
                fs.po_unit_cost,
                fs.po_total,
                fs.invoice_unit_cost,
                fs.invoice_total,
            ])

    def receiving_worksheet(self):
        purchase = self.get_instance()
        return self.render_to_response('receiving_worksheet', {
            'purchase': purchase,
        })

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        cls._defaults(config)

        # receiving worksheet
        config.add_tailbone_permission(permission_prefix, '{}.receiving_worksheet'.format(permission_prefix),
                                       "Print receiving worksheet for {}".format(model_title))
        config.add_route('{}.receiving_worksheet'.format(route_prefix), '{}/{{{}}}/receiving-worksheet'.format(url_prefix, model_key))
        config.add_view(cls, attr='receiving_worksheet', route_name='{}.receiving_worksheet'.format(route_prefix),
                        permission='{}.receiving_worksheet'.format(permission_prefix))
        


def includeme(config):
    PurchaseView.defaults(config)
