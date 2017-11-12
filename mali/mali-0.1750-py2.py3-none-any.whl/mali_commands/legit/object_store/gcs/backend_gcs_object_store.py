# coding=utf-8
import requests
from ...backend_mixin import BackendMixin
from .gcs_object_store import GCSObjectStore


class BackendGCSSignedUrlService(BackendMixin):
    def __init__(self, connection, config, handle_api):
        super(BackendGCSSignedUrlService, self).__init__(connection, config, handle_api)

    def get_signed_urls(self, methods, object_names, content_type=None, **kwargs):
        headers = []
        for key, val in kwargs.items():
            headers.append('%s:%s' % (key, val))

        msg = {
            'methods': methods,
            'paths': object_names,
            'headers': headers,
        }
        if 'content-type' in headers:
            del (msg['content_type'])
        if content_type:
            msg['content_type'] = content_type

        url = 'data_volumes/{volume_id}/gcs_urls'.format(volume_id=self._volume_id)

        result = self._handle_api(self._config, requests.post, url, msg)
        res = {}
        for method in methods:
            res[method] = result.get(method.lower(), [])
        return res


class BackendGCSObjectStore(BackendMixin, GCSObjectStore):
    def __init__(self, connection, config, handle_api, processes=-1):
        super(BackendGCSObjectStore, self).__init__(connection, config, handle_api)
        self.__bucket_name = None
        self._signed_url_service = BackendGCSSignedUrlService(connection, config, handle_api)
        self.processes = processes

    def __iter__(self):
        return super(BackendGCSObjectStore, self).__iter__()

    def close(self):
        super(BackendGCSObjectStore, self).close()

    @classmethod
    def _group_files_by_meta(cls, files):
        content_type_grouped = {}
        for ob in files:
            if ob.content_type not in content_type_grouped:
                content_type_grouped[ob.content_type] = []
            content_type_grouped[ob.content_type].append(ob)
        return content_type_grouped

    def _get_urls_for_paths(self, paths, content_type, headers):
        urls = self._signed_url_service.get_signed_urls(['HEAD', 'PUT'], paths, content_type, **headers)
        head_urls = urls['HEAD']
        put_urls = urls['PUT']
        return head_urls, put_urls

    def _upload_meta_batch(self, content_type, files):
        content_headers = self.get_content_headers()
        upload_paths = list(map(lambda x: GCSObjectStore._get_shafile_path(x.blob.id), files))
        head_urls, put_urls = self._get_urls_for_paths(upload_paths, content_type, content_headers)
        for cur_file, head_url, put_url in zip(files, head_urls, put_urls):
            self.upload(cur_file.blob, content_type, head_url, put_url)

    def add_objects(self, objects):
        grouped_files = self._group_files_by_meta(objects)
        for content_type in grouped_files:
            files = grouped_files[content_type]
            self._upload_meta_batch(content_type, files)

    @property
    def packs(self):
        return super(BackendGCSObjectStore, self).packs

    def contains_loose(self, sha):
        return super(BackendGCSObjectStore, self).contains_loose(sha)

    def contains_packed(self, sha):
        return super(BackendGCSObjectStore, self).contains_packed(sha)
