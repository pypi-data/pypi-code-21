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
Base views for purchasing batches
"""

from __future__ import unicode_literals, absolute_import

# from sqlalchemy import orm

from rattail.db import model, api
# from rattail.gpc import GPC
from rattail.time import localtime

import formalchemy as fa
from pyramid import httpexceptions

from tailbone import forms
from tailbone.views.batch import BatchMasterView2 as BatchMasterView


class PurchasingBatchView(BatchMasterView):
    """
    Master view for purchase order batches.
    """
    model_class = model.PurchaseBatch
    model_row_class = model.PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'

    grid_columns = [
        'id',
        'vendor',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'status_code',
        'executed',
    ]

    # row_grid_columns = [
    #     'sequence',
    #     'upc',
    #     # 'item_id',
    #     'brand_name',
    #     'description',
    #     'size',
    #     'cases_ordered',
    #     'units_ordered',
    #     'cases_received',
    #     'units_received',
    #     'po_total',
    #     'invoice_total',
    #     'credits',
    #     'status_code',
    # ]

    @property
    def batch_mode(self):
        raise NotImplementedError("Please define `batch_mode` for your purchasing batch view")

    def query(self, session):
        return session.query(model.PurchaseBatch)\
                      .filter(model.PurchaseBatch.mode == self.batch_mode)

    def configure_grid(self, g):
        super(PurchasingBatchView, self).configure_grid(g)

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

        if self.request.has_perm('{}.execute'.format(self.get_permission_prefix())):
            g.filters['complete'].default_active = True
            g.filters['complete'].default_verb = 'is_true'

        g.set_label('date_ordered', "Ordered")
        g.set_label('date_received', "Received")

    def grid_extra_class(self, batch, i):
        if batch.status_code == batch.STATUS_UNKNOWN_PRODUCT:
            return 'notice'

#     def make_form(self, batch, **kwargs):
#         if self.creating:
#             kwargs.setdefault('id', 'new-purchase-form')
#         form = super(PurchasingBatchView, self).make_form(batch, **kwargs)
#         return form

    def _preconfigure_fieldset(self, fs):
        super(PurchasingBatchView, self)._preconfigure_fieldset(fs)
        fs.mode.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.PURCHASE_BATCH_MODE))
        fs.store.set(renderer=forms.renderers.StoreFieldRenderer)
        fs.purchase.set(renderer=forms.renderers.PurchaseFieldRenderer, options=[])
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer,
                      attrs={'selected': 'vendor_selected',
                             'cleared': 'vendor_cleared'})
        fs.department.set(renderer=forms.renderers.DepartmentFieldRenderer,
                          options=self.get_department_options())
        fs.buyer.set(renderer=forms.renderers.EmployeeFieldRenderer)
        fs.po_number.set(label="PO Number")
        fs.po_total.set(label="PO Total", readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(readonly=True, renderer=forms.renderers.CurrencyFieldRenderer)

        fs.append(fa.Field('vendor_email', readonly=True,
                           value=lambda b: b.vendor.email.address if b.vendor.email else None))
        fs.append(fa.Field('vendor_fax', readonly=True,
                           value=self.get_vendor_fax_number))
        fs.append(fa.Field('vendor_contact', readonly=True,
                           value=lambda b: b.vendor.contact or None))
        fs.append(fa.Field('vendor_phone', readonly=True,
                           value=self.get_vendor_phone_number))

    def get_department_options(self):
        departments = self.Session.query(model.Department).order_by(model.Department.number)
        return [('{} {}'.format(d.number, d.name), d.uuid) for d in departments]

    def get_vendor_phone_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Voice':
                return phone.number

    def get_vendor_fax_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Fax':
                return phone.number

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.store,
                fs.buyer,
                fs.vendor,
                fs.department,
                fs.purchase,
                fs.vendor_email,
                fs.vendor_fax,
                fs.vendor_contact,
                fs.vendor_phone,
                fs.date_ordered,
                fs.date_received,
                fs.po_number,
                fs.po_total,
                fs.invoice_date,
                fs.invoice_number,
                fs.invoice_total,
                fs.notes,
                fs.created,
                fs.created_by,
                fs.status_code,
                fs.complete,
                fs.executed,
                fs.executed_by,
            ])

        if self.creating:
            del fs.po_total
            del fs.invoice_total
            del fs.complete
            del fs.vendor_email
            del fs.vendor_fax
            del fs.vendor_phone
            del fs.vendor_contact

            # default store may be configured
            store = self.rattail_config.get('rattail', 'store')
            if store:
                store = api.get_store(self.Session(), store)
                if store:
                    fs.model.store = store

            # default buyer is current user
            if self.request.method != 'POST':
                buyer = self.request.user.employee
                if buyer:
                    fs.model.buyer = buyer

            # TODO: something tells me this isn't quite safe..
            # all dates have today as default
            today = localtime(self.rattail_config).date()
            fs.model.date_ordered = today
            fs.model.date_received = today

        elif self.editing:
            fs.store.set(readonly=True)
            fs.vendor.set(readonly=True)
            fs.department.set(readonly=True)
            fs.purchase.set(readonly=True)

    def eligible_purchases(self, vendor_uuid=None, mode=None):
        if not vendor_uuid:
            vendor_uuid = self.request.GET.get('vendor_uuid')
        vendor = self.Session.query(model.Vendor).get(vendor_uuid) if vendor_uuid else None
        if not vendor:
            return {'error': "Must specify a vendor."}

        if mode is None:
            mode = self.request.GET.get('mode')
            mode = int(mode) if mode and mode.isdigit() else None
        if not mode or mode not in self.enum.PURCHASE_BATCH_MODE:
            return {'error': "Unknown mode: {}".format(mode)}

        purchases = self.Session.query(model.Purchase)\
                                .filter(model.Purchase.vendor == vendor)
        if mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_ORDERED)\
                                 .order_by(model.Purchase.date_ordered, model.Purchase.created)
        elif mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_RECEIVED)\
                                 .order_by(model.Purchase.date_received, model.Purchase.created)

        return {'purchases': [{'key': p.uuid,
                               'department_uuid': p.department_uuid or '',
                               'display': self.render_eligible_purchase(p)}
                              for p in purchases]}

    def render_eligible_purchase(self, purchase):
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            date = purchase.date_ordered
            total = purchase.po_total
        elif purchase.status == self.enum.PURCHASE_STATUS_RECEIVED:
            date = purchase.date_received
            total = purchase.invoice_total
        return '{} for ${:0,.2f} ({})'.format(date, total, purchase.department or purchase.buyer)

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(PurchasingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        kwargs['mode'] = self.batch_mode
        if batch.store:
            kwargs['store'] = batch.store
        elif batch.store_uuid:
            kwargs['store_uuid'] = batch.store_uuid
        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid
        if batch.department:
            kwargs['department'] = batch.department
        elif batch.department_uuid:
            kwargs['department_uuid'] = batch.department_uuid
        if batch.buyer:
            kwargs['buyer'] = batch.buyer
        elif batch.buyer_uuid:
            kwargs['buyer_uuid'] = batch.buyer_uuid
        kwargs['po_number'] = batch.po_number
        kwargs['po_total'] = batch.po_total

        # TODO: should these always get set?
        if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            kwargs['date_ordered'] = batch.date_ordered
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            kwargs['date_ordered'] = batch.date_ordered
            kwargs['date_received'] = batch.date_received
            kwargs['invoice_number'] = batch.invoice_number
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            kwargs['invoice_date'] = batch.invoice_date
            kwargs['invoice_number'] = batch.invoice_number

        if self.batch_mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                               self.enum.PURCHASE_BATCH_MODE_COSTING):
            if batch.purchase_uuid:
                purchase = self.Session.query(model.Purchase).get(batch.purchase_uuid)
                assert purchase
                kwargs['purchase'] = purchase
                kwargs['buyer'] = purchase.buyer
                kwargs['buyer_uuid'] = purchase.buyer_uuid
                kwargs['date_ordered'] = purchase.date_ordered
                kwargs['po_total'] = purchase.po_total

        return kwargs

#     def template_kwargs_view(self, **kwargs):
#         kwargs = super(PurchasingBatchView, self).template_kwargs_view(**kwargs)
#         vendor = kwargs['batch'].vendor
#         kwargs['vendor_cost_count'] = Session.query(model.ProductCost)\
#                                              .filter(model.ProductCost.vendor == vendor)\
#                                              .count()
#         kwargs['vendor_cost_threshold'] = self.rattail_config.getint(
#             'tailbone', 'purchases.order_form.vendor_cost_warning_threshold', default=699)
#         return kwargs

    def template_kwargs_create(self, **kwargs):
        kwargs['purchases_field'] = 'purchase_uuid'
        return kwargs

#     def get_row_data(self, batch):
#         query = super(PurchasingBatchView, self).get_row_data(batch)
#         return query.options(orm.joinedload(model.PurchaseBatchRow.credits))

    def configure_row_grid(self, g):
        super(PurchasingBatchView, self).configure_row_grid(g)

        g.set_type('upc', 'gpc')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('cases_received', 'quantity')
        g.set_type('units_received', 'quantity')
        g.set_type('po_total', 'currency')
        g.set_type('invoice_total', 'currency')
        g.set_type('credits', 'boolean')

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('cases_ordered', "Cases Ord.")
        g.set_label('units_ordered', "Units Ord.")
        g.set_label('cases_received', "Cases Rec.")
        g.set_label('units_received', "Units Rec.")
        g.set_label('po_total', "Total")
        g.set_label('invoice_total', "Total")
        g.set_label('credits', "Credits?")

    def make_row_grid_tools(self, batch):
        return self.make_default_row_grid_tools(batch)

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'
        if row.status_code in (row.STATUS_INCOMPLETE, row.STATUS_ORDERED_RECEIVED_DIFFER):
            return 'notice'

    def _preconfigure_row_fieldset(self, fs):
        super(PurchasingBatchView, self)._preconfigure_row_fieldset(fs)
        fs.upc.set(label="UPC")
        fs.item_id.set(label="Item ID")
        fs.brand_name.set(label="Brand")
        fs.case_quantity.set(renderer=forms.renderers.QuantityFieldRenderer, readonly=True)
        fs.cases_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_ordered.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_received.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_received.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_damaged.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_damaged.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_expired.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_expired.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.cases_mispick.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.units_mispick.set(renderer=forms.renderers.QuantityFieldRenderer)
        fs.po_line_number.set(label="PO Line Number")
        fs.po_unit_cost.set(label="PO Unit Cost", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.po_total.set(label="PO Total", renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_unit_cost.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.invoice_total.set(renderer=forms.renderers.CurrencyFieldRenderer)
        fs.credits.set(readonly=True)
        # fs.append(fa.Field('item_lookup', label="Item Lookup Code", required=True,
        #                    validate=self.item_lookup))

#     def item_lookup(self, value, field=None):
#         """
#         Try to locate a single product using ``value`` as a lookup code.
#         """
#         batch = self.get_instance()
#         product = api.get_product_by_vendor_code(Session(), value, vendor=batch.vendor)
#         if product:
#             return product.uuid
#         if value.isdigit():
#             product = api.get_product_by_upc(Session(), GPC(value))
#             if not product:
#                 product = api.get_product_by_upc(Session(), GPC(value, calc_check_digit='upc'))
#             if product:
#                 if not product.cost_for_vendor(batch.vendor):
#                     raise fa.ValidationError("Product {} exists but has no cost for vendor {}".format(
#                         product.upc.pretty(), batch.vendor))
#                 return product.uuid
#         raise fa.ValidationError("Product not found")

    def configure_row_fieldset(self, fs):
        try:
            batch = self.get_instance()
        except httpexceptions.HTTPNotFound:
            batch = self.get_row_instance().batch

        fs.configure(
            include=[
                # fs.item_lookup,
                fs.upc,
                fs.item_id,
                fs.product,
                fs.brand_name,
                fs.description,
                fs.size,
                fs.case_quantity,
                fs.cases_ordered,
                fs.units_ordered,
                fs.cases_received,
                fs.units_received,
                fs.cases_damaged,
                fs.units_damaged,
                fs.cases_expired,
                fs.units_expired,
                fs.cases_mispick,
                fs.units_mispick,
                fs.po_line_number,
                fs.po_unit_cost,
                fs.po_total,
                fs.invoice_line_number,
                fs.invoice_unit_cost,
                fs.invoice_total,
                fs.status_code,
                fs.credits,
            ])

        if self.creating:
            del fs.upc
            del fs.product
            del fs.po_total
            del fs.invoice_total
            if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
                del fs.cases_received
                del fs.units_received
            elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                del fs.cases_ordered
                del fs.units_ordered

        elif self.editing:
            # del fs.item_lookup
            fs.upc.set(readonly=True)
            fs.product.set(readonly=True)
            del fs.po_total
            del fs.invoice_total
            del fs.status_code

        elif self.viewing:
            # del fs.item_lookup
            if fs.model.product:
                del (fs.brand_name,
                     fs.description,
                     fs.size)
            else:
                del fs.product

