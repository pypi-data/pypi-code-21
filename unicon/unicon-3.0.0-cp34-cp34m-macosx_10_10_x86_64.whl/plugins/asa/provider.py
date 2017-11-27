from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider

from . import statements

from unicon.eal.dialogs import Dialog


class ASAConnectionProvider(BaseSingleRpConnectionProvider):

    def get_connection_dialog(self):
        return Dialog([statements.login_password,
                       statements.escape_char_stmt,
                       statements.press_return_stmt,
                       statements.connection_refused_stmt,
                       statements.bad_password_stmt,
                       statements.disconnect_error_stmt,
                       ])