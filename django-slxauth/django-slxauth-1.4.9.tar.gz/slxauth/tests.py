import requests

from django.test import TestCase

# Create your tests here.
from slxauth.utils import get_unsaved_user_from_token, get_unsaved_user_from_token_and_portal_config


class ParseTokenTestCase(TestCase):
    def test_token_can_be_decoded(self):
        """Sample Authentication access_token can be correctly decoded"""

        token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJsYXN0TmFtZSI6IkRvZSB0ZXN0IiwibGFuZ3VhZ2UiOiJlbiIsImlzQ3VzdG9tZXJBZG1pbiI6dHJ1ZSwiY3VzdG9tZXJOdW1iZXIiOiI1MDAwMTY3IiwidGl0bGUiOiJNUiIsImN1c3RvbWVyTmFtZSI6IkxpbmFyYSIsImF1dGhvcml0aWVzIjpbIlJPTEVfTkVXU19BUFAiLCJST0xFX1NQQUNFUyIsIlJPTEVfVklERU9TIiwiUk9MRV9HRU5FUkFMX05FV1MiLCJST0xFX1NPTEFSTFVYX0lOU0lERSIsIlJPTEVfVEVDSE5JQ0FMX0RPQ1MiLCJST0xFX1NPTEFSTFVYX0FETUlOIl0sImNsaWVudF9pZCI6Im15LWNsaWVudC13aXRoLXJlZ2lzdGVyZWQtcmVkaXJlY3QiLCJmaXJzdE5hbWUiOiJKb2huIiwic2NvcGUiOlsicmVhZCIsInRydXN0Il0sImlkIjoxMywiZXhwIjoxNTE1NTQ3OTY5LCJjcm1Db250YWN0SWQiOm51bGwsImVtYWlsIjoiam9obi5kb2UyQGV4YW1wbGUubmV0IiwianRpIjoiYjQ4NDQ0MTktYTFiNi00MGY4LWI3NTUtYTE3NzJiMjNjM2JiIn0.Gp7TR1McKE8KM-bPu1nvDMrKjvuC5Xe6CuVlPmiG-jUmlypgOl-_fonCo6OOozA90YXZPdq0n0FFt9a4oMjPXmQj00WMgOIvpH5yzRWNHArZQTH8vdAm4TU1iA2juzzz-WRQJz-khL4mvXDq24Ezcy7ZGYZ0sUZROGzWuEJi6IDcxpj659O1LWYpvXaVDocfPA5DFhrpbXQr3BePSgNAFrdm1sXOBXSRHNCeMbRVBPz1UDxRYGrXiuyU770uiVR8bbkOsS9QECgryHKpW6KO0q_xfYcEiuvOBAiaMHk7N4yALjYXq-NbRbonXVueLuKLd3lrI2_tdah96iOQ5JAh0A'

        user = get_unsaved_user_from_token(token)

        self.assertEqual(user.email, 'john.doe2@example.net')
        self.assertEqual(user.customer_no, '5000167')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe test')
        self.assertEqual(user.customer_name, 'Linara')
        self.assertEqual(user.title, 'MR')
        self.assertEqual(user.is_customer_admin, True)
        self.assertEqual(user.crm_contact_id, None)
        self.assertEqual(user.language, 'en')
        self.assertEqual(user.um_id, 13)


class FetchProfileTestCase(TestCase):
    def test_can_fetch_profile(self):

        # don't worry if this token is invalid. get a new one from my.solarlux.com (cookies tab)...
        token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJsYXN0TmFtZSI6IkRvZSB0ZXN0IiwibGFuZ3VhZ2UiOiJlbiIsImlzQ3VzdG9tZXJBZG1pbiI6dHJ1ZSwiY3VzdG9tZXJOdW1iZXIiOiI1MDAwMTY3IiwidGl0bGUiOiJNUiIsImN1c3RvbWVyTmFtZSI6IkxpbmFyYSIsImF1dGhvcml0aWVzIjpbIlJPTEVfTkVXU19BUFAiLCJST0xFX1NQQUNFUyIsIlJPTEVfVklERU9TIiwiUk9MRV9HRU5FUkFMX05FV1MiLCJST0xFX1NPTEFSTFVYX0lOU0lERSIsIlJPTEVfVEVDSE5JQ0FMX0RPQ1MiLCJST0xFX1NPTEFSTFVYX0FETUlOIl0sImNsaWVudF9pZCI6Im15LWNsaWVudC13aXRoLXJlZ2lzdGVyZWQtcmVkaXJlY3QiLCJmaXJzdE5hbWUiOiJKb2huIiwic2NvcGUiOlsicmVhZCIsInRydXN0Il0sImlkIjoxMywiZXhwIjoxNTE1NTQ3OTY5LCJjcm1Db250YWN0SWQiOm51bGwsImVtYWlsIjoiam9obi5kb2UyQGV4YW1wbGUubmV0IiwianRpIjoiYjQ4NDQ0MTktYTFiNi00MGY4LWI3NTUtYTE3NzJiMjNjM2JiIn0.Gp7TR1McKE8KM-bPu1nvDMrKjvuC5Xe6CuVlPmiG-jUmlypgOl-_fonCo6OOozA90YXZPdq0n0FFt9a4oMjPXmQj00WMgOIvpH5yzRWNHArZQTH8vdAm4TU1iA2juzzz-WRQJz-khL4mvXDq24Ezcy7ZGYZ0sUZROGzWuEJi6IDcxpj659O1LWYpvXaVDocfPA5DFhrpbXQr3BePSgNAFrdm1sXOBXSRHNCeMbRVBPz1UDxRYGrXiuyU770uiVR8bbkOsS9QECgryHKpW6KO0q_xfYcEiuvOBAiaMHk7N4yALjYXq-NbRbonXVueLuKLd3lrI2_tdah96iOQ5JAh0A'

        response = requests.get('https://my.solarlux.com/apps/users/api/user/profile', headers={
            'Authorization': 'Bearer %s' % token
        }, timeout=0.5)

        self.assertEqual(response.status_code, 200)

        portal_config = response.json()


        user = get_unsaved_user_from_token_and_portal_config(token, portal_config)

        self.assertEqual(user.avatar_attachment_id, 5)
        self.assertEqual(user.company_logo_attachment_id, None)
