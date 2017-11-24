from rest_framework import viewsets

from attrim.models import Option, Class
from attrim.restapi.serializers.models import OptionSerializer
from attrim.restapi.serializers.models import ClassSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects
    serializer_class = OptionSerializer


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects
    serializer_class = ClassSerializer
