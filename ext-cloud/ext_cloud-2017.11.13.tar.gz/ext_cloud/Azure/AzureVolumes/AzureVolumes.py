from ext_cloud.BaseCloud.BaseVolumes.BaseVolumes import BaseVolumescls
from ext_cloud.Azure.AzureVolumes.AzureVolume import AzureVolumecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls


class AzureVolumescls(AzureBaseCloudcls, BaseVolumescls):

    def __init__(self, **kwargs):
        self.__ec2 = None
        self.__sms = None
        self._credentials = kwargs['credentials']

    @property
    def __SMS(self):
        return self.__sms

    @__SMS.getter
    def __SMS(self):
        from azure.servicemanagement import ServiceManagementService
        if self.__sms is None:
            self.__sms = ServiceManagementService(self._credentials['subscription_id'], self._credentials['certificate_path'])
        return self.__sms

    def list_volumes(self):
        azure_volumes = self.__SMS.list_disks()
        volumes = []
        for azure_volume in azure_volumes:
            azure_volume = AzureVolumecls(azure_volume, credentials=self._credentials)
            volumes.append(azure_volume)

        return volumes

    def get_volume_by_id(self, volume_id):
        azure_volume = self.__SMS.get_disk(volume_id)
        volume = AzureVolumecls(azure_volume, credentials=self._credentials)
        return volume

    def get_volumes_by_name(self, volume_name):
        azure_volumes = self.list_volumes()
        volumes = []
        for azure_volume in azure_volumes:
            if azure_volume.name == volume_name:
                volumes.append(azure_volume)

        return volumes

    def get_volumes_by_tag(self, tag_name, tag_value):
        pass

    def create_volume(self, size=2, name=None, zone=None):
        pass

    def attach_volume(self, volume_id=None, instance_id=None, device_path=None):
        pass

    def detach_volume(self, volume_id=None, instance_id=None):
        pass

    def delete_volume_by_id(self, volume_id):
        self.__SMS.delete_disk(volume_id)

    def list_snapshots(self):
        pass

    def get_snapshot_by_id(self, snapshot_id):
        pass

    def create_snapshot(self, volume_id, name=None, description=None):
        pass

    def create_volume_from_snapshot(self, snapshot_id, size=2, name=None):
        pass

    def get_snapshots_by_tag(self, tag_name, tag_value):
        pass

    def delete_snapshot_by_id(self, snapshot_id):
        pass
