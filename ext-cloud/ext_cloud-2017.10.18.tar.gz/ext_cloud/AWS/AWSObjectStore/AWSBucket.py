from ext_cloud.BaseCloud.BaseObjectStore.BaseBucket import BaseBucketcls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.AWS.AWSObjectStore.AWSKey import AWSKeycls


class AWSBucketcls(AWSBaseCloudcls, BaseBucketcls):

    __s3 = None
    __aws_bucket = None

    def __init__(self, *arg, **kwargs):
        self.__aws_bucket = arg[0]

        super(AWSBucketcls, self).__init__(id=self.__aws_bucket.name, name=self.__aws_bucket.name, credentials=kwargs['credentials'])

    def get_all_keys(self):
        aws_keys = self.__aws_bucket.get_all_keys()
        keys = []
        for aws_key in aws_keys:
            key = AWSKeycls(aws_key, credentials=self._credentials)
            keys.append(key)

        return keys

    def delete(self):
        self.__aws_bucket.delete()
