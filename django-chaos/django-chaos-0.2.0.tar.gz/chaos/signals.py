# coding: utf-8
from django.dispatch import Signal


task_status_changed = Signal(providing_args=['task', 'status', 'changes', 'user'])
