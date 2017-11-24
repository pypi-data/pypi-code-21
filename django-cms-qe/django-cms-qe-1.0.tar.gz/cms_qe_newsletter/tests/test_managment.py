from unittest import mock


def test_not_set_mailchimp():
    with mock.patch('cms_qe_newsletter.external_services.sync.sync_tasks', return_value=[
        (True, 'ok'),
        (None, 'warning'),
        (False, 'error'),
    ]):
        # Import here so mock works correctly.
        from ..management.commands.cms_qe_newsletter_sync import Command

        with mock.patch('cms_qe_newsletter.management.commands.cms_qe_newsletter_sync.logger') as log_mock:
            command = Command()
            command.handle()
            assert log_mock.info.call_args_list == [
                mock.call('Newsletter sync started...'),
                mock.call('ok'),
                mock.call('Newsletter sync finished...'),
            ]
            assert log_mock.warning.call_args_list == [mock.call('warning')]
            assert log_mock.error.call_args_list == [mock.call('error')]
