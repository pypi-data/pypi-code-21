#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting
"""Report Reader JSON
"""

import ujson as json
from logging import getLogger
import requests
# from pprintpp import pprint

from .report_reader_base import (ReportReaderBase)

log = getLogger(__name__)


# @brief TUNE Multiverse Report JSON reader.
#
# @namespace tune_reporting.ReportReaderCSV
class ReportReaderJSON(ReportReaderBase):
    """Helper class for reading reading remote JSON file"""

    #  The constructor
    #  @param str report_url Download report URL
    #                         of requested report to be exported.
    def __init__(self, report_url):
        """The constructor.

            :param str report_url: Report URL to be downloaded.
        """
        super(ReportReaderJSON, self).__init__(report_url)

    #  Using provided report download URL, extract JSON contents.
    #
    def read(self):
        """Read JSON data provided remote path report_url."""
        self.data = None

        response = requests.get(url=self.report_url)

        log.info("ReportReaderJSON: Response", extra={'http_status_code': response.status_code})

        self.data = json.loads(response.text)
        self.count = len(self.data)

    def pretty_print(self, limit=0):
        """Pretty print exported data.

            :param int limit: Number of rows to print.
        """
        print("Report REPORT_URL: {}".format(self.report_url))
        print("Report total row count: {}".format(self.count))
        if self.count > 0:
            print("------------------")
            rows = list(self.data)
            i = 0
            for row in enumerate(rows):
                i = i + 1
                print("{}. {}".format(i, str(row)))
                if (limit > 0) and (i >= limit):
                    break
            print("------------------")
