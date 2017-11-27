# -*- coding: utf-8 -*-
from modelhub.core import models
from .base import BaseCommand, argument, option, types, register  # noqa


@register('copy')
class Command(BaseCommand):

    arguments = [
        argument("model_name"),
        argument("new_model_name"),
    ]

    def run(self, model_name, new_model_name):
        """copy model to a new name"""
        model = models.Model.get(model_name)
        model.copy(new_model_name)
