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
Model Master View
"""

from __future__ import unicode_literals, absolute_import

import os
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

import sqlalchemy_continuum as continuum

from rattail.db import model, Session as RattailSession
from rattail.db.continuum import model_transaction_query
from rattail.util import prettify
from rattail.time import localtime #, make_utc
from rattail.threads import Thread
from rattail.csvutil import UnicodeDictWriter

import formalchemy as fa
from pyramid import httpexceptions
from pyramid.renderers import get_renderer, render_to_response, render
from pyramid.response import FileResponse
from webhelpers2.html import HTML, tags

from tailbone import forms, grids, diffs
from tailbone.views import View
from tailbone.progress import SessionProgress


log = logging.getLogger(__name__)


class MasterView(View):
    """
    Base "master" view class.  All model master views should derive from this.
    """
    filterable = True
    pageable = True
    checkboxes = False

    listable = True
    results_downloadable_csv = False
    creatable = True
    viewable = True
    editable = True
    deletable = True
    bulk_deletable = False
    populatable = False
    mergeable = False
    downloadable = False
    cloneable = False
    executable = False
    execute_progress_template = None
    execute_progress_initial_msg = None
    supports_prev_next = False

    supports_mobile = False
    mobile_creatable = False
    mobile_filterable = False

    listing = False
    creating = False
    viewing = False
    editing = False
    deleting = False
    has_pk_fields = False

    row_attrs = {}
    cell_attrs = {}

    grid_index = None
    use_index_links = False

    has_versions = False

    # ROW-RELATED ATTRS FOLLOW:

    has_rows = False
    model_row_class = None
    rows_filterable = True
    rows_sortable = True
    rows_viewable = True
    rows_creatable = False
    rows_editable = False
    rows_deletable = False
    rows_deletable_speedbump = False
    rows_bulk_deletable = False
    rows_default_pagesize = 20
    rows_downloadable_csv = False

    mobile_rows_creatable = False
    mobile_rows_filterable = False
    mobile_rows_viewable = False
    mobile_rows_editable = False

    @property
    def Session(self):
        """
        SQLAlchemy scoped session to use when querying the database.  Defaults
        to ``tailbone.db.Session``.
        """
        from tailbone.db import Session
        return Session

    ##############################
    # Available Views
    ##############################

    def index(self):
        """
        View to list/filter/sort the model data.

        If this view receives a non-empty 'partial' parameter in the query
        string, then the view will return the rendered grid only.  Otherwise
        returns the full page.
        """
        self.listing = True
        grid = self.make_grid()

        # If user just refreshed the page with a reset instruction, issue a
        # redirect in order to clear out the query string.
        if self.request.GET.get('reset-to-default-filters') == 'true':
            return self.redirect(self.request.current_route_url(_query=None))

        # Stash some grid stats, for possible use when generating URLs.
        if grid.pageable and hasattr(grid, 'pager'):
            self.first_visible_grid_index = grid.pager.first_item

        # Return grid only, if partial page was requested.
        if self.request.params.get('partial'):
            self.request.response.content_type = b'text/html'
            self.request.response.text = grid.render_grid()
            return self.request.response

        return self.render_to_response('index', {'grid': grid})

    def mobile_index(self):
        """
        Mobile "home" page for the data model
        """
        self.listing = True
        grid = self.make_mobile_grid()
        return self.render_to_response('index', {'grid': grid}, mobile=True)

    @classmethod
    def get_mobile_grid_key(cls):
        """
        Must return a unique "config key" for the mobile grid, for sort/filter
        purposes etc.  (It need only be unique among *mobile* grids.)  Instead
        of overriding this, you can set :attr:`mobile_grid_key`.  Default is
        the value returned by :meth:`get_route_prefix()`.
        """
        if hasattr(cls, 'mobile_grid_key'):
            return cls.mobile_grid_key
        return 'mobile.{}'.format(cls.get_route_prefix())

    def get_mobile_data(self, session=None):
        """
        Must return the "raw" / full data set for the mobile grid.  This data
        should *not* yet be sorted or filtered in any way; that happens later.
        Default is the value returned by :meth:`get_data()`, in which case all
        records visible in the traditional view, are visible in mobile too.
        """
        return self.get_data(session=session)

    def make_mobile_filters(self):
        """
        Returns a set of filters for the mobile grid, if applicable.
        """

    def make_mobile_row_filters(self):
        """
        Returns a set of filters for the mobile row grid, if applicable.
        """

    def mobile_listitem_field(self):
        """
        Must return a FormAlchemy field to be appended to grid, or ``None`` if
        none is desired.
        """
        return fa.Field('listitem', value=lambda obj: obj,
                        renderer=self.mobile_listitem_renderer())

    def mobile_listitem_renderer(self):
        """
        Must return a FormAlchemy field renderer callable for the mobile grid's
        list item field.
        """
        master = self

        class ListItemRenderer(fa.FieldRenderer):

            def render_readonly(self, **kwargs):
                obj = self.raw_value
                if obj is None:
                    return ''
                title = master.get_instance_title(obj)
                url = master.get_action_url('view', obj, mobile=True)
                return tags.link_to(title, url)

        return ListItemRenderer

    def mobile_row_listitem_renderer(self):
        """
        Must return a FormAlchemy field renderer callable for the mobile row
        grid's list item field.
        """
        master = self

        class ListItemRenderer(fa.FieldRenderer):
            def render_readonly(self, **kwargs):
                return master.render_mobile_row_listitem(self.raw_value, **kwargs)

        return ListItemRenderer

    def create(self):
        """
        View for creating a new model record.
        """
        self.creating = True
        form = self.make_form(self.get_model_class())
        if self.request.method == 'POST':
            if self.validate_form(form):
                # let save_create_form() return alternate object if necessary
                obj = self.save_create_form(form) or form.fieldset.model
                self.after_create(obj)
                self.flash_after_create(obj)
                return self.redirect_after_create(obj)
        context = {'form': form}
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('create', context)

    def mobile_create(self):
        """
        Mobile view for creating a new primary object
        """
        self.creating = True
        form = self.make_mobile_form(self.get_model_class())
        if self.request.method == 'POST':
            if form.validate():
                # let save_create_form() return alternate object if necessary
                obj = self.save_create_form(form) or form.fieldset.model
                self.after_create(obj)
                self.flash_after_create(obj)
                return self.redirect_after_create(obj, mobile=True)
        return self.render_to_response('create', {'form': form}, mobile=True)

    def flash_after_create(self, obj):
        self.request.session.flash("{} has been created: {}".format(
            self.get_model_title(), self.get_instance_title(obj)))

    def save_create_form(self, form):
        self.before_create(form)
        form.save()

    def redirect_after_create(self, instance, mobile=False):
        if self.populatable and self.should_populate(instance):
            return self.redirect(self.get_action_url('populate', instance, mobile=mobile))
        return self.redirect(self.get_action_url('view', instance, mobile=mobile))

    def should_populate(self, obj):
        return True

    def populate(self):
        """
        View for populating a new object.  What exactly this means / does will
        depend on the logic in :meth:`populate_object()`.
        """
        obj = self.get_instance()
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        # showing progress requires a separate thread; start that first
        key = '{}.populate'.format(route_prefix)
        progress = SessionProgress(self.request, key)
        thread = Thread(target=self.populate_thread, args=(obj.uuid, progress)) # TODO: uuid?
        thread.start()

        # Send user to progress page.
        kwargs = {
            'cancel_url': self.get_action_url('view', obj),
            'cancel_msg': "{} population was canceled.".format(self.get_model_title()),
        }

        return self.render_progress(progress, kwargs)

    def populate_thread(self, uuid, progress): # TODO: uuid?
        """
        Thread target for populating new object with progress indicator.
        """
        # mustn't use tailbone web session here
        session = RattailSession()
        obj = session.query(self.model_class).get(uuid)
        try:
            self.populate_object(session, obj, progress=progress)
        except Exception as error:
            session.rollback()
            msg = "{} population failed".format(self.get_model_title())
            log.warning("{}: {}".format(msg, obj), exc_info=True)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "{}: {} {}".format(msg, error.__class__.__name__, error)
                progress.session.save()
            return

        session.commit()
        session.refresh(obj)
        session.close()

        # finalize progress
        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_action_url('view', obj)
            progress.session.save()

    def populate_object(self, session, obj, progress=None):
        """
        You must define this if new objects require population.
        """
        raise NotImplementedError

    def view(self, instance=None):
        """
        View for viewing details of an existing model record.
        """
        self.viewing = True
        if instance is None:
            instance = self.get_instance()
        form = self.make_form(instance)
        if self.has_rows:

            # must make grid prior to redirecting from filter reset, b/c the
            # grid will detect the filter reset request and store defaults in
            # the session, that way redirect will then show The Right Thing
            grid = self.make_row_grid(instance=instance)

            # If user just refreshed the page with a reset instruction, issue a
            # redirect in order to clear out the query string.
            if self.request.GET.get('reset-to-default-filters') == 'true':
                return self.redirect(self.request.current_route_url(_query=None))

            if self.request.params.get('partial'):
                self.request.response.content_type = b'text/html'
                self.request.response.text = grid.render_grid()
                return self.request.response

        context = {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_editable': self.editable_instance(instance),
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if self.has_rows:
            context['rows_grid'] = grid.render_complete(allow_save_defaults=False,
                                                        tools=self.make_row_grid_tools(instance))
        return self.render_to_response('view', context)

    def clone(self):
        """
        View for cloning an object's data into a new object.
        """
        self.viewing = True
        instance = self.get_instance()
        form = self.make_form(instance)
        self.configure_clone_form(form)
        if self.request.method == 'POST' and self.request.POST.get('clone') == 'clone':
            cloned = self.clone_instance(instance)
            return self.redirect(self.get_action_url('view', cloned))
        return self.render_to_response('clone', {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            'instance_url': self.get_action_url('view', instance),
            'form': form,
        })

    def configure_clone_form(self, form):
        pass

    def clone_instance(self, instance):
        raise NotImplementedError

    def versions(self):
        """
        View to list version history for an object.
        """
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)
        grid = self.make_version_grid(instance=instance)

        # return grid only, if partial page was requested
        if self.request.params.get('partial'):
            self.request.response.content_type = b'text/html'
            self.request.response.text = grid.render_grid()
            return self.request.response

        return self.render_to_response('versions', {
            'instance': instance,
            'instance_title': instance_title,
            'instance_url': self.get_action_url('view', instance),
            'grid': grid,
        })

    @classmethod
    def get_version_grid_key(cls):
        """
        Returns the unique key to be used for the version grid, for caching
        sort/filter options etc.
        """
        if hasattr(cls, 'version_grid_key'):
            return cls.version_grid_key
        return '{}.history'.format(cls.get_route_prefix())

    def get_version_data(self, instance):
        """
        Generate the base data set for the version grid.
        """
        model_class = self.get_model_class()
        transaction_class = continuum.transaction_class(model_class)
        query = model_transaction_query(self.Session(), instance, model_class,
                                        child_classes=self.normalize_version_child_classes())
        return query.order_by(transaction_class.issued_at.desc())

    def get_version_child_classes(self):
        """
        If applicable, should return a list of child classes which should be
        considered when querying for version history of an object.
        """
        return []

    def normalize_version_child_classes(self):
        classes = []
        for cls in self.get_version_child_classes():
            if not isinstance(cls, tuple):
                cls = (cls, 'uuid', 'uuid')
            elif len(cls) == 2:
                cls = tuple([cls[0], cls[1], 'uuid'])
            classes.append(cls)
        return classes

    def view_version(self):
        """
        View showing diff details of a particular object version.
        """
        instance = self.get_instance()
        model_class = self.get_model_class()
        Transaction = continuum.transaction_class(model_class)
        transactions = model_transaction_query(self.Session(), instance, model_class,
                                               child_classes=self.normalize_version_child_classes())
        transaction_id = self.request.matchdict['txnid']
        transaction = transactions.filter(Transaction.id == transaction_id).first()
        if not transaction:
            return self.notfound()
        older = transactions.filter(Transaction.issued_at <= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at.desc())\
                            .first()
        newer = transactions.filter(Transaction.issued_at >= transaction.issued_at)\
                            .filter(Transaction.id != transaction_id)\
                            .order_by(Transaction.issued_at)\
                            .first()

        instance_title = self.get_instance_title(instance)
        return self.render_to_response('view_version', {
            'instance': instance,
            'instance_title': "{} (history)".format(instance_title),
            'instance_title_normal': instance_title,
            'instance_url': self.get_action_url('versions', instance),
            'transaction': transaction,
            'changed': localtime(self.rattail_config, transaction.issued_at, from_utc=True),
            'versions': self.get_relevant_versions(transaction, instance),
            'previous_transaction': older,
            'next_transaction': newer,
            'title_for_version': self.title_for_version,
            'fields_for_version': self.fields_for_version,
            'continuum': continuum,
        })

    def title_for_version(self, version):
        cls = continuum.parent_class(version.__class__)
        return cls.get_model_title()

    def fields_for_version(self, version):
        mapper = orm.class_mapper(version.__class__)
        fields = sorted(mapper.columns.keys())
        fields.remove('transaction_id')
        fields.remove('end_transaction_id')
        fields.remove('operation_type')
        return fields

    def get_relevant_versions(self, transaction, instance):
        versions = []
        version_cls = self.get_model_version_class()
        query = self.Session.query(version_cls)\
                            .filter(version_cls.transaction == transaction)\
                            .filter(version_cls.uuid == instance.uuid)
        versions.extend(query.all())
        for cls, foreign_attr, primary_attr in self.normalize_version_child_classes():
            version_cls = continuum.version_class(cls)
            query = self.Session.query(version_cls)\
                                .filter(version_cls.transaction == transaction)\
                                .filter(getattr(version_cls, foreign_attr) == getattr(instance, primary_attr))
            versions.extend(query.all())
        return versions

    def mobile_view(self):
        """
        Mobile view for displaying a single object's details
        """
        self.viewing = True
        instance = self.get_instance()
        form = self.make_mobile_form(instance)

        context = {
            'instance': instance,
            'instance_title': self.get_instance_title(instance),
            # 'instance_editable': self.editable_instance(instance),
            # 'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if self.has_rows:
            context['model_row_class'] = self.model_row_class
            context['grid'] = self.make_mobile_row_grid(instance=instance)
        return self.render_to_response('view', context, mobile=True)

    def make_mobile_form(self, instance, **kwargs):
        """
        Make a FormAlchemy-based form for use with mobile CRUD views
        """
        fieldset = self.make_fieldset(instance)
        self.preconfigure_mobile_fieldset(fieldset)
        self.configure_mobile_fieldset(fieldset)
        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('editing', self.editing)
        kwargs.setdefault('action_url', self.request.current_route_url(_query=None))
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url(mobile=True))
        else:
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance, mobile=True))
        factory = kwargs.pop('factory', forms.AlchemyForm)
        kwargs.setdefault('session', self.Session())
        form = factory(self.request, fieldset, **kwargs)
        form.readonly = self.viewing
        return form

    def preconfigure_mobile_row_fieldset(self, fieldset):
        self._preconfigure_row_fieldset(fieldset)

    def configure_mobile_row_fieldset(self, fieldset):
        self.configure_row_fieldset(fieldset)

    def make_mobile_row_form(self, row, **kwargs):
        """
        Make a form for use with mobile CRUD views, for the given row object.
        """
        fieldset = self.make_fieldset(row)
        self.preconfigure_mobile_row_fieldset(fieldset)
        self.configure_mobile_row_fieldset(fieldset)
        kwargs.setdefault('session', self.Session())
        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('editing', self.editing)
        kwargs.setdefault('action_url', self.request.current_route_url(_query=None))
        if 'cancel_url' not in kwargs:
            kwargs['cancel_url'] = self.get_action_url('view', self.get_parent(row), mobile=True)
        factory = kwargs.pop('factory', forms.AlchemyForm)
        form = factory(self.request, fieldset, **kwargs)
        form.readonly = self.viewing
        return form

    def preconfigure_mobile_fieldset(self, fieldset):
        self._preconfigure_fieldset(fieldset)

    def configure_mobile_fieldset(self, fieldset):
        """
        Configure the given mobile fieldset.
        """
        self.configure_fieldset(fieldset)

    def get_mobile_row_data(self, parent):
        return self.get_row_data(parent)

    def mobile_row_listitem_field(self):
        """
        Must return a FormAlchemy field to be appended to row grid, or ``None``
        if none is desired.
        """
        return fa.Field('listitem', value=lambda obj: obj,
                        renderer=self.mobile_row_listitem_renderer())

    def mobile_row_route_url(self, route_name, **kwargs):
        route_name = 'mobile.{}.{}'.format(self.get_row_route_prefix(), route_name)
        return self.request.route_url(route_name, **kwargs)

    def mobile_view_row(self):
        """
        Mobile view for row items
        """
        self.viewing = True
        row = self.get_row_instance()
        parent = self.get_parent(row)
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'parent_instance': parent,
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'instance_editable': self.row_editable(row),
            'parent_model_title': self.get_model_title(),
            'form': form,
        }
        return self.render_to_response('view_row', context, mobile=True)
        
    def make_default_row_grid_tools(self, obj):
        if self.rows_creatable:
            link = tags.link_to("Create a new {}".format(self.get_row_model_title()),
                                self.get_action_url('create_row', obj))
            return HTML.tag('p', c=link)

    def make_row_grid_tools(self, obj):
        return self.make_default_row_grid_tools(obj)

    # TODO: depracate / remove this
    def get_effective_row_query(self):
        """
        Convenience method which returns the "effective" query for the master
        grid, filtered and sorted to match what would show on the UI, but not
        paged etc.
        """
        return self.get_effective_row_data(sort=False)

    def get_row_data(self, instance):
        """
        Generate the base data set for a rows grid.
        """
        raise NotImplementedError

    def get_effective_row_data(self, session=None, sort=False, **kwargs):
        """
        Convenience method which returns the "effective" data for the row grid,
        filtered (and optionally sorted) to match what would show on the UI,
        but not paged.
        """
        if session is None:
            session = self.Session()
        kwargs.setdefault('pageable', False)
        kwargs.setdefault('sortable', sort)
        grid = self.make_row_grid(session=session, **kwargs)
        return grid.make_visible_data()

    @classmethod
    def get_row_route_prefix(cls):
        """
        Route prefix specific to the row-level views for a batch, e.g.
        ``'vendorcatalogs.rows'``.
        """
        return "{}.rows".format(cls.get_route_prefix())

    @classmethod
    def get_row_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class, for "row" views, e.g. '/products/rows'.
        """
        return getattr(cls, 'row_url_prefix', '{}/rows'.format(cls.get_url_prefix()))

    @classmethod
    def get_row_permission_prefix(cls):
        """
        Permission prefix specific to the row-level data for this batch type,
        e.g. ``'vendorcatalogs.rows'``.
        """
        return "{}.rows".format(cls.get_permission_prefix())

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def row_edit_action_url(self, row, i):
        if self.row_editable(row):
            return self.get_row_action_url('edit', row)

    def row_deletable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def row_delete_action_url(self, row, i):
        if self.row_deletable(row):
            return self.get_row_action_url('delete', row)

    def row_grid_row_attrs(self, row, i):
        return {}

    @classmethod
    def get_row_model_title(cls):
        if hasattr(cls, 'row_model_title'):
            return cls.row_model_title
        return "{} Row".format(cls.get_model_title())

    @classmethod
    def get_row_model_title_plural(cls):
        return "{} Rows".format(cls.get_model_title())

    def view_index(self):
        """
        View a record according to its grid index.
        """
        try:
            index = int(self.request.GET['index'])
        except KeyError, ValueError:
            return self.redirect(self.get_index_url())
        if index < 1:
            return self.redirect(self.get_index_url())
        data = self.get_effective_data()
        try:
            instance = data[index-1]
        except IndexError:
            return self.redirect(self.get_index_url())
        self.grid_index = index
        if hasattr(data, 'count'):
            self.grid_count = data.count()
        else:
            self.grid_count = len(data)
        return self.view(instance)

    def download(self):
        """
        View for downloading a data file.
        """
        obj = self.get_instance()
        filename = self.request.GET.get('filename', None)
        path = self.download_path(obj, filename)
        response = FileResponse(path, request=self.request)
        response.content_length = os.path.getsize(path)
        content_type = self.download_content_type(path, filename)
        if content_type:
            response.content_type = six.binary_type(content_type)
        filename = os.path.basename(path).encode('ascii', 'replace')
        response.content_disposition = b'attachment; filename={}'.format(filename)
        return response

    def download_content_type(self, path, filename):
        """
        Return a content type for a file download, if known.
        """

    def edit(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.editable_instance(instance):
            self.request.session.flash("Edit is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        if self.request.method == 'POST':
            if self.validate_form(form):
                self.save_edit_form(form)
                # note we must fetch new instance title, in case it changed
                self.request.session.flash("{} has been updated: {}".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect_after_edit(instance)

        context = {
            'instance': instance,
            'instance_title': instance_title,
            'instance_deletable': self.deletable_instance(instance),
            'form': form,
        }
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('edit', context)

    def validate_form(self, form):
        return form.validate()

    def save_edit_form(self, form):
        self.save_form(form)
        self.after_edit(form.fieldset.model)

    def redirect_after_edit(self, instance):
        return self.redirect(self.get_action_url('view', instance))

    def delete(self):
        """
        View for deleting an existing model record.
        """
        if not self.deletable:
            raise httpexceptions.HTTPForbidden()

        self.deleting = True
        instance = self.get_instance()
        instance_title = self.get_instance_title(instance)

        if not self.deletable_instance(instance):
            self.request.session.flash("Deletion is not permitted for {}: {}".format(
                self.get_model_title(), instance_title), 'error')
            return self.redirect(self.get_action_url('view', instance))

        form = self.make_form(instance)

        # TODO: Add better validation, ideally CSRF etc.
        if self.request.method == 'POST':

            # Let derived classes prep for (or cancel) deletion.
            result = self.before_delete(instance)
            if isinstance(result, httpexceptions.HTTPException):
                return result

            self.delete_instance(instance)
            self.request.session.flash("{} has been deleted: {}".format(
                self.get_model_title(), instance_title))
            return self.redirect(self.get_after_delete_url(instance))

        form.readonly = True
        return self.render_to_response('delete', {
            'instance': instance,
            'instance_title': instance_title,
            'form': form})

    def bulk_delete(self):
        """
        Delete all records matching the current grid query
        """
        if self.request.method == 'POST':
            objects = self.get_effective_data()
            key = '{}.bulk_delete'.format(self.model_class.__tablename__)
            progress = SessionProgress(self.request, key)
            thread = Thread(target=self.bulk_delete_thread, args=(objects, progress))
            thread.start()
            return self.render_progress(progress, {
                'cancel_url': self.get_index_url(),
                'cancel_msg': "Bulk deletion was canceled",
            })
        else:
            self.request.session.flash("Sorry, you must POST to do a bulk delete operation")
        return self.redirect(self.get_index_url())

    def bulk_delete_objects(self, session, objects, progress=None):

        def delete(obj, i):
            session.delete(obj)
            if i % 1000 == 0:
                session.flush()

        self.progress_loop(delete, objects, progress,
                           message="Deleting objects")

    def get_bulk_delete_session(self):
        return RattailSession()

    def bulk_delete_thread(self, objects, progress):
        """
        Thread target for bulk-deleting current results, with progress.
        """
        session = self.get_bulk_delete_session()
        objects = objects.with_session(session).all()
        try:
            self.bulk_delete_objects(session, objects, progress=progress)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("execution failed for batch results")
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Bulk deletion failed: {}: {}".format(type(error).__name__, error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = self.get_index_url()
                progress.session.save()

    def execute(self):
        """
        Execute an object.
        """
        obj = self.get_instance()
        model_title = self.get_model_title()
        if self.request.method == 'POST':

            progress = self.make_execute_progress(obj)
            kwargs = {'progress': progress}
            thread = Thread(target=self.execute_thread, args=(obj.uuid, self.request.user.uuid), kwargs=kwargs)
            thread.start()

            return self.render_progress(progress, {
                'instance': obj,
                'initial_msg': self.execute_progress_initial_msg,
                'cancel_url': self.get_action_url('view', obj),
                'cancel_msg': "{} execution was canceled".format(model_title),
            }, template=self.execute_progress_template)

        self.request.session.flash("Sorry, you must POST to execute a {}.".format(model_title), 'error')
        return self.redirect(self.get_action_url('view', obj))

    def make_execute_progress(self, obj):
        key = '{}.execute'.format(self.get_grid_key())
        return SessionProgress(self.request, key)

    def execute_thread(self, uuid, user_uuid, progress=None, **kwargs):
        """
        Thread target for executing an object.
        """
        session = RattailSession()
        obj = session.query(self.model_class).get(uuid)
        user = session.query(model.User).get(user_uuid)
        try:
            self.execute_instance(obj, user, progress=progress, **kwargs)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("{} failed to execute: {}".format(self.get_model_title(), obj))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = self.execute_error_message(error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            session.commit()
            session.refresh(obj)
            success_url = self.get_execute_success_url(obj)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    def execute_error_message(self, error):
        return "Execution of {} failed: {}: {}".format(self.get_model_title(),
                                                       type(error).__name__, error)

    def get_execute_success_url(self, obj, **kwargs):
        return self.get_action_url('view', obj, **kwargs)

    def get_merge_fields(self):
        if hasattr(self, 'merge_fields'):
            return self.merge_fields
        mapper = orm.class_mapper(self.get_model_class())
        return mapper.columns.keys()

    def get_merge_coalesce_fields(self):
        if hasattr(self, 'merge_coalesce_fields'):
            return self.merge_coalesce_fields
        return []

    def get_merge_additive_fields(self):
        if hasattr(self, 'merge_additive_fields'):
            return self.merge_additive_fields
        return []

    def merge(self):
        """
        Preview and execute a merge of two records.
        """
        object_to_remove = object_to_keep = None
        if self.request.method == 'POST':
            uuids = self.request.POST.get('uuids', '').split(',')
            if len(uuids) == 2:
                object_to_remove = self.Session.query(self.get_model_class()).get(uuids[0])
                object_to_keep = self.Session.query(self.get_model_class()).get(uuids[1])

                if object_to_remove and object_to_keep and self.request.POST.get('commit-merge') == 'yes':
                    msg = six.text_type(object_to_remove)
                    try:
                        self.validate_merge(object_to_remove, object_to_keep)
                    except Exception as error:
                        self.request.session.flash("Requested merge cannot proceed (maybe swap kept/removed and try again?): {}".format(error), 'error')
                    else:
                        self.merge_objects(object_to_remove, object_to_keep)
                        self.request.session.flash("{} has been merged into {}".format(msg, object_to_keep))
                        return self.redirect(self.get_action_url('view', object_to_keep))

        if not object_to_remove or not object_to_keep or object_to_remove is object_to_keep:
            return self.redirect(self.get_index_url())

        remove = self.get_merge_data(object_to_remove)
        keep = self.get_merge_data(object_to_keep)
        return self.render_to_response('merge', {'object_to_remove': object_to_remove,
                                                 'object_to_keep': object_to_keep,
                                                 'view_url': lambda obj: self.get_action_url('view', obj),
                                                 'merge_fields': self.get_merge_fields(),
                                                 'remove_data': remove,
                                                 'keep_data': keep,
                                                 'resulting_data': self.get_merge_resulting_data(remove, keep)})

    def validate_merge(self, removing, keeping):
        """
        If applicable, your view should override this in order to confirm that
        the requested merge is valid, in your context.  If it is not - for *any
        reason* - you should raise an exception; the type does not matter.
        """

    def get_merge_data(self, obj):
        raise NotImplementedError("please implement `{}.get_merge_data()`".format(self.__class__.__name__))

    def get_merge_resulting_data(self, remove, keep):
        result = dict(keep)
        for field in self.get_merge_coalesce_fields():
            if remove[field] and not keep[field]:
                result[field] = remove[field]
        for field in self.get_merge_additive_fields():
            if isinstance(keep[field], (list, tuple)):
                result[field] = sorted(set(remove[field] + keep[field]))
            else:
                result[field] = remove[field] + keep[field]
        return result

    def merge_objects(self, removing, keeping):
        """
        Merge the two given objects.  You should probably override this;
        default behavior is merely to delete the 'removing' object.
        """
        self.Session.delete(removing)

    ##############################
    # Core Stuff
    ##############################

    @classmethod
    def get_model_class(cls, error=True):
        """
        Returns the data model class for which the master view exists.
        """
        if not hasattr(cls, 'model_class') and error:
            raise NotImplementedError("You must define the `model_class` for: {}".format(cls))
        return getattr(cls, 'model_class', None)

    @classmethod
    def get_model_version_class(cls):
        """
        Returns the version class for the master model class.
        """
        return continuum.version_class(cls.get_model_class())

    @classmethod
    def get_normalized_model_name(cls):
        """
        Returns the "normalized" name for the view's model class.  This will be
        the value of the :attr:`normalized_model_name` attribute if defined;
        otherwise it will be a simple lower-cased version of the associated
        model class name.
        """
        if hasattr(cls, 'normalized_model_name'):
            return cls.normalized_model_name
        return cls.get_model_class().__name__.lower()

    @classmethod
    def get_model_key(cls):
        """
        Return a string name for the primary key of the model class.
        """
        if hasattr(cls, 'model_key'):
            return cls.model_key
        mapper = orm.class_mapper(cls.get_model_class())
        return ','.join([k.key for k in mapper.primary_key])

    @classmethod
    def get_model_title(cls):
        """
        Return a "humanized" version of the model name, for display in templates.
        """
        if hasattr(cls, 'model_title'):
            return cls.model_title
        return cls.get_model_class().get_model_title()

    @classmethod
    def get_model_title_plural(cls):
        """
        Return a "humanized" (and plural) version of the model name, for
        display in templates.
        """
        if hasattr(cls, 'model_title_plural'):
            return cls.model_title_plural
        try:
            return cls.get_model_class().get_model_title_plural()
        except (NotImplementedError, AttributeError):
            return '{}s'.format(cls.get_model_title())

    @classmethod
    def get_route_prefix(cls):
        """
        Returns a prefix which (by default) applies to all routes provided by
        the master view class.  This is the plural, lower-cased name of the
        model class by default, e.g. 'products'.
        """
        model_name = cls.get_normalized_model_name()
        return getattr(cls, 'route_prefix', '{0}s'.format(model_name))

    @classmethod
    def get_url_prefix(cls):
        """
        Returns a prefix which (by default) applies to all URLs provided by the
        master view class.  By default this is the route prefix, preceded by a
        slash, e.g. '/products'.
        """
        return getattr(cls, 'url_prefix', '/{0}'.format(cls.get_route_prefix()))

    @classmethod
    def get_template_prefix(cls):
        """
        Returns a prefix which (by default) applies to all templates required by
        the master view class.  This uses the URL prefix by default.
        """
        return getattr(cls, 'template_prefix', cls.get_url_prefix())

    @classmethod
    def get_permission_prefix(cls):
        """
        Returns a prefix which (by default) applies to all permissions leveraged by
        the master view class.  This uses the route prefix by default.
        """
        return getattr(cls, 'permission_prefix', cls.get_route_prefix())

    def get_index_url(self, mobile=False, **kwargs):
        """
        Returns the master view's index URL.
        """
        route = self.get_route_prefix()
        if mobile:
            route = 'mobile.{}'.format(route)
        return self.request.route_url(route)

    @classmethod
    def get_index_title(cls):
        """
        Returns the title for the index page.
        """
        return getattr(cls, 'index_title', cls.get_model_title_plural())

    def get_action_url(self, action, instance, mobile=False, **kwargs):
        """
        Generate a URL for the given action on the given instance
        """
        kw = self.get_action_route_kwargs(instance)
        kw.update(kwargs)
        route_prefix = self.get_route_prefix()
        if mobile:
            route_prefix = 'mobile.{}'.format(route_prefix)
        return self.request.route_url('{}.{}'.format(route_prefix, action), **kw)

    def render_to_response(self, template, data, mobile=False):
        """
        Return a response with the given template rendered with the given data.
        Note that ``template`` must only be a "key" (e.g. 'index' or 'view').
        First an attempt will be made to render using the :attr:`template_prefix`.
        If that doesn't work, another attempt will be made using '/master' as
        the template prefix.
        """
        context = {
            'master': self,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(mobile=mobile),
            'action_url': self.get_action_url,
            'grid_index': self.grid_index,
        }

        if self.grid_index:
            context['grid_count'] = self.grid_count

        if self.has_rows:
            context['row_route_prefix'] = self.get_row_route_prefix()
            context['row_permission_prefix'] = self.get_row_permission_prefix()
            context['row_model_title'] = self.get_row_model_title()
            context['row_model_title_plural'] = self.get_row_model_title_plural()
            context['row_action_url'] = self.get_row_action_url

        context.update(data)
        context.update(self.template_kwargs(**context))
        if hasattr(self, 'template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'template_kwargs_{}'.format(template))(**context))
        if hasattr(self, 'mobile_template_kwargs_{}'.format(template)):
            context.update(getattr(self, 'mobile_template_kwargs_{}'.format(template))(**context))

        # First try the template path most specific to the view.
        if mobile:
            mako_path = '/mobile{}/{}.mako'.format(self.get_template_prefix(), template)
        else:
            mako_path = '{}/{}.mako'.format(self.get_template_prefix(), template)
        try:
            return render_to_response(mako_path, context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template, mobile=mobile):
                try:
                    return render_to_response(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render_to_response('{}/{}.mako'.format(self.get_template_prefix(), template),
                                      context, request=self.request)

    # TODO: merge this logic with render_to_response()
    def render(self, template, data):
        """
        Render the given template with the given context data.
        """
        context = {
            'master': self,
            'model_title': self.get_model_title(),
            'model_title_plural': self.get_model_title_plural(),
            'route_prefix': self.get_route_prefix(),
            'permission_prefix': self.get_permission_prefix(),
            'index_title': self.get_index_title(),
            'index_url': self.get_index_url(),
            'action_url': self.get_action_url,
        }
        context.update(data)

        # First try the template path most specific to the view.
        try:
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

        except IOError:

            # Failing that, try one or more fallback templates.
            for fallback in self.get_fallback_templates(template):
                try:
                    return render(fallback, context, request=self.request)
                except IOError:
                    pass

            # If we made it all the way here, we found no templates at all, in
            # which case re-attempt the first and let that error raise on up.
            return render('{}/{}.mako'.format(self.get_template_prefix(), template),
                          context, request=self.request)

    def get_fallback_templates(self, template, mobile=False):
        if mobile:
            return ['/mobile/master/{}.mako'.format(template)]
        return ['/master/{}.mako'.format(template)]

    def template_kwargs(self, **kwargs):
        """
        Supplement the template context, for all views.
        """
        return kwargs

    ##############################
    # Grid Stuff
    ##############################

    @classmethod
    def get_grid_key(cls):
        """
        Returns the unique key to be used for the grid, for caching sort/filter
        options etc.
        """
        if hasattr(cls, 'grid_key'):
            return cls.grid_key
        # default previously came from cls.get_normalized_model_name() but this is hopefully better
        return cls.get_route_prefix()

    def get_row_grid_key(self):
        return '{}.{}'.format(self.get_grid_key(), self.request.matchdict[self.get_model_key()])

    def get_grid_actions(self):
        main, more = self.get_main_actions(), self.get_more_actions()
        if len(more) == 1:
            main, more = main + more, []
        if len(main + more) <= 3:
            main, more = main + more, []
        return main, more

    def get_row_attrs(self, row, i):
        """
        Returns a dict of HTML attributes which is to be applied to the row's
        ``<tr>`` element.  Note that ``i`` will be a 1-based index value for
        the row within its table.  The meaning of ``row`` is basically not
        defined; it depends on the type of data the grid deals with.
        """
        if callable(self.row_attrs):
            attrs = self.row_attrs(row, i)
        else:
            attrs = dict(self.row_attrs)
        if self.mergeable:
            attrs['data-uuid'] = row.uuid
        return attrs

    def get_cell_attrs(self, row, column):
        """
        Returns a dictionary of HTML attributes which should be applied to the
        ``<td>`` element in which the given row and column "intersect".
        """
        if callable(self.cell_attrs):
            return self.cell_attrs(row, column)
        return self.cell_attrs

    def get_main_actions(self):
        """
        Return a list of 'main' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        if self.viewable and self.request.has_perm('{}.view'.format(prefix)):
            url = self.get_view_index_url if self.use_index_links else None
            actions.append(self.make_action('view', icon='zoomin', url=url))
        return actions

    def get_view_index_url(self, row, i):
        route = '{}.view_index'.format(self.get_route_prefix())
        return '{}?index={}'.format(self.request.route_url(route), self.first_visible_grid_index + i - 1)

    def get_more_actions(self):
        """
        Return a list of 'more' actions for the grid.
        """
        actions = []
        prefix = self.get_permission_prefix()
        if self.editable and self.request.has_perm('{}.edit'.format(prefix)):
            actions.append(self.make_action('edit', icon='pencil', url=self.default_edit_url))
        if self.deletable and self.request.has_perm('{}.delete'.format(prefix)):
            actions.append(self.make_action('delete', icon='trash', url=self.default_delete_url))
        return actions

    def default_edit_url(self, row, i=None):
        if self.editable_instance(row):
            return self.request.route_url('{}.edit'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def default_delete_url(self, row, i=None):
        if self.deletable_instance(row):
            return self.request.route_url('{}.delete'.format(self.get_route_prefix()),
                                          **self.get_action_route_kwargs(row))

    def make_action(self, key, url=None, **kwargs):
        """
        Make a new :class:`GridAction` instance for the current grid.
        """
        if url is None:
            route = '{}.{}'.format(self.get_route_prefix(), key)
            url = lambda r, i: self.request.route_url(route, **self.get_action_route_kwargs(r))
        return grids.GridAction(key, url=url, **kwargs)

    def get_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        try:
            mapper = orm.object_mapper(row)
        except orm.exc.UnmappedInstanceError:
            return {self.model_key: row[self.model_key]}
        else:
            keys = [k.key for k in mapper.primary_key]
            values = [getattr(row, k) for k in keys]
            return dict(zip(keys, values))

    def get_data(self, session=None):
        """
        Generate the base data set for the grid.  This typically will be a
        SQLAlchemy query against the view's model class, but subclasses may
        override this to support arbitrary data sets.

        Note that if your view is typical and uses a SA model, you should not
        override this methid, but override :meth:`query()` instead.
        """
        if session is None:
            session = self.Session()
        return self.query(session)

    def query(self, session):
        """
        Produce the initial/base query for the master grid.  By default this is
        simply a query against the model class, but you may override as
        necessary to apply any sort of pre-filtering etc.  This is useful if
        say, you don't ever want to show records of a certain type to non-admin
        users.  You would modify the base query to hide what you wanted,
        regardless of the user's filter selections.
        """
        return session.query(self.get_model_class())

    def get_effective_query(self, session=None, **kwargs):
        return self.get_effective_data(session=session, **kwargs)

    def checkbox(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        rendererd for the given row.  Default implementation returns ``True``
        in all cases.
        """
        return True

    def checked(self, instance):
        """
        Returns a boolean indicating whether ot not a checkbox should be
        checked by default, for the given row.  Default implementation returns
        ``False`` in all cases.
        """
        return False

    def results_csv(self):
        """
        Download current list results as CSV
        """
        results = self.get_effective_data()
        fields = self.get_csv_fields()
        data = six.StringIO()
        writer = UnicodeDictWriter(data, fields)
        writer.writeheader()
        for obj in results:
            writer.writerow(self.get_csv_row(obj, fields))
        response = self.request.response
        response.body = data.getvalue()
        data.close()
        response.content_length = len(response.body)
        response.content_type = b'text/csv'
        response.content_disposition = b'attachment; filename={}.csv'.format(self.get_grid_key())
        return response

    def row_results_csv(self):
        """
        Download current row results data for an object, as CSV
        """
        obj = self.get_instance()
        fields = self.get_row_csv_fields()
        data = six.StringIO()
        writer = UnicodeDictWriter(data, fields)
        writer.writeheader()
        for row in self.get_effective_row_data(sort=True):
            writer.writerow(self.get_row_csv_row(row, fields))
        response = self.request.response
        response.body = data.getvalue()
        data.close()
        response.content_length = len(response.body)
        response.content_type = b'text/csv'
        filename = self.get_row_results_csv_filename(obj)
        response.content_disposition = b'attachment; filename={}'.format(filename)
        return response

    def get_row_results_csv_filename(self, instance):
        return '{}.csv'.format(self.get_row_grid_key())

    def get_csv_fields(self):
        """
        Return the list of fields to be written to CSV download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_row_csv_fields(self):
        """
        Return the list of row fields to be written to CSV download.
        """
        fields = []
        mapper = orm.class_mapper(self.model_row_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty):
                fields.append(prop.key)
        return fields

    def get_csv_row(self, obj, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(obj, field, None)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    def get_row_csv_row(self, row, fields):
        """
        Return a dict for use when writing the row's data to CSV download.
        """
        csvrow = {}
        for field in fields:
            value = getattr(row, field, None)
            csvrow[field] = '' if value is None else six.text_type(value)
        return csvrow

    ##############################
    # CRUD Stuff
    ##############################

    def get_instance(self):
        """
        Fetch the current model instance by inspecting the route kwargs and
        doing a database lookup.  If the instance cannot be found, raises 404.
        """
        # TODO: this can't handle composite model key..is that needed?
        key = self.request.matchdict[self.get_model_key()]
        instance = self.Session.query(self.get_model_class()).get(key)
        if not instance:
            raise httpexceptions.HTTPNotFound()
        return instance

    def get_instance_title(self, instance):
        """
        Return a "pretty" title for the instance, to be used in the page title etc.
        """
        return six.text_type(instance)

    def make_form(self, instance, **kwargs):
        """
        Make a FormAlchemy-based form for use with CRUD views.
        """
        # TODO: Some hacky stuff here, to accommodate old form cruft.  Probably
        # should refactor forms soon too, but trying to avoid it for the moment.

        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('editing', self.editing)

        fieldset = self.make_fieldset(instance)
        self._preconfigure_fieldset(fieldset)
        self.configure_fieldset(fieldset)
        self._postconfigure_fieldset(fieldset)

        kwargs.setdefault('action_url', self.request.current_route_url(_query=None))
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url())
        else:
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance))
        factory = kwargs.pop('factory', forms.AlchemyForm)
        kwargs.setdefault('session', self.Session())
        form = factory(self.request, fieldset, **kwargs)
        form.readonly = self.viewing
        return form

    def save_form(self, form):
        form.save()

    def make_fieldset(self, instance, **kwargs):
        """
        Make a FormAlchemy fieldset for the given model instance.
        """
        kwargs.setdefault('session', self.Session())
        kwargs.setdefault('request', self.request)
        fieldset = fa.FieldSet(instance, **kwargs)
        fieldset.prettify = prettify
        return fieldset

    def _preconfigure_fieldset(self, fieldset):
        pass

    def configure_fieldset(self, fieldset):
        """
        Configure the given fieldset.
        """
        fieldset.configure()

    def _postconfigure_fieldset(self, fieldset):
        pass

    def before_create(self, form):
        """
        Event hook, called just after the form to create a new instance has
        been validated, but prior to the form itself being saved.
        """

    def after_create(self, instance):
        """
        Event hook, called just after a new instance is saved.
        """

    def editable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def after_edit(self, instance):
        """
        Event hook, called just after an existing instance is saved.
        """

    def deletable_instance(self, instance):
        """
        Returns boolean indicating whether or not the given instance can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def before_delete(self, instance):
        """
        Event hook, called just before deletion is attempted.
        """

    def delete_instance(self, instance):
        """
        Delete the instance, or mark it as deleted, or whatever you need to do.
        """
        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(instance)
        self.Session.flush()

    def get_after_delete_url(self, instance):
        """
        Returns the URL to which the user should be redirected after
        successfully "deleting" the given instance.
        """
        if hasattr(self, 'after_delete_url'):
            if callable(self.after_delete_url):
                return self.after_delete_url(instance)
            return self.after_delete_url
        return self.get_index_url()

    ##############################
    # Associated Rows Stuff
    ##############################

    def create_row(self):
        """
        View for creating a new row record.
        """
        self.creating = True
        parent = self.get_instance()
        index_url = self.get_action_url('view', parent)
        form = self.make_row_form(self.model_row_class, cancel_url=index_url)
        if self.request.method == 'POST':
            if form.validate():
                self.before_create_row(form)
                self.save_create_row_form(form)
                obj = form.fieldset.model
                self.after_create_row(obj)
                return self.redirect_after_create_row(obj)
        return self.render_to_response('create_row', {
            'index_url': index_url,
            'index_title': '{} {}'.format(
                self.get_model_title(),
                self.get_instance_title(parent)),
            'form': form})

    def save_create_row_form(self, form):
        self.save_row_form(form)

    def before_create_row(self, form):
        pass

    def after_create_row(self, row_object):
        pass

    def redirect_after_create_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('view', row, mobile=mobile))

    def mobile_create_row(self):
        """
        Mobile view for creating a new row object
        """
        self.creating = True
        parent = self.get_instance()
        instance_url = self.get_action_url('view', parent, mobile=True)
        form = self.make_mobile_row_form(self.model_row_class, cancel_url=instance_url)
        if self.request.method == 'POST':
            if form.validate():
                self.before_create_row(form)
                # let save() return alternate object if necessary
                obj = self.save_create_row_form(form) or form.fieldset.model
                self.after_create_row(obj)
                return self.redirect_after_create_row(obj, mobile=True)
        return self.render_to_response('create_row', {
            'instance_title': self.get_instance_title(parent),
            'instance_url': instance_url,
            'parent_object': parent,
            'form': form,
        }, mobile=True)

    def view_row(self):
        """
        View for viewing details of a single data row.
        """
        self.viewing = True
        row = self.get_row_instance()
        form = self.make_row_form(row)
        parent = self.get_parent(row)
        return self.render_to_response('view_row', {
            'instance': row,
            'instance_title': self.get_instance_title(parent),
            'instance_url': self.get_action_url('view', parent),
            'instance_editable': self.row_editable(row),
            'instance_deletable': self.row_deletable(row),
            'rows_creatable': self.rows_creatable and self.rows_creatable_for(parent),
            'model_title': self.get_row_model_title(),
            'model_title_plural': self.get_row_model_title_plural(),
            'parent_model_title': self.get_model_title(),
            'action_url': self.get_row_action_url,
            'form': form})

    def rows_creatable_for(self, instance):
        """
        Returns boolean indicating whether or not the given instance should
        allow new rows to be added to it.
        """
        return True

    def row_editable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "editable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def edit_row(self):
        """
        View for editing an existing model record.
        """
        self.editing = True
        row = self.get_row_instance()
        form = self.make_row_form(row)

        if self.request.method == 'POST':
            if form.validate():
                self.save_edit_row_form(form)
                return self.redirect_after_edit_row(row)

        parent = self.get_parent(row)
        return self.render_to_response('edit_row', {
            'instance': row,
            'row_parent': parent,
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent),
            'parent_instance': parent,
            'instance_title': self.get_row_instance_title(row),
            'instance_deletable': self.row_deletable(row),
            'form': form})

    def mobile_edit_row(self):
        """
        Mobile view for editing a row object
        """
        self.editing = True
        row = self.get_row_instance()
        instance_url = self.get_row_action_url('view', row, mobile=True)
        form = self.make_mobile_row_form(row)

        if self.request.method == 'POST':
            if form.validate():
                self.save_edit_row_form(form)
                return self.redirect_after_edit_row(row, mobile=True)

        parent = self.get_parent(row)
        return self.render_to_response('edit_row', {
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'instance_url': instance_url,
            'instance_deletable': self.row_deletable(row),
            'parent_instance': parent,
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'form': form},
        mobile=True)

    def save_edit_row_form(self, form):
        self.save_row_form(form)
        self.after_edit_row(form.fieldset.model)

    def save_row_form(self, form):
        form.save()

    def after_edit_row(self, row):
        """
        Event hook, called just after an existing row object is saved.
        """

    def redirect_after_edit_row(self, row, mobile=False):
        return self.redirect(self.get_row_action_url('view', row, mobile=mobile))

    def row_deletable(self, row):
        """
        Returns boolean indicating whether or not the given row can be
        considered "deletable".  Returns ``True`` by default; override as
        necessary.
        """
        return True

    def delete_row(self):
        """
        "Delete" a sub-row from the parent.
        """
        row = self.Session.query(self.model_row_class).get(self.request.matchdict['uuid'])
        if not row:
            raise httpexceptions.HTTPNotFound()
        self.Session.delete(row)
        return self.redirect(self.get_action_url('edit', self.get_parent(row)))

    def get_parent(self, row):
        raise NotImplementedError

    def get_row_instance_title(self, instance):
        return self.get_row_model_title()

    def get_row_instance(self):
        key = self.request.matchdict[self.get_model_key()]
        instance = self.Session.query(self.model_row_class).get(key)
        if not instance:
            raise httpexceptions.HTTPNotFound()
        return instance

    def make_row_form(self, instance, **kwargs):
        """
        Make a FormAlchemy form for use with CRUD views for a data *row*.
        """
        # TODO: Some hacky stuff here, to accommodate old form cruft.  Probably
        # should refactor forms soon too, but trying to avoid it for the moment.

        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('editing', self.editing)

        fieldset = self.make_fieldset(instance)
        self._preconfigure_row_fieldset(fieldset)
        self.configure_row_fieldset(fieldset)

        kwargs.setdefault('action_url', self.request.current_route_url(_query=None))
        if 'cancel_url' not in kwargs:
            if self.creating:
                kwargs['cancel_url'] = self.get_action_url('view', self.get_parent(instance))
            else:
                kwargs['cancel_url'] = self.get_row_action_url('view', instance)

        kwargs.setdefault('session', self.Session())
        form = forms.AlchemyForm(self.request, fieldset, **kwargs)
        form.readonly = self.viewing
        return form

    def _preconfigure_row_fieldset(self, fs):
        pass

    def configure_row_fieldset(self, fs):
        fs.configure()

    def get_row_action_url(self, action, row, mobile=False):
        """
        Generate a URL for the given action on the given row.
        """
        route_name = '{}.{}'.format(self.get_row_route_prefix(), action)
        if mobile:
            route_name = 'mobile.{}'.format(route_name)
        return self.request.route_url(route_name, **self.get_row_action_route_kwargs(row))

    def get_row_action_route_kwargs(self, row):
        """
        Hopefully generic kwarg generator for basic action routes.
        """
        # TODO: make this smarter?
        return {'uuid': row.uuid}

    def make_diff(self, old_data, new_data, **kwargs):
        return diffs.Diff(old_data, new_data, **kwargs)

    ##############################
    # Config Stuff
    ##############################

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()
        if cls.has_rows:
            row_route_prefix = cls.get_row_route_prefix()
            row_url_prefix = cls.get_row_url_prefix()
            row_model_title = cls.get_row_model_title()

        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # list/search
        if cls.listable:
            config.add_tailbone_permission(permission_prefix, '{}.list'.format(permission_prefix),
                                           "List / search {}".format(model_title_plural))
            config.add_route(route_prefix, '{}/'.format(url_prefix))
            config.add_view(cls, attr='index', route_name=route_prefix,
                            permission='{}.list'.format(permission_prefix))
            if cls.supports_mobile:
                config.add_route('mobile.{}'.format(route_prefix), '/mobile{}/'.format(url_prefix))
                config.add_view(cls, attr='mobile_index', route_name='mobile.{}'.format(route_prefix),
                                permission='{}.list'.format(permission_prefix))

            if cls.results_downloadable_csv:
                config.add_tailbone_permission(permission_prefix, '{}.results_csv'.format(permission_prefix),
                                               "Download {} as CSV".format(model_title_plural))
                config.add_route('{}.results_csv'.format(route_prefix), '{}/csv'.format(url_prefix))
                config.add_view(cls, attr='results_csv', route_name='{}.results_csv'.format(route_prefix),
                                permission='{}.results_csv'.format(permission_prefix))


        # create
        if cls.creatable or cls.mobile_creatable:
            config.add_tailbone_permission(permission_prefix, '{}.create'.format(permission_prefix),
                                           "Create new {}".format(model_title))
        if cls.creatable:
            config.add_route('{}.create'.format(route_prefix), '{}/new'.format(url_prefix))
            config.add_view(cls, attr='create', route_name='{}.create'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))
        if cls.mobile_creatable:
            config.add_route('mobile.{}.create'.format(route_prefix), '/mobile{}/new'.format(url_prefix))
            config.add_view(cls, attr='mobile_create', route_name='mobile.{}.create'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # populate new object
        if cls.populatable:
            config.add_route('{}.populate'.format(route_prefix), '{}/{{uuid}}/populate'.format(url_prefix))
            config.add_view(cls, attr='populate', route_name='{}.populate'.format(route_prefix),
                            permission='{}.create'.format(permission_prefix))

        # bulk delete
        if cls.bulk_deletable:
            config.add_route('{}.bulk_delete'.format(route_prefix), '{}/bulk-delete'.format(url_prefix))
            config.add_view(cls, attr='bulk_delete', route_name='{}.bulk_delete'.format(route_prefix),
                            permission='{}.bulk_delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.bulk_delete'.format(permission_prefix),
                                           "Bulk delete {}".format(model_title_plural))

        # merge
        if cls.mergeable:
            config.add_route('{}.merge'.format(route_prefix), '{}/merge'.format(url_prefix))
            config.add_view(cls, attr='merge', route_name='{}.merge'.format(route_prefix),
                            permission='{}.merge'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.merge'.format(permission_prefix),
                                           "Merge 2 {}".format(model_title_plural))

        # view
        if cls.viewable:
            config.add_tailbone_permission(permission_prefix, '{}.view'.format(permission_prefix),
                                           "View details for {}".format(model_title))
            if cls.has_pk_fields:
                config.add_tailbone_permission(permission_prefix, '{}.view_pk_fields'.format(permission_prefix),
                                               "View all PK-type fields for {}".format(model_title_plural))

            # view by grid index
            config.add_route('{}.view_index'.format(route_prefix), '{}/view'.format(url_prefix))
            config.add_view(cls, attr='view_index', route_name='{}.view_index'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))

            # view by record key
            config.add_route('{}.view'.format(route_prefix), '{}/{{{}}}'.format(url_prefix, model_key))
            config.add_view(cls, attr='view', route_name='{}.view'.format(route_prefix),
                            permission='{}.view'.format(permission_prefix))
            if cls.supports_mobile:
                config.add_route('mobile.{}.view'.format(route_prefix), '/mobile{}/{{{}}}'.format(url_prefix, model_key))
                config.add_view(cls, attr='mobile_view', route_name='mobile.{}.view'.format(route_prefix),
                                permission='{}.view'.format(permission_prefix))

            # version history
            if cls.has_versions and rattail_config and rattail_config.versioning_enabled():
                config.add_tailbone_permission(permission_prefix, '{}.versions'.format(permission_prefix),
                                               "View version history for {}".format(model_title))
                config.add_route('{}.versions'.format(route_prefix), '{}/{{{}}}/versions/'.format(url_prefix, model_key))
                config.add_view(cls, attr='versions', route_name='{}.versions'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))
                config.add_route('{}.version'.format(route_prefix), '{}/{{{}}}/versions/{{txnid}}'.format(url_prefix, model_key))
                config.add_view(cls, attr='view_version', route_name='{}.version'.format(route_prefix),
                                permission='{}.versions'.format(permission_prefix))

        # clone
        if cls.cloneable:
            config.add_tailbone_permission(permission_prefix, '{}.clone'.format(permission_prefix),
                                           "Clone an existing {0} as a new {0}".format(model_title))
            config.add_route('{}.clone'.format(route_prefix), '{}/{{{}}}/clone'.format(url_prefix, model_key))
            config.add_view(cls, attr='clone', route_name='{}.clone'.format(route_prefix),
                            permission='{}.clone'.format(permission_prefix))

        # download
        if cls.downloadable:
            config.add_route('{}.download'.format(route_prefix), '{}/{{{}}}/download'.format(url_prefix, model_key))
            config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                            permission='{}.download'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                           "Download associated data for {}".format(model_title))

        # edit
        if cls.editable:
            config.add_route('{0}.edit'.format(route_prefix), '{0}/{{{1}}}/edit'.format(url_prefix, model_key))
            config.add_view(cls, attr='edit', route_name='{0}.edit'.format(route_prefix),
                            permission='{0}.edit'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.edit'.format(permission_prefix),
                                           "Edit {0}".format(model_title))

        # execute
        if cls.executable:
            config.add_tailbone_permission(permission_prefix, '{}.execute'.format(permission_prefix),
                                           "Execute {}".format(model_title))
            config.add_route('{}.execute'.format(route_prefix), '{}/{{{}}}/execute'.format(url_prefix, model_key))
            config.add_view(cls, attr='execute', route_name='{}.execute'.format(route_prefix),
                            permission='{}.execute'.format(permission_prefix))

        # delete
        if cls.deletable:
            config.add_route('{0}.delete'.format(route_prefix), '{0}/{{{1}}}/delete'.format(url_prefix, model_key))
            config.add_view(cls, attr='delete', route_name='{0}.delete'.format(route_prefix),
                            permission='{0}.delete'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{0}.delete'.format(permission_prefix),
                                           "Delete {0}".format(model_title))

        ### sub-rows stuff follows

        # download row results as CSV
        if cls.has_rows and cls.rows_downloadable_csv:
            config.add_tailbone_permission(permission_prefix, '{}.row_results_csv'.format(permission_prefix),
                                           "Download {} results as CSV".format(row_model_title))
            config.add_route('{}.row_results_csv'.format(route_prefix), '{}/{{uuid}}/rows-csv'.format(url_prefix))
            config.add_view(cls, attr='row_results_csv', route_name='{}.row_results_csv'.format(route_prefix),
                            permission='{}.row_results_csv'.format(permission_prefix))

        # create row
        if cls.has_rows:
            if cls.rows_creatable or cls.mobile_rows_creatable:
                config.add_tailbone_permission(permission_prefix, '{}.create_row'.format(permission_prefix),
                                               "Create new {} rows".format(model_title))
            if cls.rows_creatable:
                config.add_route('{}.create_row'.format(route_prefix), '{}/{{{}}}/new-row'.format(url_prefix, model_key))
                config.add_view(cls, attr='create_row', route_name='{}.create_row'.format(route_prefix),
                                permission='{}.create_row'.format(permission_prefix))
            if cls.mobile_rows_creatable:
                config.add_route('mobile.{}.create_row'.format(route_prefix), '/mobile{}/{{{}}}/new-row'.format(url_prefix, model_key))
                config.add_view(cls, attr='mobile_create_row', route_name='mobile.{}.create_row'.format(route_prefix),
                                permission='{}.create_row'.format(permission_prefix))

        # view row
        if cls.has_rows:
            if cls.rows_viewable:
                config.add_route('{}.view'.format(row_route_prefix), '{}/{{uuid}}'.format(row_url_prefix))
                config.add_view(cls, attr='view_row', route_name='{}.view'.format(row_route_prefix),
                                permission='{}.view'.format(permission_prefix))
            if cls.mobile_rows_viewable:
                config.add_route('mobile.{}.view'.format(row_route_prefix), '/mobile{}/{{uuid}}'.format(row_url_prefix))
                config.add_view(cls, attr='mobile_view_row', route_name='mobile.{}.view'.format(row_route_prefix),
                                permission='{}.view'.format(permission_prefix))

        # edit row
        if cls.has_rows:
            if cls.rows_editable or cls.mobile_rows_editable:
                config.add_tailbone_permission(permission_prefix, '{}.edit_row'.format(permission_prefix),
                                               "Edit individual {} rows".format(model_title))
            if cls.rows_editable:
                config.add_route('{}.edit'.format(row_route_prefix), '{}/{{uuid}}/edit'.format(row_url_prefix))
                config.add_view(cls, attr='edit_row', route_name='{}.edit'.format(row_route_prefix),
                                permission='{}.edit_row'.format(permission_prefix))
            if cls.mobile_rows_editable:
                config.add_route('mobile.{}.edit'.format(row_route_prefix), '/mobile{}/{{uuid}}/edit'.format(row_url_prefix))
                config.add_view(cls, attr='mobile_edit_row', route_name='mobile.{}.edit'.format(row_route_prefix),
                                permission='{}.edit_row'.format(permission_prefix))

        # delete row
        if cls.has_rows and cls.rows_deletable:
            config.add_route('{}.delete'.format(row_route_prefix), '{}/{{uuid}}/delete'.format(row_url_prefix))
            config.add_view(cls, attr='delete_row', route_name='{}.delete'.format(row_route_prefix),
                            permission='{}.delete_row'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.delete_row'.format(permission_prefix),
                                           "Delete individual {} rows".format(model_title))
