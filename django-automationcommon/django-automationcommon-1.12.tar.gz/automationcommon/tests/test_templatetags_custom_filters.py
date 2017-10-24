from django.contrib.auth.models import User

import automationcommon.templatetags.custom_filters as custom_filters
from automationcommon.tests.utils import UnitTestCase


class CustomFilterTests(UnitTestCase):

    def test_username_list(self):
        self.assertEqual(custom_filters.username_list(User.objects.all()), "")
        User.objects.create(username="bl123")
        self.assertEqual(custom_filters.username_list(User.objects.all()), "bl123")
        User.objects.create(username="it123")
        self.assertEqual(custom_filters.username_list(User.objects.all()), "bl123,it123")

    def test_display_user(self):
        user = User.objects.create(username="bl123")
        self.assertEqual(custom_filters.display_user(user), "Bill Loney (bl123)")

    def test_unique_entity_id(self):
        user = User.objects.create(username="bl123")
        self.assertEqual(custom_filters.unique_entity_id(user), "User-%s" % user.id)
