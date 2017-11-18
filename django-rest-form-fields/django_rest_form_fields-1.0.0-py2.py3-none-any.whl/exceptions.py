"""
This file contains exceptions, raised by forms.* modules
"""
from typing import List

from django.core.exceptions import ValidationError


class FileSizeError(ValidationError):
    def __init__(self, allowed_size, file_size):  # type: (int, int) -> None
        self.message = "File is too big, max %d bytes are allowed (it has %d bytes)." % (allowed_size, file_size)


class FileTypeError(ValidationError):
    def __init__(self, extension, valid_extensions):  # type: (str, List[str]) -> None
        self.message = "File has invalid type, only [%s] are allowed (it has '%s')." \
                       % (', '.join(valid_extensions), extension)
