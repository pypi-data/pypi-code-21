#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helperlib.binary import Structure
import struct
import argparse
import zlib
import sys


class FileHeader3(Structure):
    _fields_ = [
        ('7s', 'magic'),
        ('1s', 'version'),
        ('24s', 'unknown'),
        ('<I', 'num_elements'),
        ('<I', 'num_elements2'),
        ('2s', 'unknown2'),
    ]


class ItemHeader3(Structure):
    _fields_ = [
        ('12s', 'unknown'),
        ('<I', 'size'),
        ('<I', 'maybe_type'),
        ('2s', 'unknown2')
    ]


class FileHeader5(Structure):
    _fields_ = [
        ('7s', 'magic'),
        ('1s', 'version'),
        ('28s', 'unknown'),
        ('<I', 'num_elements'),
        ('13s', 'unknown2'),
    ]


class ItemHeader5(Structure):
    _fields_ = [
        ('20s', 'unknown'),
        ('<I', 'size'),
        ('<I', 'maybe_type'),
        ('1s', 'unknown2')
    ]


class RBSFile:
    def __init__(self, fname_object=None):
        self.fp = None
        self.name = None
        self.__i = 0
        if fname_object is not None:
            self.open(fname_object)

    def open(self, fname_object):
        self.close()

        if isinstance(fname_object, str):
            self.name = fname_object
            self.fp = open(fname_object, 'rb')
        else:
            self.fp = fname_object

        assert self.fp.read(7) == b'UTCRBES', 'File magic does not match'
        try:
            version = self.fp.read(1).decode()
        except UnicodeDecodeError:
            raise IOError("Invalid version byte as offset {}".format(self.fp.tell() - 1))
        self.fp.seek(0)

        mymodule = sys.modules[__name__]

        fileheader_class = 'FileHeader{}'.format(version)
        itemheader_class = 'ItemHeader{}'.format(version)

        if not (hasattr(mymodule, fileheader_class) and hasattr(mymodule, itemheader_class)):
            raise IOError("Invalid version {}. Header structure not know. Please report to the github project")

        self.file_header = getattr(mymodule, fileheader_class).from_file(self.fp)
        self.ItemHeaderClass = getattr(mymodule, itemheader_class)
        self._start = self.fp.tell()


    def close(self):
        if self.fp is not None:
            self.fp.close()
            self.fp = None
            self.name = None

    def __iter__(self):
        if hasattr(self.fp, 'seek'):
            self.fp.seek(self._start)
            self.__i = 0
        return self
    
    def __next__(self):
        if self.__i >= self.file_header.num_elements:
            raise StopIteration()
        self.__i += 1
        offset = self.fp.tell()
        item_header = self.ItemHeaderClass.from_file(self.fp)
        if item_header.size > 0:
            data = self.fp.read(item_header.size)
            uncompressed = zlib.decompress(data, wbits=-zlib.MAX_WBITS)
        else:
            data = b''
            uncompressed = b''
        item_header.offset = offset
        item_header.data = data
        item_header.uncompressed = uncompressed
        return item_header

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    @classmethod
    def arparse_open(cls, fname):
        try:
            return cls(fname)
        except Exception as ex:
            raise argparse.ArgumentTypeError("Invalid file '{}' ({})".format(fname, str(ex)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('IN')

    args = parser.parse_args()

    with RBSFile(args.IN) as rbs:
        for i, item in enumerate(rbs, 1):
            print('#####################')
            print("Offset: 0x{0:x} {0}".format(item.offset))
            print("Size: 0x{0:x} {0}".format(item.size))
            print("Type?: {}".format(item.maybe_type))
            print("Data:", item.uncompressed.decode())


if __name__ == "__main__":
    main()
