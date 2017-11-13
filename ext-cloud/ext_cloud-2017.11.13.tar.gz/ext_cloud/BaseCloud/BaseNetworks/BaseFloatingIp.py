from abc import ABCMeta, abstractproperty


class BaseFloatingIpcls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return "floatingip"

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def state(self):
        pass

    @abstractproperty
    def floating_ip_address(self):
        pass

    @abstractproperty
    def fixed_ip_address(self):
        pass

    @abstractproperty
    def tenant_id(self):
        pass

    @abstractproperty
    def nic_id(self):
        pass

    @abstractproperty
    def network_id(self):
        pass

    @abstractproperty
    def subnet_id(self):
        pass
