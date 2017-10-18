from ext_cloud.BaseCloud.BaseObjectStore.BaseObjectStore import BaseObjectStorecls
from ext_cloud.AWS.AWSObjectStore.AWSBucket import AWSBucketcls
from boto import s3
from boto.s3.connection import OrdinaryCallingFormat
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSObjectStorecls(AWSBaseCloudcls, BaseObjectStorecls):

    def __init__(self, **kwargs):
        self.__s3 = None
        self._credentials['username'] = kwargs['username']
        self._credentials['password'] = kwargs['password']
        self._credentials['region_name'] = kwargs['region_name']

    @property
    def __S3(self):
        return self.__s3

    @__S3.getter
    def __S3(self):
        if self.__s3 is None:
            self.__s3 = s3.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials[
                                             'username'], aws_secret_access_key=self._credentials['password'], calling_format=OrdinaryCallingFormat())
        return self.__s3

    def get_all_buckets(self):
        aws_buckets = self.__S3.get_all_buckets()
        buckets = []
        for aws_bucket in aws_buckets:
            bucket = AWSBucketcls(aws_bucket, credentials=self._credentials)
            buckets.append(bucket)
        return buckets

    def get_bucket_by_name(self, bucket_name):
        aws_bucket = self.__S3.lookup(bucket_name)
        if aws_bucket is None:
            return None
        bucket = AWSBucketcls(aws_bucket, credentials=self._credentials)
        return bucket

    def create_bucket(self, bucket_name):
        aws_bucket = self.__S3.create_bucket(bucket_name)
        bucket = AWSBucketcls(aws_bucket, credentials=self._credentials)
        return bucket
