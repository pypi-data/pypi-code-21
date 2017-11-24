from pytest_data import use_data

from ..models import SubscribeTask
from ..external_services.sync import sync_tasks, sync_task


@use_data(
    cms_qe_mailing_list_data={'external_service': 99},
    cms_qe_subscribe_task_data={
        'attempts': 0,
        'last_error': 0,
    },
)
def test_save_failure(cms_qe_subscribe_task):
    assert SubscribeTask.objects.all().count() == 1
    result, message = list(sync_tasks())[0]
    assert 'Unsupported service 99' in message
    assert result is False
    cms_qe_subscribe_task.refresh_from_db()
    assert cms_qe_subscribe_task.attempts == 1
    assert cms_qe_subscribe_task.last_error == 'Unsupported service 99'


@use_data(cms_qe_subscribe_task_data={'attempts': 10})
def test_warning_do_not_increment_failure(cms_qe_subscribe_task):
    assert SubscribeTask.objects.all().count() == 1
    result, message = list(sync_tasks())[0]
    assert 'Skipped' in message
    assert result is None
    cms_qe_subscribe_task.refresh_from_db()
    assert cms_qe_subscribe_task.attempts == 10
    assert cms_qe_subscribe_task.last_error == ''


@use_data(cms_qe_subscribe_task_data={'attempts': 10})
def test_task_skip(cms_qe_subscribe_task):
    result, message = sync_task(cms_qe_subscribe_task)
    assert 'Skipped' in message
    assert result is None


@use_data(
    cms_qe_mailing_list_data={'external_service': 99},
    cms_qe_subscribe_task_data={
        'attempts': 0,
        'last_error': 0,
    },
)
def test_task_unsupported_service(cms_qe_subscribe_task):
    result, message = sync_task(cms_qe_subscribe_task)
    assert 'Unsupported service 99' in message
    assert result is False


@use_data(
    cms_qe_subscribe_task_data={'email': '-no-subscriber-@example.com'},
)
def test_task_with_removed_subscriber(cms_qe_subscribe_task):
    result, message = sync_task(cms_qe_subscribe_task)
    assert 'Subscriber does not exist anymore, deleting task' in message
    assert result is None


@use_data(
    cms_qe_subscriber_data={'email': 'test@example.com'},
    cms_qe_subscribe_task_data={'email': 'test@example.com'},
)
def test_task_synced(cms_qe_subscribe_task, cms_qe_subscriber, mock_mailchimp):
    result, message = sync_task(cms_qe_subscribe_task)
    assert 'OK' in message
    assert result is True
