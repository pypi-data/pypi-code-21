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
Master View
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy_continuum as continuum

from tailbone import grids
from tailbone.views import MasterView


class MasterView2(MasterView):
    """
    Base "master" view class.  All model master views should derive from this.
    """
    sortable = True
    rows_pageable = True
    mobile_pageable = True
    labels = {'uuid': "UUID"}

    @classmethod
    def get_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'grid_factory', grids.Grid)

    @classmethod
    def get_row_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        row grid instances.
        """
        return getattr(cls, 'row_grid_factory', grids.Grid)

    @classmethod
    def get_version_grid_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        version grid instances.
        """
        return getattr(cls, 'version_grid_factory', grids.Grid)

    @classmethod
    def get_mobile_grid_factory(cls):
        """
        Must return a callable to be used when creating new mobile grid
        instances.  Instead of overriding this, you can set
        :attr:`mobile_grid_factory`.  Default factory is :class:`MobileGrid`.
        """
        return getattr(cls, 'mobile_grid_factory', grids.MobileGrid)

    @classmethod
    def get_mobile_row_grid_factory(cls):
        """
        Must return a callable to be used when creating new mobile row grid
        instances.  Instead of overriding this, you can set
        :attr:`mobile_row_grid_factory`.  Default factory is :class:`MobileGrid`.
        """
        return getattr(cls, 'mobile_row_grid_factory', grids.MobileGrid)

    def get_effective_data(self, session=None, **kwargs):
        """
        Convenience method which returns the "effective" data for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        grid = self.make_grid(session=session, **kwargs)
        return grid.make_visible_data()

    def make_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new grid instance
        """
        if factory is None:
            factory = self.get_grid_factory()
        if key is None:
            key = self.get_grid_key()
        if data is None:
            data = self.get_data(session=kwargs.get('session'))
        if columns is None:
            columns = self.get_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_grid(grid)
        grid.load_settings()
        return grid

    def make_row_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Make and return a new (configured) rows grid instance.
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_row_grid_factory()
        if key is None:
            key = self.get_row_grid_key()
        if data is None:
            data = self.get_row_data(instance)
        if columns is None:
            columns = self.get_row_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_row_grid_kwargs(**kwargs)

        grid = factory(key, data, columns, **kwargs)
        self.configure_row_grid(grid)
        grid.load_settings()
        return grid

    def make_version_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new version grid instance
        """
        instance = kwargs.pop('instance', None)
        if not instance:
            instance = self.get_instance()

        if factory is None:
            factory = self.get_version_grid_factory()
        if key is None:
            key = self.get_version_grid_key()
        if data is None:
            data = self.get_version_data(instance)
        if columns is None:
            columns = self.get_version_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs = self.make_version_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_version_grid(grid)
        grid.load_settings()
        return grid

    def make_mobile_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Creates a new mobile grid instance
        """
        if factory is None:
            factory = self.get_mobile_grid_factory()
        if key is None:
            key = self.get_mobile_grid_key()
        if data is None:
            data = self.get_mobile_data(session=kwargs.get('session'))
        if columns is None:
            columns = self.get_mobile_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs.setdefault('mobile', True)
        kwargs = self.make_mobile_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_mobile_grid(grid)
        grid.load_settings()
        return grid

    def make_mobile_row_grid(self, factory=None, key=None, data=None, columns=None, **kwargs):
        """
        Make a new (configured) rows grid instance for mobile.
        """
        instance = kwargs.pop('instance', self.get_instance())

        if factory is None:
            factory = self.get_mobile_row_grid_factory()
        if key is None:
            key = 'mobile.{}.{}'.format(self.get_grid_key(), self.request.matchdict[self.get_model_key()])
        if data is None:
            data = self.get_mobile_row_data(instance)
        if columns is None:
            columns = self.get_mobile_row_grid_columns()

        kwargs.setdefault('request', self.request)
        kwargs.setdefault('mobile', True)
        kwargs = self.make_mobile_row_grid_kwargs(**kwargs)
        grid = factory(key, data, columns, **kwargs)
        self.configure_mobile_row_grid(grid)
        grid.load_settings()
        return grid

    def get_grid_columns(self):
        if hasattr(self, 'grid_columns'):
            return self.grid_columns
        # TODO
        raise NotImplementedError

    def get_row_grid_columns(self):
        if hasattr(self, 'row_grid_columns'):
            return self.row_grid_columns
        # TODO
        raise NotImplementedError

    def get_version_grid_columns(self):
        if hasattr(self, 'version_grid_columns'):
            return self.version_grid_columns
        # TODO
        return [
            'issued_at',
            'user',
            'remote_addr',
            'comment',
        ]

    def get_mobile_grid_columns(self):
        if hasattr(self, 'mobile_grid_columns'):
            return self.mobile_grid_columns
        # TODO
        return ['listitem']

    def get_mobile_row_grid_columns(self):
        if hasattr(self, 'mobile_row_grid_columns'):
            return self.mobile_row_grid_columns
        # TODO
        return ['listitem']

    def make_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new grid instances.
        """
        defaults = {
            'model_class': getattr(self, 'model_class', None),
            'width': 'full',
            'filterable': self.filterable,
            'sortable': self.sortable,
            'pageable': self.pageable,
            'extra_row_class': self.grid_extra_class,
            'url': lambda obj: self.get_action_url('view', obj),
            'checkboxes': self.checkboxes or (
                self.mergeable and self.request.has_perm('{}.merge'.format(self.get_permission_prefix()))),
            'checked': self.checked,
        }
        if 'main_actions' not in kwargs and 'more_actions' not in kwargs:
            main, more = self.get_grid_actions()
            defaults['main_actions'] = main
            defaults['more_actions'] = more
        defaults.update(kwargs)
        return defaults

    def make_row_grid_kwargs(self, **kwargs):
        """
        Return a dict of kwargs to be used when constructing a new rows grid.
        """
        route_prefix = self.get_row_route_prefix()
        permission_prefix = self.get_permission_prefix()

        defaults = {
            'model_class': self.model_row_class,
            'width': 'full',
            'filterable': self.rows_filterable,
            'sortable': self.rows_sortable,
            'pageable': self.rows_pageable,
            'default_pagesize': self.rows_default_pagesize,
            'extra_row_class': self.row_grid_extra_class,
        }

        if self.has_rows and 'main_actions' not in defaults:
            actions = []

            # view action
            if self.rows_viewable:
                view = lambda r, i: self.get_row_action_url('view', r)
                actions.append(grids.GridAction('view', icon='zoomin', url=view))

            # edit action
            if self.rows_editable:
                actions.append(grids.GridAction('edit', icon='pencil', url=self.row_edit_action_url))

            # delete action
            if self.rows_deletable and self.request.has_perm('{}.delete_row'.format(permission_prefix)):
                actions.append(grids.GridAction('delete', icon='trash', url=self.row_delete_action_url))
                defaults['delete_speedbump'] = self.rows_deletable_speedbump

            defaults['main_actions'] = actions

        defaults.update(kwargs)
        return defaults

    def make_version_grid_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when
        constructing a new version grid.
        """
        defaults = {
            'model_class': continuum.transaction_class(self.get_model_class()),
            'width': 'full',
            'pageable': True,
        }
        if 'main_actions' not in kwargs:
            route = '{}.version'.format(self.get_route_prefix())
            instance = kwargs.get('instance') or self.get_instance()
            url = lambda txn, i: self.request.route_url(route, uuid=instance.uuid, txnid=txn.id)
            defaults['main_actions'] = [
                self.make_action('view', icon='zoomin', url=url),
            ]
        defaults.update(kwargs)
        return defaults

    def make_mobile_grid_kwargs(self, **kwargs):
        """
        Must return a dictionary of kwargs to be passed to the factory when
        creating new mobile grid instances.
        """
        defaults = {
            'model_class': getattr(self, 'model_class', None),
            'pageable': self.mobile_pageable,
            'sortable': False,
            'filterable': self.mobile_filterable,
            'renderers': self.make_mobile_grid_renderers(),
            'url': lambda obj: self.get_action_url('view', obj, mobile=True),
        }
        # TODO: this seems wrong..
        if self.mobile_filterable:
            defaults['filters'] = self.make_mobile_filters()
        defaults.update(kwargs)
        return defaults

    def make_mobile_row_grid_kwargs(self, **kwargs):
        """
        Must return a dictionary of kwargs to be passed to the factory when
        creating new mobile *row* grid instances.
        """
        defaults = {
            'model_class': self.model_row_class,
            # TODO
            'pageable': self.pageable,
            'sortable': False,
            'filterable': self.mobile_rows_filterable,
            'renderers': self.make_mobile_row_grid_renderers(),
            'url': lambda obj: self.get_row_action_url('view', obj, mobile=True),
        }
        # TODO: this seems wrong..
        if self.mobile_rows_filterable:
            defaults['filters'] = self.make_mobile_row_filters()
        defaults.update(kwargs)
        return defaults

    def make_mobile_grid_renderers(self):
        return {
            'listitem': self.render_mobile_listitem,
        }

    def render_mobile_listitem(self, obj, i):
        return obj

    def make_mobile_row_grid_renderers(self):
        return {
            'listitem': self.render_mobile_row_listitem,
        }

    def render_mobile_row_listitem(self, obj, i):
        return obj

    def grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given object, or ``None``.
        """

    def row_grid_extra_class(self, obj, i):
        """
        Returns string of extra class(es) for the table row corresponding to
        the given row object, or ``None``.
        """

    def set_labels(self, obj):
        for key, label in self.labels.items():
            obj.set_label(key, label)

    def configure_grid(self, grid):
        self.set_labels(grid)

    def configure_row_grid(self, grid):
        pass

    def configure_version_grid(self, g):
        g.default_sortkey = 'issued_at'
        g.default_sortdir = 'desc'
        g.set_renderer('comment', self.render_version_comment)
        g.set_label('issued_at', "Changed")
        g.set_label('user', "Changed by")
        g.set_label('remote_addr', "IP Address")
        # TODO: why does this render '#' as url?
        # g.set_link('issued_at')

    def render_version_comment(self, transaction, column):
        return transaction.meta.get('comment', "")

    def configure_mobile_grid(self, grid):
        pass

    def configure_mobile_row_grid(self, grid):
        pass
