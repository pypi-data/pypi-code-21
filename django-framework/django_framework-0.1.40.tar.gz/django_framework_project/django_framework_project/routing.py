import importlib
from channels import route

from django.conf import settings


from django_framework.django_helpers.channel_helpers import load_channel_routing

channel_routing = []

channel_routing += load_channel_routing