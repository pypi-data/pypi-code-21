import socket
from uuid import uuid4

import re

_EXTRACT_VERSION_PATTERN = re.compile("[0-9]+(_[0-9]+)*")


def create_random_string(postfix: str= "", prefix: str="") -> str:
    """
    Creates a random string.
    :param postfix: optional postfix
    :param prefix: optional prefix
    :return: created string
    """
    return "%s%s%s" % (prefix, uuid4(), postfix)


def get_open_port() -> int:
    """
    Gets a PORT that will (probably) be available on the machine.
    It is possible that in-between the time in which the open PORT of found and when it is used, another process may
    bind to it instead.
    :return: the (probably) available PORT
    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(("", 0))
    free_socket.listen(1)
    port = free_socket.getsockname()[1]
    free_socket.close()
    return port


def extract_version_number(string: str) -> str:
    """
    Extracts a version from a string in the form: `.*[0-9]+(_[0-9]+)*.*`, e.g. Irods4_1_9CompatibleController.

    If the string contains multiple version numbers, the first (from left) is extracted.

    Will raise a `ValueError` if there is no version number in the given string.
    :param string: the string containing the version number
    :return: the extracted version
    """
    matched = _EXTRACT_VERSION_PATTERN.search(string)
    if matched is None:
        raise ValueError("No version number in string")
    return matched.group().replace("_", ".")
