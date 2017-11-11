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
Forms Core
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import AssociationProxy, ASSOCIATION_PROXY

from rattail.time import localtime
from rattail.util import prettify, pretty_boolean, pretty_hours

import colander
from colanderalchemy import SQLAlchemySchemaNode
import deform
from deform import widget as dfwidget
from pyramid.renderers import render
from webhelpers2.html import tags, HTML

from tailbone.util import raw_datetime


log = logging.getLogger(__name__)


class CustomSchemaNode(SQLAlchemySchemaNode):

    def get_schema_from_relationship(self, prop, overrides):
        """ Build and return a :class:`colander.SchemaNode` for a relationship.
        """

        # for some reason ColanderAlchemy wants to crawl our entire ORM by
        # default, by way of relationships.  this 'excludes' hack is used to
        # prevent that, by forcing skip of 2nd-level relationships

        excludes = []
        if isinstance(prop, orm.RelationshipProperty):
            for next_prop in prop.mapper.iterate_properties:
                if isinstance(next_prop, orm.RelationshipProperty):
                    excludes.append(next_prop.key)

        if excludes:
            overrides['excludes'] = excludes

        return super(CustomSchemaNode, self).get_schema_from_relationship(prop, overrides)

    def dictify(self, obj):
        """ Return a dictified version of `obj` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        dict_ = super(CustomSchemaNode, self).dictify(obj)
        for node in self:

            name = node.name
            if name not in dict_:

                try:
                    desc = getattr(self.inspector.all_orm_descriptors, name)
                    if desc.extension_type != ASSOCIATION_PROXY:
                        continue
                    value = getattr(obj, name)
                except AttributeError:
                    continue

                if value is None:
                    if isinstance(node.typ, colander.String):
                        # colander has an issue with `None` on a String type
                        #  where it translates it into "None".  Let's check
                        #  for that specific case and turn it into a
                        #  `colander.null`.
                        dict_[name] = colander.null
                    else:
                        # A specific case this helps is with Integer where
                        #  `None` is an invalid value.  We call serialize()
                        #  to test if we have a value that will work later
                        #  for serialization and then allow it if it doesn't
                        #  raise an exception.  Hopefully this also catches
                        #  issues with user defined types and future issues.
                        try:
                            node.serialize(value)
                        except:
                            dict_[name] = colander.null
                        else:
                            dict_[name] = value
                else:
                    dict_[name] = value

        return dict_

    def objectify(self, dict_, context=None):
        """ Return an object representing ``dict_`` using schema information.

        .. note::
           This method was copied from upstream and modified to add automatic
           handling of "association proxy" fields.
        """
        mapper = self.inspector
        context = mapper.class_() if context is None else context
        for attr in dict_:
            if mapper.has_property(attr):
                prop = mapper.get_property(attr)
                if hasattr(prop, 'mapper'):
                    cls = prop.mapper.class_
                    if prop.uselist:
                        # Sequence of objects
                        value = [self[attr].children[0].objectify(obj)
                                 for obj in dict_[attr]]
                    else:
                        # Single object
                        value = self[attr].objectify(dict_[attr])
                else:
                     value = dict_[attr]
                     if value is colander.null:
                         # `colander.null` is never an appropriate
                         #  value to be placed on an SQLAlchemy object
                         #  so we translate it into `None`.
                         value = None
                setattr(context, attr, value)

            else:
                # try to process association proxy field
                desc = mapper.all_orm_descriptors.get(attr)
                if desc and desc.extension_type == ASSOCIATION_PROXY:
                    value = dict_[attr]
                    if value is colander.null:
                        # `colander.null` is never an appropriate
                        #  value to be placed on an SQLAlchemy object
                        #  so we translate it into `None`.
                        value = None
                    setattr(context, attr, value)

                else:
                    # Ignore attributes if they are not mapped
                    log.debug(
                        'SQLAlchemySchemaNode.objectify: %s not found on '
                        '%s. This property has been ignored.',
                        attr, self
                    )
                    continue

        return context


class Form(object):
    """
    Base class for all forms.
    """

    def __init__(self, fields=None, schema=None, request=None, readonly=False, readonly_fields=[],
                 model_instance=None, model_class=None, nodes={}, enums={}, labels={}, renderers={},
                 widgets={}, defaults={}, validators={}, required={}, action_url=None, cancel_url=None):

        self.fields = list(fields) if fields is not None else None
        self.schema = schema
        self.request = request
        self.readonly = readonly
        self.readonly_fields = set(readonly_fields or [])
        self.model_instance = model_instance
        self.model_class = model_class
        if self.model_instance and not self.model_class:
            self.model_class = type(self.model_instance)
        if self.model_class and self.fields is None:
            self.fields = self.make_fields()
        self.nodes = nodes or {}
        self.enums = enums or {}
        self.labels = labels or {}
        self.renderers = renderers or {}
        self.widgets = widgets or {}
        self.defaults = defaults or {}
        self.validators = validators or {}
        self.required = required or {}
        self.action_url = action_url
        self.cancel_url = cancel_url

    def make_fields(self):
        """
        Return a default list of fields, based on :attr:`model_class`.
        """
        if not self.model_class:
            raise ValueError("Must define model_class to use make_fields()")

        mapper = orm.class_mapper(self.model_class)

        # first add primary column fields
        fields = [prop.key for prop in mapper.iterate_properties
                  if not prop.key.startswith('_')
                  and prop.key != 'versions']

        # then add association proxy fields
        for key, desc in sa.inspect(self.model_class).all_orm_descriptors.items():
            if desc.extension_type == ASSOCIATION_PROXY:
                fields.append(key)

        return fields

    def remove_field(self, key):
        if key in self.fields:
            self.fields.remove(key)

    def make_schema(self):
        if not self.model_class:
            # TODO
            raise NotImplementedError

        if not self.schema:

            mapper = orm.class_mapper(self.model_class)

            # first filter our "full" field list so we ignore certain ones.  in
            # particular we don't want readonly fields in the schema, or any
            # which appear to be "private"
            includes = [f for f in self.fields
                        if f not in self.readonly_fields
                        and not f.startswith('_')
                        and f != 'versions']

            # make schema - only include *property* fields at this point
            schema = CustomSchemaNode(self.model_class,
                                      includes=[p.key for p in mapper.iterate_properties
                                                if p.key in includes])

            # for now, must manually add any "extra" fields?  this includes all
            # association proxy fields, not sure how other fields will behave
            for field in includes:
                if field not in schema:
                    node = self.nodes.get(field)
                    if not node:
                        node = colander.SchemaNode(colander.String(), name=field, missing='')
                    schema.add(node)

            # apply any label overrides
            for key, label in self.labels.items():
                if key in schema:
                    schema[key].title = label

            # apply any widget overrides
            for key, widget in self.widgets.items():
                if key in schema:
                    schema[key].widget = widget

            # apply any default values
            for key, default in self.defaults.items():
                if key in schema:
                    schema[key].default = default

            # apply any validators
            for key, validator in self.validators.items():
                if key in schema:
                    schema[key].validator = validator

            # apply required flags
            for key, required in self.required.items():
                if key in schema:
                    if required:
                        schema[key].missing = colander.required
                    else:
                        schema[key].missing = None # TODO?

            self.schema = schema

        return self.schema

    def set_label(self, key, label):
        self.labels[key] = label

    def get_label(self, key):
        return self.labels.get(key, prettify(key))

    def set_readonly(self, key, readonly=True):
        if readonly:
            self.readonly_fields.add(key)
        else:
            if key in self.readonly_fields:
                self.readonly_fields.remove(key)

    def set_node(self, key, node):
        self.nodes[key] = node

    def set_type(self, key, type_):
        if type_ == 'datetime':
            self.set_renderer(key, self.render_datetime)
        elif type_ == 'datetime_local':
            self.set_renderer(key, self.render_datetime_local)
        elif type_ == 'duration':
            self.set_renderer(key, self.render_duration)
        elif type_ == 'boolean':
            self.set_renderer(key, self.render_boolean)
            self.set_widget(key, dfwidget.CheckboxWidget(true_val='True', false_val='False'))
        elif type_ == 'currency':
            self.set_renderer(key, self.render_currency)
        elif type_ == 'enum':
            self.set_renderer(key, self.render_enum)
        elif type_ == 'codeblock':
            self.set_renderer(key, self.render_codeblock)
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        elif type_ == 'text':
            self.set_widget(key, dfwidget.TextAreaWidget(cols=80, rows=8))
        else:
            raise ValueError("unknown type for '{}' field: {}".format(key, type_))

    def set_enum(self, key, enum):
        if enum:
            self.enums[key] = enum
            self.set_type(key, 'enum')
        else:
            self.enums.pop(key, None)

    def set_renderer(self, key, renderer):
        self.renderers[key] = renderer

    def set_widget(self, key, widget):
        self.widgets[key] = widget

    def set_validator(self, key, validator):
        self.validators[key] = validator

    def set_required(self, key, required=True):
        """
        Set whether or not value is required for a given field.
        """
        self.required[key] = required

    def set_default(self, key, value):
        """
        Set the default value for a given field.
        """
        self.defaults[key] = value

    def render(self, template=None, **kwargs):
        if not template:
            if self.readonly:
                template = '/forms2/form_readonly.mako'
            else:
                template = '/forms2/form.mako'
        context = kwargs
        context['form'] = self
        return render(template, context)

    def make_deform_form(self):
        if not hasattr(self, 'deform_form'):

            schema = self.make_schema()

            # get initial form values from model instance
            kwargs = {}
            if self.model_instance:
                kwargs['appstruct'] = schema.dictify(self.model_instance)

            # create form
            form = deform.Form(schema, **kwargs)

            # set readonly widget where applicable
            for field in self.readonly_fields:
                if field in form:
                    form[field].widget = ReadonlyWidget()

            self.deform_form = form

        return self.deform_form

    def render_deform(self, dform=None, template='/forms2/deform.mako', **kwargs):
        if dform is None:
            dform = self.make_deform_form()

        # TODO: would perhaps be nice to leverage deform's default rendering
        # someday..? i.e. using Chameleon *.pt templates
        # return form.render()

        context = kwargs
        context['form'] = self
        context['dform'] = dform
        context['request'] = self.request
        context['readonly_fields'] = self.readonly_fields
        context['render_field_readonly'] = self.render_field_readonly
        return render('/forms2/deform.mako', context)

    def render_field_readonly(self, field_name, **kwargs):
        label = HTML.tag('label', self.get_label(field_name), for_=field_name)
        field = self.render_field_value(field_name) or ''
        field_div = HTML.tag('div', class_='field', c=field)
        return HTML.tag('div', class_='field-wrapper {}'.format(field), c=label + field_div)

    def render_field_value(self, field_name):
        record = self.model_instance
        if self.renderers and field_name in self.renderers:
            return self.renderers[field_name](record, field_name)
        return self.render_generic(record, field_name)

    def render_generic(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return six.text_type(value)

    def render_datetime(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_datetime_local(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        value = localtime(self.request.rattail_config, value)
        return raw_datetime(self.request.rattail_config, value)

    def render_duration(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return pretty_hours(datetime.timedelta(seconds=value))

    def render_boolean(self, record, field_name):
        value = self.obtain_value(record, field_name)
        return pretty_boolean(value)

    def render_currency(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        if value < 0:
            return "(${:0,.2f})".format(0 - value)
        return "${:0,.2f}".format(value)

    def render_enum(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        enum = self.enums.get(field_name)
        if enum and value in enum:
            return six.text_type(enum[value])
        return six.text_type(value)

    def render_codeblock(self, record, field_name):
        value = self.obtain_value(record, field_name)
        if value is None:
            return ""
        return HTML.tag('pre', value)

    def obtain_value(self, record, field_name):
        try:
            return record[field_name]
        except TypeError:
            return getattr(record, field_name)

    def validate(self, *args, **kwargs):
        form = self.make_deform_form()
        return form.validate(*args, **kwargs)


class ReadonlyWidget(dfwidget.HiddenWidget):

    readonly = True

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        return HTML.tag('span', cstruct) + tags.hidden(field.name, value=cstruct, id=field.oid)
