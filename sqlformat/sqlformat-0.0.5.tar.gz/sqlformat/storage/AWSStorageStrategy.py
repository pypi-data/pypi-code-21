import os
import tempfile
from urllib.parse import urlparse

from sqlformat import StorageStrategyTemplate


class AWSStorageStrategy(StorageStrategyTemplate):
    def __init__(self, boto_client):
        self.boto_client = boto_client

    def _read_procedure(self, procedure_path):
        return self.__read_file(procedure_path)

    def _read_sql(self, sql_path):
        return self.__read_file(sql_path)

    def __read_file(self, file_path):
        s3_object = parse_s3_path(file_path, self.boto_client)
        return s3_object.content

def parse_s3_path(s3_path, boto_client):
    s3_path_info = urlparse(s3_path)
    return S3Object(s3_path_info.netloc, s3_path_info.path[1:], boto_client)

class S3Object:
    def __init__(self, bucket, key, boto_client):
        self.s3_key = key
        self.s3_bucket = bucket
        self.boto_client = boto_client

    @property
    def boto_object(self):
        return self.boto_client.Object(self.s3_bucket, self.s3_key)

    @property
    def content(self):
        local_path = None
        obj_content = None
        with tempfile.NamedTemporaryFile(delete=False) as s3_object_in_local:
            local_path = s3_object_in_local.name
            self.boto_object.download_file(local_path)
        with open(local_path) as s3_object_in_local:
            obj_content = s3_object_in_local.read()
        os.remove(local_path)
        return obj_content
