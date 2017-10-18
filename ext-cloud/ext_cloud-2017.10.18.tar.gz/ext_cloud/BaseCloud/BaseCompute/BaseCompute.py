from abc import ABCMeta, abstractmethod


class BaseComputecls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_instances(self):
        pass

    @abstractmethod
    def get_instance_by_id(self, instance_id):
        pass

    @abstractmethod
    def get_instances_by_name(self, instance_name):
        pass

    @abstractmethod
    def get_instances_by_tag(self, tag_name, tag_value):
        pass

    @abstractmethod
    def create_instance(self, image_id=None, key_name=None,
                        security_groups=None, instancetype_id=None, name=None):
        pass

    @abstractmethod
    def create_instances(self, count=1, image_id=None, key_name=None,
                         security_groups=None, instancetype_id=None, name=None):
        pass

    # ------ Key pair opertations ----------------------------------------
    @abstractmethod
    def list_keypairs(self):
        pass

    @abstractmethod
    def create_keypair(self, name=None):
        pass

    @abstractmethod
    def import_keypair(self, name=None, public_key=None):
        pass

    @abstractmethod
    def get_key_pair_by_name(self, keyname):
        pass

    # --------------  Security group operations -------------------------------
    @abstractmethod
    def list_security_groups(self):
        pass

    @abstractmethod
    def get_security_group_by_id(self, sg_id):
        pass

    @abstractmethod
    def create_security_group(self, name=None, description=None):
        pass

    # ------ Instance Type opertations ----------------------------------------
    @abstractmethod
    def list_instancetypes(self):
        pass

    @abstractmethod
    def get_matching_instancetype(self, cpus=1, memory=0.5, disk=2):
        pass
