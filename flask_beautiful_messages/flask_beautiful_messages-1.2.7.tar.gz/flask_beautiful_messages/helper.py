import os

import flask_multiple_static_folders


def get_package_root_dir():
    file_path = os.path.realpath(__file__)
    return os.path.dirname(file_path)


def get_package_template_dir():
    package_dir = get_package_root_dir()
    return os.path.join(package_dir, 'templates')


def get_package_static_dir():
    package_dir = get_package_root_dir()
    return os.path.join(package_dir, 'static')


def setup_app_with_multiple_static_folders(app):
    return flask_multiple_static_folders.transform_app(app)
