import copy

from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, TIME)


class ImageDescription(Jsonizable):
    '''
    Description class of image resource type in batchcompute service.
    '''
    resource_name = 'images'
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Description': STRING,
        'Platform': STRING,
        'EcsImageId': STRING,
        'IdempotentToken': STRING,
    }
    required = [
        'Platform',
        'EcsImageId'
    ]

    def __init__(self, dct={}):
        super(ImageDescription, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(ImageDescription, self).setproperty
        new_value = value
        super_set(key, new_value)
ImageDescription = add_metaclass(ImageDescription, CamelCasedClass)
