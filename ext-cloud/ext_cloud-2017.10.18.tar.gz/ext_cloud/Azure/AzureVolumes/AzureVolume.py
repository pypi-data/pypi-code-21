from ext_cloud.BaseCloud.BaseVolumes.BaseVolume import BaseVolumecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls


class AzureVolumecls(AzureBaseCloudcls, BaseVolumecls):

    __azure_volume = None
    __sms = None

    def __init__(self, *arg, **kwargs):
        self.__azure_volume = arg[0]

        super(AzureVolumecls, self).__init__(id=self.__azure_volume.name, name=self.__azure_volume.label, credentials=kwargs['credentials'])

    @property
    def __SMS(self):
        return self.__sms

    @__SMS.getter
    def __SMS(self):
        from azure.servicemanagement import ServiceManagementService
        if self.__sms is None:
            self.__sms = ServiceManagementService(self._credentials['subscription_id'], self._credentials['certificate_path'])
        return self.__sms

    @property
    def description(self):
        pass

    @property
    def size(self):
        return self.__azure_volume.logical_disk_size_in_gb

    @property
    def state(self):
        pass

    @property
    def instance_id(self):
        attached_to = self.__azure_volume.attached_to
        if attached_to is None:
            return
        return attached_to.hosted_service_name

    @property
    def device_name(self):
        pass

    @property
    def attach_time(self):
        pass

    @property
    def creation_time(self):
        pass

    def addtag(self, name, value):
        pass

    def gettags(self):
        pass

    def delete(self):
        self.__SMS.delete_disk(self.oid, delete_vhd=True)
