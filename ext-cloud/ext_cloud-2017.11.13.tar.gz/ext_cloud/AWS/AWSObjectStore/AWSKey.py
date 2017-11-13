from ext_cloud.BaseCloud.BaseObjectStore.BaseKey import BaseKeycls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSKeycls(AWSBaseCloudcls, BaseKeycls):

    __s3 = None
    __aws_key = None

    def __init__(self, *arg, **kwargs):
        self.__aws_key = arg[0]

        super(AWSKeycls, self).__init__(id=self.__aws_key.name, name=self.__aws_key.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        return self.__aws_key.size

    def delete(self):
        self.__aws_key.delete()
        return True

    def download(self, file_path):
        self.__aws_key.get_contents_to_filename(file_path)

    def upload(self, file_path):
        self.__aws_key.set_contents_to_filename(file_path)

    def get_url(self):
        return self.__aws_key.generate_url()
