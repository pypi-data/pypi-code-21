import boto3
from urllib.parse import urlparse

from .StorageStrategy import StorageStrategy

_s3 = boto3.resource('s3')

class S3Storage(StorageStrategy):

    def __init__(self, boto_client=_s3):
        super().__init__()
        self.client = boto_client

    def _read(self, path):
        s3_path_info = urlparse(path)
        bucket = s3_path_info.netloc
        key = s3_path_info.path[1:]
        s3_object = self.client.Object(bucket, key)
        return s3_object.get()["Body"].read().decode('utf-8')
