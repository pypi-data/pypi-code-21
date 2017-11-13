# -*- coding: utf-8 -*-
from modelhub.core.models import Model, ModelVersion
from .base import BaseCommand, argument, option, types, register


@register('checkout')
class Command(BaseCommand):

    arguments = [
        argument("model_name"),
        option("-o", "--output", type=types.Path(), help='the DIR to put checkouted model')

    ]

    def run(self, model_name, output=None):
        """Download a model to local disk."""
        model_name, version = Model.split_name_version(model_name)
        print("verifying...")
        try:
            model = Model.get(name=model_name)
        except Model.DoesNotExist:
            self.echo("Model {model_name} is not exist".format(model_name=model_name))
            return
        try:
            model_version = model.get_version(version)
        except ModelVersion.DoesNotExist:
            self.echo("Model {model.name} has no version: {version}".format(model=model, version=version))
            return

        if not output:
            output = model_version.local_path
        model_version.checkout(output)
        self.echo("Checkout {model.name}@{model_version.manifest.seq} Done, locate at {output}".format(**locals()))
