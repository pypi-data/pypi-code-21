
##### 
'''Trying to write a validator that is auto dadded to serializer fields so when you write to it
it throws an error.  we skip this for now.'''
# from rest_framework import serializers
# 
# class AltValidator(object):
#     # class level validator
#     def __init__(self, fields=None):
#         # write_once_fields passed in
#         self.fields = fields
# 
#     def set_context(self, serializer):
#         # we get the serializer's instance
#         # to check if 'update' or a 'create'
#         self.instance = getattr(serializer, "instance", None)
# 
#     def __call__(self, attrs):
#         print(attrs, 'boopa')
#         
#         
#         
#         if self.instance:  # this is an update
#             # throw error if trying to update write_once_fields
#             intersection = set(self.fields).intersection(attrs.keys())
#             if intersection:
#                 error_message = "The following fields are for read only: {fields}."
#                 raise serializers.ValidationError(error_message.format(fields=intersection))
