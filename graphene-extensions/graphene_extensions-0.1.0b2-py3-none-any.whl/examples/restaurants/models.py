from django.db import models

import graphene

from graphene_extensions.decorators import annotate_type, graphene_property


class Owner(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    owner = models.OneToOneField(Owner)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Topping(models.Model):
    name = models.CharField(max_length=120)

    @graphene_property(graphene.String)
    def str(self):
        return str(self)

    def __str__(self):
        return f'{self.name}'


class Pizza(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='pizzas')
    name = models.CharField(max_length=120)
    toppings = models.ManyToManyField(Topping, related_name='pizzas')

    @annotate_type(graphene.String)
    def str(self):
        return str(self)

    def __str__(self):
        return f'{self.name}'
