# -*- coding: utf-8 -*-
from .base import BaseCommand, argument, option, register   # noqa
from modelhub.core.models import Model


@register("list")
class Command(BaseCommand):

    arguments = []

    def run(self):
        """List all models on modelhub."""
        models = Model.all()
        for model in models:
            self.echo(model.name)
