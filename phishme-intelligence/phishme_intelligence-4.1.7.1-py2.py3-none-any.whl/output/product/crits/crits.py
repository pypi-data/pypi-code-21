#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

import logging

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pycrits import pycrits, pycritsFetchError
from phishme_intelligence.output.base_integration import BaseIntegration


class Crits(BaseIntegration):
    """
    The PhishMe Intelligence CRITs integration helper class
    """
    def __init__(self, config, product):
        """
        Initialize the PhishMe Intelligence CRITs integration helper class

        :param ConfigParser config: PhishMe Intelligence integration configuration
        :param str product: Name of integration (section name from configuration e.g. integration_mcafee_siem)
        """

        super(Crits, self).__init__(config=config, product=product)

        self.logger = logging.getLogger(__name__)

        username = self.config.get('integration_crits', 'user')
        api_key = self.config.get('integration_crits', 'api_token')
        base_url = self.config.get('integration_crits', 'host_with_protocol')

        self.source = self.config.get('integration_crits', 'source')

        # Specific to Samples in CRITs
        self.upload_type = 'metadata'

        self.crits = pycrits(base_url, username, api_key)
        self.crits.verify = self.config.getboolean('integration_crits', 'ssl_verify')
        self.crits.proxies = self._configure_proxy()

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _configure_proxy(self):
        """
        Configure proxy configuration for usage with python-requests

        :param ConfigParser config: The config.ini data
        :return:  Proxies to provide to python-requests
        :rtype: dict
        """

        if self.config.getboolean('local_proxy', 'use') is True:
            proxy_url_http = self.config.get('local_proxy', 'http')
            proxy_url_https = self.config.get('local_proxy', 'https')

            # BASIC authentication.
            if self.config.getboolean('local_proxy', 'auth_basic_use'):
                proxy_basic_user = self.config.get('local_proxy', 'auth_basic_user')
                proxy_basic_pass = self.config.get('local_proxy', 'auth_basic_pass')

                proxy_basic_auth = proxy_basic_user + ':' + proxy_basic_pass + '@'

                index_http = proxy_url_http.find('//') + 2
                index_https = proxy_url_https.find('//') + 2

                proxy_url_http = proxy_url_http[:index_http] + proxy_basic_auth + proxy_url_http[index_http:]
                proxy_url_https = proxy_url_https[:index_https] + proxy_basic_auth + proxy_url_https[index_https:]

            proxies = {'http': proxy_url_http, 'https': proxy_url_https}

        else:
            proxies = {}

        return proxies

    def process(self, intel, threat_id):
        """
        High-level method for processing PhishMe Intelligence threat ids into CRITs

        :param intel: The data returned from PhishMe Intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :param int threat_id: PhishMe Intelligence Threat ID
        :return: None
        """

        self.logger.info('Add intelligence for threat id ' + str(intel.threat_id) + ' into CRITs...')
        campaign_name = self._add_campaign(intel)

        self._add_samples(intel, campaign_name)
        self._add_indicators(intel, campaign_name)

    @staticmethod
    def _process_response(content):
        """
        Handle JSON status returned from CRITs

        :param str content: JSON returned from CRITs
        :raises: pycritsFetchError: If error code found in CRITs status
        """
        if content['return_code'] is 1:
            raise pycritsFetchError('Error returned from CRITs: ' + str(content['message']))

        # return content['id']

    def _add_campaign(self, intel):
        """
        Create a campaign TLO in CRITs

        :param intel: The data returned from PhishMe Intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :return: campaign_id: Id of the campaign created
        :rtype: int
        :return: threat_name: Name created for the campaign
        :rtype: str
        """

        threat_name = intel.label + ' (' + str(intel.threat_id) + ')'

        if intel.executiveSummary is not None:
            threat_description = intel.executiveSummary

        else:
            threat_description = ''

        try:
            params = {
                'source': self.source,
                'description': threat_description
            }
            content = self.crits.add_campaign(threat_name, params=params)
            campaign_id = self._process_response(content)
            self.logger.debug('Created campaign with name ' + threat_name + '!')
            return campaign_id, threat_name

        except pycritsFetchError as e:
            self.logger.error('Unable to create campaign with name ' + threat_name + '! Error = ' + e.message)

    def _add_samples(self, intel, campaign_name):
        """
        Create sample TLOs in a campaign and and create relationships to the campaign

        :param intel: The data returned from PhishMe Intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :param campaign_name: Name of the associated PhishMe Intelligence campaign
        """

        for executable_set in intel.executable_set:
            if executable_set.malware_family is not None and executable_set.malware_family_description is not None:
                threat_description = executable_set.malware_family + ":" + executable_set.malware_family_description
            else:
                threat_description = ''
            params = {
                'md5': executable_set.md5,
                'sha1': executable_set.sha1 if executable_set.sha1 is not None else '',
                'sha256': executable_set.sha256 if executable_set.sha256 is not None else '',
                'source': self.source,
                'description': threat_description,
                'campaign': campaign_name,
                'confidence': 'high'
            }

            try:
                content = self.crits.add_sample(self.upload_type, self.source, filename=executable_set.file_name, params=params)
                # sample_id = self._process_response(content)
                self.logger.debug('Create sample with file name ' + executable_set.file_name + ' and MD5 '
                                  + executable_set.md5)
            except pycritsFetchError as e:
                self.logger.error('Unable to create sample with file name ' + executable_set.file_name + ' and MD5 '
                                  + executable_set.md5 + '! Error = ' + e.message)

    def _add_indicators(self, intel, campaign_name):
        """
        Create Indicator TLOs in a Campaign and create Relationships to the Campaign

        :param intel: The data returned from PhishMe Intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :param str campaign_name: Name of the associated PhishMe Intelligence Campaign
        """

        for block_set in intel.block_set:
            params = {
                # All PhishMe Intelligence have high confidence due to their human vetted nature
                'indicator_confidence': 'high',
                'indicator_impact': self._get_rating(block_set.impact),
                # Due to the nature of PhishMe Intelligence this is accurate
                'attack_type': 'Phishing',
                'description': block_set.role_description,
                'campaign': campaign_name,
                'confidence': 'high'
            }
            try:
                self._add_indicator_by_type(params, block_set)

            except pycritsFetchError as e:
                self.logger.error('Unable to create indicator with name ' + block_set.watchlist_ioc + '! Error = '
                                  + e.message)

    def _add_indicator_by_type(self, params, block_set):
        """
        Process PhishMe Intelligence Indicator specifically by type of Indicator

        :param dict params: General params to be added to
        :param block_set: blockSet data for indicator to be processed
        :type block_set: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """

        if block_set.block_type == 'Domain Name':
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                indicator_value = block_set.watchlist_ioc[:-1]

            else:
                indicator_value = block_set.watchlist_ioc
            indicator_type = 'Domain'
            params['threat_type'] = 'Malicious Domain'

        elif block_set.block_type == 'IPv4 Address':
            indicator_value = block_set.watchlist_ioc
            indicator_type = block_set.block_type
            params['threat_type'] = 'Malicious IP'

        elif block_set.block_type == 'URL':
            url = block_set.watchlist_ioc.replace('[.]', '.')
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                indicator_value = url[:-1]
            else:
                indicator_value = url
            indicator_type = 'URI'
            params['threat_type'] = 'Malicious URL'

        elif block_set.block_type == 'Email':
            indicator_value = block_set.watchlist_ioc
            indicator_type = 'Email Address'
            params['threat_type'] = 'Bad Actor'

        else:
            raise pycritsFetchError('Unknown indicator type!: ' + str(block_set.block_type))

        # Derive Domain and IP TLOs when applicable
        # if block_set.block_type in ("Domain Name", "IPv4 Address", "URL"):
        #     params['add_domain'] = indicator_value
        #     params['add_relationship'] = True

        results = self.crits.add_indicator(indicator_type, indicator_value, self.source, params)
        self.logger.debug('Created indicator with name ' + block_set.watchlist_ioc)
        self._process_response(results)
        # return indicator_id

    @staticmethod
    def _get_rating(impact):
        """
        Return CRITs rating that will correspond to our Impact scores (which are from the STIX standard)

        :param str impact: Impact value of BlockSet item
        :return: impact rating to set
        :rtype: str
        """

        if impact == 'Minor':
            return 'low'
        elif impact == 'Moderate':
            return 'medium'
        elif impact == 'Major':
            return 'high'

        return 'benign'
