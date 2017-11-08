# coding=utf-8
import logging
import datetime
import httplib2
import io
import os

from mali_commands.legit.multi_process_control import MultiProcessControl
from ...connection_mixin import ConnectionMixin
from ...dulwich.object_store import BaseObjectStore
from ...dulwich.objects import hex_to_filename, sha_to_hex, Blob
from googleapiclient.discovery import build_from_document
from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload, HttpRequest
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
from mali_commands.utilities import get_content_type

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

            with open(discovery_file) as f:
                doc = f.read()
                self.__service = build_from_document(doc, http=credentials.authorize(httplib2.Http()))
        else:
            self.__service._http = credentials.authorize(httplib2.Http())

        return self.__service


def do_upload(bucket_name, volume_id, object_name, body, signed_url_service, content_type, head_url, put_url):
    # logging.debug('upload %s to %s', object_name, put_url)
    res = GCSUpload(signed_url_service).upload(
        bucket_name, volume_id, object_name, body, content_type, head_url, put_url)
    # logging.debug('uploaded %s: %s', object_name, res)


def do_download(bucket_name, volume_id, object_name, signed_url_service=None):
    return GCSDownload(signed_url_service).download(bucket_name, volume_id, object_name)


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


# HttpRequest postproc is called only on STATUS < 400
def status_404_to_204(resp):
    if resp.status == 404:
        resp.status = 204


def return_request_result(response, content):
    return response, content


class GCSDownload(GCSService):
    def download(self, bucket_name, volume_id, object_name):
        request = self._get_request(bucket_name, volume_id, object_name)
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

    def _get_request(self, bucket_name, volume_id, object_name):
        if not self.signed_url_service:
            service = self._get_authenticated_service()
            object_name = '%s/%s' % (volume_id, object_name)
            return service.objects().get_media(bucket=bucket_name, object=object_name)

        signed_urls = self.signed_url_service.get_signed_urls(['GET'], [object_name])
        url = signed_urls['GET'][0]

        http = httplib2.Http()
        return HttpRequest(http, None, url)


class GCSUpload(GCSService):
    def upload(self, bucket_name, volume_id, object_name, body, content_type=None, head_url=None, put_url=None):
        logger.debug('upload %s/%s (%s)', volume_id, object_name, '{:,}'.format(len(body)))

        request = self._get_request(bucket_name, volume_id, object_name, body, content_type, head_url, put_url)

        def progress_upload():
            status, response = request.next_chunk()

            return status.proress(), response is None

        def simple_upload():
            request.execute()
            return 1, True

        def on_failed_upload():
            logging.error('too many retries (%s) to upload %s/%s', self.NUM_RETRIES, bucket_name, object_name)

        upload_method = progress_upload if request.resumable else simple_upload

        return _retry_operation(upload_method, on_failed_upload)

    def _get_request(self, bucket_name, volume_id, object_name, body, content_type=None, head_url=None, put_url=None):

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
                return None
            else:
                service = self._get_authenticated_service()
                resumable = len(body) > self.CHUNKSIZE
                media = MediaInMemoryUpload(body, get_content_type(body), chunksize=self.CHUNKSIZE, resumable=resumable)

                direct_object_name = '%s/%s' % (volume_id, object_name)
                return service.objects().insert(
                    bucket=bucket_name, name=direct_object_name, media_body=media,
                    predefinedAcl='publicRead')

        upload_res = do_cold_upload()
        if upload_res is not None:
            return upload_res
        http = httplib2.Http()

        content_type, head_url, put_url = validate_urls(head_url, put_url, content_type)

        def chain_put_request_if_needed(resp, _):
            if resp.status == 204:
                c_type = content_type
                if c_type is None:
                    c_type = get_content_type(body)

                c_headers = GCSObjectStore.get_content_headers(c_type)
                logging.debug('file not found, uploading')

                media = MediaInMemoryUpload(body, mimetype=c_type, chunksize=self.CHUNKSIZE)
                return HttpRequest(http, return_request_result, put_url, method='PUT', body=media.getbytes(0, media.size()), headers=c_headers).execute()
            elif resp.status == 200:
                return None
            else:
                raise Exception(resp)

        request_head = HttpRequest(http, chain_put_request_if_needed, head_url, method='HEAD')
        request_head.add_response_callback(status_404_to_204)

        return request_head


class GCSObjectStore(ConnectionMixin, BaseObjectStore):
    def __init__(self, connection, use_multiprocess=True, processes=-1):
        super(GCSObjectStore, self).__init__(connection)
        self.__upload_pool = None
        self.__use_multiprocess = use_multiprocess
        self.__multi_process_control = None
        self.__processes = processes
        self.__bucket_name = connection.data_volume_config.object_store_config.get('bucket_name')
        self.__volume_id = self._connection.data_volume_config.volume_id
        self._signed_url_service = None

    @classmethod
    def get_content_headers(cls, content_type=None):
        headers = {
            'x-goog-if-generation-match': '0',
            'x-goog-acl': 'public-read',
        }

        if content_type:
            headers['Content-Type'] = content_type

        return headers

    @property
    def processes(self):
        return self.__processes

    @processes.setter
    def processes(self, value):
        self.__processes = value

    @property
    def is_multiprocess(self):
        return self.__use_multiprocess

    def close(self):
        logging.debug('%s closing', self.__class__)
        if self.__multi_process_control is not None:
            self.__multi_process_control.close()

        logging.debug('%s closed', self.__class__)

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    @classmethod
    def on_upload_error(cls, ex):
        raise ex

    def upload(self, obj, content_type=None, head_url=None, put_url=None):
        path = self._get_shafile_path(obj.id)

        if obj.type_name != b'blob':
            raise Exception('type not supported %s', obj.type_name)
        data = obj.data

        if self.is_multiprocess:
            if self.__multi_process_control is None:
                self.__multi_process_control = MultiProcessControl(self.__processes)

            self.__multi_process_control.execute(
                do_upload,
                args=(self.__bucket_name, self.__volume_id, path, data, None, content_type, head_url, put_url))

        else:
            do_upload(self.__bucket_name, self.__volume_id, path, data, self._signed_url_service, content_type, head_url, put_url)

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
        blob.set_raw_chunks(data, sha)
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

    def add_objects(self, objects):
        for obj in objects:
            self.upload(obj.blob)

    def contains_packed(self, sha):
        raise NotImplementedError(self.contains_packed)

    def contains_loose(self, sha):
        raise NotImplementedError(self.contains_loose)
