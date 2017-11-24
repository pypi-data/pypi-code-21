from ..models import MailingList


def test_get_lists_from_mailchimp(mock_mailchimp, admin_client):
    assert MailingList.objects.count() == 0
    admin_client.get('/cms-qe/newsletter/sync-lists')
    assert MailingList.objects.count() == 2


def test_get_lists_from_mailchimp_not_staff(mock_mailchimp, client):
    assert MailingList.objects.count() == 0
    client.get('/cms-qe/newsletter/sync-lists')
    assert MailingList.objects.count() == 0
