# coding=utf-8
from typing import NamedTuple

from .custom_types import FieldStorageName, FieldDisplayName, \
    FieldDataType


class StorageField(NamedTuple):

    storage_name: FieldStorageName
    display_name: FieldDisplayName
    data_type:    FieldDataType=FieldDataType.STRING
    editable:     bool=True
    visible:      bool=True

    def __str__(self):
        return f"""
        StorageField
            storage_name: {self.storage_name}
            display_name: {self.display_name}
            data_type:    {self.data_type}
            editable:     {self.editable}
            visible:      {self.visible}
        """

    def __repr__(self):
        return f"""
            StorageField(
                storage_name={self.storage_name!r},
                display_name={self.display_name!r},
                data_type={self.data_type!r},
                editable={self.editable!r},
                visible={self.visible!r}
            )
        """

