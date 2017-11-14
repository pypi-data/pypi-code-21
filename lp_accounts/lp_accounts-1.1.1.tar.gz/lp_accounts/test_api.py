from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from lp_unittest.base import BaseRestUnitTest
from rest_framework import status
from rest_framework.authtoken.models import Token
from parameterized import parameterized
from .models import User

User = get_user_model()


class AccountTestCase(BaseRestUnitTest):
    fixtures = ['users']

    def login(self, **kwargs):
        return self.post(**kwargs)

    def reset(self, **kwargs):
        return self.post(**kwargs)

    def update_password(self, **kwargs):
        return self.post(**kwargs)

    @staticmethod
    def get_admin_user():
        return User.objects.get(username='ken.griffey')

    @staticmethod
    def get_user_type_default():
        return User.objects.get(username='tino.martinez')

    @staticmethod
    def get_user_type_google():
        return User.objects.get(username='derek.jeter')

    @staticmethod
    def get_user_type_facebook():
        return User.objects.get(username='mo.vaughn')

    @staticmethod
    def get_user_type_github():
        return User.objects.get(username='bob.dylan')

    @staticmethod
    def get_user_type_linkedin():
        return User.objects.get(username='michael.jordan')

    @staticmethod
    def get_user_type_default_data():
        return {
            'username': 'test@launchpeer.com',
            'password': '5qVrlRQzxvHJViRUi4TXek6MxWu18MfKi012u40CFiI=',
            'first_name': 'Launch',
            'last_name': 'Monkey',
            'email': 'launchmonkey@launchpeer.com',
            'type': User.TYPE_DEFAULT,
        }

    @staticmethod
    def get_user_type_google_data():
        return {
            'username': 'launchmonkey_google@launchpeer.com',
            'access_token': 'thisisanaccesstoken',
            'first_name': 'Launch',
            'last_name': 'Monkey',
            'email': 'launchmonkey_google@launchpeer.com',
            'type': User.TYPE_GOOGLE,
        }

    @staticmethod
    def get_user_type_facebook_data():
        return {
            'username': 'launchmonkey_facebook@launchpeer.com',
            'access_token': 'thisisanaccesstoken',
            'first_name': 'Launch',
            'last_name': 'Monkey',
            'email': 'launchmonkey_facebook@launchpeer.com',
            'type': User.TYPE_FACEBOOK,
        }

    @staticmethod
    def get_user_type_github_data():
        return {
            'username': 'launchmonkey_github@launchpeer.com',
            'access_token': 'thisisanaccesstoken',
            'first_name': 'Launch',
            'last_name': 'Monkey',
            'email': 'launchmonkey_facebook@launchpeer.com',
            'type': User.TYPE_GITHUB,
        }


class AccountCreateTestCase(AccountTestCase):
    url = 'lp_accounts_create'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_201_CREATED),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_201_CREATED)
    ]
    REQUIRED_FIELDS = [
        ('username', 'username'),
        ('email', 'email'),
        ('password', 'password'),
        ('type', 'type')
    ]
    REQUIRED_FIELDS_GOOGLE = [
        ('username', 'username'),
        ('email', 'email'),
        ('type', 'type'),
        ('access_token', 'access_token'),
    ]
    REQUIRED_FIELDS_FACEBOOK = [
        ('username', 'username'),
        ('email', 'email'),
        ('type', 'type'),
        ('access_token', 'access_token'),
    ]
    REQUIRED_FIELDS_GITHUB = [
        ('username', 'username'),
        ('email', 'email'),
        ('type', 'type'),
        ('access_token', 'access_token'),
    ]

    @parameterized.expand(PERMISSIONS)
    def test_default_account_create_permissions(self, _, user, expected):
        self.authenticate(user)
        response = self.create(data=AccountTestCase.get_user_type_default_data())
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(PERMISSIONS)
    @override_settings(LP_ACCOUNTS_GOOGLE_APP_ID='testappid')
    def test_google_account_create_permissions(self, _, user, expected):
        self.authenticate(user)
        response = self.create(data=AccountTestCase.get_user_type_google_data())
        self.assertEqual(response.status_code, expected, response.data)

    @parameterized.expand(PERMISSIONS)
    @override_settings(LP_ACCOUNTS_FACEBOOK_APP_ID='testappid', LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET='testclientsecret')
    def test_facebook_account_create_permissions(self, _, user, expected):
        self.authenticate(user)
        response = self.create(data=AccountTestCase.get_user_type_facebook_data())
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_fields_default_account_create(self, _, field):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_default_data(), exclude=[field])
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(REQUIRED_FIELDS_GOOGLE)
    @override_settings(LP_ACCOUNTS_GOOGLE_APP_ID='testappid')
    def test_required_fields_google_account_create(self, _, field):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_google_data(), exclude=[field])
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(REQUIRED_FIELDS_FACEBOOK)
    @override_settings(LP_ACCOUNTS_FACEBOOK_APP_ID='testappid', LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET='testclientsecret')
    def test_required_fields_facebook_account_create(self, _, field):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_facebook_data(), exclude=[field])
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand(REQUIRED_FIELDS_GITHUB)
    @override_settings(LP_ACCOUNTS_GITHUB_APP_ID='testappid', LP_ACCOUNTS_GITHUB_CLIENT_SECRET='testclientsecret')
    def test_required_fields_github_account_create(self, _, field):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_github_data(), exclude=[field])
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validates_type(self):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_default_data(), injections={'type': 100})
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_secure(self):
        self.authenticate(user=None)
        data = self.modify_data(data=AccountTestCase.get_user_type_default_data(), injections={'password': 'password'})
        response = self.create(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_GOOGLE_APP_ID=None)
    def test_google_signin_config_check(self):
        self.authenticate(user=None)
        response = self.create(data=self.get_user_type_google_data())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_FACEBOOK_APP_ID=None, LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET=None)
    def test_facebook_login_config_check(self):
        self.authenticate(user=None)
        response = self.create(data=self.get_user_type_facebook_data())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_GITHUB_APP_ID=None, LP_ACCOUNTS_GITHUB_CLIENT_SECRET=None)
    def test_github_login_config_check(self):
        self.authenticate(user=None)
        response = self.create(data=self.get_user_type_github_data())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_WELCOME_EMAIL_ENABLED=True)
    def test_welcome_email_did_send(self):
        self.authenticate(user=None)
        self.create(data=self.get_user_type_default_data())
        self.assertEqual(len(mail.outbox), 1)

    def test_welcome_email_did_not_send_when_disabled(self):
        self.authenticate(user=None)
        self.create(data=self.get_user_type_default_data())
        self.assertEqual(len(mail.outbox), 0)

    def test_response_has_token(self):
        self.authenticate(user=None)
        response = self.create(data=self.get_user_type_default_data())
        self.assertContains(response, 'token', status_code=status.HTTP_201_CREATED)


