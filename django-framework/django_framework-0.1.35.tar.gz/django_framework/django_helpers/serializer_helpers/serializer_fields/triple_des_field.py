from django.conf import settings

from rest_framework import serializers

from django_framework.helpers.security_helpers import encrypter, decrypter


try:
    ENCRYPTION_KEY  = settings.ENCRYPTION_KEY
except Exception as e:
    print(e, 'reverting to default')
    ENCRYPTION_KEY = 'test'  # this is probably bad but we'll use this for now.
    
try:
    ENCRYPTION_IV  = settings.ENCRYPTION_IV
except Exception as e:
    print(e, 'reverting to default')
    ENCRYPTION_IV = None
    
class TripleDesField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        
        self.allow_unencrypt = kwargs.pop('allow_unencrypt', False)
        
        self.IV = kwargs.pop('IV', ENCRYPTION_IV)
        self.KEY = kwargs.pop('KEY', ENCRYPTION_KEY)
        
        
        super(TripleDesField, self).__init__(*args, **kwargs)
        
    def to_representation(self, value):
        if value == None:
            response = None
        else:
            if self.allow_unencrypt == True:
                response = decrypter(value,  des_key = self.KEY, iv = self.IV)
            
            else:
                response = value
            
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = encrypter(data,  des_key = self.KEY, iv = self.IV)
        return response
