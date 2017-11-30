from rest_framework import serializers
from django_framework.helpers.security_helpers import encrypter, decrypter
from django_framework.helpers.security_helpers import md5_hasher
import arrow

from django.conf import settings

try:
    ENCRYPTION_SALT  = settings.ENCRYPTION_SALT
except Exception as e:
    print(e, 'reverting to default')
    ENCRYPTION_SALT = None  # this is probably bad but we'll use this for now.

def get_hash_default():
    return ENCRYPTION_SALT

class HashField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        
        self.SALT = kwargs.pop('salt', ENCRYPTION_SALT)
        super(HashField, self).__init__(*args, **kwargs)
        
#     def to_representation(self, value):
#         '''We problbably do not need to override the base version here.'''
#         return value

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = md5_hasher(uid = data, saltz = self.SALT, label = True)
        return response


    