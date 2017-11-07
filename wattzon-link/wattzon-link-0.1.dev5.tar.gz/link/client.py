#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Client library for the WattzOn Link product.

This library is meant to be used by Link customers who own
a valid signed certificate for the REST API. If you don't
please contact the sales team.

"""
import os
import logging
import requests


_logger = logging.getLogger(__name__)


class Client(object):
    API_URL = 'api.wattzon.com'

    def __init__(self, cert=None, key=None):
        self._cert = _get_value_or_env(cert, 'LINK_API_CERT')
        self._key = _get_value_or_env(key, 'LINK_API_KEY')

    def echo(self, string):
        payload = dict(string=string)
        response = self._request('post', 'echo', json=payload)
        return response.json().get('string') if response else None

    def list_profiles(self, id=None, provider=None, start_date=None, end_date=None, tags=None, label=None):
        fields = ['id', 'provider', 'start_date', 'end_date', 'label']
        payload = dict()
        for field, value in zip(fields, [id, provider, start_date, end_date, label]):
            if value is not None:
                payload[field] = value
        if tags is not None:
            payload['tags'] = self._parse_list(tags)

        response = self._request('get', 'profiles', params=payload)
        return response.json()

    def get_bills(self, profile_id):
        resource = 'data/bills/{}'.format(profile_id)
        response = self._request('get', resource)
        return response.json()

    def fetch_pdf(self, profile_id, bill_id):
        resource = 'data/bills/{}/{}/pdf'.format(profile_id, bill_id)
        response = self._request('get', resource)
        return response.content

    def start_job(self, profile_id, mode='bill', notify=True):
        payload = {
            'profile_id': profile_id,
            'send_notification': notify,
            'mode': mode
        }
        response = self._request('post', 'jobs', json=payload)
        return response.json()

    def get_job(self, job_id):
        resource = 'jobs/{}'.format(job_id)
        response = self._request('get', resource)
        return response.json()

    @staticmethod
    def _parse_list(value):
        if type(value) is str:
            return value
        elif hasattr(value, '__iter__'):
            return ','.join(value)
        return None

    def _request(self, method, resource, **kwargs):
        """Performs a request to the API with authorization included.
        
        It also retries several times before giving up, currently the
        limit is 3. It also sets the cert authentication for requests
        and the base url for resources.
        """
        attempts = 0
        response = None
        kwargs.update(dict(cert=(self._cert, self._key)))
        url = '{}://{}/link/4.0/{}'.format('https', self.API_URL, resource)
        url += '' if url.endswith('/') else '/'

        while (response is None or not (200 <= response.status_code < 300)) and attempts < 3:
            try:
                method_fn = getattr(requests, method)
                response = method_fn(url, **kwargs)

            except AttributeError:
                _logger.error('Request http method not recognized')
                raise

            except requests.exceptions.SSLError as e:
                _logger.error('There was an error with SSL: %s', e)

            finally:
                attempts += 1

        return response


def _get_value_or_env(priority, envkey):
    if priority is not None:
        return priority
    return os.getenv(envkey)

