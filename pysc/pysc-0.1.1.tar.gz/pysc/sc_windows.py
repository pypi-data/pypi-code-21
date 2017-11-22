import os
import threading
from subprocess import list2cmdline
from contextlib import contextmanager

from pysc import win_scm_api


__all__ = [
    'create',
    'delete',
    'start',
    'stop',
    'event_stop',
]


SVC_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svc.exe')


def create(service_name, cmd, username=None, password=None):
    if not isinstance(cmd, str):
        cmd = list2cmdline(cmd)
    cmd = list2cmdline([SVC_EXE]) + ' ' + cmd

    service_start_name = username
    if not (username and password):
        pass

    with win_scm_api.create_service(
        service_name,
        cmd,
        service_start_name,
        password
    ):
        pass


def delete(service_name):
    with win_scm_api.open_service(service_name, win_scm_api.DELETE) as service:
        win_scm_api.DeleteService(service)


def start(service_name):
    win_scm_api.start(service_name)


def stop(service_name):
    win_scm_api.stop(service_name)


def event_stop(close_func):
    t = threading.Thread(target=win_scm_api.wait, args=(close_func,))
    t.daemon = True
    t.start()


def set_user(username, password=None, service_name=None):
   win_scm_api.set_user(r'.\{}'.format(username), password, service_name)


@contextmanager
def service(service_name, cmd, username=None, password=None):
    create(service_name, cmd, username, password)
    try:
        start(service_name)
        try:
            yield
        finally:
            stop(service_name)
    finally:
        delete(service_name)
