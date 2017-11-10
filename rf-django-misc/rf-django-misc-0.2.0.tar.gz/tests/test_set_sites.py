from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import TestCase


class SetSiteTest(TestCase):

    def test_set_site(self):
        call_command("set_site", "1", "my.test.domain")
        site = Site.objects.get(pk=1)
        self.assertEqual(site.domain, "my.test.domain")
        self.assertEqual(site.name, "my.test.domain")
