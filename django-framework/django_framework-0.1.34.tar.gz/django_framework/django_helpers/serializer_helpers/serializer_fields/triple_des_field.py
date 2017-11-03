from rest_framework import serializers
from django_framework.helpers.security_helpers import encrypter, decrypter
import arrow

KEY = 'test' ## this should be moved to settings...
IV = 'aya'

class TripleDesField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        
        self.allow_unencrypt = kwargs.pop('allow_unencrypt', False)
        super(TripleDesField, self).__init__(*args, **kwargs)
        
    def to_representation(self, value):
        if value == None:
            response = None
        else:
            if self.allow_unencrypt == True:
                response = decrypter(value,  des_key = KEY, iv = IV)
            
            else:
                response = value
            
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = encrypter(data,  des_key = KEY, iv = IV)
        return response


    