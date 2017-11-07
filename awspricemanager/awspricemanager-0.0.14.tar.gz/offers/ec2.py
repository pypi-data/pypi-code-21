############################################################
# Author     : Adamson dela Cruz
# Date       : Nov 6, 2017
#
# Handles request for pricing information on EC2 instances
############################################################
from __future__ import absolute_import, division, print_function
from builtins import *
import json

from offers.offer import AWSOffer
from colorama import Fore, Back, Style
from awspricemanager.constants import *
import time

class EC2Offer(AWSOffer):
    '''
    Handles request for pricing information on EC2 instances.
    '''

    def __init__(self, offers, base_url, region):
        super().__init__(offers, base_url, region)
        self.skus = None
        self.terms = None
        self.selected_skus = []

    def get_offer_terms(self, pricedb, prod):
        '''
        Fetches the pricing information using the price database and the current sku/product
        '''

        sku = prod[PRODUCT][SKU]
        ondemand = None
        reserved = None
        price = None
        prod[ONDEMAND_PRICE] = None
        prod[RESERVED_PRICE] = None

        if sku in pricedb[TERMS][ONDEMAND]:
            ondemand = pricedb[TERMS][ONDEMAND][sku]

        if sku in pricedb[TERMS][RESERVED]:
            reserved = pricedb[TERMS][RESERVED][sku]


        def get_price(term):
            '''
            Fetches the price dimension
            '''
            if term != None:
                keys = list(term.keys())
                for key in keys:
                    priceList = list(term[key][PRICE_DIMENSIONS].keys())
                    for pk in priceList:
                        price = term[key][PRICE_DIMENSIONS][pk]
                        return price

        # On Demand Pricing
        if ondemand != None:
            prod[ONDEMAND_PRICE] = get_price(ondemand)

        # Reserved Pricing
        if reserved != None:
            prod[RESERVED_PRICE] = get_price(reserved)


    def get_offer(self, offer_url):
        '''
        Using the correct offer url (accounting for region), it fetches the product Database
        with the correct pricing and other information
        '''
        pricedb = super().get_offer(offer_url)
        self.skus = {}
        self.terms = {}

        # iterate the product/sku and fetch the correct offer terms (which actually contains the price)
        for product in pricedb[PRODUCTS]:
            prod = {}
            prod[PRODUCT] = pricedb[PRODUCTS][product]
            self.get_offer_terms(pricedb, prod)
            self.skus[product] = prod

        return self.skus

    def get_ec2_price_by_instance(self, instance_type, os='linux'):
        '''
        Using the instance type and operating system, it returns
        pricing information. Assumption is that product database (skus) has been populated.
        '''
        if self.skus == None:
            print(Fore.RED + Style.BRIGHT + 'WARNING:'
            , Fore.YELLOW + Style.NORMAL, 'Product Database not initialized...', Style.RESET_ALL )
            return None

        sku_instance_type = None
        selected_skus = []

        for key in self.skus:
            sku = self.skus[key]
            props = sku[PRODUCT][ATTRIBUTES]
            if props.get(INSTANCE_TYPE) != None:
                sku_instance_type = props[INSTANCE_TYPE]
            else:
                sku_instance_type = ''

            # If we have a match, we collect the sku to return
            if sku_instance_type == instance_type and props[OPERATING_SYSTEM].lower() == os:
                selected_skus.append(sku)

        return selected_skus

        # for sku in self.selected_skus:
        #     props = sku['product']['attributes']
        #     ondemand = sku['ondemand_price']
        #     print(
        #     Fore.YELLOW + Style.BRIGHT
        #     , props['operatingSystem']
        #     , Style.NORMAL + Fore.WHITE
        #     , props['vcpu'], 'CPU'
        #     , props['clockSpeed']
        #     , Fore.GREEN, props['memory']
        #     , props['preInstalledSw']
        #     , Fore.MAGENTA, ondemand['pricePerUnit']['USD']
        #     , ondemand['unit']
        #     , Fore.WHITE, ondemand['description']
        #     , Style.RESET_ALL)
        # end = time.time()
        # print('End:', start)
        # print(Fore.WHITE + Style.BRIGHT ,'Total Time:', Style.NORMAL,end - start, 'seconds', Style.RESET_ALL)
