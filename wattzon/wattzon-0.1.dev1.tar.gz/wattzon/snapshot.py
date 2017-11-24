"""Client library for the WattzOn Snapshot product.

This library is meant to be used by Link customers who own
a valid signed certificate for the REST API. If you don't
please contact the sales team.

"""
import base64
import logging
import os
import requests
import uuid

from .common import getenv


_logger = logging.getLogger(__name__)


class Client:
    API_URL = os.getenv('SNAPSHOT_API_URL', 'snapshot.wattzon.com')

    def __init__(self, cert=None, key=None):
        self._cert = getenv(cert, 'SNAPSHOT_API_CERT')
        self._key = getenv(key, 'SNAPSHOT_API_KEY')

    def start_job(self, email, provider_id, attachments, tags=None):
        attachments = self._normalize_attachments(attachments)
        payload = {
            'attachments': attachments,
            'customer_email': email,
            'provider': provider_id
        }
        payload.update({'tags': tags} if tags else {})
        response = self._request('post', 'jobs', json=payload)
        return response.json()

    @staticmethod
    def _normalize_attachments(attachments):
        normalized_attachments = list()
        for attachment in attachments:
            fallback_name = 'unnamed_{}'.format(uuid.uuid4())
            if type(attachment) is dict:
                if 'content' not in attachment:
                    raise ValueError('Missing `content` property in attachment dict')
                if 'name' not in attachment:
                    attachment['name'] = fallback_name
                assert len(attachment.keys()) == 2
                normalized_attachments.append(attachment)
            elif type(attachment) is bytes:
                normalized_attachments.append({
                    'content': base64.b64encode(attachment).decode('utf-8'),
                    'name': fallback_name
                })
            elif type(attachment) is str:
                if not os.path.isfile(attachment):
                    raise ValueError('Attachment not found in file system')
                with open(attachment, 'rb') as attachment_file:
                    normalized_attachments.append({
                        'content': base64.b64encode(attachment_file.read()).decode('utf-8'),
                        'name': os.path.basename(attachment)
                    })
            else:
                raise ValueError('Attachment format not recognized')
        return normalized_attachments

    def get_job(self, job_id):
        resource = 'jobs/{}'.format(job_id)
        response = self._request('get', resource)
        return response.json()

    def get_jobs(self):
        response = self._request('get', 'jobs')
        return response.json()

    def _request(self, method, resource, **kwargs):
        """Performs a request to the API with authorization included.
        
        It also retries several times before giving up, currently the
        limit is 3. It also sets the cert authentication for requests
        and the base url for resources.
        """
        attempts = 0
        response = None
        kwargs.update(dict(cert=(self._cert, self._key)))
        url = '{}://{}/api/v1/{}'.format('https', self.API_URL, resource)
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

