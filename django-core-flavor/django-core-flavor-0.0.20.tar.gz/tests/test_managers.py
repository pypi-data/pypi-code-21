from django.test import TestCase
from django.utils import timezone

from . import models as test_models


class ManagersTests(TestCase):

    def test_softdeletable_delete(self):
        manager = test_models.SoftDeletable.objects
        obj = manager.create()

        self.assertIsNone(obj.removed)

        manager.delete()
        obj.refresh_from_db()

        self.assertIsNotNone(obj.removed)
        self.assertTrue(manager.removed().exists())

        manager.delete(soft=False)
        self.assertFalse(manager.removed().exists())

    def test_softdeletable_restore(self):
        manager = test_models.SoftDeletable.objects
        obj = manager.create(removed=timezone.now())

        self.assertIsNotNone(obj.removed)

        manager.restore()
        obj.refresh_from_db()

        self.assertIsNone(obj.removed)
        self.assertTrue(manager.active().exists())
