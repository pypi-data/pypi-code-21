import json
import logging
import os.path
import re
from typing import Union, Dict
import pkg_resources

LOGGER = logging.getLogger(__name__)
PACKAGE_NAME = "mac2vendors"

def write_mac_json(source: str, destination: str) -> None:
    '''
        >>> source = "vendors.txt"
        >>> destination = "vendors.json"
        >>> write_mac_json(source=source,destination=destination)
        >>> assert os.path.isfile(destination)

        :param source: Filename of the file containing the mac vendor mapping
        :type source: str
        :param destination: Filename of the json file that should contain the final vendor mapping
        :type destination: str
        :return:
    '''
    _source = pkg_resources.resource_filename(PACKAGE_NAME, source)
    _destination = pkg_resources.resource_filename(PACKAGE_NAME, destination)
    LOGGER.debug("write_mac_json - source: %s destination: %s" % (_source, _destination))
    with open(_source) as inputFile:
        LOGGER.debug(inputFile)
        lines = [line.split("\t") for line in inputFile.readlines() if
                 not line.startswith("  # ") or not line.strip() == ""]

        short = [[line[0]] + [line[1].strip("\n")] for line in lines if len(line) == 2]
        long = [line[0:2] + [line[2].rstrip("\n")] for line in lines if len(line) == 3]

        payload = {
            "short": {line[0]: line for line in short},
            "long": {line[0]: line for line in long}
        }

        write_json(_destination, payload)


def write_json(destination: str, payload: Union[str, Dict]) -> None:
    '''
    Write the json payload to the given destination.
    :param destination: The file to write the payload to
    :param payload: The payload
    :return:
    '''
    with open(destination, mode="w", encoding="utf-8") as outputFile:
        serialized_payload = json.dump(payload, outputFile)


def read_json(source: str):
    '''

    :param source: Name of the json file to read
    :return:
    '''
    with open(source, mode="r", encoding="utf-8") as inputFile:
        return json.load(inputFile)


def _assert_mapping_file_exists(file_path: str = "vendors.json", force_refresh: bool = False) -> None:
    '''
    Checks if the mapping file exists.

    :param file_path: The filepath to the mapping file
    :type str:
    :return:
    '''

    exists = os.path.exists(file_path)
    if not exists or force_refresh:
        write_mac_json("vendors.txt", "vendors.json")


def get_mac_vendor(source: str = "vendors.json", mac_address: str = "00:00:00", strict: bool = False):
    '''
    Pretest of get_mac_vendor:
    >>> write_mac_json("vendors.txt","vendors.json")

    >>> get_mac_vendor( source="vendors.json", mac_address="00:00:14:00:00:14" )
    [['00:00:14', 'Netronix']]

    >>> get_mac_vendor( source="vendors.json", mac_address="00:00:13", strict=True)
    [00:00:13] is not a valid mac address


    :param source:
    :type source: str
    :param mac:
    :type mac: str
    :return:
    '''
    _source = pkg_resources.resource_filename(PACKAGE_NAME, source)
    try:
        assert_is_mac(mac_address, strict)
    except ValueError as error:
        print(error)
        return None
    mac_addresses = read_json(source=_source)
    short = mac_addresses["short"]
    long = mac_addresses["long"]

    if len(mac_address) >= 8:
        prefix = mac_address[:8]
        mac_identifier = short[prefix] if prefix in short else long[prefix] if prefix in long else None
        if mac_identifier is not None:
            return [mac_identifier]
        return []

    long_matches = [m for key, m in long.items() if mac_address.startswith(key)]
    short_matches = [m for key, m in short.items() if
                     mac_address.startswith(key) and len(mac_address) >= len(key) or key.startswith(
                         mac_address) and len(key) > len(mac_address)]

    return short_matches + long_matches


def assert_is_mac(mac: str, strict: bool = False):
    '''
    >>> assert_is_mac("asdasd",True)
    Traceback (most recent call last):
        ...
    ValueError: [asdasd] is not a valid mac address

    >>> assert_is_mac("00:00:14:ff:fi:00", True)
    Traceback (most recent call last):
        ...
    ValueError: [00:00:14:ff:fi:00] is not a valid mac address

    >>> assert_is_mac("00:00:14:ff:fd:00", True)

    >>> assert_is_mac("00:00:14:ff:fd:00", False)

    :param mac: The mac address that has to be matched
    :param strict: strict: match all 12 bytes, not strict: Everything despite None is okay
    :return:
    '''
    if not strict:
        if mac is None:
            raise ValueError("Provide a mac address!")

        return
    else:
        mac_matches = re.search(r"([\dA-F]{2}(?:[-:][\dA-F]{2}){5})", mac, re.I)

    if not mac_matches is not None:
        raise ValueError("[%s] is not a valid mac address" % mac)
