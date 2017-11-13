class BaseResourceUsagecls:

    def __init__(self, **kwargs):
        self.__available_vms = None
        self.__free_vms = None
        self.__used_vms = None
        self.__deleted_vms = None
        self.__available_memory = None
        self.__free_memory = None
        self.__used_memory = None
        self.__hours_memory = None
        self.__available_disk = None
        self.__used_disk = None
        self.__free_disk = None
        self.__hours_disk = None
        self.__availble_cpus = None
        self.__used_cpus = None
        self.__free_cpus = None
        self.__hours_cpus = None

        for key in kwargs:
            attr = '_' + self.__class__.__name__ + '__' + key
            setattr(self, attr, kwargs[key])

    @property
    def available_vms(self):
        return self.__available_vms

    @property
    def free_vms(self):
        return self.__free_vms

    @property
    def used_vms(self):
        return self.__used_vms

    @property
    def deleted_vms(self):
        return self.__deleted_vms

    @property
    def available_memory(self):
        return self.__available_memory

    @property
    def free_memory(self):
        return self.__free_memory

    @property
    def used_memory(self):
        return self.__used_memory

    @property
    def hours_memory(self):
        return self.__hours_memory

    @property
    def available_disk(self):
        return self.__available_disk

    @property
    def used_disk(self):
        return self.__used_disk

    @property
    def free_disk(self):
        return self.__free_disk

    @property
    def hours_disk(self):
        return self.__hours_disk

    @property
    def availble_cpus(self):
        return self.__availble_cpus

    @property
    def used_cpus(self):
        return self.__used_cpus

    @property
    def free_cpus(self):
        return self.__free_cpus

    @property
    def hours_cpus(self):
        return self.__hours_cpus
