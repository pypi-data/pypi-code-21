from azure.servicemanagement import ServiceManagementService
from azure.servicemanagement import OSVirtualHardDisk
from azure.servicemanagement import LinuxConfigurationSet
from azure.servicemanagement import WindowsConfigurationSet
from azure.servicemanagement import ConfigurationSet
from azure.servicemanagement import ConfigurationSetInputEndpoint
from azure.storage import BlobService
from ext_cloud.BaseCloud.BaseCompute.BaseCompute import BaseComputecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls
from ext_cloud.Azure.AzureCompute.AzureInstance import AzureInstancecls


class AzureComputecls(AzureBaseCloudcls, BaseComputecls):

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

    def list_instances(self):
        azure_instances = self.__SMS.list_hosted_services()
        instances = []
        for azure_instance in azure_instances:
            instance = AzureInstancecls(azure_instance, credentials=self._credentials)
            instances.append(instance)

        return instances

    def get_instance_by_id(self, instance_id):
        pass

    def get_instances_by_name(self, instance_name):
        pass

    def get_instances_by_tag(self, tag_name, tag_value):
        pass

    def create_instance(self, image_id=None, instancetype_id="ExtraSmall", name=None, storage_name=None, username=None, password=None):
        storage_account = None
        service_name = name

        result = self.__SMS.check_hosted_service_name_availability(service_name)
        if result is False:
            msg = "Hosted service with name:{} exists. please use different name".format(name)
            raise Exception(msg)

        azure_storages = self.__SMS.list_storage_accounts()
        if storage_name is None:
            # storage name not provided,pick any storage account as stroage
            # account is an expensive operation
            for azure_storage in azure_storages:
                storage_account = azure_storage
                storage_name = storage_account.service_name
                break
        else:
            for azure_storage in azure_storages:
                if azure_storage.service_name == storage_name:
                    storage_account = azure_storage
                    break
        if storage_account is None:
            if storage_name is None:
                storage_name = service_name

            response = self.__SMS.create_storage_account(storage_name, service_name, service_name, location=self._credentials['region_name'])
            import time
            # use index loop name as _ instead of i or j to keep pylinit happy
            for _ in range(60):
                status = self.__SMS.get_operation_status(response.request_id)
                time.sleep(2)
                if not status == "InProgress":
                    break

        keys = self.__SMS.get_storage_account_keys(storage_name)
        blob_service = BlobService(account_name=storage_name, account_key=keys.storage_service_keys.primary)

        blob_service.create_container(service_name)
        target_blob_name = name + ".vhd"
        os_image_url = "http://{}.blob.core.windows.net/{}/{}".format(storage_name, service_name, target_blob_name)

        azure_images = self.__SMS.list_os_images()
        image = None
        for azure_image in azure_images:
            if azure_image.name == image_id:
                image = azure_image
                break

        os_config = None
        endpoint_config = ConfigurationSet()
        endpoint_config.configuration_set_type = 'NetworkConfiguration'

        if image.os == 'Windows':
            os_config = WindowsConfigurationSet(computer_name=name, admin_username=username, admin_password=password)
            os_config.domain_join = None

            endpoint1 = ConfigurationSetInputEndpoint(name='rdp', protocol='tcp', port='3389', local_port='3389', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)

            endpoint2 = ConfigurationSetInputEndpoint(name='web', protocol='tcp', port='80', local_port='80', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)

            endpoint_config.input_endpoints.input_endpoints.append(endpoint1)
            endpoint_config.input_endpoints.input_endpoints.append(endpoint2)

            from azure.servicemanagement import WinRM
            from azure.servicemanagement import Listener
            endpoint_config.win_rm = WinRM()
            listner = Listener(protocol='http')
            os_config.win_rm.listeners.listeners.append(listner)
        if image.os == 'Linux':
            os_config = LinuxConfigurationSet(host_name=name, user_name=username,
                                              user_password=password,
                                              disable_ssh_password_authentication=False)

            os_config.domain_join = None
            endpoint1 = ConfigurationSetInputEndpoint(name='ssh', protocol='tcp', port='22', local_port='22', load_balanced_endpoint_set_name=None, enable_direct_server_return=False)
            endpoint_config.input_endpoints.input_endpoints.append(endpoint1)

        os_hd = OSVirtualHardDisk(image_id, os_image_url, disk_label=target_blob_name)

        self.__SMS.create_hosted_service(service_name, service_name, location=self._credentials['region_name'])
        # service_account = self.__SMS.get_hosted_service_properties(service_name)

        self.__SMS.create_virtual_machine_deployment(service_name=service_name, deployment_name=service_name, deployment_slot='production', label=service_name, role_name=service_name, system_config=os_config, os_virtual_hard_disk=os_hd, role_size=instancetype_id, network_config=endpoint_config)

        new_service = self.__SMS.get_hosted_service_properties(service_name)
        azure_instance = AzureInstancecls(new_service, credentials=self._credentials)
        return azure_instance

    def create_instances(self, count=1, image_id=None, key_name=None, security_groups=None, instancetype_id='Small', name=None, zone=None, subnet_id=None, private_ips=None, user_data=None):
        pass
    # --- Key pair operations -----------

    def list_keypairs(self):
        pass

    def create_keypair(self, name=None):
        pass

    def import_keypair(self, name=None, public_key=None):
        pass

    def get_key_pair_by_name(self, keyname):
        pass

    # --- Instance type operations --------------

    def list_instancetypes(self):
        from ext_cloud.Azure.AzureCompute.AzureInstanceTypeDict import INSTANCE_TYPES
        from ext_cloud.Azure.AzureCompute.AzureInstanceType import AzureInstanceTypecls

        azure_instancetypes_dict = INSTANCE_TYPES
        instancetypes = []
        for azure_instancetype in azure_instancetypes_dict:
            instancetype = AzureInstanceTypecls(azure_instancetypes_dict[azure_instancetype], credentials=self._credentials)
            instancetypes.append(instancetype)
        return instancetypes

    def get_matching_instancetype(self, cpus=1, memory=0.5, disk=2):
        pass

    # -- Security group operations -----------

    def list_security_groups(self):
        pass

    def get_security_group_by_id(self, sg_id):
        pass

    def create_security_group(self, name=None, description=None):
        pass
