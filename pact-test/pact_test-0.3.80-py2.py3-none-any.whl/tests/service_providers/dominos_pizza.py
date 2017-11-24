import os
import sys
import json
import requests
from pact_test.models.service_provider_test import *


def get_pizza(type):
    pepperoni = type == 'pepperoni'
    out = requests.post(
        'http://localhost:9999/pizzas/' + type + '/',
        data=json.dumps({'pepperoni': pepperoni})
    )
    return out.json() if out.status_code == 200 else out


@service_consumer('UberEats')
@has_pact_with('Dominos Pizza')
class DominosPizzaTest(ServiceProviderTest):

    @given('a pizza exists')
    @upon_receiving('a request for a NON-pepperoni pizza')
    @with_request({'method': 'post', 'path': '/pizzas/margherita/', 'body': {'pepperoni': False}})
    @will_respond_with({'status': 400, 'body': {'reason': 'we ONLY serve pepperoni pizza'}})
    def test_get_pizza(self):
        pizza = get_pizza('margherita')
        assert pizza.status_code == 400

    @given('a pizza exists')
    @upon_receiving('a request for a pepperoni pizza')
    @with_request({'method': 'post', 'path': '/pizzas/pepperoni/', 'body': {'pepperoni': True}})
    @will_respond_with({'status': 200, 'body': json.dumps({'type': 'pepperoni'})})
    def test_get_pepperoni_pizza(self):
        pizza = get_pizza('pepperoni')
        assert pizza['type'] == 'pepperoni'
