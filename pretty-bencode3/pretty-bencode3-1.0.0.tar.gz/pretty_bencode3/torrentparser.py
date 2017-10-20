# -*-coding: utf-8 -*-
from .belement import Bdict, BencodeError


class BitTorrent:
    def __init__(self, io):
        self.content = open(io, "rb").read() if type(io) == str else io.read()
        self.bt = Bdict.load(self.content)[0]

    @property
    def infohash(self):
        from hashlib import sha1
        # infohash = SHA1(info_chunk)
        if b"info" in self.content:
            info_chunk_slice = slice(self.content.find(b"info") + 4,
                                     self.content.find(b"nodes") - 2 if b"nodes" in self.content else -1)
            return sha1(self.content[info_chunk_slice]).hexdigest()
        else:
            raise BencodeError("Invalid torrent file")

    @property
    def magnet(self):
        return "magnet:?xt=urn:btih:{0}".format(self.infohash.upper())

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, "bt")[item]
        except KeyError:
            raise AttributeError("{0} object has no attribute '{1}'".format(self.__class__.__name__, item))

    def __getitem__(self, item):
        return self.bt.__getitem__(item)

    def __setitem__(self, key, value):
        return self.bt.__setitem__(key, value)

    def __delattr__(self, item):
        return self.bt.__delitem__(item)

    def dump(self):
        return self.bt.dump()

    def __str__(self):
        return str(self.bt)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, repr(self.bt))

    def save(self, io):
        with open(io, "wb") as output:
            output.write(self.bt.dump())