import hashlib
import crcmod
from io import BufferedReader
from .s3_etag import S3Etag

"""
A file-like object that computes checksums for the data written to it, discarding the actual data.
"""


class ChecksummingSink:

    def __init__(self, *args, **kwargs):
        self._hashers = dict(crc32c=crcmod.predefined.Crc("crc-32c"),
                             sha1=hashlib.sha1(),
                             sha256=hashlib.sha256(),
                             s3_etag=S3Etag())

    def write(self, data):
        for hasher in self._hashers.values():
            hasher.update(data)

    def get_checksums(self):
        checksums = {}
        checksums.update({name: hasher.hexdigest() for name, hasher in self._hashers.items()})
        return checksums

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass
