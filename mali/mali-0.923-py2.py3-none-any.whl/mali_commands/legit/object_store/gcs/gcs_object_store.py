# coding=utf-8
import logging
import datetime
from threading import Semaphore

import httplib2
import io
import os

from ...connection_mixin import ConnectionMixin
from ...dulwich.object_store import BaseObjectStore
from ...dulwich.objects import hex_to_filename, hex_to_sha, sha_to_hex, ShaFile, Blob
from googleapiclient.discovery import build_from_document
from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload, HttpRequest
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from multiprocessing import Pool


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GCSServiceOperationError(Exception):
    pass


class GCSService(object):
    RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)
    CHUNKSIZE = 2 * 1024 * 1024
    DEFAULT_MIMETYPE = 'application/octet-stream'
    NUM_RETRIES = 5

    def __init__(self, signed_url_service):
        self.signed_url_service = signed_url_service
        self.__service = None

    def _get_authenticated_service(self):
        credentials = GoogleCredentials.get_application_default()

        if self.__service is None:
            discovery_file = os.path.join(os.path.dirname(__file__), 'gcs-v1.json')

            with open(discovery_file, encoding='utf8') as f:
                doc = f.read()
                self.__service = build_from_document(doc, http=credentials.authorize(httplib2.Http()))
        else:
            self.__service._http = credentials.authorize(httplib2.Http())

        return self.__service


def do_upload(bucket_name, object_name, body, signed_url_service=None):
    GCSUpload(signed_url_service).upload(bucket_name, object_name, body)


def do_download(bucket_name, object_name, signed_url_service=None):
    return GCSDownload(signed_url_service).download(bucket_name, object_name)


def __raise_on_request_error(http_operation):
    try:
        return http_operation()
    except HttpError as err:
        if err.resp.status == 412:
            logging.debug('file already uploaded')
            return 1, True

        if err.resp.status < 500:
            raise


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


class GCSDownload(GCSService):
    def download(self, bucket_name, object_name):
        request = self._get_request(bucket_name, object_name)
        fd = io.BytesIO()
        media = MediaIoBaseDownload(fd, request, chunksize=self.CHUNKSIZE)

        def on_failed_download():
            logging.error('too many retries (%s) to download %s/%s', self.NUM_RETRIES, bucket_name, object_name)

        def http_download():
            progress, done = media.next_chunk()

            return progress, done

        _retry_operation(http_download, on_failed_download)

        data = fd.getvalue()
        logger.debug('downloaded  %s(%s)', object_name, len(data))

        return data

    def _get_request(self, bucket_name, object_name):
        if not self.signed_url_service:
            service = self._get_authenticated_service()
            return service.objects().get_media(bucket=bucket_name, object=object_name)

        url = self.signed_url_service.get_signed_urls('GET', [object_name])[0]

        http = httplib2.Http()
        return HttpRequest(http, None, url)


class GCSUpload(GCSService):
    def upload(self, bucket_name, object_name, body):
        logger.debug('upload %s (%s)', object_name, '{:,}'.format(len(body)))

        request = self._get_request(bucket_name, object_name, body)

        def progress_upload():
            status, response = request.next_chunk()

            return status.proress(), response is None

        def simple_upload():
            request.execute()
            return 1, True

        def on_failed_upload():
            logging.error('too many retries (%s) to upload %s/%s', self.NUM_RETRIES, bucket_name, object_name)

        upload_method = progress_upload if request.resumable else simple_upload

        _retry_operation(upload_method, on_failed_upload)

    @classmethod
    def __get_content_type(cls, body):
        import puremagic
        import mimetypes
        mimetypes.init()
        mimetypes.add_type(mimetypes.types_map.get('.jpg'), '.jfif')

        ext = puremagic.from_string(body)
        return mimetypes.types_map.get(ext)

    def _get_request(self, bucket_name, object_name, body):
        headers = {
            'x-goog-if-generation-match': '0',
            'x-goog-acl': 'public-read',
        }

        content_type = self.__get_content_type(body)

        if not self.signed_url_service:
            service = self._get_authenticated_service()
            resumable = len(body) > self.CHUNKSIZE
            media = MediaInMemoryUpload(body, self.DEFAULT_MIMETYPE, chunksize=self.CHUNKSIZE, resumable=resumable)

            return service.objects().insert(bucket=bucket_name, name=object_name, media_body=media)

        url = self.signed_url_service.get_signed_urls('PUT', [object_name], content_type, **headers)[0]

        media = MediaInMemoryUpload(body, mimetype=content_type, chunksize=self.CHUNKSIZE)
        http = httplib2.Http()

        def post_proc(resp, content):
            return resp, content

        if content_type:
            headers['content-type'] = content_type

        return HttpRequest(http, post_proc, url, method='PUT', body=media.getbytes(0, media.size()), headers=headers)


class GCSObjectStore(ConnectionMixin, BaseObjectStore):
    def __init__(self, connection):
        super(GCSObjectStore, self).__init__(connection)
        self.__use_multiprocess = False
        self.__upload_pool = Pool(4)
        self.__max_waiting_semaphore = Semaphore(10)
        self.__bucket_name = connection.data_volume_config.object_store_config.get('bucket_name')
        self._signed_url_service = None

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    def on_upload_result(self, result):
        self.__max_waiting_semaphore.release()

    @classmethod
    def on_upload_error(cls, ex):
        raise ex

    def add_object(self, obj):
        """Add a single object to this object store.

        :param obj: Object to add
        """

        path = self._get_shafile_path(obj.id)

        if obj.type_name == b'blob':
            data = obj.data
            logger.debug(
                'uploading %s %s:%s %s bytes',
                path, obj.type_name, obj.type_num, '{:,}'.format(len(obj.data)))
        else:
            raise Exception('type not supported %s', obj.type_name)

        if self.__use_multiprocess:
            self.__upload_pool.apply_async(
                do_upload, args=(self.__bucket_name, path, data), callback=self.on_upload_result,
                error_callback=self.on_upload_result)
            t = datetime.datetime.utcnow()
            self.__max_waiting_semaphore.acquire()
        else:
            do_upload(self.__bucket_name, path, data, signed_url_service=self._signed_url_service)

    def _get_loose_object(self, sha):
        logger.debug('get object %s', sha)
        path = self._get_shafile_path(sha)
        data = do_download(self.__bucket_name, path, signed_url_service=self._signed_url_service)
        blob = Blob()
        blob.set_raw_chunks(data, sha)
        return blob

    def get_raw(self, name):
        """Obtain the raw text for an object.

        :param name: sha for the object.
        :return: tuple with numeric type and object contents.
        """
        if len(name) == 40:
            sha = hex_to_sha(name)
            hex_sha = name
        elif len(name) == 20:
            sha = name
            hex_sha = None
        else:
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

    def add_objects(self, objects):
        raise NotImplementedError(self.add_objects)

    def contains_packed(self, sha):
        raise NotImplementedError(self.contains_packed)

    def contains_loose(self, sha):
        raise NotImplementedError(self.contains_loose)
