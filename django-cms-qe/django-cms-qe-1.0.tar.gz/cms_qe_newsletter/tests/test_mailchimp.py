from constance.test import override_config
from django.conf import settings
import pytest
from pytest_data import use_data

from ..external_services.mailchimp import sync_mailing_lists, sync_subscribe, sync_unsubscribe
from ..models import MailingList


@pytest.mark.slow
@override_config(
    MAILCHIMP_USERNAME=settings.TEST_MAILCHIMP_USERNAME,
    MAILCHIMP_API_KEY=settings.TEST_MAILCHIMP_API_KEY,
)
def test_sync_mailing_lists_integrate():
    # Check connection with MailChimp.
    _test_sync_mailing_lists()


def test_sync_mailing_lists(mock_mailchimp):
    _test_sync_mailing_lists()


def _test_sync_mailing_lists():
    assert MailingList.objects.count() == 0
    sync_mailing_lists()
    assert MailingList.objects.count() == 2


@use_data(cms_qe_mailchimp_subscribe_data={'id': 'subid'})
def test_sync_subscribe(mock_mailchimp):
    assert 'subid' == sync_subscribe('listid', 'test@example.com', 'first', 'last')


def test_sync_unsubscribe(mock_mailchimp):
    # No exception.
    sync_unsubscribe('listid', 'test@example.com')
