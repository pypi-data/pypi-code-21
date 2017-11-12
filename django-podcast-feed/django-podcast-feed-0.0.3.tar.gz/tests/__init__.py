from django.test import TestCase

from podcast_feed import PodcastFeed


class InvalidPodcastFeed(PodcastFeed):
    pass


class MyPodcastFeed(PodcastFeed):
    pass


class TestPodcastFeed(TestCase):
    fixtures = ('episodes.json',)

    def setUp(self):
        feed = PodcastFeed()

    def test_channel_namespace(self):
        pass

    def test_channel_elements(self):
        pass

    def test_item_elements(self):
        pass

    def test_channel_description(self):
        """<itunes:summary should match <description"""
        pass
