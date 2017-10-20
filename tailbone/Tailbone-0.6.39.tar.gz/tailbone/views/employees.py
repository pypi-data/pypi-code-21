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
Employee Views
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db import model

import formalchemy as fa

from tailbone import forms, grids
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView, AutocompleteView


class EmployeesView(MasterView):
    """
    Master view for the Employee class.
    """
    model_class = model.Employee
    has_versions = True

    grid_columns = [
        'id',
        'first_name',
        'last_name',
        'phone',
        'email',
        'status',
    ]

    def configure_grid(self, g):
        super(EmployeesView, self).configure_grid(g)

        g.joiners['phone'] = lambda q: q.outerjoin(model.EmployeePhoneNumber, sa.and_(
            model.EmployeePhoneNumber.parent_uuid == model.Employee.uuid,
            model.EmployeePhoneNumber.preference == 1))
        g.joiners['email'] = lambda q: q.outerjoin(model.EmployeeEmailAddress, sa.and_(
            model.EmployeeEmailAddress.parent_uuid == model.Employee.uuid,
            model.EmployeeEmailAddress.preference == 1))

        g.filters['first_name'] = g.make_filter('first_name', model.Person.first_name)
        g.filters['last_name'] = g.make_filter('last_name', model.Person.last_name)

        g.filters['email'] = g.make_filter('email', model.EmployeeEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.EmployeePhoneNumber.number,
                                           label="Phone Number")

        if self.request.has_perm('employees.edit'):
            g.filters['status'].default_active = True
            g.filters['status'].default_verb = 'equal'
            g.filters['status'].default_value = self.enum.EMPLOYEE_STATUS_CURRENT
            g.filters['status'].set_value_renderer(grids.filters.EnumValueRenderer(self.enum.EMPLOYEE_STATUS))
        else:
            del g.filters['id']
            del g.filters['status']

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['first_name'] = lambda q, d: q.order_by(getattr(model.Person.first_name, d)())
        g.sorters['last_name'] = lambda q, d: q.order_by(getattr(model.Person.last_name, d)())

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.EmployeeEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.EmployeePhoneNumber.number, d)())

        g.default_sortkey = 'first_name'

        g.set_enum('status', self.enum.EMPLOYEE_STATUS)

        g.set_label('id', "ID")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('id')
        g.set_link('first_name')
        g.set_link('last_name')

        if not self.request.has_perm('employees.edit'):
            g.hide_column('id')
            g.hide_column('status')

    def query(self, session):
        q = session.query(model.Employee).join(model.Person)
        if not self.request.has_perm('employees.edit'):
            q = q.filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)
        return q

    def editable_instance(self, employee):
        if self.rattail_config.demo():
            return not bool(employee.user and employee.user.username == 'chuck')
        return True

    def deletable_instance(self, employee):
        if self.rattail_config.demo():
            return not bool(employee.user and employee.user.username == 'chuck')
        return True

    def _preconfigure_fieldset(self, fs):
        fs.append(forms.AssociationProxyField('first_name'))
        fs.append(forms.AssociationProxyField('last_name'))
        fs.append(StoresField('stores'))
        fs.append(DepartmentsField('departments'))

        fs.person.set(renderer=forms.renderers.PersonFieldRenderer)
        fs.display_name.set(label="Short Name")
        fs.phone.set(label="Phone Number", readonly=True)
        fs.email.set(label="Email Address", readonly=True)
        fs.status.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.EMPLOYEE_STATUS))
        fs.id.set(label="ID")

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.person,
                fs.first_name,
                fs.last_name,
                fs.display_name,
                fs.phone,
                fs.email,
                fs.status,
                fs.full_time,
                fs.full_time_start,
                fs.id,
                fs.stores,
                fs.departments,
            ])
        if not self.viewing:
            del fs.first_name
            del fs.last_name

    def get_version_child_classes(self):
        return [
            (model.Person, 'uuid', 'person_uuid'),
            (model.EmployeePhoneNumber, 'parent_uuid'),
            (model.EmployeeEmailAddress, 'parent_uuid'),
            (model.EmployeeStore, 'employee_uuid'),
            (model.EmployeeDepartment, 'employee_uuid'),
        ]


class StoresField(fa.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('type', fa.types.Set)
        kwargs.setdefault('options', Session.query(model.Store).order_by(model.Store.name))
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('multiple', True)
        kwargs.setdefault('size', 3)
        fa.Field.__init__(self, name=name, **kwargs)

    def get_value(self, employee):
        return [s.uuid for s in employee.stores]

    def sync(self):
        if not self.is_readonly():
            employee = self.parent.model
            old_stores = set([s.uuid for s in employee.stores])
            new_stores = set(self._deserialize())
            for uuid in new_stores:
                if uuid not in old_stores:
                    employee._stores.append(model.EmployeeStore(store_uuid=uuid))
            for uuid in old_stores:
                if uuid not in new_stores:
                    store = Session.query(model.Store).get(uuid)
                    assert store
                    employee.stores.remove(store)


class DepartmentsField(fa.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('type', fa.types.Set)
        kwargs.setdefault('options', Session.query(model.Department).order_by(model.Department.name))
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('multiple', True)
        kwargs.setdefault('size', 10)
        fa.Field.__init__(self, name=name, **kwargs)

    def get_value(self, employee):
        return [d.uuid for d in employee.departments]

    def sync(self):
        if not self.is_readonly():
            employee = self.parent.model
            old_depts = set([d.uuid for d in employee.departments])
            new_depts = set(self._deserialize())
            for uuid in new_depts:
                if uuid not in old_depts:
                    employee._departments.append(model.EmployeeDepartment(department_uuid=uuid))
            for uuid in old_depts:
                if uuid not in new_depts:
                    dept = Session.query(model.Department).get(uuid)
                    assert dept
                    employee.departments.remove(dept)


class EmployeesAutocomplete(AutocompleteView):
    """
    Autocomplete view for the Employee model, but restricted to return only
    results for current employees.
    """
    mapped_class = model.Person
    fieldname = 'display_name'

    def filter_query(self, q):
        return q.join(model.Employee)\
            .filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)

    def value(self, person):
        return person.employee.uuid


def includeme(config):

    # autocomplete
    config.add_route('employees.autocomplete',  '/employees/autocomplete')
    config.add_view(EmployeesAutocomplete, route_name='employees.autocomplete',
                    renderer='json', permission='employees.list')

    EmployeesView.defaults(config)
