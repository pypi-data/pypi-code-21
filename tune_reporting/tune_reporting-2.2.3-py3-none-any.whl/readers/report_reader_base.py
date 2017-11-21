#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""
Report Reader Base
"""

from logging import getLogger

from abc import ABCMeta, abstractproperty

log = getLogger(__name__)


# @brief TUNE Multiverse Report Reader abstract base class.
#
# @namespace tune_reporting.ReportReaderBase
class ReportReaderBase(object):
    """Base Abstract class."""

    __metaclass__ = ABCMeta

    __report_url = None

    #  Integration Name
    #  @var str
    __integration = ""

    __data = None

    @property
    def data(self):
        """Provide created reader populated with file data."""
        return self.__data

    @data.setter
    def data(self, value):
        """Provide data value."""
        self.__data = value

    #  The constructor
    #  @param str report_url Download report URL
    #                         of requested report to be exported.
    def __init__(self, report_url):
        """Constructor

            :param str report_url: Download report URL.
        """
        if not report_url:
            raise ValueError(error_message="Undefined 'report_url'")

        if not report_url or \
           not isinstance(report_url, str) or \
           len(report_url) < 1:
            raise ValueError("Parameter 'report_url' is not defined.")

        self.__report_url = report_url

    @abstractproperty
    def read(self):
        """Get property for TuneManagementRequest Action Name."""
        return

    @property
    def report_url(self):
        """REPORT_URL of completed report on SQS."""
        return self.__report_url

    @property
    def generator(self):
        """Generate report data."""
        if not self.data or len(self.data) == 0:
            yield []
        else:
            for (i, item) in enumerate(self.data):
                yield item
