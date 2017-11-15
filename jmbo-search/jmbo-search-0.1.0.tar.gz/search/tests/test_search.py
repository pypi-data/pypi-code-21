import uuid

from mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase, LiveServerTestCase

from search import signals, tasks
from search.models import IndexedItem
from jmbo.models import ModelBase
from photologue.models import Photo


class TestSignalHandlers(TestCase):
    def test_add_to_index(self):
        pass

    def test_remove_from_index(self):
        pass

    def test_handle_index_update(self):
        pass


class TestSignalUtils(TestCase):
    def test_build_params(self):
        pass

    def test_not_in_queue(self):
        pass


class TestModelBaseSignalProcessor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.instance = ModelBase.objects.create()
        cls.processor = signals.ModelBaseSignalProcessor(None, None)
        cls.content_type = ContentType.objects.get_for_model(
            cls.instance.__class__
        )
        cls.callback_params = {
            "content_type_id": cls.content_type.id,
            "pk": cls.instance.pk
        }
        cls.empty_kwargs = {}

    def test_setup(self):
        self.assertTrue(
            models.signals.post_save.has_listeners(self.processor)
        )
        self.assertTrue(
            models.signals.pre_delete.has_listeners(self.processor)
        )

    @patch("search.tasks.update_index")
    def test_handle_save_update_index(self, task):
        self.processor.handle_save(None, self.instance, **self.empty_kwargs)

        indexed_item = IndexedItem.objects.get(
                instance_pk=self.instance.pk,
                content_type_pk=self.content_type.pk
                )
        self.assertIsNotNone(indexed_item)

        task.assert_called_once()
        task.assert_called_with(
            callback = signals.ADD_CALLBACK,
            callback_params = self.callback_params,
            **self.empty_kwargs
        )

    @patch("search.tasks.update_index")
    def test_handle_delete_update_index(self, task):
        self.processor.handle_delete(None, self.instance, **self.empty_kwargs)

        indexed_item = IndexedItem.objects.get(
                instance_pk=self.instance.pk,
                content_type_pk=self.content_type.pk
                )
        self.assertIsNotNone(indexed_item)

        task.assert_called_once()
        task.assert_called_with(
            callback = signals.DELETE_CALLBACK,
            callback_params = self.callback_params,
            **self.empty_kwargs
        )

    @patch("search.tasks.update_index")
    @patch("search.signals.build_params")
    def test_handle_save_build_params(self, params_builder, update_index):
        tasks.update_index = update_index
        self.processor.handle_save(None, self.instance, **self.empty_kwargs)
        params_builder.assert_called_with(None, self.instance)

    @patch("search.tasks.update_index")
    @patch("search.signals.build_params")
    def test_handle_delete_build_params(self, params_builder, update_index):
        tasks.update_index = update_index
        self.processor.handle_delete(None, self.instance, **self.empty_kwargs)
        params_builder.assert_called_with(None, self.instance)

    @patch("search.tasks.update_index")
    def test_handle_save_indexable_content_type(self, update_index):
        # create an indexable object
        self.processor.handle_save(None, self.instance, **self.empty_kwargs)

        update_index.assert_called_once()

        self.assertEquals(IndexedItem.objects.all().count(), 1)
        
        indexed_item = IndexedItem.objects.get(
            instance_pk = self.instance.pk,
            content_type_pk = self.content_type.pk
        )
        self.assertIsNotNone(indexed_item)

    @patch("search.tasks.update_index")
    def test_handle_save_nonindexable_content_type(self, update_index):
        # create non-indexable object
        instance = Photo.objects.create()
        self.processor.handle_save(None, instance, **self.empty_kwargs)

        update_index.assert_not_called()

        self.assertEquals(IndexedItem.objects.all().count(), 0)

    @patch("search.tasks.update_index")
    def test_handle_delete_indexable_content_type(self, update_index):
        # create an indexable object
        self.processor.handle_delete(None, self.instance, **self.empty_kwargs)

        update_index.assert_called_once()

        self.assertEquals(IndexedItem.objects.all().count(), 1)

        indexed_item = IndexedItem.objects.get(
            instance_pk = self.instance.pk,
            content_type_pk = self.content_type.pk
        )
        self.assertIsNotNone(indexed_item)

    @patch("search.tasks.update_index")
    def test_handle_delete_nonindexable_content_type(self, update_index):
        # create non-indexable object
        instance = Photo.objects.create()
        self.processor.handle_delete(None, instance, **self.empty_kwargs)

        update_index.assert_not_called()

        self.assertEquals(IndexedItem.objects.all().count(), 0)

