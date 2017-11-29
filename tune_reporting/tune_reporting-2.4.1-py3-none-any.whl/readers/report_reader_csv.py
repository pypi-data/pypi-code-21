#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""Report Reader CSV
"""

from logging import getLogger
import sys
import csv
import requests

# from pprintpp import pprint

from .report_reader_base import (ReportReaderBase)

log = getLogger(__name__)


# @brief TUNE Multiverse Report CSV reader.
#
# @namespace tune_reporting.ReportReaderCSV
class ReportReaderCSV(ReportReaderBase):
    """Helper class for reading reading remote CSV file
    """

    #  The constructor
    #  @param str report_url Download report URL
    #                         of requested report to be exported.
    def __init__(self, report_url):
        """The constructor.

            :param str report_url: Report URL to be downloaded.
        """
        if not report_url:
            raise ValueError(error_message="Undefined 'report_url'")
        self.reader = None
        super(ReportReaderCSV, self).__init__(report_url)

    #  Using provided report download URL, extract CSV contents.
    #
    def read(self, csv_delimiter=','):
        """Read CSV data provided remote path report_url.

        Args:
            csv_delimiter:

        Returns:

        """
        self.data = None

        response = requests.get(url=self.report_url, stream=True)

        log.info("ReportReaderCSV: Response", extra={'http_status_code': response.status_code})

        data = response.text

        reader = csv.DictReader(data.splitlines(), delimiter=csv_delimiter)

        self.data = list(reader)
        self.count = len(self.data)

    def next(self):
        """Retrieve the next item from the iterator."""
        try:
            row = self.reader.__next__()
            return [str(value, "utf-8") for value in row]

        except StopIteration:
            pass

        return None

    def __iter__(self):
        """This method is called when an iterator is required for a container.
        """
        # pylint: disable=not-an-iterable
        for row in self.reader:
            yield row
        # pylint: enable=not-an-iterable

    def pretty_print(self, limit=0):
        """Pretty print exported data.

            :param int limit: Number of rows to print.
        """
        print("Report REPORT_URL: {}".format(self.report_url))
        print("------------------")

        if sys.version_info >= (3, 0, 0):
            # pylint: disable=not-an-iterable
            for row in self.reader:
                print(', '.join(row))
            # pylint: enable=not-an-iterable
        else:
            i = 0
            while True:
                row = self.next()
                if row is None:
                    break
                i += 1
                print("{}. {}".format(i, str(row)))
                if (limit > 0) and (i >= limit):
                    break

        print("------------------")
