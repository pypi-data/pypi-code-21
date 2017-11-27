"""
Module:
    unicon.plugins.generic

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
    This module imports connection provider class which has
    exposes two methods named connect and disconnect. These
    methods are implemented in such a way so that they can
    handle majority of platforms and subclassing is seldom
    required.
"""
from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.bases.routers.connection_provider import BaseDualRpConnectionProvider
from unicon.eal.dialogs import Dialog
from .statements import GenericStatements
from unicon import log




class GenericSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    # def connect(self):
    #     print('connecting from connection provider')
    #
    # def disconnect(self):
    #     print('disconnecting from connection provider')

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        generic_statements = GenericStatements()
        #############################################################
        # Initial connection Statement
        #############################################################

        pre_connection_statement_list = [generic_statements.escape_char_stmt,
                                         generic_statements.press_return_stmt,
                                         generic_statements.continue_connect_stmt,
                                         generic_statements.connection_refused_stmt,
                                         generic_statements.disconnect_error_stmt]

        #############################################################
        # Authentication Statement
        #############################################################

        authentication_statement_list = [generic_statements.bad_password_stmt,
                                         generic_statements.login_incorrect,
                                         generic_statements.login_stmt,
                                         generic_statements.useraccess_stmt,
                                         generic_statements.password_stmt
                                         ]

        connection_statement_list = authentication_statement_list + pre_connection_statement_list

        return Dialog(connection_statement_list)


class GenericDualRpConnectionProvider(BaseDualRpConnectionProvider):
    """ Implements Generic dualRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    # def connect(self):
    #     print('connecting from connection provider')
    #
    # def disconnect(self):
    #     print('disconnecting from connection provider')

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device
            Any additional Statements(prompts) to be handled during
            initial connection has to be updated here,
            connection provider uses this method to fetch connection
            dialog
        """
        generic_statements = GenericStatements()
        #############################################################
        # Initial connection Statement
        #############################################################

        pre_connection_statement_list = [generic_statements.escape_char_stmt,
                                         generic_statements.press_return_stmt,
                                         generic_statements.continue_connect_stmt,
                                         generic_statements.connection_refused_stmt]

        #############################################################
        # Authentication Statement
        #############################################################

        authentication_statement_list = [generic_statements.bad_password_stmt,
                                         generic_statements.login_stmt,
                                         generic_statements.password_stmt
                                         ]

        connection_statement_list = authentication_statement_list + pre_connection_statement_list

        return Dialog(connection_statement_list)
