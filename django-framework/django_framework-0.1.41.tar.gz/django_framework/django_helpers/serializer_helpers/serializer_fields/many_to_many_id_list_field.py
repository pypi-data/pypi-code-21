from rest_framework import serializers

class ManyToManyIdListField(serializers.Field):
    
    def __init__(self, **kwargs):

        if kwargs.get('validators') == None or len(kwargs.get('validators')) == 0:
            kwargs['validators'] = [ManyToManyIdListField.many_to_many_update_format_validation]
        else:
            kwargs['validators'].append(ManyToManyIdListField.many_to_many_update_format_validation)

        super(ManyToManyIdListField, self).__init__(**kwargs)
    
    def to_representation(self, value):
        if hasattr(value, "all"):
            response = [m.id for m in value.all()]

        return response

    def to_internal_value(self, data):
        return data

    @staticmethod
    def many_to_many_update_format_validation(value):
        # we require value to be a dictionary:
        if type(value) is not dict:
            raise serializers.ValidationError('This field can only be updated via a dictionary. {"field_name" : {"update_action" : (add|set|clear|remove), "data" : [<list of PK>, ]}}')
        
        if value.get('update_action') == None:
            raise serializers.ValidationError('Must include key "update_action". {"field_name" : {"update_action" : (add|set|clear|remove), "data" : [<list of PK>, ]}}')
        
        if value.get('update_action') not in ['add', 'set', 'clear', 'remove']:
            raise serializers.ValidationError('update action can only be: add, set, clear or remove')
        
        if value.get('data') == None:
            raise serializers.ValidationError('Must include key "data". {"field_name" : {"update_action" : (add|set|clear|remove), "data" : [<list of PK>, ]}}')
    
        if type(value.get('data')) != list:
            raise serializers.ValidationError('data must be a list. {"field_name" : {"update_action" : (add|set|clear|remove), "data" : [<list of PK>, ]}}')
        
        else:
            for v in value.get('data'):
                if v in [None, '']:
                    raise serializers.ValidationError('data must be a of PK. {"field_name" : {"update_action" : (add|set|clear|remove), "data" : [<list of PK>, ]}}')
    