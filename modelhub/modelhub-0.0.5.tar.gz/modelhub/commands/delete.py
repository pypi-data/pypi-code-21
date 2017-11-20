# -*- coding: utf-8 -*-
from modelhub.core.models import Model
from .base import BaseCommand, argument, option, register


@register("delete")
class Command(BaseCommand):

    arguments = [
        argument("model_name"),
        option("-r", "--remote", is_flag=True, help='CAUTION! This removes your model from modelhub remotely.'),
        option("-f", "--force", is_flag=True, help='CAUTION! This removes your model permantly.')
    ]

    def run(self, model_name, remote=False, force=False):
        """Delete your model locally or remotely."""
        model_name, version = Model.split_name_version(model_name)
        username, email = self.get_user_info()

        if remote:
            model = Model.get(name=model_name)
            if not version:
                if email == model.manifest.owner_email:
                    if force or input("{count} version of model {model.name} will be removed permanently, confirm delete? Input 'yes':\n>>".format(model=model, count=len(model.versions))) == "yes":
                        model.delete()
                else:
                    self.echo("You have no permission to delete model {model.name}".format(model=model))
            else:
                model_version = model.get_version(version)
                if email != model.owner_email and email != version:
                    self.echo("You have no permission to delete model {model.name}@{version}".format(model=model, version=version))
                model_version.delete()
        else:
            model = Model(name=model_name)
            if not version:
                if force or input("all local versions of model {model.name} will be removed, confirm delete? Input 'yes':\n>>".format(
                    model=model,
                    # count=len([model.versions for )
                )) == "yes":
                    model.delete_local()
            else:
                model_version = model.get_version(version)
                model_version.delete_local()
