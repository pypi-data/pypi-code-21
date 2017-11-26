# -*- coding: utf8 -*-
import logging
import datetime
from collections import OrderedDict

import requests

from ...connection_mixin import ConnectionMixin
from ...dulwich.object_store import BaseObjectStore
from ...dulwich.objects import hex_to_filename, sha_to_hex, Blob

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GCSServiceOperationError(Exception):
    pass


__gcs_service = None
__gcs_credentials = None


def gcs_credentials():
    import google.auth.exceptions

    global __gcs_credentials

    if __gcs_credentials is None:
        try:
            __gcs_credentials = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            pass

    return __gcs_credentials


def gcs_service(credentials=None):
    from google.cloud import storage

    global __gcs_service

    if __gcs_service is None:
        __gcs_service = storage.Client(credentials=credentials)

    return __gcs_service


class GCSService(object):
    RETRYABLE_ERRORS = (IOError, )
    DEFAULT_MIMETYPE = 'application/octet-stream'
    NUM_RETRIES = 5

    def __init__(self, signed_url_service):
        self.__service = None
        self.signed_url_service = signed_url_service


def do_upload(bucket_name, volume_id, object_name, full_path_to_data, signed_url_service, content_type, head_url, put_url, credentials=None):
    GCSUpload(signed_url_service).upload(
        bucket_name, volume_id, object_name, full_path_to_data, content_type, head_url, put_url, credentials=credentials)


def do_download(bucket_name, volume_id, object_name, signed_url_service=None):
    return GCSDownload(signed_url_service).download(bucket_name, volume_id, object_name)


def do_delete_all(bucket_name, volume_id, max_files):
    return GCSDeleteAll(signed_url_service=None).delete_all(bucket_name, volume_id, max_files)


def __raise_on_request_error(http_operation):

    return http_operation()


def _retry_operation(http_operation, on_failed):
    start_time = datetime.datetime.utcnow()

    retries = 0
    done = False
    while not done:
        try:
            progress, done = __raise_on_request_error(http_operation)
        except GCSService.RETRYABLE_ERRORS as ex:
            logging.debug('retry operation because of %s', ex)
            retries += 1

            if retries == GCSService.NUM_RETRIES:
                on_failed()
                raise GCSServiceOperationError()

            continue

    logger.debug('operation took %s', datetime.datetime.utcnow() - start_time)


def return_request_result(response, content):
    return response, content


class GCSDeleteAll(GCSService):
    @classmethod
    def delete_all(cls, bucket_name, volume_id, max_files=None):
        import google.cloud.exceptions

        logging.info('delete all at %s/%s', bucket_name, volume_id)
        gcs = gcs_service()

        try:
            list_iter = gcs.bucket(bucket_name).list_blobs(prefix=volume_id)
        except google.cloud.exceptions.NotFound:
            logging.warning('bucket %s was not found', bucket_name)
            return

        total_deleted = 0
        for blob in list_iter:
            try:
                gcs.bucket(bucket_name).delete_blob(blob.name)
            except google.cloud.exceptions.NotFound:
                pass

            total_deleted += 1

            if max_files is not None and max_files == total_deleted:
                break

        logging.info('total deleted %s', total_deleted)

        return total_deleted


class GCSDownload(GCSService):
    def download(self, bucket_name, volume_id, object_name):
        if not self.signed_url_service:
            gcs = gcs_service()

            object_name = '%s/%s' % (volume_id, object_name)
            blob = gcs.bucket(bucket_name).blob(object_name)
            data = blob.download_as_string()
        else:
            signed_urls = self.signed_url_service.get_signed_urls(['GET'], [object_name])
            url = signed_urls['GET'][0]

            r = requests.get(url)
            r.raise_for_status()
            data = r.content

        logger.debug('downloaded  %s(%s)', object_name, len(data))

        return data


