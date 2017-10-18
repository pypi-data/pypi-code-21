from ext_cloud.BaseCloud.BaseCompute.BaseInstance import BaseInstancecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls
from azure.servicemanagement import ServiceManagementService


class AzureInstancecls(AzureBaseCloudcls, BaseInstancecls):

    __public_ip = None
    __state = None
    __azure_service = None
    __sms = None
    __image_id = None
    __image_name = None
    __os_type = None

    def __init__(self, *arg, **kwargs):
        self.__azure_service = arg[0]
        self._azure_ref = arg[0]
        super(AzureInstancecls, self).__init__(id=self.__azure_service.service_name, name=self.__azure_service.service_name, credentials=kwargs['credentials'])

    @property
    def __SMS(self):
        return self.__sms

    @__SMS.getter
    def __SMS(self):
        if self.__sms is None:
            self.__sms = ServiceManagementService(self._credentials['subscription_id'], self._credentials['certificate_path'])
        return self.__sms

    def _update(self):
        properties = self.__SMS.get_deployment_by_name(self.name, self.name)
        if properties is None:
            return
        if len(properties.role_instance_list) > 0:
            self.__state = properties.role_instance_list[0].instance_status

        if len(properties.role_list.roles) > 0:
            self.__image_id = properties.role_list.roles[0].os_virtual_hard_disk.source_image_name
            self.__os_type = properties.role_list.roles[0].os_virtual_hard_disk.os

    @property
    def size(self):
        pass

    @property
    def state(self):
        self._update()
        return self.__state

    @property
    def arch(self):
        pass

    @property
    def network_id(self):
        pass

    @property
    def subnet_id(self):
        pass

    @property
    def private_ip(self):
        pass

    @property
    def public_ip(self):
        pass

    @property
    def instance_type(self):
        pass

    @property
    def image_id(self):
        if self.__image_id is None:
            self._update()
        return self.__image_id

    @property
    def image_name(self):
        if self.image_id is None:
            return
        if self.__image_name is None:
            azure_image = self.__SMS.get_os_image(self.image_id)
            self.__image_name = azure_image.label
        return self.__image_name

    @property
    def keypair_name(self):
        pass

    @property
    def dns_name(self):
        return self.name + ".cloudapp.net"

    @property
    def creation_time(self):
        import datetime
        dt = datetime.datetime.strptime(self.__azure_service.hosted_service_properties.date_created, '%Y-%m-%dT%H:%M:%SZ')

        return dt.strftime("%B %d, %Y %I:%M:%S %p")

    @property
    def os_type(self):
        if self.__os_type is None:
            self._update()
        return self.__os_type

    def start(self):
        self.__SMS.start_role(self.name, self.name, self.name)
        return True

    def stop(self):
        self.__SMS.shutdown_role(
            self.name, self.name, self.name, post_shutdown_action='StoppedDeallocated')
        return True

    def reboot(self):
        self.__SMS.restart_role(self.name, self.name, self.name)

    def delete(self):

        properties = self.__SMS.get_deployment_by_name(self.name, self.name)
        media_link = properties.role_list.roles[0].os_virtual_hard_disk.media_link
        storage_name = media_link[media_link.find("//") + 2:media_link.find(".blob")]

        from ext_cloud.Azure.AzureVolumes.AzureVolumes import AzureVolumescls
        volume_service = AzureVolumescls(credentials=self._credentials)
        volumes = volume_service.list_volumes()
        volume_to_be_deleted = None
        for volume in volumes:
            if volume.instance_id == self.name:
                volume_to_be_deleted = volume
                break

        self.__SMS.delete_deployment(self.name, self.name)
        self.__SMS.delete_hosted_service(self.name)
        volume_to_be_deleted.delete()
        # delete image from storge
        from azure.storage import BlobService

        keys = self.__SMS.get_storage_account_keys(storage_name)
        blob_service = BlobService(account_name=storage_name, account_key=keys.storage_service_keys.primary)

        blob_service.delete_container(self.name, fail_not_exist=True)
