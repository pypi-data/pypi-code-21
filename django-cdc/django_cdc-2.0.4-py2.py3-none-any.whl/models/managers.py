from __future__ import unicode_literals

import logging
import pickle

from django.db import models

from django_cdc import settings as local_settings
from django_cdc.models.tracker import FieldInstanceTracker
from services import Service

logger = logging.getLogger(__name__)

try:
    from django.utils.timezone import now as datetime_now
    assert datetime_now
except ImportError:
    import datetime
    datetime_now = datetime.datetime.now

models.signals.post_update = models.signals.Signal()
models.signals.post_bulk_create = models.signals.Signal()


class OverrideSave():
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        self.original_save = instance.save

    def __getstate__(self):
        return (self.instance)

    def __setstate__(self, instance):
        self.instance = instance
        self.original_save = instance.save

    def __call__(self, **kwargs):
        ret = self.original_save(**kwargs)
        update_fields = kwargs.get('update_fields')
        if not update_fields and update_fields is not None:  # () or []
            fields = update_fields
        elif update_fields is None:
            fields = None
        else:
            fields = (
                field for field in update_fields if
                field in self.fields
            )
        getattr(self.instance, "tracker").set_saved_fields(
            fields=fields
        )
        return ret

class DjangoCDCQuerySet(models.query.QuerySet):

    def update(self, **kwargs):
        super(DjangoCDCQuerySet, self).update(**kwargs)
        models.signals.post_update.send(sender=self.model,
                                        queryset=self,
                                        updates=kwargs)

    def bulk_create(self, objs, batch_size=None):
        super(DjangoCDCQuerySet, self).bulk_create(objs)
        models.signals.post_bulk_create.send(sender=self.model,
                                             objs=objs)


def get_base_manager(base):
    """add dynamic inheritance for getting functionality
     of different manager of model class"""
    class DjangoCDCManager(base):

        def __init__(self, model, attname,
                     services=None, exclude=None,
                     foreign_keys=None, instance=None,
                     partition_key=None):
            super(DjangoCDCManager, self).__init__()
            self.model = model
            self.instance = instance
            self.attname = attname
            self._exclude = exclude or []
            self.foreign_keys = foreign_keys or {}
            self.services = services or []
            self.partition_key = partition_key
            # set a hidden attribute on the  instance to control wether
            # we should track changes
            if instance is not None and not hasattr(
                    instance, '__is_%s_enabled' % attname):
                setattr(instance, '__is_%s_enabled' % attname, True)

        def enable_tracking(self):
            if self.instance is None:
                raise ValueError("Tracking can only be enabled or disabled "
                                 "per model instance, not on a model class")
            setattr(self.instance, '__is_%s_enabled' % self.attname, True)

        def disable_tracking(self):
            if self.instance is None:
                raise ValueError("Tracking can only be enabled or disabled "
                                 "per model instance, not on a model class")
            setattr(self.instance, '__is_%s_enabled' % self.attname, False)

        def is_tracking_enabled(self):
            if local_settings.DISABLE_DJANGO_CDC:
                return False
            if self.instance is None:
                raise ValueError("Tracking can only be enabled or disabled "
                                 "per model instance, not on a model class")
            return getattr(self.instance, '__is_%s_enabled' % self.attname)

        def get_queryset(self):
            super(DjangoCDCManager, self).get_query_set()
            return DjangoCDCQuerySet(self.model, using=self.db)

        def create_data_entry(self, instance, action_type,
                              updates=None, *args, **kwargs):
            my_list = []
            name = ""
            if isinstance(instance, list):
                for var in instance:
                    name = var._meta.db_table
                    if getattr(var, self.attname).is_tracking_enabled():
                        data_entry = self.__get_data_entry(var,
                                                           action_type,
                                                           self._exclude,
                                                           self.foreign_keys,
                                                           updates)
                        if data_entry:
                            my_list.append(data_entry)
                    else:
                        logger.info("Tracking is disabled")
            else:
                if getattr(instance, self.attname).is_tracking_enabled():
                    name = instance._meta.db_table
                    data_entry = self.__get_data_entry(instance,
                                                       action_type,
                                                       self._exclude,
                                                       self.foreign_keys,
                                                       updates)
                    if data_entry:
                        my_list.append(data_entry)
                else:
                    logger.info("Tracking is disabled")
            if my_list and self.services:
                if self.partition_key:
                    my_list.append(self.partition_key.column)
                for service in self.services:
                    obj = Service.factory(service)
                    obj.put_data_entry(name, *my_list)
            elif my_list:
                logger.info("Payload Data" + str(my_list))

        def __get_data_entry(self, instance, action_type,
                             exclude, foreign_keys, updates):
            is_field_changed = True
            changed_fields = []
            attrs = {}
            if not updates and action_type == 'U':
                changed_fields = self.__get_changed_fields(instance, exclude)
                if not changed_fields:
                    is_field_changed = False
                else:
                    attrs["changed_fields"] = changed_fields
            elif updates:
                attrs["changed_fields"] = list(updates)

            if is_field_changed:
                prefix_for_foreign_key = "__"
                for field in instance._meta.fields:
                    if field.name in foreign_keys.keys():
                        data = foreign_keys[field.name]
                        foreign_key_instance = getattr(instance, field.name)
                        attr_key = "{0}{1}".format(field.name,
                                                   prefix_for_foreign_key)
                        if isinstance(data, list):
                            for val in data:
                                attrs[attr_key + val] = getattr(
                                    foreign_key_instance, val, None)
                        else:
                            attrs[attr_key + data] = getattr(
                                foreign_key_instance, data, None)
                    if field.attname not in exclude:
                        name = field.name \
                                if field.get_internal_type() == 'ForeignKey' \
                                else field.attname
                        attrs[name] = getattr(instance,
                                              field.attname)
                attrs["cdc_action"] = action_type

            else:
                logger.info("No field updated...exit!!")
            return attrs

        def __get_changed_fields(self, instance, exclude, *args, **kwargs):
            fields = []
            if hasattr(instance, 'tracker'):
                for field in instance._meta.fields:
                    if field.attname not in exclude and \
                            instance.tracker.has_changed(field.attname):
                        name = field.name \
                            if field.get_internal_type() == 'ForeignKey' \
                            else field.attname
                        fields.append(name)
            return fields
    return DjangoCDCManager


