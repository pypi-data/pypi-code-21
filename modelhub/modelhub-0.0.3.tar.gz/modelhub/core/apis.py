# -*- coding: utf-8 -*-
# import contextlib
from . import conf
import boto3
import botocore
import os
import io
import hashlib
import json
import threading
import tempfile
import sys
from .utils import cached_property

# from collections import OrderedDict


# class API(object):

#     def __init__(self):
#         self.base_path = urllib.parse.urljoin(conf.API_URI, "model")

#     def __getattr__(self, attr):
#         url = urllib.parse.urljoin(self.base_path, attr)

#         @contextlib.wraps(session.post)
#         def post(*args, **kwargs):
#             return session.post(url, *args, **kwargs)
#         return post


def get_path_last_child(path: str):
    return list(filter(None, path.split("/")))[-1]


class ProgressPercentage(object):

    def __init__(self, size):
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            if self._size:
                percentage = (self._seen_so_far / self._size) * 100
                to_write = "\r>>%s / %s  (%.2f%%)" % (
                    self._seen_so_far, self._size,
                    percentage)
            else:
                to_write = "\r>>%s"
            sys.stdout.write(to_write)
            sys.stdout.flush()
            if self._seen_so_far == self._size:
                sys.stdout.write("\n")


class API(object):
    @cached_property
    def session(self):
        return boto3.session.Session(
            aws_access_key_id=conf.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=conf.AWS_SECRET_ACCESS_KEY,
            region_name=conf.AWS_REGION_NAME,
        )

    @cached_property
    def s3(self):
        return self.session.resource('s3')

    @cached_property
    def bucket(self):
        return self.s3.Bucket(conf.AWS_BUCKET_NAME)

    @cached_property
    def client(self):
        return self.session.client("s3")

    def _ls_request(self, full_path, recursive=False):
        kwargs = {} if recursive else {"Delimiter": "/"}
        print(full_path)
        return api.client.list_objects_v2(Bucket=conf.AWS_BUCKET_NAME, Prefix=full_path, StartAfter=full_path, **kwargs)

    def ls_subfolder(self, *paths):
        full_path = os.path.join(conf.AWS_BASE_PATH, *paths)
        # TODO
        return [os.path.relpath(item["Prefix"], full_path) for item in self._ls_request(full_path)["CommonPrefixes"]]

    def ls_file(self, *paths, recursive=False):
        full_path = os.path.join(conf.AWS_BASE_PATH, *paths)
        if not full_path.endswith("/"):
            full_path += "/"
        res = self._ls_request(full_path, recursive=recursive).get("Contents", [])
        for item in res:
            item["name"] = os.path.basename(item["Key"])
            item["path"] = os.path.relpath(item["Key"], full_path)

        return res

    def get_file(self, fp, *paths, md5: bool=None, progressbar: bool=False, size: int=None, auto_copy=True)->io.BytesIO:
        full_path = os.path.join(conf.AWS_BASE_PATH, *paths)
        if progressbar:
            callback = ProgressPercentage(size)
        else:
            callback = None

        if md5 is not None and auto_copy:
            _fp = fp
            fp = tempfile.TemporaryFile()
        try:
            self.bucket.download_fileobj(full_path, fp, Callback=callback)
        except botocore.exceptions.ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                raise self.FileDoesNotExist(full_path) from e
            raise
        fp.seek(0)
        if md5 is not None:
            new_md5 = self.md5sum(fp)
            if md5 != new_md5:
                raise self.FileCorruptError(full_path, new_md5)
            if auto_copy:
                self.copy_file(fp, _fp)
                fp.close()
                fp = _fp
        return fp

    def get_json(self, *paths):
        with io.BytesIO() as f:
            self.get_file(f, *paths)
            return json.loads(f.read().decode())

    def upload_file(self, fp: io.BytesIO, *paths, progressbar=False):
        full_path = os.path.join(conf.AWS_BASE_PATH, *paths)
        if progressbar:
            size = self.get_fp_size(fp)
            callback = ProgressPercentage(size)
        else:
            callback = None
        self.bucket.upload_fileobj(fp, full_path, Callback=callback)

    def upload_json(self, content, *paths, **kwargs):
        with io.BytesIO() as f:
            json_str = json.dumps(content, **kwargs)
            f.write(json_str.encode())
            f.seek(0)
            self.upload_file(f, *paths)

    def delete_file(self, *paths, recursive=False):
        full_path = os.path.join(conf.AWS_BASE_PATH, *paths)
        if not full_path.endswith("/"):
            full_path += "/"
        if recursive:
            paths = [file_item["Key"] for file_item in self.ls_file(*paths, recursive=True)]
        else:
            paths = []
        paths.append(full_path)
        # print(paths)
        res = self.bucket.delete_objects(Delete=dict(
            Objects=[
                dict(
                    Key=path
                )
                for path in paths
            ]
        ))
        assert res.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
        # print("res", res)
        return [item["Key"] for item in res["Deleted"]]

    class FileDoesNotExist(Exception):
        pass

    class FileCorruptError(Exception):
        pass

    @staticmethod
    def md5sum(fp):
        d = hashlib.md5()
        while True:
            buf = fp.read(4096)  # 128 is smaller than the typical filesystem block
            if not buf:
                fp.seek(0)
                break
            d.update(buf)
        return d.hexdigest()

    @staticmethod
    def copy_file(from_fp, to_fp):
        while True:
            buf = from_fp.read(4096)  # 128 is smaller than the typical filesystem block
            if not buf:
                break
            to_fp.write(buf)
        to_fp.seek(0)
        from_fp.seek(0)

    @staticmethod
    def get_fp_size(fp: io.BytesIO):
        fp.seek(0, os.SEEK_END)
        res = fp.tell()
        fp.seek(0)
        return res


api = API()
