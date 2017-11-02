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
Customer Views
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa
from sqlalchemy import orm

import formalchemy as fa
from pyramid.httpexceptions import HTTPNotFound

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView, AutocompleteView

from rattail.db import model


class CustomersView(MasterView):
    """
    Master view for the Customer class.
    """
    model_class = model.Customer
    has_versions = True
    supports_mobile = True
    grid_columns = [
        'id',
        'number',
        'name',
        'phone',
        'email',
    ]

    def configure_grid(self, g):
        super(CustomersView, self).configure_grid(g)

        g.joiners['email'] = lambda q: q.outerjoin(model.CustomerEmailAddress, sa.and_(
            model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
            model.CustomerEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.CustomerPhoneNumber, sa.and_(
            model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
            model.CustomerPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.CustomerEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.CustomerPhoneNumber.number,
                                           label="Phone Number")

        # TODO
        # name=self.filter_ilike_and_soundex(model.Customer.name),

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.CustomerEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.CustomerPhoneNumber.number, d)())

        g.default_sortkey = 'name'

        g.set_label('id', "ID")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('id')
        g.set_link('number')
        g.set_link('name')

    def get_mobile_data(self, session=None):
        # TODO: hacky!
        return self.get_data(session=session).order_by(model.Customer.name)

    def get_instance(self):
        try:
            instance = super(CustomersView, self).get_instance()
        except HTTPNotFound:
            pass
        else:
            if instance:
                return instance

        key = self.request.matchdict['uuid']

        # search by Customer.id
        instance = self.Session.query(model.Customer)\
                               .filter(model.Customer.id == key)\
                               .first()
        if instance:
            return instance

        # search by CustomerPerson.uuid
        instance = self.Session.query(model.CustomerPerson).get(key)
        if instance:
            return instance.customer

        # search by CustomerGroupAssignment.uuid
        instance = self.Session.query(model.CustomerGroupAssignment).get(key)
        if instance:
            return instance.customer

        raise HTTPNotFound

    def _preconfigure_fieldset(self, fs):
        fs.id.set(label="ID")
        fs.append(forms.fields.DefaultPhoneField('default_phone', label="Phone Number"))
        fs.append(forms.fields.DefaultEmailField('default_email', label="Email Address"))
        fs.email_preference.set(renderer=forms.EnumFieldRenderer(self.enum.EMAIL_PREFERENCE),
                                attrs={'auto-enhance': 'true'})
        fs.email_preference._null_option = ("(no preference)", '')
        fs.append(forms.AssociationProxyField('people', renderer=forms.renderers.PeopleFieldRenderer,
                                              readonly=True))
        fs.active_in_pos.set(label="Active in POS")
        fs.active_in_pos_sticky.set(label="Always Active in POS")

    def configure_fieldset(self, fs):
        include = [
            fs.id,
            fs.name,
            fs.default_phone,
            fs.default_email,
            fs.email_preference,
            fs.active_in_pos,
            fs.active_in_pos_sticky,
        ]
        if not self.creating:
            include.extend([
                fs.people,
            ])
        fs.configure(include=include)

    def configure_mobile_fieldset(self, fs):
        fs.configure(
            include=[
                fs.email,
                fs.phone,
            ])

    def get_version_child_classes(self):
        return [
            (model.CustomerPhoneNumber, 'parent_uuid'),
            (model.CustomerEmailAddress, 'parent_uuid'),
            (model.CustomerMailingAddress, 'parent_uuid'),
            (model.CustomerPerson, 'customer_uuid'),
        ]


def unique_id(value, field):
    customer = field.parent.model
    query = Session.query(model.Customer).filter(model.Customer.id == value)
    if customer.uuid:
        query = query.filter(model.Customer.uuid != customer.uuid)
    if query.count():
        raise fa.ValidationError("Customer ID must be unique")


class CustomerNameAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer name.
    """
    mapped_class = model.Customer
    fieldname = 'name'


class CustomerPhoneAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer phone number.

    .. note::
       As currently implemented, this view will only work with a PostgreSQL
       database.  It normalizes the user's search term and the database values
       to numeric digits only (i.e. removes special characters from each) in
       order to be able to perform smarter matching.  However normalizing the
       database value currently uses the PG SQL ``regexp_replace()`` function.
    """
    invalid_pattern = re.compile(r'\D')

    def prepare_term(self, term):
        return self.invalid_pattern.sub('', term)

    def query(self, term):
        return Session.query(model.CustomerPhoneNumber)\
            .filter(sa.func.regexp_replace(model.CustomerPhoneNumber.number, r'\D', '', 'g').like('%{0}%'.format(term)))\
            .order_by(model.CustomerPhoneNumber.number)\
            .options(orm.joinedload(model.CustomerPhoneNumber.customer))

    def display(self, phone):
        return "{0} {1}".format(phone.number, phone.customer)

    def value(self, phone):
        return phone.customer.uuid


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    uuid = request.params.get('uuid')
    customer = Session.query(model.Customer).get(uuid) if uuid else None
    if not customer:
        return {}
    return {
        'uuid':                 customer.uuid,
        'name':                 customer.name,
        'phone_number':         customer.phone.number if customer.phone else '',
        }


def includeme(config):

    # autocomplete
    config.add_route('customers.autocomplete', '/customers/autocomplete')
    config.add_view(CustomerNameAutocomplete, route_name='customers.autocomplete',
                    renderer='json', permission='customers.list')
    config.add_route('customers.autocomplete.phone', '/customers/autocomplete/phone')
    config.add_view(CustomerPhoneAutocomplete, route_name='customers.autocomplete.phone',
                    renderer='json', permission='customers.list')

    # info
    config.add_route('customer.info', '/customers/info')
    config.add_view(customer_info, route_name='customer.info',
                    renderer='json', permission='customers.view')

    CustomersView.defaults(config)
