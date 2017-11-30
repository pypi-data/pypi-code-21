from rest_framework import serializers

import arrow

class UnixEpochDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value == None:
            response = None
        else:
            response = arrow.get(value).timestamp
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = arrow.get(data).datetime
        return response

class UnixEpochDateTimeFieldHuman(serializers.SerializerMethodField):
    def __init__(self, source_name, *arg, **kwargs):
        self.source_name = source_name
        super(UnixEpochDateTimeFieldHuman, self).__init__(*arg, **kwargs)
        
    
    def to_representation(self, value):
        atime = getattr(value, self.source_name) # get the value of interest!
        
        if atime == None:
            response = None
        else:
            response = arrow.get(atime).format('YYYY-MM-DD HH:mm:ss') # 24 hour formatted human readable time.  It is in UTC
        return response






    