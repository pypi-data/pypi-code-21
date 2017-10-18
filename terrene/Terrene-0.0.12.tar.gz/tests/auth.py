import unittest


class CredentialsTestCases(unittest.TestCase):
    def test_email_password_credentials(self):
        import os
        from terrene.auth import EmailPasswordCredentials

        credentials = EmailPasswordCredentials(
            email=os.environ.get('EMAIL'), password=os.environ.get('PASSWORD'))

    def test_bad_credentials(self):
        from terrene.auth import EmailPasswordCredentials
        import coreapi
        try:
            credentials = EmailPasswordCredentials(
                email='random@random.com', password='bad_password')
            raise AssertionError('bad credentials should not work')
        except coreapi.exceptions.ErrorMessage:
            pass


class UserTestCases(unittest.TestCase):
    def test_user_manager(self):
        import os
        from terrene.auth import EmailPasswordCredentials
        from terrene.auth import UserManager

        credentials = EmailPasswordCredentials(
            email=os.environ.get('EMAIL'), password=os.environ.get('PASSWORD'))
        user_manager = UserManager(credentials=credentials)

        assert user_manager.current_user is not None

    def test_user_profile_changes(self):

        import os
        from terrene.auth import EmailPasswordCredentials
        from terrene.auth import UserManager

        credentials = EmailPasswordCredentials(
            email=os.environ.get('EMAIL'), password=os.environ.get('PASSWORD'))
        user_manager = UserManager(credentials=credentials)
        user = user_manager.current_user

        original_first_name = user.first_name
        user.first_name = 'My New Name'
        user.save()
        user.retrieve()
        assert user.first_name == 'My New Name'

        user.first_name = original_first_name
        user.save()
        user.retrieve()
        assert user.first_name == original_first_name
