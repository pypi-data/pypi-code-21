from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login


class ConnectExistingUsersSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        from django.contrib.auth.models import User

        user = sociallogin.user

        if user.id:
            return

        try:
            # if user exists, connect the account to the existing account and login
            user = User.objects.get(username=user.username)

            sociallogin.state['process'] = 'connect'
            perform_login(request, user, 'none')
        except User.DoesNotExist:
            pass
