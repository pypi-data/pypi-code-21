
from django.apps import apps
from django.core.management import call_command
from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def setUp(self):
        if apps.is_installed('modeltranslation'):
            call_command('sync_translation_fields', interactive=False)
