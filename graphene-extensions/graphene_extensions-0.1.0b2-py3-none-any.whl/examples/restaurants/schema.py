import graphene
from graphene_extensions import ModelListField

from graphene_extensions import ModelType

from .models import Owner, Restaurant, Pizza, Topping


class OwnerType(ModelType):
    class Meta:
        model = Owner
        fields = '__all__'


class RestaurantType(ModelType):
    class Meta:
        model = Restaurant
        fields = '__all__'


class PizzaType(ModelType):
    class Meta:
        model = Pizza
        fields = '__all__'


class ToppingType(ModelType):
    class Meta:
        model = Topping
        fields = '__all__'


class Query(graphene.ObjectType):
    owners = ModelListField(OwnerType)
    restaurants = ModelListField(RestaurantType)
    pizzas = ModelListField(PizzaType)
    toppings = ModelListField(ToppingType)


schema = graphene.Schema(query=Query)
