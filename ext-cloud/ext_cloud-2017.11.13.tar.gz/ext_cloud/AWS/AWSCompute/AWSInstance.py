from ext_cloud.BaseCloud.BaseCompute.BaseInstance import BaseInstancecls
from boto import ec2
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSInstancecls(AWSBaseCloudcls, BaseInstancecls):

    __aws_instance = None
    _ec2 = None
    _compute = None

    def __init__(self, *arg, **kwargs):
        self.__aws_instance = arg[0]
        self._aws_ref = arg[0]
        name = None
        if 'Name' in self.__aws_instance.tags:
            name = self.__aws_instance.tags['Name']

        super(AWSInstancecls, self).__init__(id=self.__aws_instance.id, name=name, credentials=kwargs['credentials'])

    # override name property
    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.__aws_instance.add_tag('Name', value)
        self._name = value

    @property
    def _EC2(self):
        return self._ec2

    @_EC2.getter
    def _EC2(self):
        if self._ec2 is None:
            self._ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials[
                                              'username'], aws_secret_access_key=self._credentials['password'])
        return self._ec2

    @property
    def _COMPUTE(self):
        return self._compute

    @_COMPUTE.getter
    def _COMPUTE(self):
        if self._compute is None:
            from ext_cloud.AWS.AWSCompute.AWSCompute import AWSComputecls
            self._compute = AWSComputecls(**self._credentials)
        return self._compute

    @property
    def size(self):
        pass

    @property
    def state(self):
        return self.__aws_instance.state

    @property
    def image_id(self):
        return self.__aws_instance.image_id

    @property
    def image_name(self):
        image_list = []
        image_list.append(self.image_id)
        aws_images = self._EC2.get_all_images(image_ids=image_list)
        for aws_image in aws_images:
            return aws_image.name
        return None

    @property
    def arch(self):
        return self.__aws_instance.architecture

    @property
    def network_id(self):
        return self.__aws_instance.vpc_id

    @property
    def subnet_id(self):
        return self.__aws_instance.subnet_id

    @property
    def private_ip(self):
        return self.__aws_instance.private_ip_address

    @property
    def public_ip(self):
        return self.__aws_instance.ip_address

    @property
    def keypair_name(self):
        return self.__aws_instance.key_name

    @property
    def dns_name(self):
        return self.__aws_instance.dns_name

    @property
    def creation_time(self):
        import datetime
        dt = datetime.datetime.strptime(
            self.__aws_instance.launch_time, '%Y-%m-%dT%H:%M:%S.%fZ')

        return dt.strftime("%B %d, %Y %I:%M:%S %p")

    @property
    def os_type(self):
        return self.__aws_instance.platform

    @property
    def instance_type(self):
        return self.__aws_instance.instance_type

    @property
    def cpus(self):
        instance_type = self._COMPUTE.get_instancetype_by_id(
            self.instance_type)
        if instance_type is None:
            return
        return instance_type.cpus

    @property
    def memory(self):
        instance_type = self._COMPUTE.get_instancetype_by_id(
            self.instance_type)
        if instance_type is None:
            return
        return instance_type.memory

    def start(self):
        return self.__aws_instance.start()

    def stop(self):
        return self.__aws_instance.stop()

    def reboot(self):
        return self.__aws_instance.reboot()

    def delete(self):
        return self.__aws_instance.terminate()

    def add_security_group(self, security_group):
        pass

    def update(self):
        aws_reservations = self._EC2.get_all_instances(instance_ids=[self.oid])
        self.__aws_instance = aws_reservations[0].instances[0]
        return self
