from colab.plugins.utils.apps import ColabPluginAppConfig
from colab_audiencias.tasks import login_user, logout_user
from django.contrib.auth.signals import user_logged_in, user_logged_out


class AudienciasAppConfig(ColabPluginAppConfig):
    name = 'colab_audiencias'
    verbose_name = 'Colab Audiencias Plugin'
    short_name = 'audiencias'
    namespace = 'audiencias'

    def connect_signal(self):
        user_logged_in.connect(login_user)
        user_logged_out.connect(logout_user)
