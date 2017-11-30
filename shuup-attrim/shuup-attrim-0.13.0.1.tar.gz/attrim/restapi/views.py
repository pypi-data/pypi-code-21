from rest_framework import viewsets
from shuup.api.mixins import ProtectedModelViewSetMixin, PermissionHelperMixin
from shuup.core.models import ProductType

from attrim.models import Option, Class
from attrim.restapi.serializers.cls import ClassSerializer
from attrim.restapi.serializers.option import OptionSerializer
from attrim.restapi.serializers.product_type import ProductTypeSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects
    serializer_class = OptionSerializer


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects
    serializer_class = ClassSerializer


class ProductTypeViewSet(PermissionHelperMixin, ProtectedModelViewSetMixin, viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
