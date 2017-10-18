from abc import ABCMeta, abstractmethod


class BaseVolumescls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_volumes(self):
        pass

    @abstractmethod
    def create_volume(self, size=2, name=None):
        pass

    @abstractmethod
    def attach_volume(self, volume_id=None, instance_id=None, device_path=None):
        pass

    @abstractmethod
    def detach_volume(self, volume_id=None, instance_id=None):
        pass

    @abstractmethod
    def list_snapshots(self):
        pass

    @abstractmethod
    def delete_volume_by_id(self, volume_id):
        pass

    @abstractmethod
    def create_snapshot(self, volume_id, name=None, description=None):
        pass

    @abstractmethod
    def get_volumes_by_tag(self, tag_name, tag_value):
        pass

    @abstractmethod
    def delete_snapshot_by_id(self, snapshot_id):
        pass
