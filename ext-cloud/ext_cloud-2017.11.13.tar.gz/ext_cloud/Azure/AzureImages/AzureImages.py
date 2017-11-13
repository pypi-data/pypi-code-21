from ext_cloud.BaseCloud.BaseImages.BaseImages import BaseImagescls
from ext_cloud.Azure.AzureImages.AzureImage import AzureImagecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls

from azure.servicemanagement import ServiceManagementService


class AzureImagescls(AzureBaseCloudcls, BaseImagescls):

    def __init__(self, **kwargs):
        self.__sms = None
        self._credentials = kwargs['credentials']

    @property
    def __SMS(self):
        return self.__sms

    @__SMS.getter
    def __SMS(self):
        if self.__sms is None:
            self.__sms = ServiceManagementService(self._credentials['subscription_id'], self._credentials['certificate_path'])
        return self.__sms

    def list_images(self):
        azure_images = self.__SMS.list_os_images()
        images = []
        for azure_image in azure_images:
            image = AzureImagecls(azure_image, credentials=self._credentials)
            images.append(image)
        return images

    def get_image_by_id(self, image_id):
        image_list = []
        image_list.append(image_id)
        azure_images = self._EC2.get_all_images(image_ids=image_list)
        for azure_image in azure_images:
            image = AzureImagecls(azure_image, credentials=self._credentials)
            return image
        return None

    def create_image_from_instance(self, instance_id, name=None):
        pass
