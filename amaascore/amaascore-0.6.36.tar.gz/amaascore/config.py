# POTENTIALLY SUPPORT MULTIPLE ENVIRONMENTS
from __future__ import absolute_import, division, print_function, unicode_literals
from collections import namedtuple

ENVIRONMENT = 'production'
ENDPOINTS = {
    'asset_managers': 'assetmanager',
    'assets': 'asset',
    'books': 'book',
    'corporate_actions': 'corporateaction',
    'fundamentals': 'fundamental',
    'market_data': 'marketdata',
    'monitor': 'monitor',
    'parties': 'party',
    'transactions': 'transaction'
}

EnvironmentConfig = namedtuple('EnvironmentConfig',
                               'environment base_url api_version cognito_region cognito_pool cognito_client_id')
CONFIGURATIONS = {'production': EnvironmentConfig(environment='production',
                                                  base_url='https://api.amaas.com',
                                                  api_version='sg1.0',
                                                  cognito_region='ap-southeast-1',
                                                  cognito_pool='ap-southeast-1_0LilJdUR3',
                                                  cognito_client_id='7b7kt883veb7rr2toolj1ukp6j'),
                  'staging': EnvironmentConfig(environment='staging',
                                               base_url='https://api-staging.amaas.com',
                                               api_version='v1.0',
                                               cognito_region='ap-southeast-1',
                                               cognito_pool='ap-southeast-1_De6j7TWIB',
                                               cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk'),
                  'dev': EnvironmentConfig(environment='dev',
                                           base_url='https://api-dev.amaas.com',
                                           api_version='v1.0',
                                           cognito_region='ap-southeast-1',
                                           cognito_pool='ap-southeast-1_De6j7TWIB',
                                           cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk'),
                  'local': EnvironmentConfig(environment='local',
                                             base_url='http://localhost:8000',
                                             api_version='',
                                             cognito_region='ap-southeast-1',
                                             cognito_pool='ap-southeast-1_De6j7TWIB',
                                             cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk')}

