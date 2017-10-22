# load credentials
import logging
import utils
from utils import safe_read_simple_url, safe_get_json

"""
This is for Elastic group spotinst-agent specific
"""


def init__configuration(config, debug=False):
    instance_details = None
    log = logging.getLogger('spotinst-agent')

    if debug:
        # for debug
        log.warning("spotinst-agent is running with mock credentials for debug purposes")
        instance_details = {'instance_id': 'i-1234567890',
                            'authentication_token': 'DUMMY-TOKEN'}
        return instance_details

    locator_url = config['instance_id_locator_url']
    instance_id = get_instance_id(locator_url, log)

    creds = utils.retrieve_creds()
    authentication_token = creds["token"]
    account_id = creds["account_id"]

    if instance_id and authentication_token:
        instance_details = {'instance_id': instance_id, 'authentication_token': authentication_token,
                            'account_id': account_id}

    return instance_details


def get_instance_id(locator_url, log):
    response = None
    if locator_url:
        if locator_url.startswith("http://"):
            response = safe_read_simple_url(locator_url, log)
            response = str(response)

        else:
            with open(locator_url) as file:
                response = file.read().splitlines()[0]

        log.debug("found instance id - {}".format(response))
        if not response:
            log.error("response is null, can't get instance id")
            return None

    return response
