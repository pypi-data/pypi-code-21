# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from .http_utils import get_account_info
from .models import TUserAccessToken, TUserExtra


class OAuthAccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if auth is None or not isinstance(auth, list) or len(auth) < 2 or 'Bearer' != auth[0]:
            return None

        access_token = auth[1]

        dt_now = datetime.now()
        saved = TUserAccessToken.objects.filter(access_token=access_token)

        valid = saved.filter(recheck_after__lte=dt_now)
        if valid.exists():
            # 验证成功
            user = valid.first().user
            return user, access_token
        else:
            if not saved.exists():
                saved.delete()

            status, response = get_account_info(settings.OAUTH_ACCOUNT_URL, 'Bearer', access_token)
            if status != 200:
                raise AuthenticationFailed

            account_info = json.loads(response)
            username = account_info.get('username')

            user_model = get_user_model()
            try:
                user = user_model.objects.select_related('extra').get(username=username)
            except ObjectDoesNotExist:
                user = user_model.objects.create(username=username)

            remote_privileges_list = account_info.get('privileges', [])

            if not hasattr(user, 'extra'):
                TUserExtra.objects.create(
                    user=user,
                    full_name=account_info.get('full_name'),
                    phone_number=account_info.get('mobile'),
                    access_token=access_token,
                    token_type='Bearer',
                    expires_in=600,
                    remote_privileges='|'.join(remote_privileges_list))
            else:
                user.extra.full_name = account_info.get('full_name')
                user.extra.access_token = access_token
                user.extra.token_type = 'Bearer'
                user.extra.expires_in = 600
                user.extra.remote_privileges = '|'.join(remote_privileges_list)
                user.extra.save()

            TUserAccessToken.objects.create(
                access_token=access_token,
                user=user,
                recheck_after=dt_now + timedelta(minutes=10))

            return user, access_token


