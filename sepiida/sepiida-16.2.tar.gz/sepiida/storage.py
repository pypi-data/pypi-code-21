import base64
import contextlib
import io
import logging
import urllib.parse

import requests

import sepiida.zipbuf


LOGGER = logging.getLogger(__name__)

class StorageException(Exception):
    pass

class AlreadyUploadedException(StorageException):
    pass

class NotUploadedException(StorageException):
    pass

class NoFileException(StorageException):
    pass

def _auth_header():
    settings = sepiida.environment.get()
    credentials = 'api:{}'.format(settings.API_TOKEN).encode('utf-8')
    return {'Authorization' : 'Basic {}'.format(base64.b64encode(credentials).decode('utf-8'))}

def upload_link(key, bucket, overwrite=False):
    settings = sepiida.environment.get()
    payload = {
        'bucket'    : bucket,
        'key'       : str(key),
    }
    url = urllib.parse.urljoin(settings.STORAGE_SERVICE, 'file/')

    if len('{}?filter[key]={}'.format(url, key)) <= 2000:
        response = requests.get('{}?filter[key]={}'.format(url, key), headers=_auth_header())
    else:
        response = requests.get(url, data='filter[key]={}'.format(key), headers=_auth_header())

    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    if len(resources) < 1:
        response = requests.post(url, json=payload, headers=_auth_header())
        if not response.ok:
            try:
                errors = response.json()['errors']
                if 'DuplicateKeyError' in [error['code'] for error in errors]:
                    raise AlreadyUploadedException('A file with key {} has already been uploaded'.format(key))
            except (ValueError, KeyError):
                pass
            raise StorageException('Unknown storage error: {}'.format(response.text))
        upload_location = response.headers['upload-location']
    else:
        if resources[0].get('uploaded') and not overwrite:
            raise AlreadyUploadedException('A file with key {} has already been uploaded'.format(key))

        upload_location = resources[0].get('upload-location')

    return upload_location

def download_link(key):
    settings = sepiida.environment.get()
    url = urllib.parse.urljoin(settings.STORAGE_SERVICE, 'file/')

    if len('{}?filter[key]={}'.format(url, key)) <= 2000:
        response = requests.get('{}?filter[key]={}'.format(url, key), headers=_auth_header())
    else:
        response = requests.get(url, data='filter[key]={}'.format(key), headers=_auth_header())

    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    if len(resources) < 1:
        raise NoFileException('A file with key {} does not exist in the database'.format(key))

    download_location = resources[0].get('content')

    if not download_location:
        raise NotUploadedException('A file with key {} has not yet been uploaded'.format(key))

    return download_location


def get_files(keys):
    settings = sepiida.environment.get()
    url = urllib.parse.urljoin(settings.STORAGE_SERVICE, 'file/')
    _filter = ','.join(map(str, keys))

    response = requests.get(url, data='filter[key]={}'.format(_filter), headers=_auth_header())
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    file_to_key_map = {resource['key'] : resource for resource in resources}

    return file_to_key_map

def put(key, bucket, content, mimetype, overwrite=False, compress=False):
    upload_location = upload_link(key, bucket, overwrite)

    if compress:
        if isinstance(content, bytes):
            content = io.BytesIO(content)
        content = sepiida.zipbuf.ZipBuffer(content)
        mimetype = 'application/zlib.' + mimetype
        LOGGER.debug("Adding compression to data and changing mimetype to %s", mimetype)

    response = requests.put(upload_location, data=content, headers={'content-type': mimetype})
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

def get(key, output_filename=None):
    download_location = download_link(key)

    response = requests.get(download_location, stream=True)
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    stream = response.raw
    content_type = response.headers.get('content-type')
    if content_type.startswith('application/zlib.'):
        LOGGER.debug("Found content type of %s, unzipping", content_type)
        stream = sepiida.zipbuf.UnzipBuffer(stream)

    if output_filename:
        with open(output_filename, 'wb') as f:
            while True:
                block = stream.read(1024 * 100)
                if not block:
                    break
                f.write(block)
        stream = open(output_filename, 'rb')
    return contextlib.closing(stream)
