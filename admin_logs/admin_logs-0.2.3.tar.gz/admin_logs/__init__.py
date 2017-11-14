import logging

from admin_logs.log import AdminLogHandler


__version__ = (0, 2, '3')


default_app_config = 'admin_logs.apps.AdminLogsConfig'


BASE_HANDLER = AdminLogHandler()
BASE_HANDLER.setLevel(logging.DEBUG)
HANDLER_ADDED = False


def add_handler():
    global HANDLER_ADDED
    if HANDLER_ADDED:
        return
    HANDLER_ADDED = True

    logging.root.addHandler(BASE_HANDLER)

add_handler()
