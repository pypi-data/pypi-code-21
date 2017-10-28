# -*- coding: utf-8; -*-
# -*- coding: utf-8; -*-
"""
Views for ${model_title} batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from tailbone.views.batch import FileBatchMasterView

from .handler import ${model_name}Handler


class ${model_name}View(FileBatchMasterView):
    """
    Master view for ${model_title} batches.
    """
    model_class = model.${model_name}
    batch_handler_class = ${model_name}Handler
    model_row_class = model.${model_name}Row
    model_title = "${model_title} Batch"
    model_title_plural = "${model_title} Batches"
    route_prefix = 'batch.${model_name.lower()}s'
    url_prefix = '/batch/${table_name.replace('_', '-')}'

    def get_instance_title(self, batch):
        return six.text_type(batch.vendor)

    def configure_grid(self, g):
        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)
        g.configure(
            include=[
                g.created,
                g.created_by,
                g.vendor,
                g.effective,
                g.filename,
                g.executed,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer)
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

    def configure_row_grid(self, g):
        g.configure(
            include=[
                g.sequence,
                g.upc.label("UPC"),
                g.description,
                g.status_code,
            ],
            readonly=True)

    def row_grid_row_attrs(self, row, i):
        attrs = {}
        if row.status_code == row.STATUS_SOME_CONCERN:
            attrs['class_'] = 'notice'
        if row.status_code == row.STATUS_UTTER_CHAOS:
            attrs['class_'] = 'warning'
        return attrs


def includeme(config):

    # fix permission group title
    config.add_tailbone_permission_group('${model_name.lower()}s', "${model_title}s")

    ${model_name}View.defaults(config)
