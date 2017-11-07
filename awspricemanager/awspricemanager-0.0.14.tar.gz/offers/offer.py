########################################################################
# Created By    : Adamson dela Cruz
# Date Created  : Nov 6, 2018
#
# Base class for AWS Offers
########################################################################
from __future__ import absolute_import, division, print_function
from builtins import *
from future.standard_library import install_aliases
install_aliases()

import urllib.request, json

class AWSOffer(object):

    def __init__(self, offers, base_url, region):
        self.base_url = base_url
        self.region = region
        self.offers = offers

    def get_offer(self, offer_url):
        '''
        Returns the offer document.
        '''
        with urllib.request.urlopen(self.base_url + offer_url) as url:
            result = json.loads(url.read().decode())
            return result
