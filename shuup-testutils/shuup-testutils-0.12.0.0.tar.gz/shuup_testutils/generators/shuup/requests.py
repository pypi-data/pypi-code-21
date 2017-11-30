from django.http import HttpRequest
from django.test import RequestFactory
from shuup.testing.factories import get_default_shop
from shuup.testing.factories import create_random_person
from shuup.testing.utils import apply_request_middleware


def gen_shuup_request(factory: RequestFactory) -> HttpRequest:
    request = factory.get('/')
    request.shop = get_default_shop()
    request.customer = create_random_person()
    apply_request_middleware(request)
    return request
