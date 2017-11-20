# -*- coding: utf-8 -*-
from modelhub.core import models


def get_model_path(model_name, version=None, ensure_newest_version=False):
    model = models.Model(model_name)
    if version:
        version = model.get_version(version)
    else:
        if ensure_newest_version:
            version = model.latest_version
        else:
            for version in reversed(model.versions):
                if version.local_exists:
                    break
            else:
                version = model.latest_version

    if not version.local_exists:
        version.checkout()
    return version.local_path
