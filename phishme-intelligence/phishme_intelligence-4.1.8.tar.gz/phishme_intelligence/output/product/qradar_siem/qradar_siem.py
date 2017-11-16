from __future__ import unicode_literals

"""
Copyright 2013-2016 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

PhishMe QRadar SIEM Module
Author: Josh Larkins
Support: support@phishme.com
ChangesetID: CHANGESETID_VERSION_STRING

"""

import logging
import sys
import requests

from phishme_intelligence.output.base_integration import BaseIntegration

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class QRadarSiem(BaseIntegration):

    def __init__(self, config, product):
        """

        :param config:
        :param product:
        :return:
        """

        super(QRadarSiem, self).__init__(config=config, product=product)

        self.headers = {
            'SEC': self.config.get(self.product, 'api_token'),
            'Version': '5.1',
            'Accept': 'application/json'
        }
        self.logger = logging.getLogger(__name__)

        self.url = 'https://' + self.config.get(self.product, 'host') + '/api/'

    def rest_api(self, endpoint, method='get', data=None):

        headers = self.headers
        url = self.url + endpoint

        if method == 'get':
            response = requests.get(url=url, headers=headers, verify=False)
            return response

        elif method == 'post':
            response = requests.post(url=url, headers=headers, data=data, verify=False)
            return response

    def _populate_reference_set(self, set_name, value):
        """
        Populate QRadar Reference Set.
        """

        logging.info('_populate_reference_set | set_name: {0}, value: {1}'.format(set_name, value))

        # Set up the connection to QRadar SIEM.
        endpoint = 'reference_data/sets/%s' % set_name

        data = {
            'name': set_name,
            'value': value,
            'source': 'PhishMe'
            }

        # Send the data to QRadar SIEM's API.
        response = self.rest_api(endpoint, method='post', data=data)

        # Get response data.
        if response is None:
            logging.info(' Message: Unable to connect to QRadar')
        elif response.status_code != 200:
            logging.info('data: ' + str(data) + ' Message: ' + response.content.decode())

    def _populate_reference_table(self, table_name, outer_key, inner_key, value):
        """
        Populate QRadar Reference Table.
        """

        logging.info('_populate_reference_table | table_name: {0}, outer_key: {1}, inner_key: {2}, value: {3}'.format(
            table_name, outer_key, inner_key, value))

        # Set up the connection to QRadar SIEM.
        endpoint = 'reference_data/tables/%s' % table_name

        data = {
            'name': table_name,
            'outer_key': outer_key,
            'inner_key': inner_key,
            'value': value,
            'source': 'PhishMe'
        }

        # Send the data to QRadar SIEM's API.
        response = self.rest_api(endpoint, method='post', data=data)

        # Get response data.
        if response is None:
            logging.info(' Message: Unable to connect to QRadar')
        elif response.status_code != 200:
            logging.info('data: ' + str(data) + ' Message: ' + response.content.decode())

    def process(self, mrti, threat_id):
        """

        :param mrti:
        :param threat_id:
        :return:
        """

        threathq_url = mrti.threathq_url
        active_threat_report_url = mrti.active_threat_report
        brand = mrti.brand
        first_published = mrti.first_published
        last_published = mrti.last_published

        # Process the md5 hash of all the executables in this threat.
        md5_list = []
        for item in mrti.executable_set:

            # executable_set = intelligence.Malware.ExecutableSet(item)

            malware_type = item.type
            malware_family = item.malware_family
            md5 = item.md5

            # Don't waste time sending the same md5 to QRadar over and over again.
            if md5 not in md5_list:
                md5_list.append(md5)

                ref_set_name = self.config.get(self.product, 'malicious_md5_set')
                ref_table_name = self.config.get(self.product, 'malicious_md5_table')

                self._populate_reference_set(set_name=ref_set_name, value=md5)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5, inner_key='Provider',
                    value='PhishMe Intelligence'
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='First Seen Date',
                    value=first_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name, outer_key=md5,
                    inner_key='Last Seen Date',
                    value=last_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Identifier',
                    value=threat_id
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Threat Details',
                    value=threathq_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Active Threat Report',
                    value=active_threat_report_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Brand',
                    value=brand
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Malware Family',
                    value=malware_family
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=md5,
                    inner_key='Infrastructure Type',
                    value=malware_type
                )

        # Process sha hashes.
        sha_list = []
        for item in mrti.executable_set:

            # executable_set = intelligence.Malware.ExecutableSet(item)

            malware_type = item.type
            malware_family = item.malware_family
            sha = item.sha256

            # Don't waste time sending the same sha to QRadar over and over again.
            if sha not in sha_list:
                sha_list.append(sha)

                ref_set_name = self.config.get(self.product, 'malicious_sha_set')
                ref_table_name = self.config.get(self.product, 'malicious_sha_table')

                self._populate_reference_set(set_name=ref_set_name, value=sha)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Provider',
                    value='PhishMe Intelligence'
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='First Seen Date',
                    value=first_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Last Seen Date',
                    value=last_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Identifier',
                    value=threat_id
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Threat Details',
                    value=threathq_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Active Threat Report',
                    value=active_threat_report_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Brand',
                    value=brand
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Malware Family',
                    value=malware_family
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=sha,
                    inner_key='Infrastructure Type',
                    value=malware_type
                )

        # Process all items from PhishMe's recommended blocklist in this threat.
        for item in mrti.block_set:

            # block_set = intelligence.Malware.BlockSet(item)

            malware_family = item.malware_family
            role = item.role
            watchlist_ioc = item.watchlist_ioc
            impact = item.impact

            if item.block_type == 'Domain Name':
                ref_set_name = self.config.get(self.product, 'watchlist_domain_set')
                ref_table_name = self.config.get(self.product, 'watchlist_domain_table')

                self._populate_reference_set(set_name=ref_set_name, value=watchlist_ioc)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Provider',
                    value='PhishMe Intelligence'
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Impact Rating',
                    value=impact
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='First Seen Date',
                    value=first_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Last Seen Date',
                    value=last_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Identifier',
                    value=threat_id
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Threat Details',
                    value=threathq_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Active Threat Report',
                    value=active_threat_report_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Brand',
                    value=brand
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Malware Family',
                    value=malware_family
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Infrastructure Type',
                    value=role
                )

            elif item.block_type == 'IPv4 Address':
                ref_set_name = self.config.get(self.product, 'watchlist_ipv4_set')
                ref_table_name = self.config.get(self.product, 'watchlist_ipv4_table')

                self._populate_reference_set(set_name=ref_set_name, value=watchlist_ioc)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Provider',
                    value='PhishMe Intelligence'
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Impact Rating',
                    value=impact
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='First Seen Date',
                    value=first_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Last Seen Date',
                    value=last_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Identifier',
                    value=threat_id
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Threat Details',
                    value=threathq_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Active Threat Report',
                    value=active_threat_report_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Brand',
                    value=brand
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Malware Family',
                    value=malware_family)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Infrastructure Type',
                    value=role
                )

            elif item.block_type == 'URL':
                ref_set_name = self.config.get(self.product, 'watchlist_url_set')
                ref_table_name = self.config.get(self.product, 'watchlist_url_table')

                self._populate_reference_set(set_name=ref_set_name, value=watchlist_ioc)
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Provider',
                    value='PhishMe Intelligence'
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Impact Rating',
                    value=impact
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='First Seen Date',
                    value=first_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Last Seen Date',
                    value=last_published
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Identifier',
                    value=threat_id
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Threat Details',
                    value=threathq_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Active Threat Report',
                    value=active_threat_report_url
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Brand',
                    value=brand
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Malware Family',
                    value=malware_family
                )
                self._populate_reference_table(
                    table_name=ref_table_name,
                    outer_key=watchlist_ioc,
                    inner_key='Infrastructure Type',
                    value=role
                )

            else:
                logging.info('Unknown blockType: ' + item.block_type)

    def create_reference_set(self, name, element_type, ttl):
        endpoint = 'reference_data/sets'

        data = {
            'name': name,
            'element_type': element_type,
            'time_to_live': ttl,
        }

        response = self.rest_api(endpoint, method='post', data=data)

        if response.status_code == 201:
            logging.info('ref set:   ' + name + '  status: created!')
        else:
            logging.info('Creating Ref set:   ' + name + '  status: failed!  http: ' + str(response.status_code))
            logging.info(response.text)
            raise RuntimeError('Unable to create reference set, http: ' + str(response.status_code))

    def create_reference_table(self, name, key_type, def_element_type, field_names_types, ttl):

        endpoint = 'reference_data/tables'

        data = {
            'name': name,
            'element_type': def_element_type,
            'outer_key_label': key_type,
            'key_name_types': field_names_types,
            'time_to_live': ttl,
        }

        response = self.rest_api(endpoint, method='post', data=data)

        if response.status_code == 201:
            logging.info('Ref Table: ' + name + '  Status: Created!')
        else:
            logging.info('Creating Ref Table: ' + name + '  Status: Failed!  HTTP: ' + str(response.status_code))
            logging.info(response.text)
            raise RuntimeError('Unable to create reference table: http: ' + str(response.status_code))

    def create_collections(self):
        # field sets for various table types
        # generic_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
        #                        '{"key_name":"Confidence","element_type":"NUM"},' \
        #                        '{"key_name":"First Seen Date","element_type":"DATE"},' \
        #                        '{"key_name":"Last Seen Date","element_type":"DATE"}' \
        #                        ']'

        malware_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
                               '{"key_name":"Impact Rating","element_type":"ALN"},' \
                               '{"key_name":"First Seen Date","element_type":"DATE"},' \
                               '{"key_name":"Last Seen Date","element_type":"DATE"},' \
                               '{"key_name":"Malware Family","element_type":"ALN"},' \
                               '{"key_name":"Identifier","element_type":"NUM"},' \
                               '{"key_name":"Threat Details","element_type":"ALNIC"},' \
                               '{"key_name":"Active Threat Report","element_type":"ALNIC"},' \
                               '{"key_name":"Brand","element_type":"ALN"},' \
                               '{"key_name":"Infrastructure Type","element_type":"ALN"}' \
                               ']'

        # phishing_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
        #                         '{"key_name":"Confidence","element_type":"NUM"},' \
        #                         '{"key_name":"First Seen Date","element_type":"DATE"},' \
        #                         '{"key_name":"Last Seen Date","element_type":"DATE"},' \
        #                         '{"key_name":"Identifier","element_type":"NUM"},' \
        #                         '{"key_name":"Portal URL","element_type":"ALNIC"},' \
        #                         '{"key_name":"Report URL","element_type":"ALNIC"},' \
        #                         '{"key_name":"Brand","element_type":"ALNIC"}' \
        #                         ']'

        # botnet_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
        #                       '{"key_name":"Confidence","element_type":"NUM"},' \
        #                       '{"key_name":"First Seen Date","element_type":"DATE"},' \
        #                       '{"key_name":"Last Seen Date","element_type":"DATE"},' \
        #                       '{"key_name":"Botnet Name","element_type":"ALNIC"}' \
        #                       ']'

        # anon_table_fields = '[{"key_name":"Provider","element_type":"ALN"},' \
        #                     '{"key_name":"Confidence","element_type":"NUM"},' \
        #                     '{"key_name":"First Seen Date","element_type":"DATE"},' \
        #                     '{"key_name":"Last Seen Date","element_type":"DATE"},' \
        #                     '{"key_name":"Anonymizer Name","element_type":"ALNIC"}' \
        #                     ']'

        ttl = self.config.get(self.product, 'ttl')

        # Malware URLs
        self.create_reference_set(
            self.config.get(
                self.product,
                'watchlist_url_set'
            ),
            'ALNIC',
            ttl
        )
        self.create_reference_table(
            self.config.get(self.product, 'watchlist_url_table'),
            'MalwareURL',
            'ALNIC',
            malware_table_fields,
            ttl
        )

        # Malware Hostnames
        self.create_reference_set(
            self.config.get(self.product, 'watchlist_domain_set'),
            'ALN',
            ttl
        )
        self.create_reference_table(
            self.config.get(self.product, 'watchlist_domain_table'),
            'MalwareHost',
            'ALNIC',
            malware_table_fields,
            ttl
        )

        # Malware IPs
        self.create_reference_set(
            self.config.get(self.product, 'watchlist_ipv4_set'),
            'IP',
            ttl
        )
        self.create_reference_table(
            self.config.get(self.product, 'watchlist_ipv4_table'),
            'MalwareIP',
            'IP',
            malware_table_fields,
            ttl
        )

        # Malware Hashes MD5
        self.create_reference_set(
            self.config.get(self.product, 'malicious_md5_set'),
            'ALN',
            ttl
        )
        self.create_reference_table(
            self.config.get(self.product, 'malicious_md5_table'),
            'MalwareHash',
            'ALNIC',
            malware_table_fields,
            ttl
        )

        # Malware Hashes SHA
        self.create_reference_set(
            self.config.get(self.product, 'malicious_sha_set'),
            'ALN',
            ttl
        )
        self.create_reference_table(
            self.config.get(self.product, 'malicious_sha_table'),
            'MalwareHash',
            'ALNIC',
            malware_table_fields,
            ttl
        )

    def verify_collections(self):
        sets_endpoint = 'reference_data/sets'
        tables_endpoint = 'reference_data/tables'
        pm_sets = [
            self.config.get(self.product, 'watchlist_domain_set'),
            self.config.get(self.product, 'watchlist_ipv4_set'),
            self.config.get(self.product, 'watchlist_url_set'),
            self.config.get(self.product, 'malicious_md5_set'),
            self.config.get(self.product, 'malicious_sha_set')
        ]

        pm_tables = [
            self.config.get(self.product, 'watchlist_domain_table'),
            self.config.get(self.product, 'watchlist_ipv4_table'),
            self.config.get(self.product, 'watchlist_url_table'),
            self.config.get(self.product, 'malicious_md5_table'),
            self.config.get(self.product, 'malicious_sha_table')
        ]

        collections_exist = True

        set_response = self.rest_api(sets_endpoint)
        if set_response.status_code != 200:
            logging.info('Unable to retrieve sets')
            logging.info('Request returned status code: ' + set_response.status_code)
            raise RuntimeError('Unable to retrieve reference sets, http: ' + str(set_response.status_code))
        else:
            ref_sets = [ref_set['name'] for ref_set in set_response.json()]
            for ref_set in pm_sets:
                if ref_set not in ref_sets:
                    collections_exist = False
                    logging.info('%s Reference Set does not exist' % ref_set)


        table_response = self.rest_api(tables_endpoint)
        if table_response.status_code != 200:
            logging.info('Unable to retrieve reference tables')
            logging.info('Request returned status code: ' + table_response.status_code)
            raise RuntimeError('Unable to retrieve reference tables, http: ' + str(table_response.status_code))
        else:
            tables = [table['name'] for table in table_response.json()]
            for table in pm_tables:
                if table not in tables:
                    collections_exist = False
                    logging.info('%s Reference Table does not exist' % table)

        if not collections_exist:
            logging.info('Creating Reference Collections')
            try:
                self.create_collections()
            except RuntimeError as exc:
                logging.error('Unable to create reference collections: %s' % exc)
                sys.exit('Unable to create reference collections: %s' % exc)

