from colab.plugins.utils.apps import ColabPluginAppConfig
from colab_pauta.tasks import login_user, logout_user
from django.contrib.auth.signals import user_logged_in, user_logged_out


class ColabPautaAppConfig(ColabPluginAppConfig):
    name = 'colab_pauta'
    verbose_name = 'Colab Pauta Plugin'
    short_name = 'colab_pauta'
    namespace = 'colab_pauta'

    def connect_signal(self):
        user_logged_in.connect(login_user)
        user_logged_out.connect(logout_user)
