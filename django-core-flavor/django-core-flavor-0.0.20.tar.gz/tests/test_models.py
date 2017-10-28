import uuid

from django.test import TestCase
from core_flavor import models

from . import models as test_models


class ModelsTests(TestCase):

    def test_upload_to(self):
        upload_to = models.UUIDUploadTo('/%Y/path')
        self.assertRegex(
            upload_to(None, 'test.x'), r'/\d{4}/path/[0-9a-f]{32}.x'
        )

    def test_soft_deletable(self):
        obj = test_models.SoftDeletable.objects.create()
        self.assertIsNone(obj.removed)

        obj.delete()
        self.assertIsNotNone(obj.removed)

        obj.delete(soft=False)
        self.assertIsNone(obj.pk)

    def test_timestamped_uuid(self):
        obj = test_models.TimeStampedUUID.objects.create()

        self.assertIsInstance(obj.id, uuid.UUID)
        self.assertGreater(obj.modified, obj.created)
