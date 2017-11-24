# -*- coding: utf-8 -*

from modelhub.core.models import Model, ModelVersion
from .base import BaseCommand, argument, option, types, register


@register("submit")
class Command(BaseCommand):

    arguments = [
        argument("model_name", type=types.STRING),
        argument("model_path", type=types.Path(file_okay=False, exists=True), default="."),
        option("--comment", "-m", prompt=True, help='model name shoule be a str')
    ]

    def run(self, model_name, model_path, comment):
        """Submit your model to modelhub."""
        try:
            model = Model.get(model_name)
        except Model.DoesNotExist:
            self.echo("Error: model {model_name} not exist, you need execute 'modelhub create {model_name}' ahead".format(model_name=model_name))
            return
        submit_username, submit_email = self.get_user_info()
        try:
            model_version = ModelVersion.create(model, model_path, comment=comment, submit_username=submit_username, submit_email=submit_email)
        except ModelVersion.ValidationError as e:
            self.echo(e.args[0])
        else:
            self.echo("Done submit model {model.name}, version {model_version.manifest.seq}, size {model_version.manifest.compressed_size}".format(**locals()))
