from abc import ABCMeta, abstractproperty


class BaseHypervisorcls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def state(self):
        pass

    @abstractproperty
    def arch(self):
        pass

    @abstractproperty
    def host_name(self):
        pass

    @abstractproperty
    def short_host_name(self):
        pass

    @abstractproperty
    def cpus(self):
        pass

    @abstractproperty
    def vcpus_used(self):
        pass

    @abstractproperty
    def disk_gb(self):
        pass

    @abstractproperty
    def disk_used_gb(self):
        pass

    @abstractproperty
    def free_disk_gb(self):
        pass

    @abstractproperty
    def memory_mb(self):
        pass

    @abstractproperty
    def memory_used_mb(self):
        pass

    @abstractproperty
    def memory_free_mb(self):
        pass

    @abstractproperty
    def running_vms(self):
        pass
