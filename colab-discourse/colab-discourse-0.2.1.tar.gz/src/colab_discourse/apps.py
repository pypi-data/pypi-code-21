from django.contrib.auth.signals import user_logged_in, user_logged_out
from colab.plugins.utils.apps import ColabPluginAppConfig
from colab_discourse.tasks import login_user, logout_user


class DiscourseAppConfig(ColabPluginAppConfig):
    name = 'colab_discourse'
    verbose_name = 'Colab Discourse Plugin'
    short_name = 'discourse'
    namespace = 'discourse'

    def connect_signal(self):
        user_logged_in.connect(login_user)
        user_logged_out.connect(logout_user)
