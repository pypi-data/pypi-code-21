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
Person Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from rattail.db import model, api

import formalchemy as fa
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.views import MasterView2 as MasterView, AutocompleteView


class CustomersFieldRenderer(fa.FieldRenderer):

    def render_readonly(self, **kwargs):
        customers = self.raw_value
        if not customers:
            return ''

        items = []
        for customer in customers:
            customer = customer.customer
            text = six.text_type(customer)
            if customer.id:
                text = "({}) {}".format(customer.id, text)
            elif customer.number:
                text = "({}) {}".format(customer.number, text)
            items.append(HTML.tag('li', c=tags.link_to(text, self.request.route_url('customers.view', uuid=customer.uuid))))

        return HTML.tag('ul', c=items)


class UsersFieldRenderer(fa.FieldRenderer):

    def render_readonly(self, **kwargs):
        users = self.raw_value
        items = []
        for user in users:
            text = user.username
            url = self.request.route_url('users.view', uuid=user.uuid)
            items.append(HTML.tag('li', c=tags.link_to(text, url)))
        if items:
            return HTML.tag('ul', c=items)
        elif self.request.has_perm('users.create'):
            return HTML.tag('button', type='button', id='make-user', c="Make User")
        else:
            return ""


class PeopleView(MasterView):
    """
    Master view for the Person class.
    """
    model_class = model.Person
    model_title_plural = "People"
    route_prefix = 'people'
    has_versions = True

    grid_columns = [
        'display_name',
        'first_name',
        'last_name',
        'phone',
        'email',
    ]

    def configure_grid(self, g):
        super(PeopleView, self).configure_grid(g)

        g.joiners['email'] = lambda q: q.outerjoin(model.PersonEmailAddress, sa.and_(
            model.PersonEmailAddress.parent_uuid == model.Person.uuid,
            model.PersonEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.PersonPhoneNumber, sa.and_(
            model.PersonPhoneNumber.parent_uuid == model.Person.uuid,
            model.PersonPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.PersonEmailAddress.address)
        g.filters['phone'] = g.make_filter('phone', model.PersonPhoneNumber.number)

        g.joiners['customer_id'] = lambda q: q.outerjoin(model.CustomerPerson).outerjoin(model.Customer)
        g.filters['customer_id'] = g.make_filter('customer_id', model.Customer.id)

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.PersonEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.PersonPhoneNumber.number, d)())

        g.default_sortkey = 'display_name'

        g.set_label('display_name', "Full Name")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")
        g.set_label('customer_id', "Customer ID")

        g.set_link('display_name')
        g.set_link('first_name')
        g.set_link('last_name')

    def get_instance(self):
        # TODO: I don't recall why this fallback check for a vendor contact
        # exists here, but leaving it intact for now.
        key = self.request.matchdict['uuid']
        instance = self.Session.query(model.Person).get(key)
        if instance:
            return instance
        instance = self.Session.query(model.VendorContact).get(key)
        if instance:
            return instance.person
        raise HTTPNotFound

    def editable_instance(self, person):
        if self.rattail_config.demo():
            return not bool(person.user and person.user.username == 'chuck')
        return True

    def deletable_instance(self, person):
        if self.rattail_config.demo():
            return not bool(person.user and person.user.username == 'chuck')
        return True

    def _preconfigure_fieldset(self, fs):
        fs.display_name.set(label="Full Name")
        fs.phone.set(label="Phone Number", readonly=True)
        fs.email.set(label="Email Address", readonly=True)
        fs.address.set(label="Mailing Address", readonly=True)
        fs.employee.set(renderer=forms.renderers.EmployeeFieldRenderer, attrs={'hyperlink': True}, readonly=True)
        fs._customers.set(renderer=CustomersFieldRenderer, readonly=True)
        fs.users.set(renderer=UsersFieldRenderer, readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.first_name,
                fs.middle_name,
                fs.last_name,
                fs.display_name,
                fs.phone,
                fs.email,
                fs.address,
                fs.employee,
                fs._customers,
                fs.users,
            ])

    def get_version_child_classes(self):
        return [
            (model.PersonPhoneNumber, 'parent_uuid'),
            (model.PersonEmailAddress, 'parent_uuid'),
            (model.PersonMailingAddress, 'parent_uuid'),
            (model.Employee, 'person_uuid'),
            (model.CustomerPerson, 'person_uuid'),
            (model.VendorContact, 'person_uuid'),
        ]

    def make_user(self):
        uuid = self.request.POST['person_uuid']
        person = self.Session.query(model.Person).get(uuid)
        if not person:
            return self.notfound()
        if person.users:
            raise RuntimeError("person {} already has {} user accounts: ".format(
                person.uuid, len(person.users), person))
        user = model.User()
        user.username = api.make_username(person)
        user.person = person
        user.active = False
        self.Session.add(user)
        self.Session.flush()
        self.request.session.flash("User has been created: {}".format(user.username))
        return self.redirect(self.request.route_url('users.view', uuid=user.uuid))

    @classmethod
    def defaults(cls, config):
        cls._people_defaults(config)
        cls._defaults(config)

    @classmethod
    def _people_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()

        # make user for person
        config.add_route('{}.make_user'.format(route_prefix), '{}/make-user'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='make_user', route_name='{}.make_user'.format(route_prefix),
                        permission='users.create')


class PeopleAutocomplete(AutocompleteView):

    mapped_class = model.Person
    fieldname = 'display_name'


class PeopleEmployeesAutocomplete(PeopleAutocomplete):
    """
    Autocomplete view for the Person model, but restricted to return only
    results for people who are employees.
    """

    def filter_query(self, q):
        return q.join(model.Employee)


def includeme(config):

    # autocomplete
    config.add_route('people.autocomplete', '/people/autocomplete')
    config.add_view(PeopleAutocomplete, route_name='people.autocomplete',
                    renderer='json', permission='people.list')
    config.add_route('people.autocomplete.employees', '/people/autocomplete/employees')
    config.add_view(PeopleEmployeesAutocomplete, route_name='people.autocomplete.employees',
                    renderer='json', permission='people.list')

    PeopleView.defaults(config)
