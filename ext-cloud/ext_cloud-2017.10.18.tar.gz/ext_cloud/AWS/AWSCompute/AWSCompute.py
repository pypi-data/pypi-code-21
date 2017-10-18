from ext_cloud.BaseCloud.BaseCompute.BaseCompute import BaseComputecls
from ext_cloud.AWS.AWSCompute.AWSInstance import AWSInstancecls
from ext_cloud.AWS.AWSCompute.AWSInstanceType import AWSInstanceTypecls
from ext_cloud.AWS.AWSCompute.AWSSecurityGroup import AWSSecurityGroupcls
from ext_cloud.AWS.AWSCompute.AWSKeypair import AWSKeypaircls
from boto import ec2
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.AWS.AWSCompute.AWSInstanceTypeDict import INSTANCE_TYPES


class AWSComputecls(AWSBaseCloudcls, BaseComputecls):

    def __init__(self, **kwargs):
        self.__ec2 = None
        self._credentials = kwargs

    @property
    def __EC2(self):
        return self.__ec2

    @__EC2.getter
    def __EC2(self):
        if self.__ec2 is None:
            self.__ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__ec2

    # ------ instance  opertations ----------------------------------------

    def list_instances(self):
        aws_reservations = self.__EC2.get_all_instances()
        instances = []
        if aws_reservations is None:
            return instances
        for aws_reservation in aws_reservations:
            aws_instances = aws_reservation.instances
            for aws_instance in aws_instances:
                instance = AWSInstancecls(aws_instance, credentials=self._credentials)
                instances.append(instance)

        return instances

    def get_instance_by_id(self, instance_id):
        fetched_instance = self.__EC2.get_only_instances(instance_ids=instance_id)[0]
        if fetched_instance is None:
            return None
        instance = AWSInstancecls(fetched_instance, credentials=self._credentials)
        return instance

    def get_instances_by_name(self, instance_name):
        return self.get_instances_by_tag('Name', instance_name)

    def get_instances_by_tag(self, tag_name, tag_value):
        instance_filters = {'tag-key': tag_name, 'tag-value': tag_value}
        instances = []
        aws_instances = self.__EC2.get_only_instances(filters=instance_filters)
        if aws_instances is None:
            return instances
        for aws_instance in aws_instances:
            instance = AWSInstancecls(aws_instance, credentials=self._credentials)
            instances.append(instance)

        return instances

    def create_instance(self, image_id=None, key_name=None, security_groups=None, security_group_ids=None, instancetype_id="m1.small", name=None, zone=None, subnet_id=None, private_ips=None, user_data=None):
        instances = self.create_instances(count=1, image_id=image_id, key_name=key_name, security_groups=security_groups, security_group_ids=security_group_ids, instancetype_id=instancetype_id, name=name, zone=zone, subnet_id=subnet_id, private_ips=private_ips, user_data=user_data)

        if len(instances) > 0:
            return instances[0]
        else:
            return []

    def create_instances(self, count=1, image_id=None, key_name=None, security_groups=None, security_group_ids=None, instancetype_id='m1.small', name=None, zone=None, subnet_id=None, private_ips=None, user_data=None):

        if zone is None:
            aws_zones = self.__EC2.get_all_zones()
            zone = aws_zones[0].name
            if subnet_id is None:
                aws_zones = self.__EC2.get_all_zones()
                zone = aws_zones[0].name
            else:
                from ext_cloud.AWS.AWSNetworks.AWSNetworks import AWSNetworkscls
                subnet = subnet = AWSNetworkscls(**self._credentials).get_subnet_by_id(subnet_id)
                zone = subnet.zone

        # if vm need to be booted in subnet, use security_group_id instead of
        # security_group name.
        if subnet_id is None:
            aws_reservation = self.__EC2.run_instances(image_id, key_name=key_name, security_groups=security_groups, min_count=count, max_count=count, instance_type=instancetype_id, placement=zone, subnet_id=subnet_id, private_ip_address=private_ips, user_data=user_data)
        else:
            aws_reservation = self.__EC2.run_instances(image_id, key_name=key_name, security_group_ids=security_group_ids, min_count=count, max_count=count, instance_type=instancetype_id, placement=zone, subnet_id=subnet_id, private_ip_address=private_ips, user_data=user_data)

        instances = []
        aws_instances = aws_reservation.instances
        for aws_instance in aws_instances:
            instance = AWSInstancecls(aws_instance, credentials=self._credentials)
            if name is not None:
                instance.name = name
            instances.append(instance)

        return instances

    def stop_instances(self, instance_ids=None):
        return self.__EC2.stop_instances(instance_ids=instance_ids)

    def start_instances(self, instance_ids=None):
        return self.__EC2.start_instances(instance_ids=instance_ids)

    def delete_instances(self, instance_ids=None):
        return self.__EC2.terminate_instances(instance_ids=instance_ids)

    # ------ Key pair opertations ----------------------------------------

    def list_keypairs(self):
        aws_keypairs = self.__EC2.get_all_key_pairs()
        keypairs = []
        for aws_keypair in aws_keypairs:
            keypair = AWSKeypaircls(aws_keypair, credentials=self._credentials)
            keypairs.append(keypair)
        return keypairs

    def create_keypair(self, name=None):
        aws_keypair = self.__EC2.create_key_pair(name)
        keypair = AWSKeypaircls(aws_keypair, credentials=self._credentials)
        return keypair

    def import_keypair(self, name=None, public_key=None):
        aws_keypair = self.__EC2.import_key_pair(name, public_key)
        keypair = AWSKeypaircls(aws_keypair, credentials=self._credentials)
        return keypair

    def get_key_pair_by_name(self, keyname):
        aws_keypair = self.__EC2.get_key_pair(keyname=keyname)
        if aws_keypair is None:
            return None
        keypair = AWSKeypaircls(aws_keypair, credentials=self._credentials)
        return keypair

    # ------ Instance Type opertations ----------------------------------------

    def list_instancetypes(self):
        aws_instancetypes_dict = INSTANCE_TYPES
        instancetypes = []
        for aws_instancetype in aws_instancetypes_dict:
            instancetype = AWSInstanceTypecls(aws_instancetypes_dict[aws_instancetype], credentials=self._credentials)
            instancetypes.append(instancetype)
        return instancetypes

    def get_instancetype_by_id(self, instancetype_id):
        instance_types = self.list_instancetypes()
        for instance_type in instance_types:
            if instance_type.id == instancetype_id:
                return instance_type

        return None

    def get_matching_instancetype(self, cpus=1, memory=0.5, disk=2):
        instance_types = self.list_instancetypes()
        if len(instance_types) == 0:
            return None
        best_match = None
        for instance_type in instance_types:
            if instance_type.cpus >= cpus and instance_type.memory >= memory and instance_type.disk >= disk:
                best_match = instance_type

        if best_match is None:
            return None
        for instance_type in instance_types:
            if instance_type.cpus >= cpus and instance_type.memory >= memory and instance_type.disk >= disk:
                if instance_type.cpus < best_match.cpus:
                    best_match = instance_type
                elif instance_type.cpus == best_match.cpus:
                    if instance_type.memory < best_match.cpus:
                        best_match = instance_type
                    elif instance_type.memory == best_match.memory:
                        if instance_type.disk < best_match.disk:
                            best_match = instance_type
        return best_match

    # --------------  Security group operations -------------------------------

    def list_security_groups(self):
        aws_security_groups = self.__EC2.get_all_security_groups()
        security_groups = []
        for aws_security_group in aws_security_groups:
            security_group = AWSSecurityGroupcls(aws_security_group, credentials=self._credentials)
            security_groups.append(security_group)

        return security_groups

    def get_security_group_by_id(self, sg_id):
        aws_security_groups = self.__EC2.get_all_security_groups(group_ids=sg_id)
        if len(aws_security_groups) < 1:
            return None
        aws_security_group = aws_security_groups[0]
        security_group = AWSSecurityGroupcls(aws_security_group, credentials=self._credentials)
        return security_group

    def create_security_group(self, name=None, description=None, network_id=None):
        aws_security_group = self.__EC2.create_security_group(name, description, vpc_id=network_id)
        security_group = AWSSecurityGroupcls(aws_security_group, credentials=self._credentials)
        return security_group
