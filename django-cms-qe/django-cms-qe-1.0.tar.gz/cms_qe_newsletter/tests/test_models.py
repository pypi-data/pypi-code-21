from django.core.exceptions import ValidationError
from pytest_data import use_data
import pytest

from ..models import Subscriber, SubscribeTask, SERVICE_MAILCHIMP


def test_clean_newsletter_plugin(cms_qe_newsletter_plugin):
    cms_qe_newsletter_plugin.fullname_show = False
    cms_qe_newsletter_plugin.fullname_require = True
    with pytest.raises(ValidationError):
        cms_qe_newsletter_plugin.clean()


def test_validate_mailing_list(cms_qe_mailing_list):
    cms_qe_mailing_list.external_service = SERVICE_MAILCHIMP
    cms_qe_mailing_list.external_id = None
    with pytest.raises(ValidationError):
        cms_qe_mailing_list.clean()


def test_save_will_create_task(cms_qe_mailing_list):
    sub = Subscriber(
        mailing_list=cms_qe_mailing_list,
        email='test@example.com',
    )
    assert SubscribeTask.objects.all().count() == 0
    sub.save()
    assert SubscribeTask.objects.all().count() == 1


@use_data(cms_qe_subscriber_data={'external_id': 'test_id'})
def test_delete_will_create_task(cms_qe_subscriber):
    assert SubscribeTask.objects.all().count() == 0
    cms_qe_subscriber.delete()
    assert SubscribeTask.objects.all().count() == 1


@use_data(cms_qe_subscriber_data={'external_id': None})
def test_delete_will_remove_pending_task(cms_qe_subscriber):
    assert SubscribeTask.objects.all().count() == 1
    cms_qe_subscriber.delete()
    assert SubscribeTask.objects.all().count() == 0
