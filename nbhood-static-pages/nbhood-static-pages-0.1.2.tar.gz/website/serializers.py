from django.conf import settings
from rest_framework.serializers import ModelSerializer, StringRelatedField
from rest_framework import fields, serializers
# from django.utils.text import slugify
import models
from collections import OrderedDict

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = '__all__'

class gTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.gTitle
        fields = '__all__'

    def to_representation(self, obj):
        return (obj.name, obj.value)

class gTextboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.gTextbox
        fields = '__all__'

    def to_representation(self, obj):
        return (obj.name, obj.value)

class ComponentSerializer(serializers.ModelSerializer):
    titles = gTitleSerializer(many=True)
    textboxs = gTextboxSerializer(many=True)
    class Meta:
        model = models.Component
        fields = ('name', 'titles', 'textboxs')

    def to_representation(self, obj):
        serialized_obj = super(ComponentSerializer, self).to_representation(obj)
        result = {}
        data = {}
        for key, value in serialized_obj["titles"]:
            data[key] = value
        for key, value in serialized_obj["textboxs"]:
            data[key] = value

        # data[slugify(title["name"])] = title["value"]

        result[serialized_obj["name"]] = data
        return (serialized_obj["name"], data)

class PageSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True)
    class Meta:
        model = models.Page
        fields = '__all__'

    def to_representation(self, obj):
        serialized_obj = super(PageSerializer, self).to_representation(obj)
        data = {}
        data["name"] = obj.name
        for key, value in serialized_obj["components"]:
            data[key] = value

        return data       
