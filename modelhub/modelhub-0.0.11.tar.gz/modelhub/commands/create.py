# -*- coding: utf-8 -*-
from modelhub.core.models import Model
from .base import BaseCommand, argument, option, register


@register("create")
class Command(BaseCommand):

    arguments = [
        argument("name"),
        option("-m", "--desc", prompt=True, help='describe your model here.')
    ]

    def run(self, name, desc):
        """Create a new model."""
        try:
            Model.get(name=name)
        except Model.DoesNotExist:
            pass
        else:
            self.echo("Model {name} already exists".format(name=name))
            return
        Model.create(name, desc, *self.get_user_info())
