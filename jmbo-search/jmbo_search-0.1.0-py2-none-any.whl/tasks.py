from importlib import import_module

from celery import shared_task


@shared_task
def update_index(callback=None, callback_params=None, **kwargs):
    if callback is not None:
        module_name, func_name = callback.rsplit(".", 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
        func(callback_params)
