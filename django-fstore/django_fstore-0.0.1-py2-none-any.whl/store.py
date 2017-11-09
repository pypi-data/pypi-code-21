# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from datetime import timedelta

from django.core.files import File
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.views.generic import View
from django.utils.http import urlquote
from django.conf import settings

from minio import Minio
from minio.error import ResponseError


def _get_content_type(file_ext):
    d = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/msword',
        '.png': 'image/png',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.tif': 'image/tiff',
        '.mp4': 'video/mpeg4',
        '.mp3': 'audio/mp3',
        '.svg': 'text/xml',
        '.txt': 'text/plain',
        '.swf': 'application/x-shockwave-flash',
        '.xap': 'application/x-silverlight-app',
        '.ipa': 'application/vnd.iphone',
        '.apk': 'application/vnd.android.package-archive',
        '.html': 'text/html',
        '.css': 'text/css'
    }
    return d.get(file_ext, 'application/octet-stream')


class MinioDownloadView(View):

    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        return mc.download(file_name)


class MinioOpenView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        return mc.open(file_name)


class MinioSignedView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.copy()
        file_name = query.get('file', None)

        if file_name is None:
            raise Http404()

        mc = MinioStore()
        url = mc.presigned_get_object(file_name)
        return HttpResponsePermanentRedirect(url)


class MinioStore(object):

    def __init__(self, endpoint=None, access_key=None, secret_key=None, secure=None, bucket_name=None):
        try:
            if endpoint is None:
                self.endpoint = settings.MINIO_ENDPOINT
            if access_key is None:
                self.access_key = settings.MINIO_ACCESS_KEY
            if secret_key is None:
                self.secret_key = settings.MINIO_SECRET_KEY
            if secure is None:
                self.secure = settings.MINIO_SECURE
            if bucket_name is None:
                self.bucket_name = settings.MINIO_BUCKET_NAME

            self.mc = Minio(self.endpoint, self.access_key,
                            self.secret_key, self.secure)
        except ResponseError as err:
            raise err

    def put_file(self, f, name=None, size=None, content_type=None):
        if not isinstance(f, File):
            raise ValueError

        if name is None:
            name = f.name
        if size is None:
            size = f.size
        if content_type is None:
            content_type = f.content_type

        self.put_object(name, f, size, content_type)

    def put_object(self, object_name, data, length, content_type='application/octet-stream'):
        try:
            self.mc.put_object(
                self.bucket_name, object_name, data, length, content_type)
        except ResponseError as err:
            raise err

    def get_object(self, object_name):
        req = self.mc.get_object(self.bucket_name, object_name)
        return req

    def presigned_get_object(self, object_name, expires=timedelta(days=7)):
        return self.mc.presigned_get_object(self.bucket_name, object_name, expires)

    def _download(self, object_name, content_type='application/octet-stream', out_file_name=None, is_download=True):
        re = self.get_object(object_name)

        if out_file_name is None:
            out_file_name = object_name

        response = HttpResponse(re.data)
        response['Content-Type'] = content_type
        if is_download:
            response[
                'Content-Disposition'] = 'attachment;filename="%s"' % (urlquote(out_file_name))
        else:
            response['Content-Disposition'] = 'filename="%s"' % (
                urlquote(out_file_name))
        return response

    def download(self, object_name, out_file_name=None):
        content_type = 'application/octet-stream'
        return self._download(object_name, content_type, out_file_name)

    def open(self, object_name, out_file_name=None):
        if out_file_name is None:
            out_file_name = object_name

        _, _ext = os.path.splitext(out_file_name)
        content_type = _get_content_type(_ext.lower())
        return self._download(object_name, content_type, out_file_name, False)
