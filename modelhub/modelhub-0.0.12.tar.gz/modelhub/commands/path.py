# -*- coding: utf-8 -*-
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model


@register("path")
class Command(BaseCommand):

    arguments = [
        argument("model_name")
    ]

    def run(self, model_name):
        """Show local path of the given model and version"""
        model_name, version = Model.split_name_version(model_name)
        model = Model.get_local(model_name, fallback_to_remote=False)
        if not version:
            version = model.latest_local_version
        else:
            version = model.get_version(version)
            if not version.local_exists:
                raise version.DoesNotExist("Version {version.manifest.seq} dost not exist at local".format(version=version))
        self.echo(version.local_path)
