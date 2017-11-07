from collections import namedtuple
from munch import Munch


class ChargehoundObject(Munch):
    pass


class List(ChargehoundObject):
    pass


class Dispute(ChargehoundObject):
    pass


class Product(ChargehoundObject):
    pass


class Response(ChargehoundObject):
    pass


HTTPResponse = namedtuple('HTTPResponse', 'status')