class DjangoCDCDescriptor(object):
    def __init__(self, model, manager_class,
                 attname, exclude=None, foreign_keys=None, services=None,
                 partition_key=None):
        self.model = model
        self.manager_class = manager_class
        self.attname = attname
        self._exclude = exclude or []
        self.foreign_keys = foreign_keys or {}
        self.services = services or []
        self.partition_key = partition_key

    def __get__(self, instance, owner):
        if instance is None:
            return self.manager_class(self.model, self.attname)
        return self.manager_class(self.model, self.attname, self.services,
                                  self._exclude, self.foreign_keys, instance,
                                  self.partition_key)


class DjangoCDC(object):
    tracker_class = FieldInstanceTracker

    def __init__(self, exclude=None,
                 services=None, foreign_keys=None,
                 partition_key=None):
        self._exclude = exclude or []
        self.foreign_keys = foreign_keys or {}
        self.services = services or []
        self.manager_class = None
        self.partition_key = partition_key

    def contribute_to_class(self, cls, name):
        self.manager_name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def initialize_tracker(self, sender, instance, **kwargs):
        if not isinstance(instance, self.model_class):
            return  # Only init instances of given model (including children)
        tracker = self.tracker_class(instance,
                                     self.fields,
                                     self.field_map)
        setattr(instance, "tracker", tracker)
        tracker.set_saved_fields()
        self.patch_save(instance)

    def patch_save(self, instance):
        instance.save = OverrideSave(instance)

    def post_bulk_create(self, objs, *args, **kwargs):
        if objs:
            manager = getattr(objs[0], self.manager_name)
            manager.create_data_entry(list(objs), 'I')

    def post_update(self, queryset, updates, *args, **kwargs):
        # FIELD_TRACKER NOT WORKING
        if queryset:
            manager = getattr(queryset[0], self.manager_name)
            manager.create_data_entry(list(queryset), 'U', updates)

    def post_save(self, instance, created, **kwargs):
        # ignore if it is disabled
        # if getattr(instance, self.manager_name).is_tracking_enabled():
        manager = getattr(instance, self.manager_name)
        manager.create_data_entry(instance, created and 'I' or 'U')

    def post_delete(self, instance, **kwargs):
        # ignore if it is disabled
        # if getattr(instance, self.manager_name).is_tracking_enabled():
        manager = getattr(instance, self.manager_name)
        manager.create_data_entry(instance, 'D')

    def get_field_map(self, cls):
        """Returns dict mapping fields names to model attribute names"""
        field_map = dict((field, field) for field in self.fields)
        all_fields = dict((f.name, f.attname) for f in cls._meta.fields)
        field_map.update(**dict((k, v) for (k, v) in all_fields.items()
                                if k in field_map))
        return field_map

    def finalize(self, sender, **kwargs):
        # log_entry_model = self.create_data_entry_model(sender)
        # prev_instance=models.signals.pre_save.connect(self.pre_save,sender=sender,weak=False)

        self.manager_class = get_base_manager(sender.objects.__class__)
        self.manager_class(sender, self.manager_name, self.services,
                           self._exclude, self.foreign_keys
                           ).contribute_to_class(sender, 'objects')

        # For Field tracking
        self.fields = (field.attname for field in sender._meta.fields)
        self.fields = set(self.fields)
        self.field_map = self.get_field_map(sender)
        models.signals.post_init.connect(self.initialize_tracker)
        self.model_class = sender
        setattr(sender, "tracker", self)
        models.signals.post_bulk_create.connect(
            self.post_bulk_create, sender=sender, weak=False)
        models.signals.post_update.connect(
            self.post_update, sender=sender, weak=False)
        models.signals.post_save.connect(
            self.post_save, sender=sender, weak=False)
        models.signals.post_delete.connect(
            self.post_delete, sender=sender, weak=False)
        descriptor = DjangoCDCDescriptor(
            sender, self.manager_class, self.manager_name,
            self._exclude, self.foreign_keys, self.services, self.partition_key)
        setattr(sender, self.manager_name, descriptor)
