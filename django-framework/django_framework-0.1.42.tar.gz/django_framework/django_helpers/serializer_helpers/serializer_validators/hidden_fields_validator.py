from rest_framework import serializers


class HiddenFieldsValidator(object):
    # this did not function properly!
    def __init__(self, fields=None):
        # hidden fields passed in
        self.fields = fields

    def __call__(self, attrs):
        # class level validator, if any are passed in throw an error
        if set(self.fields).intersection(attrs.keys()):
            error_message = "You shouldn't be accessing those fields. Admin has been notified."
            raise serializers.ValidationError(detail=error_message)
