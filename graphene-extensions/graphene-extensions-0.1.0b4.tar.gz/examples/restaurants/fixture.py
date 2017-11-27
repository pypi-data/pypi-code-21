from django.db import transaction

from .models import Owner, Restaurant, Pizza, Topping


@transaction.atomic()
def restaurants_fixture():
    if any(model.objects.exists() for model in (Owner, Restaurant, Pizza, Topping)):
        return print('Some restaurant objects already exist, skipping...')

    luigi = Owner.objects.create(name='Luigi')
    john = Owner.objects.create(name='John')

    cheese = Topping.objects.create(name='cheese')
    salami = Topping.objects.create(name='salami')
    basil = Topping.objects.create(name='basil')
    tomato = Topping.objects.create(name='tomato')
    ham = Topping.objects.create(name='ham')
    ananas = Topping.objects.create(name='ananas')

    italian_pizzeria = Restaurant.objects.create(name='Italian pizzeria', owner=luigi)
    new_york_pizza = Restaurant.objects.create(name='New York pizza', owner=john)

    margarita = Pizza.objects.create(name='margarita', restaurant=italian_pizzeria)
    pepperoni = Pizza.objects.create(name='pepperoni', restaurant=italian_pizzeria)
    hawaii = Pizza.objects.create(name='hawaii', restaurant=new_york_pizza)

    margarita.toppings.set((cheese, tomato, basil))
    pepperoni.toppings.set((cheese, tomato, basil, salami))
    hawaii.toppings.set((ananas, tomato, ham, cheese))

    print('Restaurant fixture loaded!')
