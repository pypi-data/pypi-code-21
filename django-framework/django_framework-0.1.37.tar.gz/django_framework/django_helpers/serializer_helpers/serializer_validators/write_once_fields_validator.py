from rest_framework import serializers

class WriteOnceFieldsValidator(object):
    # class level validator
    def __init__(self, fields=None):
        # write_once_fields passed in
        self.fields = fields

    def set_context(self, serializer):
        # we get the serializer's instance
        # to check if 'update' or a 'create'
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs):
        if self.instance:  # this is an update
            
            # if unique_together is set in Model.meta, then Django always passes it in...even on updates...
            # this screens for that case. by allowing it to pass as long as it is the same value.
            
            # check all variables that are being upated!
            failed_write_once_fields = []
            for attr, value in attrs.items():
                # self.fields is the write_once only variables
                if attr in self.fields and getattr(self.instance, attr) != value:
                    failed_write_once_fields.append(attr)

#             intersection = set(self.fields).intersection(attrs.keys())
            if failed_write_once_fields:
                error_message = "The following fields can only be set on creation: {fields}."
                raise serializers.ValidationError(error_message.format(fields=failed_write_once_fields))