class DefaultAccountLoginTestCase(AccountTestCase):
    url = 'lp_accounts_login'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_200_OK),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('username', 'username'),
        ('password', 'password'),
        ('account_type', 'account_type')
    ]

    def setUp(self):
        super(DefaultAccountLoginTestCase, self).setUp()
        data = self.get_user_type_default_data()
        user = User.objects.create(**data)
        user.set_password(data['password'])
        user.save()
        self.data = {
            'username': data['username'],
            'password': data['password'],
            'account_type': data['type']
        }

    @parameterized.expand(PERMISSIONS)
    def test_can_login(self, _, user, expected):
        self.authenticate(user=user)
        response = self.login(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_fields(self, _, field):
        data = self.modify_data(self.data, exclude=[field])
        response = self.login(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(LP_ACCOUNTS_GOOGLE_APP_ID='testappid')
class GoogleAccountLoginTestCase(AccountTestCase):
    url = 'lp_accounts_login'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_200_OK),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('username', 'username'),
        ('access_token', 'access_token'),
        ('account_type', 'account_type')
    ]

    def setUp(self):
        super(GoogleAccountLoginTestCase, self).setUp()
        data = self.get_user_type_default_data()
        data['type'] = User.TYPE_GOOGLE
        user = User.objects.create(**data)
        user.save()
        self.data = {
            'username': data['username'],
            'access_token': data['password'],
            'account_type': data['type']
        }

    @parameterized.expand(PERMISSIONS)
    def test_can_login(self, _, user, expected):
        self.authenticate(user=user)
        response = self.login(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_fields(self, _, field):
        data = self.modify_data(self.data, exclude=[field])
        response = self.login(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_GOOGLE_APP_ID=None)
    def test_config_check(self):
        response = self.login(data=self.data)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, response.data)


@override_settings(LP_ACCOUNTS_FACEBOOK_APP_ID='testappid', LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET='testclientsecret')
class FacebookAccountLoginTestCase(AccountTestCase):
    url = 'lp_accounts_login'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_200_OK),
        ('Authenticated User', AccountTestCase.get_user_type_default(),
         status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User',
         AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('username', 'username'),
        ('access_token', 'access_token'),
        ('account_type', 'account_type')
    ]

    def setUp(self):
        super(FacebookAccountLoginTestCase, self).setUp()
        data = self.get_user_type_default_data()
        data['type'] = User.TYPE_FACEBOOK
        user = User.objects.create(**data)
        user.save()
        self.data = {
            'username': data['username'],
            'access_token': data['password'],
            'account_type': data['type']
        }

    @parameterized.expand(PERMISSIONS)
    def test_can_login(self, _, user, expected):
        self.authenticate(user=user)
        response = self.login(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_fields(self, _, field):
        data = self.modify_data(self.data, exclude=[field])
        response = self.login(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_FACEBOOK_APP_ID=None, LP_ACCOUNTS_FACEBOOK_CLIENT_SECRET=None)
    def test_config_check(self):
        response = self.login(data=self.data)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, response.data)


