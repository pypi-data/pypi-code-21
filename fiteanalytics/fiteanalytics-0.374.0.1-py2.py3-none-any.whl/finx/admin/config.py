# *****************************************************
# * FinX is a set of tools for Financial Data Science *
# * Copyright (C) 2017  Fite Analytics LLC            *
# *****************************************************
#
# This file is part of FinX.
#
#     FinX is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FinX is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FinX.  If not, see <http://www.gnu.org/licenses/>.
import os
import pandas as pd
import yaml
import requests
import json

class Config():

    def __init__(self):
        finx_conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finx.conf')
        with open(finx_conf_path,'r') as yml:
            self.settings = yaml.load(yml)
            self.finx_conf_path = finx_conf_path

    def install_finx(self, finx_key, test=False):
        if test:
            url = self.settings['endpoints']['test_install']
        else:
            url = self.settings['endpoints']['install']
        # try:
        payload = {'finx_key' : finx_key}
        response = requests.get(url, params=payload)
        try:
            json_dict = json.loads(response.text)
        except:
            print('Invalid Key Input')
            return None
        with open(self.finx_conf_path,'r') as yml:
            settings = yaml.load(yml)
            settings['identity']['finx_key']= finx_key
            settings['identity']['fred_client_secret']= json_dict['fred_client_secret']
            settings['identity']['sf1_client_secret']= json_dict['sf1_client_secret']
            settings['endpoints']['content']['fred'] = json_dict['content_endpoint']['fred']
            settings['endpoints']['content']['fite'] = json_dict['content_endpoint']['fite']
            settings['endpoints']['hydrosledger'] = json_dict['hydrosledger_endpoint']
            settings['endpoints']['content']['financials_features'] = json_dict['financials_features']
            settings['endpoints']['content']['stock'] = json_dict['stock']
        with open(self.finx_conf_path, 'w') as yml:
            yaml.dump(settings,yml)
        print('Installation Complete!')
        return None

    def save_endpoints(self,
        content_endpoints,
        calculation_endpoints,
        identity_endpoints,
        hydrosledger_endpoints):
        with open(self.finx_conf_path,'r') as yml:
            settings = yaml.load(yml)
            settings['endpoints']['content']=content_endpoints
            settings['endpoints']['calculation']=calculation_endpoints
            settings['endpoints']['identity']=identity_endpoints
            settings['endpoints']['hydrosledger']=hydrosledger_endpoints
        with open(self.finx_conf_path,'w') as yml:
            yaml.dump(settings,yml)
        return None

    def print_endpoints(self):
        return (pd.DataFrame(self.settings['endpoints']).transpose())

    def print_identity(self):
        return (pd.DataFrame(self.settings['identity'],index=[0]))

def help():
    print('-------------------------------------')
    print('fiteanalytics.finx.admin help')
    print('-------------------------------------')
    print('Functions in this package are used by other FinX functions.')
    print('They are not intended for use by other programs.')
    print('-------------------------------------')
    return None
