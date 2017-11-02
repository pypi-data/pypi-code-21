# coding=utf-8
import logging
import time
import requests
import json
import datetime
from .json_encoder import MissingLinkJsonEncoder

KEEP_ALIVE_EVENT = 'KEEP_ALIVE'


class PostRequests(object):
    retry_interval = 1
    max_retries = 3

    def __init__(self, owner_id, project_token, host, stoppable=False):
        host = host or 'https://missinglinkai.appspot.com'

        self.logger = logging.getLogger('missinglink')

        self.owner_id = owner_id
        self.project_token = project_token
        self.experiment_token = None
        self.host = host
        self.packet_sequence = 0
        self.stoppable = stoppable
        self.stopped = False
        self.project_id = None
        self.experiment_id = None
        self.session = requests.session()

    def send_commands(self, commands, throw_exceptions=False):
        if self.experiment_token is None:
            self.logger.debug('create experiment failed or not called')
            return {}

        self.packet_sequence += 1

        params = {
            'cmds': commands,
            'token': self.experiment_token,
            'sequence': self.packet_sequence,
        }

        return self._post_and_retry('/callback/step', params, throw_exceptions=throw_exceptions)

    def send_images(self, data):
        data['project_token'] = self.project_token

        return self._post_and_retry('/callback/images', data)

    def send_keep_alive(self):
        keep_alive_cmd = (KEEP_ALIVE_EVENT, None, datetime.datetime.utcnow().isoformat())
        params = {
            'cmds': [keep_alive_cmd],
            'token': self.experiment_token,
        }

        return self._post_and_retry('/callback/step', params)

    def create_new_experiment(self, keep_alive_interval, throw_exceptions=None):
        self.logger.info(
            'create new experiment for owner (%s), keep alive interval (%s) seconds',
            self.owner_id, keep_alive_interval)

        params = {
            'owner_id': self.owner_id,
            'token': self.project_token,
            'keep_alive': keep_alive_interval,
            'stoppable': self.stoppable,
        }

        if throw_exceptions is None:
            throw_exceptions = True

        res = self._post_and_retry('/callback/step/begin', params, throw_exceptions=throw_exceptions)

        if not res:
            return {}

        self.experiment_token = res.get('token')
        self.project_id = res.get('project_id')
        self.experiment_id = res.get('experiment_id')

        return res

    def _post_and_retry(self, endpoint, json_dictionary, throw_exceptions=False):
        headers = {'content-type': 'application/json'}
        data = json.dumps(json_dictionary, cls=MissingLinkJsonEncoder, sort_keys=True)

        if self.project_id is not None:
            params = {'project_id': self.project_id, 'experiment_id': self.experiment_id}
        else:
            params = {'owner_id': self.owner_id, 'project_token': self.project_token}

        self.logger.debug('post data. len: (%s) params (%s)', len(data), ','.join(json_dictionary.keys()))

        url = self.host + endpoint

        last_error = None

        for _ in range(self.max_retries):
            try:
                res = self.session.post(url, data=data, params=params, headers=headers)
                self.logger.debug("Got response from server with status %s", res.status_code)
                res.raise_for_status()

                result = json.loads(res.text)

                return result
            except IOError as e:
                if throw_exceptions:
                    raise

                last_error = e
            except Exception as e:
                if throw_exceptions:
                    raise

                self.logger.exception('failed to send missinglink request')
                last_error = e

            time.sleep(self.retry_interval)

        self.logger.warning(
            'failed to communicate with missinglink server:\n%s\n', last_error)

        return {}


def get_post_requests(owner_id, project_token, host=None, on_create_dispatch=None):
    def default_create_dispatch():
        return PostRequests(owner_id, project_token, host)

    on_create_dispatch = on_create_dispatch or default_create_dispatch

    return on_create_dispatch()


def post_requests_for_experiment(owner_id, project_token, host=None, stoppable=False):
    def create_for_experiment():
        post_requests = PostRequests(owner_id, project_token, host, stoppable=stoppable)

        return post_requests

    return get_post_requests(owner_id, project_token, host, on_create_dispatch=create_for_experiment)
