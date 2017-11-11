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
Views for maintaining vendor catalogs
"""

from __future__ import unicode_literals, absolute_import

import logging

from rattail.db import model, api
from rattail.vendors.catalogs import iter_catalog_parsers

import formalchemy

from tailbone import forms
from tailbone.db import Session
from tailbone.views.batch import FileBatchMasterView2 as FileBatchMasterView


log = logging.getLogger(__name__)


class VendorCatalogsView(FileBatchMasterView):
    """
    Master view for vendor catalog batches.
    """
    model_class = model.VendorCatalog
    model_row_class = model.VendorCatalogRow
    default_handler_spec = 'rattail.batch.vendorcatalog:VendorCatalogHandler'
    url_prefix = '/vendors/catalogs'
    editable = False
    rows_bulk_deletable = True

    grid_columns = [
        'created',
        'created_by',
        'vendor',
        'effective',
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
        'old_unit_cost',
        'unit_cost',
        'unit_cost_diff',
        'status_code',
    ]

    def get_parsers(self):
        if not hasattr(self, 'parsers'):
            self.parsers = sorted(iter_catalog_parsers(), key=lambda p: p.display)
        return self.parsers

    def configure_grid(self, g):
        super(VendorCatalogsView, self).configure_grid(g)
        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

    def get_instance_title(self, batch):
        return unicode(batch.vendor)

    def configure_fieldset(self, fs):
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer)
        fs.filename.set(label="Catalog File")

        if self.creating:
            parser_options = [(p.display, p.key) for p in self.get_parsers()]
            parser_options.insert(0, ("(please choose)", ''))
            fs.parser_key.set(renderer=formalchemy.fields.SelectFieldRenderer,
                              options=parser_options, label="File Type")
            fs.configure(
                include=[
                    fs.filename,
                    fs.parser_key,
                    fs.vendor,
                ])

        else:
            fs.configure(
                include=[
                    fs.vendor.readonly(),
                    fs.filename,
                    fs.effective.readonly(),
                    fs.created,
                    fs.created_by,
                    fs.executed,
                    fs.executed_by,
                ])

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorCatalogsView, self).get_batch_kwargs(batch)
        kwargs['parser_key'] = batch.parser_key
        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid
        return kwargs

    def configure_row_grid(self, g):
        super(VendorCatalogsView, self).configure_row_grid(g)
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('old_unit_cost', "Old Cost")
        g.set_label('unit_cost', "New Cost")
        g.set_label('unit_cost_diff', "Diff.")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'
        if row.status_code in (row.STATUS_NEW_COST, row.STATUS_UPDATE_COST):
            return 'notice'

    def template_kwargs_create(self, **kwargs):
        parsers = self.get_parsers()
        for parser in parsers:
            if parser.vendor_key:
                vendor = api.get_vendor(Session(), parser.vendor_key)
                if vendor:
                    parser.vendormap_value = "{{uuid: '{}', name: '{}'}}".format(
                        vendor.uuid, vendor.name.replace("'", "\\'"))
                else:
                    log.warning("vendor '{}' not found for parser: {}".format(
                        parser.vendor_key, parser.key))
                    parser.vendormap_value = 'null'
            else:
                parser.vendormap_value = 'null'
        kwargs['parsers'] = parsers
        return kwargs


def includeme(config):
    VendorCatalogsView.defaults(config)
