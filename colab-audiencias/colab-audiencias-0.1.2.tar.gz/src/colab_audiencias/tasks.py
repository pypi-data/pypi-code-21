from django.contrib.sites.models import Site
from colab.plugins import helpers
import requests
import json


def login_user(sender, user, request, **kwargs):
    prefix = helpers.get_plugin_prefix('colab_audiencias', regex=False)
    base_url = Site.objects.get_current().domain
    base_url = "{}/{}".format(base_url, prefix)
    avatar = None
    if hasattr(user.profile.avatar, 'url'):
        avatar = user.profile.avatar.url
    user_data = {
        'email': user.email,
        'name': user.get_full_name(),
        'avatar': avatar
    }
    remote_user_data = json.dumps(user_data)
    headers = {'Auth-user': user.username,
               'Remote-User-Data': remote_user_data}

    response = requests.get(base_url, headers=headers)
    session = response.cookies.get('audiencias_session')
    request.COOKIES.set("audiencias_session", session)


def logout_user(sender, user, request, **kwargs):
    request.COOKIES.delete('audiencias_session')
