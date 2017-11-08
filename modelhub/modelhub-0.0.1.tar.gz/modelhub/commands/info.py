# -*- coding: utf-8 -*-
import os
from .base import BaseCommand, argument, option, types, register # noqa
from modelhub.core.models import Model


@register("info")
class Command(BaseCommand):

    arguments = [
        argument("model_path_or_name"),
    ]

    def run(self, model_path_or_name):
        """
        Get info of a model
        """

        if self._is_model_path(model_path_or_name):
            self.local_model_info(model_path_or_name)
        else:
            model_name, version = Model.split_name_version(model_path_or_name)
            model = Model.get(name=model_name)
            if version is None:
                self.remote_list_version(model)
            else:
                self.remote_version_info(model.get_version(version))

    def _is_model_path(self, model_path_or_name):

        if "/" in model_path_or_name:
            return True
        if self._validate_path(model_path_or_name):
            return True

        return False

    def _validate_path(self, local_path):
        return os.path.exists(local_path)

    def local_model_info(self, model_path):
        # from tensorflow.contrib.saved_model.python.saved_model import reader
        from tensorflow.python.tools.saved_model_cli import _show_all
        # saved_model = reader.read_saved_model(model_path)
        try:
            _show_all(model_path)
        except OSError as e:
            print(e)
            print("Hint: perhaps forget version? Try add version_number")

    def remote_list_version(self, model):
        self._print_model_info(model)
        print("Versions:")
        for version in reversed(model.versions):
            print("""id:\t{version.seq}
local:{is_local}
user:\t{version.submit_username}<{version.submit_email}>
date:\t{version_datetime}
comment:\t{version.comment}
require GPU:\t{version.require_gpu}
size:\t{version.compressed_size:,}
            """.format(model=model.manifest, version=version.manifest, version_datetime=version.manifest.submit_datetime.ToDatetime(), is_local=version.local_exists))

    def _print_model_info(self, model):
        print("""name:\t{model.name}
desc:\t{model.description}
owner:\t{model.owner_name}<{model.owner_email}>
            """.format(model=model.manifest))

    def remote_version_info(self, version):
        self._print_model_info(version.model)
        print(version.manifest)
