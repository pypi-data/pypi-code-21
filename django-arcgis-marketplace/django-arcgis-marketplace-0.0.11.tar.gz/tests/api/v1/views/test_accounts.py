from rest_framework import status

from ...views import BaseViewTests


class AccountViewTests(BaseViewTests):

    def test_account_list_200_OK(self):
        self.user.is_staff = True
        self.user.save()

        response = self.client.get(self.reverse('account-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_list_403_FORBIDDEN(self):
        response = self.client.get(self.reverse('account-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_account_detail_200_OK(self):
        response = self.client.get(self.account.get_absolute_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.account.id.hex)
