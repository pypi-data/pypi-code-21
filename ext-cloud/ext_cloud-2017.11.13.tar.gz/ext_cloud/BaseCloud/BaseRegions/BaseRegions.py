from abc import ABCMeta, abstractmethod


class BaseRegionscls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_regions(self):
        pass

    @abstractmethod
    def get_region_by_id(self, instance_id):
        pass

    @abstractmethod
    def get_region_by_name(self, instance_name):
        pass
