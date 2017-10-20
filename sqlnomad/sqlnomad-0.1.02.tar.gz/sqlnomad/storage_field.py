# coding=utf-8
from typing import NamedTuple

from .custom_types import FieldStorageName, FieldDisplayName


class StorageField(NamedTuple):

    storage_name: FieldStorageName
    display_name: FieldDisplayName

    def __str__(self):
        return f"""
        StorageField
            storage_name: {self.storage_name}
            display_name: {self.display_name}
        """

    def __repr__(self):
        return f"""
            StorageField(
                storage_name={self.storage_name!r},
                display_name={self.display_name!r}
            )
        """

