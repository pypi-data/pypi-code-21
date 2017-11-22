# Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import datetime

from threatconnect import ResourceType


class PhishMeIntelligenceProcessor(object):
    """
    Helper class for storing PhishMe Intelligence before sending to ThreatConnect. It builds out the Batch API dictionary
    for those ThreatConnect types that support it and helps with direct creation of those ThreatConnect types that don't
    """

    def __init__(self, owner, logger, tcex, tc):
        """
        Initialize the PhishMeIntelligenceProcessor object

        :param str owner:  ThreatConnect owner/group for PhishMe Intelligence
        :param logger: The logging object to use for logging
        :type logger: :class:`logging.logger`
        :param tcex: The TcEx object used for interaction with the Batch API
        :type tcex: :class:`tcex.TcEx`
        :param tc: The ThreatConnect object used for communication with ThreatConnect
        :type tc: :class:`threatconnect.ThreatConnect`
        """

        self.owner = owner
        self.indicator_list = []
        self.current_indicator = {}
        self.current_group = None
        self.current_document = None
        self.current_group_id = None
        self.current_document_id = None
        self.jobs = tcex.jobs
        self.logger = logger
        self.threatconnect = tc

        self._initialize_indicator()
        self._initialize_group()

    def add_ip_indicator(self, ip):
        """
        Create ThreatConnect indicator of type Address (and group association) for Batch API list

        :param str ip: The Ip Address to add
        """
        self.indicator_list.append((ip, "Address"))
        self.current_indicator["summary"] = ip
        self.current_indicator["type"] = "Address"
        self._add_indicator_group_association(self.current_indicator)

    def add_email_indicator(self, email):
        """
        Create ThreatConnect indicator of type EmailAddress (and group association) for Batch API list

        :param str email: The email address to add
        """
        self.indicator_list.append((email, "EmailAddress"))
        # ThreatConnect Batch API does not like uppercase letters in email addresses
        self.current_indicator["summary"] = email.lower()
        self.current_indicator["type"] = "EmailAddress"
        self._add_indicator_group_association(self.current_indicator)

    def add_host_indicator(self, host):
        """
        Create ThreatConnect indicator of type Host (and group association) for Batch API list

        :param str host: The hostname to add
        """
        self.indicator_list.append((host, "Host"))
        self.current_indicator["summary"] = host.lower()
        self.current_indicator["type"] = "Host"
        self._add_indicator_group_association(self.current_indicator)

    def add_url_indicator(self, url):
        """
        Create ThreatConnect indicator of type URL (and group association) for Batch API list

        :param str url: The URL to add
        """
        self.indicator_list.append((url, "URL"))
        self.current_indicator["summary"] = url
        self.current_indicator["type"] = "Url"
        self._add_indicator_group_association(self.current_indicator)

    def add_file_indicator(self, md5, sha1=None, sha256=None):
        """
        Create ThreatConnect indicator of type File (and group association) for Batch API list

        :param str md5: MD5 of file indicator
        :param sha1: SHA-1 of file indicator
        :param sha256: SHA-256 of file indicator
        """
        self.indicator_list.append((md5, "File"))
        self.current_indicator["type"] = "File"
        self.current_indicator["summary"] = md5
        if sha1 is not None:
            self.current_indicator["summary"] += " : " + sha1
        if sha256 is not None:
            self.current_indicator["summary"] += " : " + sha256
        self._add_indicator_group_association(self.current_indicator)

        # All file indicators will have a rating of 3 (Medium)
        self.add_indicator_rating(3)

    def _add_indicator_group_association(self, indicator):
        """
        Sets up group association for indicator being processed

        :param dict indicator: indicator to add association to
        """
        indicator["associatedGroup"] = []
        if self.current_group_id is not None:
            indicator["associatedGroup"].append(str(self.current_group_id))
        if self.current_document_id is not None:
            indicator["associatedGroup"].append(str(self.current_document_id))

    def add_indicator_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute for current indicator being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        if "attribute" not in self.current_indicator:
            self.current_indicator["attribute"] = []

        new_indicator_attribute = {"type": attribute_type,
                                   "value": value}
        self.current_indicator["attribute"].append(new_indicator_attribute)

    def add_group_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute to current group being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        self.current_group.add_attribute(attribute_type, value)

    def add_indicator_tag(self, name):
        """
        add tag to current indicator being processed

        :param str name: tag to add
        """
        if "tag" not in self.current_indicator:
            self.current_indicator["tag"] = []

        new_tag = {"name": name}
        self.current_indicator["tag"].append(new_tag)

    def add_group_tag(self, name):
        """
        add tag to current group being processed

        :param str name: tag to add
        """
        self.current_group.add_tag(name)

    def add_indicator_rating(self, rating):
        """
        add rating value to current indicator being processed

        :param str name: tag to add
        """
        self.current_indicator["rating"] = rating

    def add_group(self, group_type, group_name, published_date):
        """
        Create group stub (this is not the commit to ThreatConnect)

        :param str group_type:  Type of group
        :param str group_name:  Name of group
        :param int published_date: published date (epoch timestamp)
        """
        if group_type == "Threat":
            self.current_group = self.threatconnect.threats().add(group_name, self.owner)
        else:
            self.current_group = self.threatconnect.incidents().add(group_name, self.owner)
            # Set Incident event date to firstPublished data of Threat ID
            self.current_group.set_event_date(datetime.datetime.fromtimestamp(published_date/1000).strftime('%Y-%m-%dT%X'))

    def add_document(self, document_name, file_name, active_threat_report, group_type):
        """
        Create document stub (this is not the commit to ThreatConnect)

        :param str document_name: Name to give Document type
        :param str file_name:  Name of document
        :param str active_threat_report:
        :param str group_type: Type of group this document will be associated wit
        """
        self.current_document = self.threatconnect.documents().add(document_name, self.owner)
        self.current_document.set_file_name(file_name)
        self.current_document.upload(active_threat_report)
        if group_type == "Threat":
            self.current_document.associate_group(ResourceType.THREATS, self.current_group_id)
        else:
            self.current_document.associate_group(ResourceType.INCIDENTS, self.current_group_id)

    def add_document_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute to current document being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        self.current_document.add_attribute(attribute_type, value)

    def add_document_tag(self, tag):
        """
        add tag to current document being processed

        :param str name: tag to add
        """

        self.current_document.add_tag(tag)

    def group_ready(self):
        """
        Call this method to indicate that group is ready to be "processed" (sent to ThreatConnect instance)

        :return: None
        """
        self._process_group(self.current_group)

    def document_ready(self):
        """
        Call this method to indicate that document is ready to be "processed" (sent to ThreatConnect instance)

        :return: None
        """
        self._process_document(self.current_document)

    def indicator_ready(self, source, threat_id):
        """
        Call this method to indicate that indicator is ready to be processed. This method also handles the situation
        where duplicate indicators exist in the current batch.

        :param str source: source of intelligence (always PhishMe Intelligence at this point)
        :param int threat_id:  Current Phishme Intelligence threat id being processed
        :return: None
        """
        # If indicator value already exists in list return the matched indicator dict
        matching_indicator = self._check_for_duplicate_indicator(self.current_indicator)
        if matching_indicator is not None:
            # Check if matched indicator contains attribute with Threat ID..
            for attribute in matching_indicator["attribute"]:
                # If it does then we don't need to add anything
                if attribute["value"] == source + ' via Threat ID ' + str(threat_id):
                    self.logger.debug("Indicator " + matching_indicator["summary"].split(" :")[0]
                                      + " already has Threat ID " + str(threat_id) +
                                      " information so just add back to list...")
                    self._process_indicator(matching_indicator)
                    return
            # If it doesn't add tags and attributes to existing indicator
            for attribute in self.current_indicator["attribute"]:
                matching_indicator["attribute"].append(attribute)
            for tag in self.current_indicator["tag"]:
                if tag["name"] == "Threat ID " + str(threat_id):
                    matching_indicator["tag"].append(tag)
            # Check rating; if it's higher is duplicate indicator use that otherwise use the other
            if matching_indicator['rating'] < self.current_indicator['rating']:
                matching_indicator['rating'] = self.current_indicator['rating']
            self.logger.debug("Indicator " + matching_indicator["summary"].split(" :")[0] +
                              " did not have Threat ID " + str(threat_id) +
                              " information so added tags and attributes...")
            self._process_indicator(matching_indicator)
        else:
            self._process_indicator(self.current_indicator)

    def _process_group(self, group):
        """
        Commit group to ThreatConnect and prepare for next group

        :param group: ThreatConnect group object
        :type group: :class:`threatconnect-python.threatconnect.GroupObject`
        """
        try:
            group.commit()
            self.logger.info("Group " + group.name + " Successfully Committed to ThreatConnect!")
            self.logger.info("--------------------------------------------------")
            self.current_group_id = group.id
        except RuntimeError as e:
            self.current_group_id = None
            self.logger.error("Error committing Group " + group.name + " to ThreatConnect: " + str(e))
        finally:
            self._initialize_group()

    def _process_document(self, document):
        """
        Commit document to ThreatConnect and prepare for next group

        :param document: ThreatConnect document object
        :type doucment: :class:`threatconnect-python.threatconnect.DocumentObject`
        """

        try:
            document.commit()
            self.logger.info("Document " + document.name + " Successfully Committed to ThreatConnect!")
            self.logger.info("--------------------------------------------------")
            self.current_document_id = document.id
        except RuntimeError as e:
            self.current_document_id = None
            self.logger.error("Error committing Document " + document.name + " to ThreatConnect: " + str(e))
        finally:
            self._initialize_document()

    def _process_indicator(self, indicator):
        """
        Add ThreatConnect indicator to batch processing queue

        :param dict indicator: ThreatConnect Indicator is is ready for batch processing
        """
        self.jobs.indicator(indicator)
        self._initialize_indicator()

    def _check_for_duplicate_indicator(self, indicator):
        """
        Helper method to search for a duplicate indicator; if it exists return it and remove it from current list

        :param indicator: indicator that we are looking for a duplicate of
        :return: Duplicate indicator (if one exists)
        :rtype: dict or None
        """
        indicator_to_match = indicator["summary"].split(" :")[0]
        try:
            existing_indicators = self.jobs.unprocessed_indicators
            # We have found a match
            matched_indicator = next(indicator for indicator in existing_indicators if
                                     indicator["summary"].split(" :")[0] == indicator_to_match)
            # Remove match from existing list and return
            existing_indicators[:] = [indicator for indicator in existing_indicators if
                                      indicator["summary"].split(" :")[0] != indicator_to_match]
            self.jobs.unprocessed_indicators = existing_indicators
            # Return matched indicator
            self.logger.debug("Indicator " + indicator["summary"].split(" :")[0] + " Is already in processing list...")
            return matched_indicator
        except StopIteration:
            # No existing indicator, so
            return None

    def commit(self):
        """
        Kick off batch processing of indicators to push into ThreatConnect

        :return: None
        """
        try:
            self.jobs.process(self.owner, indicator_batch=True)
        except Exception as e:
            self.logger.error("Failure Batch Processing Indicators: " + str(e))

    def _initialize_indicator(self):
        """
        Preparation for processing new Indicator to add to ThreatConnect batch processing queue
        """
        self.current_indicator = {"confidence": 100}  # Always high confidence due to analyst vetting

    def _initialize_group(self):
        """
        Preparation for processing new group to push into ThreatConnect
        """
        self.current_group = None

    def _initialize_document(self):
        """
        Prepartion for processing new document to push into ThreatConnect
        """
        self.current_document = None
