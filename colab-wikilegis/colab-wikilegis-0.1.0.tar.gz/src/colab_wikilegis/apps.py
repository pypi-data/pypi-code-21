from colab.plugins.utils.apps import ColabPluginAppConfig
from colab_wikilegis.tasks import login_user, logout_user
from django.contrib.auth.signals import user_logged_in, user_logged_out


class WikilegisAppConfig(ColabPluginAppConfig):
    name = 'colab_wikilegis'
    verbose_name = 'Colab Wikilegis Plugin'
    short_name = 'wikilegis'
    namespace = 'wikilegis'

    def connect_signal(self):
        user_logged_in.connect(login_user)
        user_logged_out.connect(logout_user)
