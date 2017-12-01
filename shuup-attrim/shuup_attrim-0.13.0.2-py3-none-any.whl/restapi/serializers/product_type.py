from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from shuup.core.models import ProductType, Product


class ProductTypeSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)

    class Meta:
        fields = ('id', 'translations')
        model = ProductType
