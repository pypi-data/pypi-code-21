from ext_cloud.BaseCloud.BaseImages.BaseImage import BaseImagecls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSImagecls(AWSBaseCloudcls, BaseImagecls):
    __aws_image = None

    def __init__(self, *arg, **kwargs):
        self.__aws_image = arg[0]

        super(AWSImagecls, self).__init__(id=self.__aws_image.id, name=self.__aws_image.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        lst = self.__aws_image.block_device_mapping.viewvalues()
        size = 0
        for item in lst:
            if item.size is not None:
                size = item.size
                continue
        return size

    @property
    def state(self):
        return self.__aws_image.state

    @property
    def architecture(self):
        return self.__aws_image.architecture

    @property
    def description(self):
        return self.__aws_image.description

    @property
    def os_type(self):
        return self.__aws_image.platform
