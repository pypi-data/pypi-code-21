import logging
from datetime import datetime, timedelta
from fe_core.models import Entity
import requests
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from oauth2_provider.oauth2_validators import OAuth2Validator, AccessToken
from oauth2_provider.settings import oauth2_settings

log = logging.getLogger("oauth2_provider")

UserModel = get_user_model()


class FEOAuth2Validator(OAuth2Validator):
    def _get_token_from_authentication_server(self, token, introspection_url, introspection_token):
        bearer = "Bearer {}".format(introspection_token)

        try:
            response = requests.post(
                introspection_url,
                data={"token": token}, headers={"Authorization": bearer}
            )
        except requests.exceptions.RequestException:
            log.exception("Introspection: Failed POST to %r in token lookup", introspection_url)
            return None
        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "username" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.USERNAME_FIELD: content["username"]}
                )
            else:
                user = None

            if user is not None and 'entity' in content:
                entity, _created = Entity.objects.get_or_create(uuid=content['entity'])
                user.entity = entity
                user.save()

            max_caching_time = datetime.now() + timedelta(
                seconds=oauth2_settings.RESOURCE_SERVER_TOKEN_CACHING_SECONDS
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")
            expires = make_aware(expires)

            try:
                access_token = AccessToken.objects.select_related("application", "user").get(token=token)
            except AccessToken.DoesNotExist:
                access_token = AccessToken.objects.create(
                    token=token,
                    user=user,
                    application=None,
                    scope=scope,
                    expires=expires
                )
            else:
                access_token.expires = expires
                access_token.scope = scope
                access_token.save()

            return access_token
