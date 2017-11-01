import json
import logging
from urllib.parse import urljoin

import requests

LOGGER = logging.getLogger(__name__)

def handle(service_root, url, method, status, uri):
    if url is None:
        LOGGER.info("Not doing callback, no URL provided")
        return

    if method is None:
        LOGGER.info("Not doing callback, no method provided")
        return

    payload = {
        'status'    : status,
        'uri'       : uri,
    }

    callback_payload = {
        "method" : method,
        "url"    : url,
        "body"   : json.dumps(payload),
    }
    response = requests.post(urljoin(service_root, '/job/'), json=callback_payload)
    if not response.ok:
        LOGGER.error("Failed to put callback job on the callback queue: %s %s", response.status_code, response.text)
