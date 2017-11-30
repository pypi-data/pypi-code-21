from rest_framework import serializers

class ChoiceSelectionField(serializers.Field):
    
    '''THis allows Choices to be selected via either the number or the string!'''
    def to_internal_value(self, value):
        if value == None:
            return value
        
        choices = self.parent.Meta.model._meta.get_field(self.field_name).choices
        try:
            value = int(value)
            for c in choices:
                if value == c[0]: # always number first!
                    return value
        except ValueError: # int(value) throws a value error
            for c in choices:
                if value == c[1]:
                    return c[0]

        raise serializers.ValidationError('The inputted value could not be mapped to a proper choice!')
    
    def to_representation(self, value):
        if value is None:
            return value
        return int(value)

class ChoiceSelectionFieldHuman(serializers.SerializerMethodField):
    '''Note that this version is READONLY!  We translate an integer to a human readable based on the choices of the field
    '''
    def __init__(self, source_name, *arg, **kwargs):
        self.source_name = source_name
        super(ChoiceSelectionFieldHuman, self).__init__(*arg, **kwargs)
        
        
    
    def to_representation(self, value):
        if value is None:
            return value
        
        choices = self.parent.Meta.model._meta.get_field(self.source_name).choices
        
        value = getattr(value, self.source_name)
        
        for c in choices:
            if value == c[0]:
                return c[1]
        
        raise serializers.ValidationError('The inputted value could not be serialized to text!')
