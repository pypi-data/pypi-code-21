#
# Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import requests
from tcex import TcEx
from threatconnect import ThreatConnect
from six.moves import configparser
from .pm_intel_processor import PhishMeIntelligenceProcessor

from phishme_intelligence.output.base_integration import BaseIntegration


class PmThreatConnect(BaseIntegration):
    def __init__(self, config, product):
        """
        Initialize PmThreatConnect object

        :param config: Integration configuration values
        :type config: :class:`configparser.ConfigParser`
        :param logger: Logging mechanism for the integration
        :type logger: :class:`logging.Logger`
        """

        super(PmThreatConnect, self).__init__(config=config, product=product)

        # Set up ThreatConnect
        api_default_org = config.get('integration_threatconnect', 'api_default_org')
        api_base_url = config.get('integration_threatconnect', 'api_base_url')
        threatconnect_logging = config.get('integration_threatconnect', 'threatconnect_log_file')
        threatconnect_logging_level = config.get('integration_threatconnect', 'threatconnect_log_level')

        try:
            tc_token = config.get('integration_threatconnect', 'tc_token')
            tc_token_expires = config.get('integration_threatconnect', 'tc_token_expires')
            self.threatconnect = ThreatConnect(api_token=tc_token, api_token_expires=tc_token_expires,
                                                 api_org=api_default_org, api_url=api_base_url)  # type: PmThreatConnect
        except configparser.NoOptionError: #If tc_token does not exist we are using Access ID/Secret Key based validation
            api_access_id = config.get('integration_threatconnect', 'api_access_id')
            api_secret_key = config.get('integration_threatconnect', 'api_secret_key')
            self.threatconnect = ThreatConnect(api_aid=api_access_id, api_sec=api_secret_key, api_org=api_default_org,
                                                 api_url=api_base_url)  # type: PmThreatConnect


        self.phishme_intel_auth = (config.get('pm_api', 'user'), config.get('pm_api', 'pass'))
        self.phishme_intel_proxy = self._set_phishme_intel_proxy(config)
        self.owner = api_default_org
        self.tcex = TcEx()
        self.pm_intel_processor = PhishMeIntelligenceProcessor(self.owner, self.logger, self.tcex, self.threatconnect)
        self.source = 'PhishMe Intelligence'
        self.max_threat_label_length = 90
        self.tc_group = config.get('integration_threatconnect', 'threatconnect_group')

        # Set up ThreatConnect logging
        self.threatconnect.set_tcl_file(threatconnect_logging, threatconnect_logging_level)

        self._set_threatconnect_proxy(config)

    def _set_threatconnect_proxy(self, config):
        """
        Set up ThreatConnect proxy (if relevant)

        :param config: :class:`configparser.ConfigParser`
        """
        if config.getboolean('integration_threatconnect', 'use_local_proxy'):
            if len(config.get('local_proxy', 'http').split('://')) > 1:
                rest_of_url = config.get('local_proxy', 'http').split('://')[1]
            else:
                rest_of_url = config.get('local_proxy', 'http')
            proxy_url, proxy_port = rest_of_url.split(':')
            if config.getboolean('local_proxy', 'auth_basic_use'):
                auth_basic_user = config.get('local_proxy', 'auth_basic_user')
                auth_basic_pass = config.get('local_proxy', 'auth_basic_pass')
                self.threatconnect.set_proxies(proxy_url, proxy_port, auth_basic_user, auth_basic_pass)
            else:
                self.threatconnect.set_proxies(proxy_url, proxy_port)

    def _set_phishme_intel_proxy(self, config):
        """
        Setting PhishMe intel proxy values (that are used for getting the HTML Active Threat Report)

        :param config: The config values from the config.ini file
        :type: :class:`configparser.ConfigParser`
        :return: proxies dictionary (can be empty)
        :rtype: dict
        """
        # Configure proxy support if required.
        if config.getboolean('local_proxy', 'use') is True:
            proxy_url_http = config.get('local_proxy', 'http')
            proxy_url_https = config.get('local_proxy', 'https')

            # BASIC authentication.
            if config.getboolean('local_proxy', 'auth_basic_use'):
                proxy_basic_user = config.get('local_proxy', 'auth_basic_user')
                proxy_basic_pass = config.get('local_proxy', 'auth_basic_pass')

                proxy_basic_auth = proxy_basic_user + ':' + proxy_basic_pass + '@'

                index_http = proxy_url_http.find('//') + 2
                index_https = proxy_url_https.find('//') + 2

                proxy_url_http = proxy_url_http[:index_http] + proxy_basic_auth + proxy_url_http[index_http:]
                proxy_url_https = proxy_url_https[:index_https] + proxy_basic_auth + proxy_url_https[index_https:]

            proxies = {'http': proxy_url_http, 'https': proxy_url_https}

        else:
            proxies = {}

        return proxies

    def process(self, mrti, threat_id):
        """
        Main method called to begin processing of PhishMe Intelligence into ThreatConnect

        :param mrti: PhishMe Intelligence threat to process
        :type mrti: :class:`phishme_intelligence.core.intelligence.Malware`
        :param int threat_id: Threat ID of PhishMe Intelligence threat being processed
        :return: None
        """
        self._process_group(mrti)
        self._process_document(mrti)
        self._process_blockset(mrti)
        self._process_executableset(mrti)

    def post_run(self, config_file_location):
        """
        Method called after sync of Phishme Intelligence. Kicks off batch processing of indicators into ThreatConnect
        and saves position value

        :param str config_file_location: location of config.ini file (we don't use this value)
        :return:  None
        """
        self._commit_threat_intelligence()
        self.tcex.results_tc('param.intel_position', self.config.get('pm_api', 'position'))


    def _commit_threat_intelligence(self):
        """
        Helper method for logging and beginning batch procesing of indicators into ThreatConnect
        """
        # Batch process indicators
        self.logger.info("Begin Batch Processing of Indicators and their Group Associations to ThreatConnect...")
        self.pm_intel_processor.commit()
        self.logger.info("Indicators Successfully Processed!")

    def _process_document(self, intel):
        """
        Process Active Threat Report as ThreatConnect Document

        :param intel: PhishMe Intelligence campaign to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        document_name = "Active Threat Report for Threat ID " + str(intel.threat_id)
        file_name = "PhishMe_Intelligence_ATR_" + str(intel.threat_id) + ".html"

        if not intel.json['hasReport']:
            self.logger.info(
                "Threat with Threat ID " + str(intel.threat_id) + " does not have Active Threat Report so not "
                                                                  "creating document...")
            return
        else:
            try:
                report = requests.get(intel.active_threat_report_api, auth=self.phishme_intel_auth,
                                      proxies=self.phishme_intel_proxy)
            except Exception as e:
                self.logger.error("Unable to download Active Threat Report " + intel.active_threat_report +
                                   "! Skipping creation of Document...")
                return

            self.pm_intel_processor.add_document(document_name=document_name, file_name=file_name,
                                                 active_threat_report = report.content, group_type=self.tc_group)
            self.pm_intel_processor.add_document_attribute('Source', self.source + ' via Threat ID '
                                                           + str(intel.threat_id))
            self.pm_intel_processor.add_document_tag(self.source)

            self.pm_intel_processor.document_ready()


    def _process_blockset(self, intel):
        """
        Processing PhishMe Intelligence Block Set values related to current Threat being processed. These are network
        watch list items related to a particular threat ID

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        for block_set in intel.block_set:
            self._set_blockset_indicator_value(block_set)
            self._set_blockset_attributes(intel, block_set)
            self._set_standard_indicator_attributes(intel)

            self.pm_intel_processor.add_indicator_rating(self._get_rating(block_set.impact))

            self.pm_intel_processor.indicator_ready(self.source, intel.threat_id)
            self.logger.debug("Indicator " + block_set.watchlist_ioc + " Added to Processing List!")

    def _process_executableset(self, intel):
        """
        Processing ExecutableSet values of current campaign being processed. These values are hashes of files
        observed on endpoints as a result of interacting with a phishing email

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        for executable_set in intel.executable_set:
            self.pm_intel_processor.add_file_indicator(executable_set.md5, executable_set.sha1, executable_set.sha256)
            self._set_executableset_attributes(executable_set, intel)
            self._set_standard_indicator_attributes(intel)

            self.pm_intel_processor.indicator_ready(self.source, intel.threat_id)
            self.logger.debug("Indicator " + executable_set.md5 + " Added to Processing List!")

    def _set_executableset_attributes(self, executable_set, intel):
        """
        Set attributes specific to Executable Set PhishMe Intelligence value

        :param executable_set: The Executable Set value being processed
        :type executable_set: :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet`
        :param intel: Campaign intelligence data (full set)
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        self.pm_intel_processor.add_indicator_attribute("Description", executable_set.malware_family_description +
                                              '( Threat ID ' + str(intel.threat_id) + ')')
        if executable_set.subtype is None:
            self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", executable_set.type +
                                                            '( Threat ID ' + str(intel.threat_id) + ')')
        else:
            self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", executable_set.type +
                                                            ': ' + executable_set.subtype + '( Threat ID ' +
                                                            str(intel.threat_id) + ')')

    def _process_group(self, intel):
        """
        Generate Group that will correspond to campaign being processed from PhishMe Intelligence

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """

        # Need to make sure Threat name is less than 100 characters...
        if len(intel.label) > self.max_threat_label_length:
            self.logger.info("Threat label longer than 90 characters so removing malware families from Threat name...")
            group_label_first_part = intel.label.split(" - ")[0]
            group_name = group_label_first_part + " - Multiple malware families (" + str(intel.threat_id) + ")"
        else:
            group_name = intel.label + " (" + str(intel.threat_id) + ")"

        self.pm_intel_processor.add_group(group_type=self.tc_group, group_name=group_name,
                                          published_date=intel.first_published)

        if intel.executiveSummary is not None:
            self.pm_intel_processor.add_group_attribute('Description', self.tcex.s(intel.executiveSummary,
                                                                                   errors='ignore'))

        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context',
                                                    'Active Threat Report URL: ' + intel.active_threat_report)
        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context',
                                                    'Threat Detail Page URL: ' + intel.threathq_url)

        self.pm_intel_processor.add_group_attribute('Source', self.source + ' via Threat ID ' + str(intel.threat_id))
        self.pm_intel_processor.add_group_tag(self.source)

        self.pm_intel_processor.group_ready()

    def _get_rating(self, impact):
        """
        Return ThreatConnect rating that will correspond to our Impact scores (which are from the STIX standard)

        :param str impact: Impact value of BlockSet item
        :return: impact rating to set
        :rtype: int
        """
        if impact == "Minor":
            return 1
        elif impact == "Moderate":
            return 3
        elif impact == "Major":
            return 5

        return 0

    def _set_blockset_indicator_value(self, block_set):
        """
        Set Indicator value based on type of BlockSet indicator

        :param block_set: BlockSet value
        :rtype block_set: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """
        if block_set.block_type == "Domain Name":
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                self.pm_intel_processor.add_host_indicator(block_set.watchlist_ioc[:-1])
            else:
                self.pm_intel_processor.add_host_indicator(block_set.watchlist_ioc)
        elif block_set.block_type == "IPv4 Address":
            self.pm_intel_processor.add_ip_indicator(block_set.watchlist_ioc)
        elif block_set.block_type == "URL":
            url = block_set.watchlist_ioc.replace("[.]", ".")
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                self.pm_intel_processor.add_url_indicator(self.tcex.s(url[:-1], errors='ignore'))
            else:
                self.pm_intel_processor.add_url_indicator(self.tcex.s(url, errors='ignore'))

        elif block_set.block_type == "Email":
            self.pm_intel_processor.add_email_indicator(block_set.watchlist_ioc)

    def _set_standard_indicator_attributes(self, intel):
        """
        Set attributes to indicators that are shared between Executable Set and Block Set types

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                              'Active Threat Report URL: ' + intel.active_threat_report)
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                              'Threat Detail Page URL: ' + intel.threathq_url)
        self.pm_intel_processor.add_indicator_attribute('Source', self.source + ' via Threat ID ' + str(intel.threat_id))
        self.pm_intel_processor.add_indicator_tag(self.source)

    def _set_blockset_attributes(self, intel, block_set):
        """
        Set attributes that are specific to Block Set indicators in ThreatConnect

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :param block_set: specific BlockSet value to process
        :type block_set: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """
        if block_set.malware_family_description is not None and block_set.malware_family is not None:
            self.pm_intel_processor.add_indicator_attribute("Description",
                                                            block_set.malware_family + ": " +
                                                            block_set.malware_family_description + ' (Threat ID ' +
                                                            str(intel.threat_id) + ')')

        self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", block_set.role + ': '
                                                        + block_set.role_description + ' (Threat ID ' +
                                                        str(intel.threat_id) + ')')





