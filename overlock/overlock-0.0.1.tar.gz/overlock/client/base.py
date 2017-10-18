from abc import ABCMeta, abstractmethod


class BaseClient(metaclass=ABCMeta):

    @abstractmethod
    def update_state(self, new_state):
        """ Update existing state with new state """

    @abstractmethod
    def update_metadata(self, new_metadata):
        """ Update metadata with new metadata """

    @abstractmethod
    def update_lifecycle(self, key_type, comment):
        """ Update the lifecycle of the program """

    @abstractmethod
    def associate_device(self, device_id):
        """ Associate another device with this client """
