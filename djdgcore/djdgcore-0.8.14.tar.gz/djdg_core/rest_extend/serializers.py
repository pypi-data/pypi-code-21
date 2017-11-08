#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/18
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import serializers
from djdg_core.exceptions import StandardResponseError
from collections import defaultdict
from rest_framework.serializers import html
from rest_framework.serializers import ValidationError
from rest_framework.serializers import api_settings
from rest_framework.serializers import empty
from django.db.models.fields.related import ManyToManyField
from rest_framework.serializers import LIST_SERIALIZER_KWARGS


def exclude_field(instance, field_name, include_fields=None, exclude_fields=None):
    f = instance._meta.get_field(field_name)
    if isinstance(f, ManyToManyField):
        return True
    elif include_fields and f.name not in include_fields:
        return True
    elif exclude_fields and f.name in exclude_fields:
        return True
    return False


class SimpleListSerializer(serializers.ListSerializer):
    """
    默认的ListSerializer update操作
    """
    def update(self, instance, validated_data):
        ist_map = {ist.id: ist for ist in instance}
        upd_set = set()
        ret = []
        for item in validated_data:
            if 'id' in item:
                upd_set.add(item['id'])
                # 更新现有数据
                ist = ist_map.get(item['id'], None)
                if ist:
                    ret.append(self.child.update(ist, item))
            else:
                # 创建新数据
                ret.append(self.child.create(item))
        # 删除数据
        ist_del = set(ist_map.keys()) - upd_set
        for ist_id in ist_del:
            ist = ist_map[ist_id]
            ist.delete()
        return ret


class DifferenceBaseSerializer(serializers.BaseSerializer):
    """
    差别化序列化
    """
    model_primary_key = 'id'
    include_fields = None
    exclude_fields = None

    def __init__(self, instance=None, data=empty, **kwargs):
        super(DifferenceBaseSerializer, self).__init__(instance=instance, data=data, **kwargs)
        self.difference = {}

    def _do_diff(self, validated_data, instance, diff_type):
        diff = {}
        serl_inst = getattr(self, 'child', self)
        if instance is not None:
            instance_data = serl_inst.to_representation(instance)
        else:
            instance_data = {}
        init_data = serl_inst.to_representation(validated_data)
        if 'create' == diff_type:
            for k, v in init_data.iteritems():
                if exclude_field(instance, k, self.include_fields, self.exclude_fields):
                    continue
                diff[k] = (None, v)
        elif 'update' == diff_type:
            for k, v in init_data.iteritems():
                if exclude_field(instance, k, self.include_fields, self.exclude_fields):
                    continue
                a = instance_data.get(k)
                if str(a) != str(v):
                    diff[k] = (a, v)
        elif 'delete' == diff_type:
            for k, v in instance_data.iteritems():
                if exclude_field(instance, k, self.include_fields, self.exclude_fields):
                    continue
                diff[k] = (v, None)
        else:
            raise StandardResponseError(7, '{}是无效的差异类型！'.format(diff_type))
        if diff:
            diff['__diff_type'] = diff_type
            diff[self.model_primary_key] = instance_data.get(self.model_primary_key)
            self._make_diff(diff)
            return True
        return False

    def _make_diff(self, diff):
        self.difference = diff


class DifferenceSerializer(DifferenceBaseSerializer, serializers.Serializer):
    """
    差别化序列化
    """
    @classmethod
    def many_init(cls, *args, **kwargs):
        allow_empty = kwargs.pop('allow_empty', None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            'child': child_serializer,
            'child_cls': cls
        }
        if allow_empty is not None:
            list_kwargs['allow_empty'] = allow_empty
        list_kwargs.update({
                               key: value for key, value in kwargs.items()
                               if key in LIST_SERIALIZER_KWARGS
                               })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', serializers.ListSerializer)
        return list_serializer_class(*args, **list_kwargs)

    def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
            'Serializer `%s.%s` has old-style version 2 `.save_object()` '
            'that is no longer compatible with REST framework 3. '
            'Use the new-style `.create()` and `.update()` methods instead.' %
            (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )
        if self.instance is not None:
            if self._do_diff(validated_data, self.instance, 'update'):
                self.instance = self.update(self.instance, validated_data)
                assert self.instance is not None, (
                    '`update()` did not return an object instance.'
                )
        else:
            self.instance = self.create(validated_data)
            self._do_diff(validated_data, self.instance, 'create')
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        return self.instance


class DifferenceModelSerializer(DifferenceSerializer, serializers.ModelSerializer):
    """
    差别化序列化工具
    """


class DifferenceListSerializer(DifferenceBaseSerializer, serializers.ListSerializer):
    """
    差别化列表序列化工具
    """
    def __init__(self, *args, **kwargs):
        self.child_cls = kwargs.pop('child_cls', None)
        super(DifferenceListSerializer, self).__init__(*args, **kwargs)
        self.differences = defaultdict(list)
        self._separation = None
        self._validated_separation = defaultdict(list)

    def separation(self, data):
        if self._separation is None:
            instance_map = {getattr(ist, self.model_primary_key): ist for ist in self.instance} if self.instance is not None else {}
            _separation = defaultdict(list)
            keep_keys = set()
            for d in data:
                if self.model_primary_key not in d:
                    _separation['create'].append(d)
                elif d[self.model_primary_key] in instance_map:
                    _separation['update'].append([instance_map[d[self.model_primary_key]], d])
                    keep_keys.add(d[self.model_primary_key])
                else:
                    d.pop(self.model_primary_key, None)
                    _separation['create'].append(d)
            for k, i in instance_map.iteritems():
                if k not in keep_keys:
                    _separation['delete'].append(i)
            self._separation = _separation
        return self._separation

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        if not isinstance(data, list):
            message = self.error_messages['not_a_list'].format(
                input_type=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })

        if not self.allow_empty and len(data) == 0:
            message = self.error_messages['empty']
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })

        ret = []
        errors = []
        for k, vl in self.separation(data).iteritems():
            for v in vl:
                if 'create' == k:
                    init_kw = {'data': v}
                elif 'update' == k:
                    init_kw = {'data': v[1], 'instance': v[0]}
                else:
                    self._validated_separation[k].append(v)
                    continue
                try:
                    validated = self.child_cls(**init_kw).run_validation(init_kw['data'])
                    init_kw.pop('data', None)
                    sep_valid = dict(data=validated, **init_kw)
                except ValidationError as exc:
                    errors.append(exc.detail)
                else:
                    ret.append(validated)
                    self._validated_separation[k].append(sep_valid)
                    errors.append({})

        if any(errors):
            raise ValidationError(errors)

        return ret

    def save(self, **kwargs):
        """
        Save and return a list of object instances.
        """
        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )
        instance_list = []
        for k, vl in self._validated_separation.iteritems():
            for v in vl:
                if 'create' == k:
                    attrs = dict(list(v['data'].items()) + list(kwargs.items()))
                    instance = self.child.create(attrs)
                    self._do_diff(attrs, instance, 'create')
                    instance_list.append(instance)
                elif 'update' == k:
                    attrs = dict(list(v['data'].items()) + list(kwargs.items()))
                    instance = v['instance']
                    if self._do_diff(attrs, v['instance'], 'update'):
                        instance = self.update(v['instance'], attrs)
                    instance_list.append(instance)
                else:
                    self._do_diff(None, v, 'delete')
                    self.delete(v)
        self.instance = instance_list
        return self.instance

    def _make_diff(self, diff):
        self.differences[diff['__diff_type']].append(diff)

    def delete(self, instance):
        instance.delete()
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.iteritems():
            setattr(instance, k, v)
        instance.save()
        return instance