class GCSUpload(GCSService):
    def upload(self, bucket_name, volume_id, object_name, full_path_to_data, content_type=None, head_url=None, put_url=None, credentials=None):
        from mali_commands.utilities import get_content_type

        with open(full_path_to_data, 'rb') as f:
            body = f.read()

        logger.debug('upload %s/%s (%s)', volume_id, object_name, '{:,}'.format(len(body)))

        def validate_urls(head, put, current_content_type):
            if head is None or put is None:
                if current_content_type is None:
                    current_content_type = get_content_type(body)

                urls = self.signed_url_service.get_signed_urls(
                    ['PUT', 'HEAD'], [object_name], current_content_type, **GCSObjectStore.get_content_headers())
                put = urls['PUT'][0]
                head = urls['HEAD'][0]

            return current_content_type, head, put

        def do_cold_upload():
            if self.signed_url_service or put_url:
                return False

            current_gcs = gcs_service(credentials=credentials)

            direct_object_name = '%s/%s' % (volume_id, object_name)

            blob = current_gcs.bucket(bucket_name).blob(direct_object_name)
            if blob.exists():
                return True

            blob.upload_from_string(body, get_content_type(body))

            return True

        upload_res = do_cold_upload()
        if upload_res:
            return

        content_type, head_url, put_url = validate_urls(head_url, put_url, content_type)

        resp = requests.head(head_url)

        if resp.status_code in (204, 404):
            c_type = content_type or get_content_type(body)
            c_headers = GCSObjectStore.get_content_headers(c_type)

            logging.debug('file not found, uploading')

            r = requests.put(put_url, data=body, headers=c_headers)
            r.raise_for_status()


class GCSObjectStore(ConnectionMixin, BaseObjectStore):
    def __init__(self, connection, use_multiprocess=True, processes=-1):
        super(GCSObjectStore, self).__init__(connection)
        self.__upload_pool = None
        self._use_multiprocess = use_multiprocess
        self._multi_process_control = None
        self._processes = processes
        self.__bucket_name = connection.data_volume_config.object_store_config.get('bucket_name')
        self.__volume_id = self._connection.data_volume_config.volume_id
        self._signed_url_service = None

    def delete_all(self, max_files=None):
        return do_delete_all(self.__bucket_name, self.__volume_id, max_files)

    @classmethod
    def get_content_headers(cls, content_type=None):

        headers = OrderedDict()
        if content_type:
            headers['Content-Type'] = content_type

        headers['x-goog-acl'] = 'public-read'
        headers['x-goog-if-generation-match'] = '0'

        return headers

    @property
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, value):
        self._processes = value

    @property
    def is_multiprocess(self):
        return self._use_multiprocess and self._processes != 1

    def close(self):
        logging.debug('%s closing', self.__class__)
        if self._multi_process_control is not None:
            self._multi_process_control.close()

        logging.debug('%s closed', self.__class__)

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    @classmethod
    def on_upload_error(cls, ex):
        raise ex

    def upload(self, obj, content_type=None, head_url=None, put_url=None, callback=None):
        path = self._get_shafile_path(obj.blob.id)

        credentials = gcs_credentials()

        if self.is_multiprocess:
            if self._multi_process_control is None:
                from ...multi_process_control import get_multi_process_control

                self._multi_process_control = get_multi_process_control(self._processes)

            self._multi_process_control.execute(
                do_upload,
                args=(self.__bucket_name, self.__volume_id, path, obj.full_path, None, content_type, head_url, put_url, credentials), callback=callback)

        else:
            do_upload(self.__bucket_name, self.__volume_id, path, obj.full_path, self._signed_url_service, content_type, head_url, put_url)
            if callback is not None:
                callback(obj)

    def add_object(self, obj):

        """Add a single object to this object store.

        :param obj: Object to add
        """
        self.upload(obj)

    def _get_loose_object(self, sha):
        logger.debug('get object %s', sha)
        path = self._get_shafile_path(sha)
        data = do_download(self.__bucket_name, self.__volume_id, path, signed_url_service=self._signed_url_service)
        blob = Blob()
        blob.set_raw_chunks([data], sha)
        return blob

    def get_raw(self, name):
        """Obtain the raw text for an object.

        :param name: sha for the object.
        :return: tuple with numeric type and object contents.
        """
        hex_sha = name

        if len(name) != 40 and len(name) != 20:
            raise AssertionError("Invalid object name %r" % name)

        if hex_sha is None:
            hex_sha = sha_to_hex(name)

        ret = self._get_loose_object(hex_sha)
        if ret is not None:
            return ret.type_num, ret.as_raw_string()

        raise KeyError(hex_sha)

    @property
    def packs(self):
        raise NotImplementedError(self.packs)

    def __iter__(self):
        raise NotImplementedError(self.__iter__)

    def add_objects(self, objects, callback=None):
        for obj in objects:
            self.upload(obj, callback=callback)

    def contains_packed(self, sha):
        raise NotImplementedError(self.contains_packed)

    def contains_loose(self, sha):
        raise NotImplementedError(self.contains_loose)
