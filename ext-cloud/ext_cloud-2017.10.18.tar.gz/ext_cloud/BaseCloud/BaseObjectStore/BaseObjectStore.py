from abc import ABCMeta, abstractmethod, abstractproperty


class BaseObjectStorecls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractmethod
    def get_all_buckets(self):
        pass

    @abstractmethod
    def get_bucket_by_name(self, bucket_name):
        pass

    @abstractmethod
    def create_bucket(self, bucket_name):
        pass
