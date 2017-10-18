from ext_cloud.BaseCloud.BaseImages.BaseImage import BaseImagecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls


class AzureImagecls(AzureBaseCloudcls, BaseImagecls):
    __azure_image = None

    def __init__(self, *arg, **kwargs):
        self.__azure_image = arg[0]

        super(AzureImagecls, self).__init__(id=self.__azure_image.name, name=self.__azure_image.label, credentials=kwargs['credentials'])

    @property
    def size(self):
        return self.__azure_image.logical_size_in_gb

    @property
    def state(self):
        return "ACTIVE"

    @property
    def os_type(self):
        return self.__azure_image.os
