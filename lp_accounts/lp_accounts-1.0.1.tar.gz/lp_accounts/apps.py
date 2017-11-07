from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'lp_accounts'
    verbose_name = 'Accounts'

    def ready(self):
        super(AccountConfig, self).ready()

        # noinspection PyUnresolvedReferences
        import lp_accounts.signals