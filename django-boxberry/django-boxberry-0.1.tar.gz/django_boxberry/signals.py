# coding: utf-8
from django.db.models.signals import Signal

new_parsel_status = Signal(providing_args=['status'])
