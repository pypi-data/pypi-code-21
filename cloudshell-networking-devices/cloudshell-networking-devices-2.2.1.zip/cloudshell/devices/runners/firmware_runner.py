#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractproperty

from cloudshell.core.logger import qs_logger
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.devices.runners.interfaces.firmware_runner_interface import FirmwareRunnerInterface


class FirmwareRunner(FirmwareRunnerInterface):
    def __init__(self, logger):
        """Handle firmware upgrade process

        :param qs_logger logger: logger
        """
        self._logger = logger
        self._timeout = 3600

    @abstractproperty
    def cli_handler(self):
        """ CLI Handler property
        :return: CLI handler
        """

        pass

    @abstractproperty
    def load_firmware_flow(self):
        """ Load Firmaware flow property
        :return: LoadFirmawareFlow object
        """

        pass

    def load_firmware(self, path, vrf_management_name=None):
        """Update firmware version on device by loading provided image, performs following steps:

            1. Copy bin file from remote tftp server.
            2. Clear in run config boot system section.
            3. Set downloaded bin file as boot file and then reboot device.
            4. Check if firmware was successfully installed.

        :param path: full path to firmware file on ftp/tftp location
        :param vrf_management_name: VRF Name
        :return: status / exception
        """

        url = UrlParser.parse_url(path)
        required_keys = [UrlParser.FILENAME, UrlParser.HOSTNAME, UrlParser.SCHEME]

        if not url or not all(key in url for key in required_keys):
            raise Exception(self.__class__.__name__, "Path is wrong or empty")

        self.load_firmware_flow.execute_flow(path, vrf_management_name, self._timeout)
