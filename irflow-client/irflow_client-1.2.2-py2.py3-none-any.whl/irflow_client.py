"""Python SDK and Wrapper for the IR-Flow REST API

"""
from json import dumps
import pprint
import logging
import requests
import sys
import tempfile

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

# The next to lines suppress the SSL Warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class IRFlowClient(object):
    """Python SDK for the IR-Flow REST API.

    """
    end_points = {
        'create_alert': 'api/v1/alerts',
        'get_alert': 'api/v1/alerts',
        'put_alert_close': 'api/v1/alerts/close',
        'put_incident_on_alert': 'api/v1/alerts/%s/incident/%s',
        'get_attachment': 'api/v1/attachments/%s/download',
        'put_attachment': 'api/v1/%s/%s/attachments',
        'get_fact_group': 'api/v1/fact_groups',
        'put_fact_group': 'api/v1/fact_groups',
        'create_incident': 'api/v1/incidents',
        'get_incident': 'api/v1/incidents/%s',
        'put_incident': 'api/v1/incidents/%s',
        'put_alert_on_incident': 'api/v1/incidents/%s/alerts/%s',
        'get_picklist_list': 'api/v1/picklists',
        'get_picklist': 'api/v1/picklists/%s',
        'add_item_to_picklist': 'api/v1/picklists/%s/picklist_items',
        'get_picklist_item_list': 'api/v1/picklist_items',
        'create_picklist_item': 'api/v1/picklist_items',
        'get_picklist_item': 'api/v1/picklist_items/%s',
        'restore_picklist_item': 'api/v1/picklist_items/%s/restore',
        'delete_picklist_item': 'api/v1/picklist_items/%s',
        'object_type': 'api/v1/object_types',
        'version': 'api/v1/version'
    }

    def __init__(self, config_args=None, config_file=None):
        """Create an API Client instance

        Args:
             config_args (dict): Key, Value pairs of IR-Flow API configuration options
             config_file (str): Path to a valid Ir-Flow configuration file
        """
        # Create a PrettyPrint object so we can dump JSon structures if debug = true.
        self.pp = pprint.PrettyPrinter(indent=4)

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        # Make sure we have config info we need
        if not (config_args or config_file):
            print('Missing config input parameters. Need either api.conf, or to pass in config_args to'
                  'initialize IRFlowClient Class \n'
                  )
        if config_args and config_file:
            print('!!! Warning !!! Since you provided both input args and an api.conf file, we are'
                  'defaulting to the input args.')

        # parse config_args dict
        if config_args:
            self._get_config_args_params(config_args)

        # Else parse api.conf
        elif config_file:
            self._get_config_file_params(config_file)

        # Get a reusable session object.
        self.session = requests.Session()
        # Set the X-Authorization header for all calls through the API
        # The rest of the headers are specified by the individual calls.
        self.session.headers.update({'X-Authorization': "{} {}".format(self.api_user, self.api_key)})

    def _get_config_args_params(self, config_args):
        """Helper function to check/parse configuration arguments provided as a dict

        Args:
            config_args (dict): A dict of the following keys:

        Keys:
            address (str): IR-Flow Server FQDN or IP Address
            api_user (str): IR-Flow API User
            api_key (str): above user's api key
            protocol (str): https unless otherwise specified, default = HTTPS
            debug (bool): enable debug output, default = None
            verbose (int): turn up the verbosity default = 0 (optional)
        """

        # Checking for missing config values

        if isinstance(config_args['address'], str):
            self.address = config_args['address']
        elif not config_args['address']:
            raise KeyError('You have the wrong or missing key or value')
        else:
            raise KeyError('You have the wrong or missing key or value')

        if isinstance(config_args['api_user'], str):
            self.api_user = config_args['api_user']
        elif not config_args['api_user']:
            raise KeyError('You have the wrong or missing key or value')
        else:
            raise KeyError('You have the wrong or missing key or value')

        if isinstance(config_args['api_key'], str):
            self.api_key = config_args['api_key']
        elif not config_args['api_key']:
            raise KeyError('You have the wrong or missing key or value')
        else:
            raise KeyError('You have the wrong or missing key or value')

        if config_args['protocol']:
            self.protocol = config_args['protocol']
        else:
            self.protocol = 'https'
        if config_args['debug']:
            self.debug = config_args['debug']
        else:
            self.debug = False
        try:
            if config_args['verbose']:
                self.verbose = int(config_args['verbose'])
        except KeyError:
            self.verbose = 1

        # Dump Configuration if --debug
        if self.debug:
            self.dump_settings()

    def _get_config_file_params(self, config_file):
        """Helper function to parse configuration arguments from a valid IR-Flow configuration file

        Args:
            config_file (str): Path to a valid IR-Flow configuration file
        """
        config = configparser.ConfigParser()
        config.read(config_file)

        # Make sure the Config File has the IRFlowAPI Section
        if not config.has_section('IRFlowAPI'):
            print('Config file "{}" does not have the required section "[IRFlowAPI]"'.format(config_file))
            self.logger.error('Config file "{}" does not have the required section "[IRFlowAPI]"'.format(config_file))
            sys.exit()

        missing_config = False
        # Check for missing required configuration keys
        if not config.has_option('IRFlowAPI', 'address'):
            self.logger.error(
                'Configuration File "{}" does not contain the "address" option in the [IRFlowAPI] '
                'section'.format(config_file)
            )
            missing_config = True
        if not config.has_option('IRFlowAPI', 'api_user'):
            self.logger.error(
                'Configuration File "{}" does not contain the "api_user" option in the [IRFlowAPI] '
                'section'.format(config_file)
            )
            missing_config = True
        if not config.has_option('IRFlowAPI', 'api_key'):
            self.logger.error(
                'Configuration File "{}" does not contain the "api_key" option in the [IRFlowAPI] '
                'section'.format(config_file)
            )
            missing_config = True

        # Do not need to check for protocol, it is optional.  Will assume https if missing.
        # Do not need to check for debug, it is optional.  Will assume False if missing.

        # If the required keys do not exist, then simply exit
        if missing_config:
            print('Missing config')
            sys.exit()

        # Now set the configuration values on the self object.
        self.address = config.get('IRFlowAPI', 'address')
        self.api_user = config.get('IRFlowAPI', 'api_user')
        self.api_key = config.get('IRFlowAPI', 'api_key')
        if config.has_option('IRFlowAPI', 'protocol'):
            self.protocol = config.get('IRFlowAPI', 'protocol')
        else:
            self.protocol = 'https'
        if config.has_option('IRFlowAPI', 'debug'):
            self.debug = config.getboolean('IRFlowAPI', 'debug')
        else:
            self.debug = False
        if config.has_option('IRFlowAPI', 'verbose'):
            self.verbose = int(config.get('IRFlowAPI', 'verbose'))
        else:
            self.verbose = 1

        # Dump Configuration if --debug
        if self.debug:
            self.dump_settings()

    def dump_settings(self):
        """Helper function to print configuration information
        """
        self.logger.info('Configuration Settings\n'
                         '\tAddress: "{}"\n'
                         '\tAPI_User: "{}"\n'
                         '\tAPI_Key: "{}"\n'
                         '\tProtocol: "{}"\n'
                         '\tDebug: "{}"\n'
                         '\tVerbose: "{}"'.format(self.address,
                                                  self.api_user,
                                                  self.api_key,
                                                  self.protocol,
                                                  self.debug,
                                                  self.verbose)
                         )

    def dump_request_debug_info(self, heading, url, headers=None, data=None, params=None):
        """Helper function to dump request info to the debug stream on the logging bus

        Args:
            heading (str): A string heading for the debug message - typically the name of the endpoint being queried
            url (str): The full url of the API endpoint
            headers (dict): The headers of this request, if desired
            data (dict): Key, Value pairs of data in the body of a request, if desired
            params (dict): Key, Value pairs of parameters passed in a request, if desired
        """
        debug_string = '========== {} ==========\n' \
                       'URL: "{}"\n' \
                       'Session Headers: "{}"'.format(heading, url, self.session.headers)
        if headers:
            debug_string += '\nHeaders: "{}"'.format(headers)
        if data:
            debug_string += '\nBody: "{}"'.format(data)
        if params:
            debug_string += '\nParams: "{}"'.format(params)

        self.logger.debug(debug_string)

    def dump_response_debug_info(self, heading, status, json):
        """Helper function to dump response info from a request to the debug stream on the logging bus

        Args:
            heading (str): A string heading for the debug message, the word 'Response' will be appended
            status (int): The HTTP response code of the previously made request
            json (dict): The full json response body as returned by the IR-Flow API
        """
        self.logger.debug('========== {} Response ==========\n'
                          'HTTP Status: "{}"\n'
                          'Response JSON:\n{}'.format(heading, status, dumps(json, indent=2)))

    def get_version(self):
        """Function to get Current IR-Flow Version

        Returns:
            str: IR-Flow Version Number
                Example: 4.6.0"""

        url = "%s://%s/%s" % (self.protocol, self.address, self.end_points['version'])
        headers = {'Content-type': 'application/json'}

        response = self.session.get(url, verify=False, headers=headers)
        return str(response.json()['data']['version'])

    def close_alert(self, alert_num, close_reason):
        """Close the alert with the provided number, for the provided reason

        Args:
            alert_num (int): The IR-Flow assigned alert number of the alert to close
            close_reason (str): The reason for which to close the desired alert

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_alert_close'])
        data = {"alert_num": "%s" % alert_num, "close_reason_name": "%s" % close_reason}
        headers = {'Content-type': 'application/json'}

        if self.debug:
            self.dump_request_debug_info('Close Alert', url, headers, data=data)

        response = self.session.put(url, json=data, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Close Alert', response.status_code, response.json())

        return response.json()

    def attach_incident_to_alert(self, incident_num, alert_num):
        """Attach the specified alert to the specified incident

        .. note:: This API endpoint will be deprecated in a future release. You should use :func:`attach_alert_to_incident`, which accomplishes the same outcome, and is how this would be done naturally in the interface. No new code should use this function.

        Args:
            incident_num (int): The Incident Number of the Incident to which the specified alert should be attached
            alert_num (int): The IR-Flow Assigned Alert Number of the Alert to attach to the specified incident

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_incident_on_alert'])
        url = url % (alert_num, incident_num)
        headers = {'Content-type': 'application/json'}

        if self.debug:
            self.dump_request_debug_info('Attach Incident to Alert', url, headers=headers)

        response = self.session.put(url, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Attach Incident to Alert', response.status_code, response.json())

        return response.json()

    def upload_attachment_to_alert(self, alert_num, filename):
        """Upload an attachment to the specified alert

        Args:
            alert_num (int): The IR-Flow Assigned Alert number of the Alert to which the desired filed should be
                uploaded
            filename (str): The path to the file to be uploaded

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_attachment'])
        url = url % ('alerts', alert_num)
        data = {'file': open(filename, 'rb')}
        headers = {}

        if self.debug:
            self.dump_request_debug_info('Upload Attachment to Alert', url, headers=headers)

        response = self.session.post(url, data={}, files=data, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Upload Attachment to Alert', response.status_code, response.json())

        return response.json()

    def upload_attachment_to_incident(self, incident_id, filename):
        """Upload an attachment to the specified incident

        Args:
            incident_id (int): The ID of the Incident to which the desired file should be uploaded
            filename (str): The path to the file to be uploaded

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_attachment'])
        url = url % ('incidents', incident_id)
        data = {'file': open(filename, 'rb')}
        headers = {}

        if self.debug:
            self.dump_request_debug_info('Upload Attachment to Incident', url, headers=headers)

        response = self.session.post(url, data={}, files=data, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Upload Attachment to Incident', response.status_code, response.json())

        return response.json()

    def upload_attachment_to_task(self, task_id, filename):
        """Upload an attachment to the specified task

        Args:
            task_id (int): The ID of the task to which the desired file should be uploaded
            filename (str): The path to the file to be uploaded

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_attachment'])
        url = url % ('tasks', task_id)
        data = {'file': open(filename, 'rb')}
        headers = {}

        if self.debug:
            self.dump_request_debug_info('Upload Attachment to Alert', url, headers=headers)

        response = self.session.post(url, data={}, files=data, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Upload Attachment to Alert Response', response.status_code, response.json())

        return response.json()

    def download_attachment(self, attachment_id, attachment_output_file):
        """Download the attachment with the specified ID

        Args:
            attachment_id (int): The ID of the attachment to be downloaded
            attachment_output_file (str): The full path to the file on disk to which the desired attachment should be
                saved

        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_attachment'])
        url = url % attachment_id

        if self.debug:
            self.dump_request_debug_info('Download Attachment', url)

        with open(attachment_output_file, 'wb') as handle:
            response = self.session.get(url, stream=True, verify=False)
            for block in response.iter_content(1024):
                handle.write(block)

        if self.debug:
            self.dump_response_debug_info('Download Attachment', response.status_code, response.json())

    def download_attachment_string(self, attachment_id):
        """Download an attachment and return it as text

        Args:
            attachment_id (int): The ID of the attachment to be downloaded

        Returns:
            str: The textual contents of the downloaded file
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_attachment'])
        url = url % attachment_id

        if self.debug:
            self.dump_request_debug_info('Download Attachment String', url)

        # Get a temporary file to download the results into
        temp = tempfile.TemporaryFile()

        response = self.session.get(url, stream=True, verify=False)
        # Iterate, downloading data 1,024 bytes at a time
        for block in response.iter_content(1024):
            temp.write(block)

        # Rewind the file to the beginning so we can read it into a string
        temp.seek(0)
        if self.debug:
            self.dump_response_debug_info('Download Attachment String', response.status_code, response.json())

        return temp.read()

    def put_fact_group(self, fact_group_id, fact_data):
        """Put new or updated fact data in the specified fact group

        Args:
            fact_group_id (int): The IR-Flow assigned ID of the fact_group to be updated
            fact_data (dict): Key, Value pairs of fact fields as specified in IR-Flow and their values

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s/%s' % (self.protocol, self.address, self.end_points['get_fact_group'], fact_group_id)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        fact_payload = {'fields': fact_data}
        if self.debug:
            self.dump_request_debug_info('Put Fact Group', url, headers=headers)

        response = self.session.put(url, json=fact_payload, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Put Fact Group', response.status_code, response.json())

        return response.json()

    def get_fact_group(self, fact_group_id):
        """Retrieve the current data in the specified fact group

        Args:
            fact_group_id (int): The IR-Flow assigned IF of the fact_group to retrieve

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s/%s' % (self.protocol, self.address, self.end_points['get_fact_group'], fact_group_id)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get Fact Group', url, headers=headers)

        response = self.session.get(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get Fact Group', response.status_code, response.json())

        return response.json()

    def get_alert(self, alert_num):
        """Retrieve the alert with the specified alert number

        Args:
            alert_num (int): The IR-Flow assigned alert number of the alert to retrieve

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s/%s' % (self.protocol, self.address, self.end_points['get_alert'], alert_num)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get Alert', url, headers=headers)

        response = self.session.get(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get Alert', response.status_code, response.json())

        return response.json()

    def create_alert(self, alert_fields, description=None, incoming_field_group_name=None,
                     suppress_missing_field_warning=False):
        """Create an alert of the desired field group name with the specified fields and description

        Args:
            alert_fields (dict): Key, Value pairs of fields configured in IR-Flow and their values
            description (str): An optional string description for the alert
            incoming_field_group_name (str): The string name of the incoming field group name for this alert as
                specified in IR-Flow
            suppress_missing_field_warning (bool): Suppress the API warnings indicating missing fields if `True` -
                defaults to `False`

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['create_alert'])
        params = {
            'fields': alert_fields,
            'suppress_missing_field_warning': suppress_missing_field_warning
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        if description is not None:
            params['description'] = description
        if incoming_field_group_name is not None:
            params['data_field_group_name'] = incoming_field_group_name

        if self.debug:
            self.dump_request_debug_info('Create Alert', url, headers=headers, params=params)

        response = self.session.post(url, json=params, verify=False, headers=headers)
        if self.debug:
            self.dump_response_debug_info('Create Alert', response.status_code, response.json())

        return response.json()

    def create_incident(self, incident_fields, incident_type_name, incident_subtype_name=None, description=None):
        """Create an incident of the desired type and subtype with the specified fields and description

        Args:
            incident_fields (dict): Key, Value pairs of fields configured in IR-Flow and their values
            incident_type_name (str): The string name of the incident type with which this incident should be created
            incident_subtype_name (str): The string name of the incident subtype with which this incident should be
                created (optional)
            description (str): An optional string description for the incident
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['create_incident'])
        params = {
            'fields': incident_fields,
            'incident_type_name': incident_type_name,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        if incident_subtype_name is not None:
            params['incident_subtype_name'] = incident_subtype_name
        if description is not None:
            params['description'] = description

        if self.debug:
            self.dump_request_debug_info('Create Incident', url, headers=headers, params=params)

        response = self.session.post(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Create Incident', response.status_code, response.json())

        return response.json()

    def get_incident(self, incident_num):
        """Retrieve the incident with the specified ID

        Args:
            incident_num (int): The IR-Flow assigned ID of the incident to be retrieved

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_incident'])
        url = url % incident_num
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get Incident', url, headers=headers)

        response = self.session.get(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get Incident', response.status_code, response.json())

        return response.json()

    def update_incident(self, incident_num, incident_fields, incident_type_name, incident_subtype_name=None,
                        description=None):
        """Update the incident of the provided number, type, and subtype with the provided fields and description

        Args:
            incident_num (int): The IR-Flow assigned ID of the incident to update
            incident_fields (dict): Key, Value pairs of fields configured in IR-Flow and their values
            incident_type_name (str): The string name of the incident type of the desired incident
            incident_subtype_name (str): The string name of the incident subtype of the desired incident (optional)
            description (str): An optional string description for the incident

        Returns:
             dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_incident'])
        url = url % incident_num
        params = {
            'fields': incident_fields,
            'incident_type_name': incident_type_name,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        if incident_subtype_name is not None:
            params['incident_subtype_name'] = incident_subtype_name
        if description is not None:
            params['description'] = description

        if self.debug:
            self.dump_request_debug_info('Update Incident', url, headers=headers, params=params)

        response = self.session.put(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Update Incident', response.status_code, response.json())

        return response.json()

    def attach_alert_to_incident(self, alert_num, incident_num):
        """Attach the specified alert to the specified incident

        Args:
            incident_num (int): The Incident Number of the Incident to which the specified alert should be attached
            alert_num (int): The IR-Flow Assigned Alert Number of the Alert to attach to the specified incident

        Returns:
            dict: The full json response object returned by the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['put_alert_on_incident'])
        url = url % (incident_num, alert_num)
        headers = {'Content-type': 'application/json'}

        if self.debug:
            self.dump_request_debug_info('Attach Alert to Incident', url, headers=headers)

        response = self.session.put(url, headers=headers, verify=False)

        if self.debug:
            self.dump_response_debug_info('Attach Alert to Incident', response.status_code, response.json())

        return response.json()

    def list_picklists(self, with_trashed=False, only_trashed=False):
        """List all picklists

        Args:
            with_trashed (bool): Include deleted picklists - `False` by default
            only_trashed (bool): List only deleted picklists - `False` by default

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_picklist_list'])
        params = {
            'with_trashed': with_trashed,
            'only_trashed': only_trashed,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get List of Picklists', url, headers=headers, params=params)

        response = self.session.get(url, params=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get List of Picklists', response.status_code, response.json())

        return response.json()

    def get_picklist(self, picklist_id):
        """Retrieve the picklist with the desired ID

        Args:
            picklist_id (int): The IR-Flow assigned id of the picklist to be retrieved

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_picklist'])
        url = url % picklist_id
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get Picklist', url, headers=headers)

        response = self.session.get(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get Picklist', response.status_code, response.json())

        return response.json()

    def add_item_to_picklist(self, picklist_id, value, label, description=None):
        """Add an item with the provided value, label, and description to the picklist matching the provided ID

        Args:
            picklist_id (int): The IR-Flow assigned ID of the picklist to which the new item should be added
            value (str): The string value submitted to actions and integrations for this picklist item
            label (str): The label to be displayed for this picklist item
            description (str): An optional description for this picklist item

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['add_item_to_picklist'])
        url = url % picklist_id
        params = {
            'value': value,
            'label': label,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        if description is not None:
            params['description'] = description

        if self.debug:
            self.dump_request_debug_info('Add Item to Picklist', url, headers=headers, params=params)

        response = self.session.post(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Add Item to Picklist', response.status_code, response.json())

        return response.json()

    def list_picklist_items(self, picklist_id, with_trashed=False, only_trashed=False):
        """Retrieve a list of all picklist items in a specified list

        Args:
            picklist_id (int): The IR-Flow Assigned ID of the picklist whose items to list
            with_trashed (bool): Include deleted items - `False` by default
            only_trashed (bool): Only list deleted items - `False` by default

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_picklist_item_list'])
        params = {
            'picklist_id': picklist_id,
            'with_trashed': with_trashed,
            'only_trashed': only_trashed,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get List of Picklist Items', url, headers=headers, params=params)

        response = self.session.get(url, params=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get List of Picklist Items', response.status_code, response.json())

        return response.json()

    def create_picklist_item(self, picklist_id, value, label, description=None):
        """Create a new item in a specified picklist

        Args:
            picklist_id (int): The IR-Flow assigned ID of the picklist to which the new item should be added
            value (str): The string value submitted to actions and integrations for this picklist item
            label (str): The label to be displayed for this picklist item
            description (str): An optional description for this picklist item

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['create_picklist_item'])
        params = {
            'picklist_id': picklist_id,
            'value': value,
            'label': label,
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        if description is not None:
            params['description'] = description

        if self.debug:
            self.dump_request_debug_info('Add Picklist Item', url, headers=headers, params=params)

        response = self.session.post(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Add PIcklist Item', response.status_code, response.json())

        return response.json()

    def get_picklist_item(self, picklist_item_id):
        """Retrieve the picklist item corresponding to the specified ID

        Args:
            picklist_item_id (int): The IR-Flow assigned ID of the picklist item to be retrieved

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['get_picklist_item'])
        url = url % picklist_item_id
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Get Picklist Item', url, headers=headers)

        response = self.session.get(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Get Picklist Item', response.status_code, response.json())

        return response.json()

    def restore_picklist_item(self, picklist_item_id):
        """Restore a previously deleted picklist item

        Args:
            picklist_item_id (int): The IR-Flow assigned ID of the picklist item to be restored

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['restore_picklist_item'])
        url = url % picklist_item_id
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Restore Picklist Item', url, headers=headers)

        response = self.session.put(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Restore Picklist Item', response.status_code, response.json())

        return response.json()

    def delete_picklist_item(self, picklist_item_id):
        """Mark a picklist item as deleted

        Args:
            picklist_item_id (int): The IR-Flow assigned ID of the picklist item to be deleted

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['delete_picklist_item'])
        url = url % picklist_item_id
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if self.debug:
            self.dump_request_debug_info('Delete Picklist Item', url, headers=headers)

        response = self.session.delete(url, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Delete Picklist Item', response.status_code, response.json())

        return response.json()

    def create_object_type(self, type_name, type_label, parent_type_name=None, parent_type_id=None):
        """Create an object type of the provided parent type or id with the provided name and label

        Args:
            type_name (str): The string name for this object type
            type_label (str): The label for this object type
            parent_type_name (str): The string name of the parent object type - required if no `parent_type_id` is
                specified
            parent_type_id (int): The id of the parent object type - required if no `parent_type_name` is specified

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        if type_name is None:
            raise TypeError("type_name is required")
        if type_label is None:
            raise TypeError("type_label is required")
        if parent_type_name is None and parent_type_id is None:
            raise TypeError("Either parent_type_name or parent_type_id is required")

        url = '%s://%s/%s' % (self.protocol, self.address, self.end_points['object_type'])
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }

        params = {
            'type_name': type_name,
            'type_label': type_label,
            'parent_type_name': parent_type_name,
            'parent_type_id': parent_type_id
        }

        if self.debug:
            self.dump_request_debug_info('Store Object Type', url, headers=headers, params=params)

        response = self.session.post(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Store Object Type', response.status_code, response.json())

        return response.json()

    def attach_field_to_object_type(self, object_type_name, field_name, object_type_id=None, field_id=None):
        """Attach an existing field to an object of the specified name or id

        Args:
            object_type_name (str): The string name of the object to which the specified field should be added -
                required only if no `object_type_id` is provided
            field_name (str): The string name of the field to be added to the specified object - required only if no
                `field_id` is provided
            object_type_id (int): The IR-Flow assigned ID of the object to which the specified field should be added -
                required only if no `object_type_name` is provided
            field_id (int): The IR-Flow assigned IF of the field to be added to the specified object - required only if
                no `field_name` is provided

        Returns:
            dict: The full json response object from the IR-Flow API
        """
        url = '%s://%s/%s/%s' % (self.protocol, self.address, self.end_points['object_type'], 'attach_field')
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        params = {
            'object_type_name': object_type_name,
            'field_name': field_name,
            'object_type_id': object_type_id,
            'field_id': field_id
        }

        if self.debug:
            self.dump_request_debug_info('Attach Field to Object Type', url, headers=headers, params=params)

        response = self.session.put(url, json=params, verify=False, headers=headers)

        if self.debug:
            self.dump_response_debug_info('Attach Field to Object Type', response.status_code, response.json())

        return response.json()

    # The following helper functions are also defined in the irflow_client
    @staticmethod
    def get_field_by_name(field_name, field_list):
        """Helper function to return a field via a string name match given a field and field list

        Args:
            field_name (str): The string name of the desired field
            field_list (list): A list of field objects

        Returns:
            dict: The field object if found, `None` otherwise
        """
        for field in field_list:
            if field['field']['field_name'] == field_name:
                return field
        return None
