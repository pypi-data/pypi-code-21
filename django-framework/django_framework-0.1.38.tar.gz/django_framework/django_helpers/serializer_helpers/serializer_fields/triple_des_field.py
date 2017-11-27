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
    
    
def get_encryption_default():
    return ENCRYPTION_IV, ENCRYPTION_KEY


class TripleDesField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        
        # should the serializer convert to plain text
        # note if this is set to True, will override show_partial
        self.allow_unencrypt = kwargs.pop('allow_unencrypt', False)
        
        # None or Integer, determines how many letters to convert to plain text for the end of the word
        # will always prepend 10 '*'.  Note that for short passwords, a large show_partial will show the entire value
        self.show_partial = kwargs.pop('show_partial', None)
        
        # the IV to use
        self.IV = kwargs.pop('IV', ENCRYPTION_IV)
        
        # the KEY to use
        self.KEY = kwargs.pop('KEY', ENCRYPTION_KEY)
        
        
        super(TripleDesField, self).__init__(*args, **kwargs)
        
    def to_representation(self, value):
        if value == None:
            response = None
        else:
            
            if self.allow_unencrypt == True:
                # encrypt the data!
                response = decrypter(value,  des_key = self.KEY, iv = self.IV)
                    
            elif self.show_partial != None:
                # partially unencrypt data.  If 0, show 0 values
                response = decrypter(value,  des_key = self.KEY, iv = self.IV)
                    # always have 10 stars, and show the last X characters. Note for short values, it could expose all of it!!
                if self.show_partial == 0:
                    response = '*' * 10
                else:
                    response = '*' * 10 + response[-1*int(self.show_partial):]
            else:
                # unencrypt nothing! show the full encrypted string
                response = value
            
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = encrypter(data,  des_key = self.KEY, iv = self.IV)
        return response