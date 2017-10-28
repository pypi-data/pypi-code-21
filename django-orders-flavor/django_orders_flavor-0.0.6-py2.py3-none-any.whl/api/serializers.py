from rest_framework import serializers

from core_flavor.drf import fields as core_fields
from core_flavor.drf import serializers as core_serializers
from core_flavor.utils import import_from_string
from core_flavor.utils import round_decimals as rd

from countries import models as countries_models

from .. import models
from .. import settings as orders_settings


class CurrencySerializer(serializers.ModelSerializer):

    class Meta:
        model = countries_models.Currency
        fields = '__all__'


class ItemSerializer(core_serializers.PolymorphicSerializer):
    id = serializers.UUIDField(source='id.hex', read_only=True)
    price = core_fields.DecimalField()
    tax_rate = core_fields.DecimalField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = models.Item
        fields = (
            'id', 'name', 'description', 'price', 'tax_rate', 'amount',
            'image', 'modified', 'created')

        child_serializers = [
            import_from_string(serializer)
            for serializer in orders_settings.ORDERS_ITEMS_SERIALIZERS
        ]

    def get_amount(self, obj):
        return rd(obj.amount)


class ItemInOrderBaseSerializer(serializers.ModelSerializer):
    price = core_fields.DecimalField(read_only=True)


class ItemInOrderWriteOnlySerializer(ItemInOrderBaseSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Item.objects.all(),
        required=True)

    class Meta:
        model = models.ItemInOrder
        fields = ('id', 'quantity', 'price', 'tax_rate', 'created')
        read_only_fields = ('price', 'tax_rate')


class ItemInOrderReadOnlySerializer(ItemInOrderBaseSerializer):
    item = ItemSerializer()

    class Meta:
        model = models.ItemInOrder
        fields = ('item', 'quantity', 'price', 'tax_rate', 'created')


class BaseOrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='id.hex', read_only=True)
    amount = core_fields.DecimalField(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = models.Order
        fields = (
            'id', 'items', 'amount', 'currency', 'status',
            'status_changed', 'created')

        read_only_fields = ('status', 'status_changed')


class OrderWriteOnlySerializer(BaseOrderSerializer):
    items = ItemInOrderWriteOnlySerializer(many=True, source='items_in_order')

    def create(self, validated_data):
        items = validated_data.pop('items_in_order')
        order = super().create(validated_data)

        for validated_data in items:
            item = validated_data.pop('id')
            models.ItemInOrder.objects.create(
                order_id=order.id,
                item_id=item.id,
                price=item.price,
                tax_rate=item.tax_rate,
                **validated_data)

        order.amount = order._get_amount()
        order.save()
        return order


class OrderReadOnlySerializer(BaseOrderSerializer):
    items = ItemInOrderReadOnlySerializer(many=True, source='items_in_order')