#     def before_create_row(self, form):
#         row = form.fieldset.model
#         batch = self.get_instance()
#         batch.add_row(row)
#         # TODO: this seems heavy-handed but works..
#         row.product_uuid = self.item_lookup(form.fieldset.item_lookup.value)

#     def after_create_row(self, row):
#         self.handler.refresh_row(row)

#     def after_edit_row(self, row):
#         batch = row.batch

#         # first undo any totals previously in effect for the row
#         if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING and row.po_total:
#             batch.po_total -= row.po_total
#         elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING and row.invoice_total:
#             batch.invoice_total -= row.invoice_total

#         self.handler.refresh_row(row)

#     def redirect_after_create_row(self, row):
#         self.request.session.flash("Added item: {} {}".format(row.upc.pretty(), row.product))
#         return self.redirect(self.request.current_route_url())

#     def delete_row(self):
#         """
#         Update the PO total in addition to marking row as removed.
#         """
#         row = self.Session.query(self.model_row_class).get(self.request.matchdict['uuid'])
#         if not row:
#             raise httpexceptions.HTTPNotFound()
#         if row.po_total:
#             row.batch.po_total -= row.po_total
#         if row.invoice_total:
#             row.batch.invoice_total -= row.invoice_total
#         row.removed = True
#         return self.redirect(self.get_action_url('view', row.batch))

#     def get_execute_success_url(self, batch, result, **kwargs):
#         # if batch execution yielded a Purchase, redirect to it
#         if isinstance(result, model.Purchase):
#             return self.request.route_url('purchases.view', uuid=result.uuid)

#         # otherwise just view batch again
#         return self.get_action_url('view', batch)


    @classmethod
    def _purchasing_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # eligible purchases (AJAX)
        config.add_route('{}.eligible_purchases'.format(route_prefix), '{}/eligible-purchases'.format(url_prefix))
        config.add_view(cls, attr='eligible_purchases', route_name='{}.eligible_purchases'.format(route_prefix),
                        renderer='json', permission='{}.view'.format(permission_prefix))

    @classmethod
    def defaults(cls, config):
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)
