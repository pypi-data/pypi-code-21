VERSION = '1.5.2'


import requests
from pkg_resources import parse_version


def versions(name):
    """
    Get Versions from Pypi
    :param name:
    :return:
    """
    url = "https://pypi.python.org/pypi/{}/json".format(name)
    return sorted(requests.get(url).json()["releases"], key=parse_version)


def get_current_version():
    """
    Checks if current version is latest
    :return: Bool
    """
    latest_version = versions("tensorport")[-1]
    return latest_version == VERSION
