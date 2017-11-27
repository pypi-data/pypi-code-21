# -*- coding: utf-8 -*-
from .base import BaseCommand, argument, option, register   # noqa
from modelhub.core.models import Model


@register("list")
class Command(BaseCommand):

    arguments = [
        option("--local_only", "-l", is_flag=True)
    ]

    def run(self, local_only):
        """List all models on modelhub."""
        models = Model.all()
        for model in models:
            if local_only and not model.local_exists:
                continue
            self.echo(model.name)