@override_settings(LP_ACCOUNTS_GITHUB_APP_ID='testappid', LP_ACCOUNTS_GITHUB_CLIENT_SECRET='testclientsecret')
class GithubAccountLoginTestCase(AccountTestCase):
    url = 'lp_accounts_login'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_200_OK),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('username', 'username'),
        ('access_token', 'access_token'),
        ('account_type', 'account_type')
    ]

    def setUp(self):
        super(GithubAccountLoginTestCase, self).setUp()
        data = self.get_user_type_default_data()
        data['type'] = User.TYPE_GITHUB
        user = User.objects.create(**data)
        user.save()
        self.data = {
            'username': data['username'],
            'access_token': data['password'],
            'account_type': data['type']
        }

    @parameterized.expand(PERMISSIONS)
    def test_can_login(self, _, user, expected):
        self.authenticate(user=user)
        response = self.login(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_fields(self, _, field):
        data = self.modify_data(self.data, exclude=[field])
        response = self.login(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(LP_ACCOUNTS_GITHUB_APP_ID=None, LP_ACCOUNTS_GITHUB_CLIENT_SECRET=None)
    def test_config_check(self):
        response = self.login(data=self.data)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, response.data)


class AccountRetrieveTestCase(AccountTestCase):
    url = 'lp_accounts_retrieve'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_401_UNAUTHORIZED),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_200_OK),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_200_OK)
    ]

    @parameterized.expand(PERMISSIONS)
    def test_permissions(self, _, user, expected):
        self.authenticate(user=user)
        response = self.retrieve()
        self.assertEqual(response.status_code, expected)


class AccountUpdateTestCase(AccountTestCase):
    url = 'lp_accounts_update'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_401_UNAUTHORIZED),
        ('Authenticated User', AccountTestCase.get_user_type_default(), status.HTTP_200_OK),
        ('Authenticated Admin User', AccountTestCase.get_admin_user(), status.HTTP_200_OK)
    ]

    @parameterized.expand(PERMISSIONS)
    def test_permissions(self, _, user, expected):
        self.authenticate(user=user)
        response = self.update(data={})
        self.assertEqual(response.status_code, expected, response.data)


class AccountResetPasswordRequestTestCase(AccountTestCase):
    url = 'lp_accounts_password_reset'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_204_NO_CONTENT),
        ('Authenticated User', AccountTestCase.get_user_type_default(),
         status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User',
         AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('email', 'email')
    ]

    def setUp(self):
        super(AccountResetPasswordRequestTestCase, self).setUp()
        user = self.get_user_type_default()
        self.data = {
            'email': user.email
        }

    @parameterized.expand(PERMISSIONS)
    def test_permissions(self, _, user, expected):
        self.authenticate(user=user)
        response = self.reset(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_field(self, _, field):
        data = self.modify_data(data=self.data, exclude=[field])
        response = self.reset(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_email_sent(self):
        response = self.reset(data=self.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_validates_email(self):
        data = self.modify_data(data=self.data, injections={
                                'email': 'notanemail@launchpeer.com'})
        response = self.reset(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_contains_token(self):
        self.reset(data=self.data)
        user = User.objects.get(email=self.data['email'])
        token, created = Token.objects.get_or_create(user=user)
        self.assertIn(token.key, mail.outbox[0].body)

    @override_settings(LP_ACCOUNTS_PASSWORD_RESET_SENDER='test@launchpeer.com')
    def test_email_sender_is_configurable(self):
        self.reset(data=self.data)
        self.assertEqual('test@launchpeer.com', mail.outbox[0].from_email)


class AccountResetPasswordTestCase(AccountTestCase):
    url = 'lp_accounts_password_update'

    PERMISSIONS = [
        ('Anonymous User', None, status.HTTP_200_OK),
        ('Authenticated User', AccountTestCase.get_user_type_default(),
         status.HTTP_403_FORBIDDEN),
        ('Authenticated Admin User',
         AccountTestCase.get_admin_user(), status.HTTP_403_FORBIDDEN)
    ]
    REQUIRED_FIELDS = [
        ('token', 'token'),
        ('password', 'password')
    ]

    def setUp(self):
        super(AccountResetPasswordTestCase, self).setUp()
        user = self.get_user_type_default()
        token, created = Token.objects.get_or_create(user=user)
        self.data = {
            'token': token.key,
            'password': 'newpassword'
        }

    @parameterized.expand(PERMISSIONS)
    def test_permissions(self, _, user, expected):
        self.authenticate(user=user)
        response = self.update_password(data=self.data)
        self.assertEqual(response.status_code, expected)

    @parameterized.expand(REQUIRED_FIELDS)
    def test_required_field(self, _, field):
        data = self.modify_data(data=self.data, exclude=[field])
        response = self.update_password(data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
