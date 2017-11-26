
from django.test import TestCase

from djangocms_googlecalendar.models import GoogleCalendar


class GoogleCalendarTestCase(TestCase):

    def setUp(self):
        GoogleCalendar.objects.create(
            title='test',
            api_key='123',
            calendar_id='abc'
        )

    def test_google_calendar_instance(self):
        """Google Calendar has been created"""
        google_calendar = GoogleCalendar.objects.get(title='test')
        self.assertEqual(google_calendar.title, 'test')


