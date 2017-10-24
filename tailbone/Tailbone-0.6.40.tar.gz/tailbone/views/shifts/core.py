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
Views for employee shifts
"""

from __future__ import unicode_literals, absolute_import

import datetime

import humanize

from rattail.db import model
from rattail.time import localtime

import formalchemy

from tailbone import forms
from tailbone.views import MasterView2 as MasterView


class ShiftLengthField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.shift_length)
        super(ShiftLengthField, self).__init__(name, **kwargs)

    def shift_length(self, shift):
        if not shift.start_time or not shift.end_time:
            return
        if shift.end_time < shift.start_time:
            return "??"
        return humanize.naturaldelta(shift.end_time - shift.start_time)


def render_shift_length(shift, column):
    if not shift.start_time or not shift.end_time:
        return ""
    if shift.end_time < shift.start_time:
        return "??"
    return humanize.naturaldelta(shift.end_time - shift.start_time)


class ScheduledShiftsView(MasterView):
    """
    Master view for employee scheduled shifts.
    """
    model_class = model.ScheduledShift
    url_prefix = '/shifts/scheduled'

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        g.joiners['employee'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['employee'] = g.make_filter('employee', model.Person.display_name,
                                              default_active=True, default_verb='contains')

        g.default_sortkey = 'start_time'
        g.default_sortdir = 'desc'

        g.set_renderer('length', render_shift_length)

        g.set_label('employee', "Employee Name")

    def configure_fieldset(self, fs):
        fs.append(ShiftLengthField('length'))
        fs.configure(
            include=[
                fs.employee,
                fs.store,
                fs.start_time,
                fs.end_time,
                fs.length,
            ])


class WorkedShiftsView(MasterView):
    """
    Master view for employee worked shifts.
    """
    model_class = model.WorkedShift
    url_prefix = '/shifts/worked'
    has_versions = True

    grid_columns = [
        'employee',
        'store',
        'start_time',
        'end_time',
        'length',
    ]

    def configure_grid(self, g):
        super(WorkedShiftsView, self).configure_grid(g)

        g.joiners['employee'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['employee'] = g.make_filter('employee', model.Person.display_name)
        g.sorters['employee'] = g.make_sorter(model.Person.display_name)

        g.joiners['store'] = lambda q: q.join(model.Store)
        g.filters['store'] = g.make_filter('store', model.Store.name)
        g.sorters['store'] = g.make_sorter(model.Store.name)

        # TODO: these sorters should be automatic once we fix the schema
        g.sorters['start_time'] = g.make_sorter(model.WorkedShift.punch_in)
        g.sorters['end_time'] = g.make_sorter(model.WorkedShift.punch_out)
        g.default_sortkey = 'start_time'
        g.default_sortdir = 'desc'

        g.set_renderer('length', render_shift_length)

        g.set_label('employee', "Employee Name")
        g.set_label('store', "Store Name")
        g.set_label('punch_in', "Start Time")
        g.set_label('punch_out', "End Time")

    def get_instance_title(self, shift):
        time = shift.start_time or shift.end_time
        date = localtime(self.rattail_config, time).date()
        return "WorkedShift: {}, {}".format(shift.employee, date)

    def _preconfigure_fieldset(self, fs):
        fs.append(ShiftLengthField('length'))
        fs.employee.set(readonly=True, renderer=forms.renderers.EmployeeFieldRenderer)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.employee,
                fs.store,
                fs.start_time,
                fs.end_time,
                fs.length,
            ])
        if self.editing:
            del fs.length


def includeme(config):
    ScheduledShiftsView.defaults(config)
    WorkedShiftsView.defaults(config)
