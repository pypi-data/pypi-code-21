import logging

from admin_logs.log import AdminLogHandler


__version__ = (0, 2, '6')


default_app_config = 'admin_logs.apps.AdminLogsConfig'


BASE_HANDLER = AdminLogHandler()


def add_handler():
    for handler in logging.root.handlers:
        if isinstance(handler, AdminLogHandler):
            break
    else:
        BASE_HANDLER.setLevel(logging.DEBUG)
        logging.root.addHandler(BASE_HANDLER)

add_handler()
