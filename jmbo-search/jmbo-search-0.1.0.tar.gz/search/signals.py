from __future__ import print_function
import logging

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from haystack import signals
from haystack.exceptions import NotHandled
from haystack import connection_router, connections

from jmbo.models import ModelBase

from search import tasks
from search.models import IndexedItem


logger = logging.getLogger(__name__)

ADD = "add"
DELETE = "delete"
ADD_CALLBACK = "search.signals.add_to_index"
DELETE_CALLBACK = "search.signals.remove_from_index"


def add_to_index(callback_params):
    """Driver method used by async task to add instance to index.
    """
    handle_index_update(action=ADD, callback_params=callback_params)


def remove_from_index(callback_params):
    """Driver method used by async task to remove instance from index.
    """
    handle_index_update(action=DELETE, callback_params=callback_params)


def handle_index_update(action=None, callback_params={}):
    """This one does the actual work of re-indexing the instance.
    """
    if action is None or action == "":
        logger.warn("Indexing action cannot be None or empty!")
        return

    ct_id = callback_params["content_type_id"]
    model = ContentType.objects.get(id=ct_id).model_class()
    instance = model.objects.get(pk=callback_params["pk"])

    using_backends = connection_router.for_write(instance=instance)
    for using in using_backends:
        try:
            unified_index = connections[using].get_unified_index()
            index = unified_index.get_index(model)
            if action == ADD:
                if instance.state == "unpublished":
                    index.remove_object(instance, using=using)
                else:
                    index.update_object(instance, using=using)
            elif action == DELETE:
                index.remove_object(instance, using=using)

            # clean up the index item table now.
            try:
                item = IndexedItem.objects.get(
                    content_type_pk=ct_id, instance_pk=instance.pk
                )
                item.delete()
            except ObjectDoesNotExist:
                logger.warn("IndexedItem not found... continuing.")
        except NotHandled:
            logger.warn("No indexing backend found for %s" % instance)


def build_params(sender, instance):
    """Utility method to set up the callback parameters.
    """
    ct = ContentType.objects.get_for_model(instance.__class__)
    callback_params = {
        "content_type_id": ct.id,
        "pk": instance.pk,
    }
    return callback_params


def not_in_queue(ct, instance):
    try:
        IndexedItem.objects.get(content_type_pk=ct.id, instance_pk=instance.pk)
    except ObjectDoesNotExist:
        return True
    return False


class ModelBaseSignalProcessor(signals.BaseSignalProcessor):
    def setup(self):
        """Bind the signals to our jmbo ModelBase only.
        """
        models.signals.post_save.connect(self.handle_save)
        models.signals.pre_delete.connect(self.handle_delete)

    def teardown(self):
        """Remove the signals from our jmbo ModelBase.
        """
        models.signals.post_save.disconnect(self.handle_save)
        models.signals.post_delete.disconnect(self.handle_delete)

    def handle_save(self, sender, instance, **kwargs):
        """Defer the actual indexing to a celery async task.
        """
        # We only index jmbo ModelBase and its children
        if not isinstance(instance, ModelBase):
            return

        ct = ContentType.objects.get_for_model(instance.__class__)
        if not_in_queue(ct, instance):
            item_kwargs = {
                "content_type_pk": ct.id,
                "instance_pk": instance.pk
            }
            item = IndexedItem.objects.create(**item_kwargs)
            item.save()

            params = build_params(sender, instance)
            tasks.update_index(
                callback=ADD_CALLBACK,
                callback_params=params,
                **kwargs
            )

    def handle_delete(self, sender, instance, **kwargs):
        """Defer the actual indexing to a celery async task.
        """
        # We only index jmbo ModelBase and its children
        if not isinstance(instance, ModelBase):
            return

        ct = ContentType.objects.get_for_model(instance.__class__)
        if not_in_queue(ct, instance):
            item_kwargs = {
                "content_type_pk": ct.id,
                "instance_pk": instance.pk
            }
            item = IndexedItem.objects.create(**item_kwargs)
            item.save()

            params = build_params(sender, instance)
            tasks.update_index(
                callback=DELETE_CALLBACK,
                callback_params=params,
                **kwargs
            )
