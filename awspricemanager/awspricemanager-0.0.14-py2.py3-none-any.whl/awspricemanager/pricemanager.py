############################################################
# Author     : Adamson dela Cruz
# Date       : Nov 6, 2017
#
#
############################################################
from __future__ import absolute_import, division, print_function
from future.standard_library import install_aliases
from builtins import *
install_aliases()

import boto3, os
import urllib.request, json

from colorama import Fore, Back, Style
from offers.offer import *
from offers.ec2 import *
from awspricemanager.constants import *

base_url = 'https://pricing.us-east-1.amazonaws.com'
price_index = '{}/offers/v1.0/aws/index.json'.format(base_url)
region = os.getenv(REGION)


class PriceManager():
    '''
    Class that handles pricing information on different AWS services
    '''

    def __init__(self):
        '''
        Loads the offer index. Contains the starting point of offers for different AWS services
        '''
        with urllib.request.urlopen(price_index) as url:
            data = json.loads(url.read().decode())
            self.offers = data[OFFERS]


    def get_offer_url(self, offer):
        '''
        From the region index, this method will return the correct price index for the current region
        Example:
            "ap-southeast-2" : {
              "regionCode" : "ap-southeast-2",
              "currentVersionUrl" : "/offers/v1.0/aws/AmazonEC2/20171026015458/ap-southeast-2/index.json"
            }
        '''

        offer_url = None
        with urllib.request.urlopen(base_url + self.offers[offer][CURRENT_REGION_INDEX_URL]) as url:
            self.region_data = json.loads(url.read().decode())
            #self.offers = data['offers']
            if self.region_data != None:
                offer_url = self.region_data[REGIONS][region]

        return offer_url

    def get_ec2_price_by_instance(self, instance_type, os):
        '''
        Returns the price of an EC2 instance using the instance type and operating system
        '''
        ec2_offer = EC2Offer(self.offers, base_url, region)
        offer_url = self.get_offer_url(EC2)
        ec2_offer.skus = ec2_offer.get_offer(offer_url[CURRENT_VERSION_URL])

        return ec2_offer.get_ec2_price_by_instance(instance_type, os)
