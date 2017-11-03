#! /usr/bin/python3

import os
import logging

from datadog.api.exceptions import ApiNotInitialized

from magen_logger.logger_config import LogDefaults, initialize_logger
from magen_utils_apis.dd_events_wrapper import DDEventsWrapper

from hwa.hwa_server.hwa_utils import read_dict_from_file
from hwa.hwa_server.hwa_urls import HwaUrls

__author__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__version__ = "0.1"
__copyright__ = "Copyright(c) 2015, Cisco Systems, Inc."
__status__ = "alpha"

logger = logging.getLogger(LogDefaults.default_log_name)

g_events_ctrl = None

# Must call before init of DDEventsWrapper superclass (and datadog library)
def HwaEventSvcInitialize():
    hwa_urls = HwaUrls()
    var_list=('DATADOG_API_KEY', 'DATADOG_APP_KEY')

    dd_secrets = read_dict_from_file(hwa_urls.datadogclt_secret_file)
    if not dd_secrets:
        logger.info("datadog secrets file (%s) not found",
                    hwa_urls.datadogclt_secret_file)
        return

    for var in var_list: # require that all variables in secrets file
        value = dd_secrets.get(var)
        if not value:
            logger.error("datadog secrets file (%s) missing %s",
                         hwa_urls.datadogclt_secret_file, var)
            return
    for var in var_list:
        value = dd_secrets.get(var)
        os.environ[var] = value


class HwaEvents(DDEventsWrapper):
    # An arbitrary string to use for aggregation,
    # max length of 100 characters.
    # If you specify a key, all events using that key
    # will be grouped together in the Event Stream.
    _aggregation_key = 'TEST000'  # don't use just yet please

    _known_actions = {
        'open': 'file.open',
        'create': 'file.create',
        'view': 'file.view',
        'share': 'collaborator.add',
        'file.open': 'file.open',
        'file.create': 'file.create',
        'file.view': 'file.view',
        'collaborator.add': 'collaborator.add'
    }

    _known_results = {
        'granted': 'access.granted',
        'denied': 'access.denied',
        'shared': 'access.shared'
    }

    def __init__(self, app_name=None):
        if not app_name and not super().app_tag:
            raise ValueError("app_name must be provided at least once")
        name = app_name if app_name else super().app_tag
        super(HwaEvents, self).__init__(app_name, logger)

    @classmethod
    def construct_event(cls, validation_data: dict, **kwargs):
        """
        Construct event from given dictionary and kwargs
        :param validation_data: usually it is a response data from Policy
        :param kwargs:
        :return: constructed event data dict
        """
        event_data = dict()
        event_data['result'] = cls._known_results[validation_data['access']]
        event_data['client_id'] = kwargs['client_id']
        event_data['action'] = cls._known_actions[kwargs['action']]
        event_data['application'] = kwargs['application']
        event_data['resource_id'] = kwargs['resource_id']
        event_data['asset_name'] = kwargs['asset_name']
        event_data['severity'] = kwargs['severity'] if kwargs.get('severity', None) else 50
        event_data['reason'] = validation_data['cause'] \
            if validation_data['access'] == 'denied' and validation_data.get('cause', None) else None
        return event_data

    def send_event(self, event_name: str, event_data: dict, alert=None, default_tags=False):
        try:
            super().send_event(event_name, event_data, alert, default_tags)
        except ApiNotInitialized:
            pass

def HwaEventsSendEvt(event_name, alert, response, **event_kwgs):
    global g_events_ctrl
    hwa_urls = HwaUrls()

    if not g_events_ctrl:
        g_events_ctrl = HwaEvents(app_name="magen-" + hwa_urls.hwa_app_tag)

    g_events_ctrl.send_event(
        event_name,
        event_data=HwaEvents.construct_event(response, **event_kwgs),
        alert=alert)
