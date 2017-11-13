from abc import ABCMeta, abstractmethod


class BaseImagescls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_images(self):
        pass

    @abstractmethod
    def create_image_from_instance(self, instance_id, name=None):
        pass
