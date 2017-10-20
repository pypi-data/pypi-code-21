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
Customer Order Views
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView


class CustomerOrdersView(MasterView):
    """
    Master view for customer orders
    """
    model_class = model.CustomerOrder
    route_prefix = 'custorders'
    creatable = False
    editable = False
    deletable = False

    grid_columns = [
        'id',
        'customer',
        'person',
        'created',
        'status_code',
    ]

    def query(self, session):
        return session.query(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrder.customer))

    def configure_grid(self, g):
        super(CustomerOrdersView, self).configure_grid(g)

        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['customer'] = g.make_filter('customer', model.Customer.name,
                                              label="Customer Name",
                                              default_active=True,
                                              default_verb='contains')
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            label="Person Name",
                                            default_active=True,
                                            default_verb='contains')

        g.set_sorter('customer', model.Customer.name)
        g.set_sorter('person', model.Person.display_name)

        g.default_sortkey = 'created'
        g.default_sortdir = 'desc'

        # TODO: enum choices renderer
        g.set_label('status_code', "Status")
        g.set_label('id', "ID")

    def _preconfigure_fieldset(self, fs):
        fs.customer.set(options=[])
        fs.id.set(label="ID", readonly=True)
        fs.person.set(renderer=forms.renderers.PersonFieldRenderer)
        fs.created.set(readonly=True)
        fs.status_code.set(label="Status")

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id,
                fs.customer,
                fs.person,
                fs.created,
                fs.status_code,
            ])


def includeme(config):
    CustomerOrdersView.defaults(config)
