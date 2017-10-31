"""[summary].

[description]
"""
import os
from megalus.core import utils
from megalus.projects.config import profile


def run(application, dev):
    """[summary].

    [description]

    Arguments:
        application {[type]} -- [description]
        dev {[type]} -- [description]

    Returns
    -------
        bool -- [description]

    """
    data = profile.get_data()
    if not data:
        return False

    container_id, name = utils.get_app(
        application=application,
        title="Rodar em modo Watch",
        data=data
    )
    if not name:
        return False

    dc_data = utils.get_compose_data(data)

    try:
        app_folder = dc_data['services'][name][
            'build']['context'].split('/')[-1]
    except BaseException:
        utils.console('Pasta não encontrada.', style="error")
        return False

    watch_path = os.path.join(
        data.project_path,
        app_folder,
        'frontend'
    )
    if dev:
        os.system(
            'cd {}/ && ./node_modules/.bin/webpack --config '
            'webpack.config.js\n'.format(
                watch_path)
        )

    os.system(
        'cd {}/ && ./node_modules/.bin/webpack --config '
        'webpack.config.js --watch\n'.format(
            watch_path)
    )
